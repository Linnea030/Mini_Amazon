import socket
import time
import threading
import select
import psycopg2

import google.protobuf
import world_amazon_pb2
import amazon_ups_pb2
import helper
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

# send to world
def send_world(socket_world,conn):
    while True:
        # check whether there is any unprocessed order(is_processed==False)
        # if so, send APurchasemore to world, and ACreatePackage to UPS
        cursor = conn.cursor()
        with helper.order_lock_db:
            # look for newly-created order
            sql = '''SELECT id, product_id, count FROM web_order WHERE is_processed = FALSE;'''
            cursor.execute(sql)
            new_order = cursor.fetchone()
        
            # if has newly-created order
            if new_order:
                with helper.seq_lock:
                    # APurchasemore to world
                    APurchasemore = helper.generate_buy(new_order, conn)
                    helper.add_toWorld(APurchasemore)

                    # send ACreatePackage to UPS
                    ACreatePackage = helper.generate_ACreatePackage(new_order[0], conn)
                    helper.add_messageToUPS(ACreatePackage)
                
        # select an ACommands to send
        time.sleep(1)
        with helper.toworld_lock:
            if (len(helper.toWorld) > 0):
                keys = list(helper.toWorld)
                for key in keys:
                #for key in helper.toWorld.keys():
                    if key in helper.toWorld:
                        print('send message to world with seq_num '+str(key))
                        helper.send_msg(socket_world, helper.toWorld[key])

# recv from world warehouse
def recv_world(socket_world,conn):
    cursor = conn.cursor()
    while True:
        world_response = world_amazon_pb2.AResponses()
        msg = helper.recv_msg(socket_world)
        if msg == "":
            continue
        world_response.ParseFromString(msg)
        print("----------Recv from World----------- \n"+str(world_response))

        # handle acks
        ######如果收到ack则将发送的command从toWorld pop出来 不再send该command
        with helper.toworld_lock:
            for ack in world_response.acks:
                keys = list(helper.toWorld)
                for key in keys:
                    if ack == key and key in helper.toWorld:
                        helper.toWorld.pop(key)

        # handle AErr
        if len(world_response.error) > 0:
            print("From World: error!")
            for res in world_response.error:
                print("Error: " + res.err + " with originsequm " + str(res.originseqnum))
                print("Error seqnum = " + str(res.seqnum))
                helper.ack_to_world(socket_world,res.seqnum)

        # recv APurchaseMore(arrived)
        if len(world_response.arrived) > 0:
            print("From World: APurchaseMore")
            for arrive in world_response.arrived:
                # ack to world
                helper.ack_to_world(socket_world,arrive.seqnum)
                # acquire this item's count now in the warehouse(database)
                ######提取目前所有的库存数量
                sql = '''SELECT num_in_stock FROM web_product WHERE id = %s;'''
                cursor.execute(sql, (arrive.things[0].id,))
                curr_count = cursor.fetchone()
                # the item's count after the replenish
                remaining_items = arrive.things[0].count + curr_count[0]

                ######提取对应的订单
                sql = '''SELECT id, count FROM web_order WHERE is_processed = TRUE AND is_packed = FALSE AND product_id = %s;'''
                cursor.execute(sql, (arrive.things[0].id,))
                orders = cursor.fetchall()
                ######所有订单中，寻找符合world购买对应数量的商品的订单进行处理
                for order in orders:
                    # when remaining size>=0, update the order's is_packed and is_order_placed to true
                    if remaining_items >= order[1]:
                        remaining_items -= order[1]
                        # update database (is_packed,is_order_placed,status), generate APack
                        sql = '''UPDATE web_order SET is_packed = TRUE, status = 'packing' WHERE id = %s;'''
                        cursor.execute(sql, (order[0],))
                        conn.commit()

                        sql = '''SELECT id, description FROM web_product WHERE id = %s;'''
                        cursor.execute(sql, (arrive.things[0].id,))
                        product = cursor.fetchone()

                        ######返回Apack给world
                        with helper.seq_lock:
                            APack= helper.generate_pack(order, product)
                            helper.add_toWorld(APack)
                            print("Add to World dic: Apack - In received from APurchaesMore!")
                        # update database, generate ASendTruck
                        sql = '''UPDATE web_order SET is_truck_requested = TRUE WHERE id = %s;'''
                        cursor.execute(sql, (order[0],))
                        conn.commit()
                        with helper.seq_lock:
                            ############ send给UPS 要一辆卡车
                            APickupReq = helper.generate_APickupReq()
                            helper.add_messageToUPS(APickupReq)
                            print("Add to UPS dic: APickupReq - In received from APurchaesMore!")
                    else:
                        continue
                ######更新库存量
                #update count in warehouse (it should still be 0)
                sql = '''UPDATE web_product SET num_in_stock = %s WHERE id = %s;'''
                cursor.execute(sql, (remaining_items,arrive.things[0].id))
                conn.commit()

        #recv Apacked(topack)
        if len(world_response.ready) > 0:
            print("From World: APacked!")
            for pack in world_response.ready:
                #ack to world
                helper.ack_to_world(socket_world, pack.seqnum)
                #change status to packed (this is useful to the next step)
                with helper.order_lock_db:
                    sql = '''UPDATE web_order SET status = 'packed' WHERE id = %s;'''
                    cursor.execute(sql, (pack.shipid,))
                    conn.commit()
                    
                # if is_truck_arrived, generate a APutOnTruck Acommand and send it to world
                # also, send ALoad to UPS
                with helper.order_lock_db:
                    sql = '''SELECT web_order.id, warehouse_id, truck_id, status, address_x, address_y, ups_username, 
                            web_product.id, count, web_product.name, web_product.description 
                            FROM web_order, web_product 
                            WHERE web_order.product_id=web_product.id AND is_truck_arrived=TRUE AND web_order.id = %s;'''
                    cursor.execute(sql, (pack.shipid, ))
                    order_to_putOnTruck = cursor.fetchone() # order = []
                
                if order_to_putOnTruck is not None:
                    # update database
                    sql = '''UPDATE web_order SET is_loaded = TRUE, status = 'loading' WHERE id = %s;'''
                    cursor.execute(sql, (order_to_putOnTruck[0],))
                    conn.commit()
                    
                    with helper.seq_lock:
                        APutOnTruck = helper.generate_APutOnTruck(order_to_putOnTruck)
                        helper.add_toWorld(APutOnTruck)
                        print("Add to World dic: APutOnTruck - In received APacked from World")
                    
                    # send ALoad to UPS
                    with helper.seq_lock:
                        ALoad = helper.generate_ALoad(order_to_putOnTruck)
                        helper.add_messageToUPS(ALoad)
                        print("Add to UPS dic: ALoad - In received APacked from World")
                            
        #recv ALoaded(loaded)
        if len(world_response.loaded)>0:
            print("From World: ALoaded!")
            
            last_shipid = -9999
            for load in world_response.loaded:
                #ack to world
                helper.ack_to_world(socket_world, load.seqnum)
                #change status to loaded
                sql = '''UPDATE web_order SET status = 'loaded' WHERE is_loaded = TRUE AND id = %s;'''
                cursor.execute(sql, (load.shipid,))
                conn.commit()
                #generate AFinishLoading
                sql = '''SELECT id FROM web_order WHERE id = %s;'''
                cursor.execute(sql, (load.shipid,))
                order = cursor.fetchone()              
                    
                with helper.order_lock_db:
                    sql = '''UPDATE web_order SET status = 'delivering', is_delivered = TRUE WHERE status = 'loaded' AND id = %s;'''
                    cursor.execute(sql, (load.shipid,))
                    conn.commit()
                
                last_shipid = load.shipid
            
            # note: need to be modified
            # find whether there is any order belonging to the current truck but not loaded
            count = 9999
            truckid = -9999
            with helper.order_lock_db:
                sql = '''SELECT truck_id FROM web_order WHERE id = %s;'''
                cursor.execute(sql, (last_shipid, ))
                truckid_list = cursor.fetchone() 
                truckid = truckid_list[0]
                
                sql = '''SELECT COUNT(*) FROM web_order WHERE truck_id = %s AND status<>'loaded' AND status<>'delivering' AND status<>'delivered';'''
                cursor.execute(sql, (truckid, ))
                count_list = cursor.fetchone() 
                count = count_list[0]
            
            # if every order belonging to the truck is loaded
            if count==0:
                with helper.seq_lock:
                    ALoadComplete = helper.generate_ALoadComplete(truckid)
                    helper.add_messageToUPS(ALoadComplete)
                    print("Add to UPS: ALoadComplete - In received ALoaded from world")

        #recv APackage(packagestatus)
        if len(world_response.packagestatus)>0:
            print("From World: APackage!")
            for packagestatus in world_response.packagestatus:
                #ack to world
                helper.ack_to_world(socket_world, packagestatus.seqnum)
                #change status to loaded
                sql = '''UPDATE web_order SET status = %s WHERE id = %s;'''
                cursor.execute(sql, (packagestatus.status, packagestatus.packageid))
                conn.commit()

# send message to UPS
# periodically look up for message to be sent to UPS in the dictionary messageToUPS
# after sending the message, directly pop the message out
def sendMsgToUPS():
    while True:
        # select an a msg to send
        time.sleep(1)#wait 1 s
        with helper.messageToUPS_lock:
            if(len(helper.messageToUPS)>0):
                keys = list(helper.messageToUPS)
                for key in keys:
                #for key in tools.toUPS.keys():
                    if key in helper.messageToUPS:
                        # connect with UPS server
                        print("in UPS send")
                        sk_UPS = helper.connectUPS()
                        helper.send_msg(sk_UPS, helper.messageToUPS[key])
                        
                        print("send message to UPS with seqnum " + str(key))
                        # close the socket connected with UPS
                        sk_UPS.close()
                        # since no ack with UPS, pop the msg after sending
                        helper.messageToUPS.pop(key)
                        
def recvMsgFromUPS(dbConn):
    # set up socket as a server
    sk_amazon = helper.setUpAmazonServer()
    
    # keep trying to accept UPS connection
    while True:
        connWithUPS, address = sk_amazon.accept()
        print("UPS: accept UPS connection")
        
        # recv msg from UPS
        recv_msg = helper.recv_msg(connWithUPS)
        if recv_msg == "":
            connWithUPS.close()
            continue
        
        ups_command = amazon_ups_pb2.UCommand()
        ups_command.ParseFromString(recv_msg)
        
        print("----- Receive from UPS -----")
        print(str(ups_command))
        
        # handle UCommand
        helper.UCommandHandler(ups_command, dbConn)
        
        connWithUPS.close()

if __name__ == '__main__':
    # Connect to database
    conn = helper.connect_db()
    cursor = conn.cursor()

    # # create warehouse
    sql = '''INSERT INTO web_warehouse (whid, x, y) VALUES (%s, %s, %s) ON CONFLICT(whid) DO NOTHING'''
    cursor.execute(sql,(1, 1, 1))
    conn.commit()

    # # create category
    sql = '''INSERT INTO web_category (id, category) VALUES (%s, %s) ON CONFLICT(id) DO NOTHING'''
    cursor.execute(sql,(1, 'FOOD'))
    conn.commit()
    sql = '''INSERT INTO web_category (id, category) VALUES (%s, %s) ON CONFLICT(id) DO NOTHING'''
    cursor.execute(sql,(2, 'STUDY'))
    conn.commit()

    # # create product
    sql = '''INSERT INTO web_product (id, name, description, price, avg_score, category_id, num_in_stock) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT(id) DO NOTHING'''
    cursor.execute(sql,(1, 'book', 'a useful book', 10, 5, 2, 3))
    conn.commit()
    sql = '''INSERT INTO web_product (id, name, description, price, avg_score, category_id, num_in_stock) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT(id) DO NOTHING'''
    cursor.execute(sql,(2, 'chips', 'good good', 20, 3, 1, 2))
    conn.commit()

    # Connect to the world with world id = 1
    cmd = world_amazon_pb2.AConnect()
    cmd.worldid = 1
    cmd.isAmazon = True
    warehouse = cmd.initwh.add()
    warehouse.id = 1
    warehouse.x = 1
    warehouse.y = 1
    socket_world = helper.connectWorld(cmd)
    print('Connect to world!')

    # #handle the communication with world, UPS
    th_world_send = threading.Thread(target=send_world, args=(socket_world, conn))
    th_world_recv = threading.Thread(target=recv_world, args=(socket_world, conn))
    th_UPS_recv = threading.Thread(target=recvMsgFromUPS,args=(conn,))
    th_UPS_send = threading.Thread(target=sendMsgToUPS)

    # #start threads
    th_world_send.start()
    th_world_recv.start()
    th_UPS_send.start()
    th_UPS_recv.start()