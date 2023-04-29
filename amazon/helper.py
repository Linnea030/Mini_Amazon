import socket
import threading
import select
import psycopg2

import world_amazon_pb2
import amazon_ups_pb2

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

# seqnum for sending
order_lock_db = threading.Lock()
seq_num = 1
seq_lock = threading.Lock()

# <seq_num, ACommand> for world
# <seq_num, AMsg> for UPS
toWorld = {}
messageToUPS = {}
# the lock for the dict
toworld_lock = threading.Lock()
#the lock for the dict
messageToUPS_lock = threading.Lock()

#for connection with UPS and World
###group1
UPSHOST, UPSPORT = "vcm-30609.vm.duke.edu",22222
WHOST, WPORT = "vcm-30609.vm.duke.edu",23456
###group2
# UPSHOST, UPSPORT = "vcm-33379.vm.duke.edu",22222
# WHOST, WPORT = "vcm-33379.vm.duke.edu",23456
###自测用
# UPSHOST, UPSPORT = "vcm-30971.vm.duke.edu", 22222
# WHOST, WPORT = "vcm-30971.vm.duke.edu", 23456

# for setting up socket as server
AmazonHOST, AmazonPORT = "0.0.0.0", 11111

################### toUPS: helper functions for client to set up socket and connect, and for server to set up socket ##################

# connect with UPS server as client and return the socket set up
def connectUPS():
    sk_UPS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    UPS_ip = socket.gethostbyname(UPSHOST)
    
    ip_port = (UPS_ip, UPSPORT)
    sk_UPS.connect(ip_port)

    print("UPS: connected with UPS")
    
    return sk_UPS

# set up the socket server to connect with UPS
# return the socket_amazon
# use socket_amazon to accept connection
def setUpAmazonServer():
    ip_port = (AmazonHOST, AmazonPORT)
               
    sk_amazon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk_amazon.bind(ip_port)
    sk_amazon.listen(20)

    print("UPS: Server with UPS set up")
    
    return sk_amazon
    
###################### send and recv messages(including send acks) and connection function #####################

#send message to socket
def send_msg(socket,msg):
    to_send = msg.SerializeToString()
    _EncodeVarint(socket.sendall,len(to_send))
    socket.sendall(to_send)

# recv message by socket and decode it
def recv_msg(socket):
    var_int_buff = []
    while True:
        buf = socket.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = socket.recv(msg_len)
    print("---------------Recv message---------------\n"+str(whole_message))
    return whole_message

#send ack to world
def ack_to_world(s,ack):
    ack_cmd = world_amazon_pb2.ACommands()
    ack_cmd.acks.append(ack)
    ack_cmd.disconnect = False
    send_msg(s,ack_cmd)

#connect to world
def connectWorld(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    world_ip = socket.gethostbyname(WHOST)
    s.connect((world_ip,WPORT))
    send_msg(s,cmd)
    connect_reply = world_amazon_pb2.AConnected()
    connect_reply.ParseFromString(recv_msg(s))
    print("Connect to world" + str(connect_reply.worldid) + " with result "+ str(connect_reply.result))
    return s

#connect to database
def connect_db():
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="db",
        port="5432"
    )
    print("Opened database successfully by backend!")
    return conn

#########################generate ACommands to world############################

#add message toWorld
#args: (seq_num(全局变量), msg)
def add_toWorld(msg):
    global seq_num
    toWorld[seq_num] = msg
    seq_num=seq_num+1

#generate APurchasemore
#买买家下单对应个数的商品 这样可以保证每次都有库存
def generate_buy(buying_order, conn):
    cursor = conn.cursor()
    print("Generate APurchaseMore")
    ######找到对应购买的product
    wh_purchase_num = buying_order[2]
    sql = '''SELECT id, name, description FROM web_product WHERE id = %s;'''
    cursor.execute(sql, (buying_order[1],))
    product_to_buy = cursor.fetchone()
    ######更新处理过的order表格
    sql = '''UPDATE web_order SET is_processed = TRUE, status = 1 WHERE id = %s;'''
    cursor.execute(sql, (buying_order[0],))
    conn.commit()
    #generate ACommands
    Acmd = world_amazon_pb2.ACommands()
    Acmd.disconnect = False
    tobuy = Acmd.buy.add()
    #only one warehouse with whid = 1
    tobuy.whnum = 1
    tobuy.seqnum = seq_num
    item = tobuy.things.add()
    item.id = product_to_buy[0]
    item.description = product_to_buy[2]
    item.count = wh_purchase_num
    return Acmd

#generate APack
def generate_pack(order, product):
    print("Generate APack")
    Acmd = world_amazon_pb2.ACommands()
    Acmd.disconnect = False
    topack = Acmd.topack.add()
    topack.whnum = 1
    topack.shipid = order[0]#packageid
    topack.seqnum = seq_num
    item = topack.things.add()
    item.id = product[0]
    item.description = product[1]
    item.count = order[1]#count
    return Acmd

#generate APutOnTruck
# @parameter:
# list order: (web_order.id, warehouse_id, truck_id, status, address_x, address_y, ups_username, 
#                            web_product.id, count, web_product.name, web_product.description)
def generate_APutOnTruck(order):
    print("Generate APutOnTruck")
    
    Acmd = world_amazon_pb2.ACommands()
    
    Acmd.disconnect = False
    
    toload = Acmd.load.add()
    toload.whnum = order[1]
    toload.truckid = order[2]
    toload.shipid = order[0]
    toload.seqnum = seq_num
    
    return Acmd

#generate AQuery
def generate_query(order):
    print("Generate AQuery")
    Acmd = world_amazon_pb2.ACommands()
    Acmd.disconnect = False
    query = Acmd.queries.add()
    query.packageid = order[0]#packageid
    query.seqnum = seq_num
    return Acmd

#########################generate ACommands to UPS############################
#add to messageToUPS
#args: (seq_num(全局变量), msg)
def add_messageToUPS(msg):
    global seq_num
    messageToUPS[seq_num] = msg
    seq_num += 1
    print(str(msg))

# @parameter:
# order_id
def generate_ACreatePackage(order_id, conn):
    cursor = conn.cursor()
    sql = '''SELECT web_order.id, warehouse_id, status, address_x, address_y, ups_username, 
            web_product.id, count, web_product.name, web_product.description 
            FROM web_order, web_product 
            WHERE web_order.product_id=web_product.id AND web_order.id = %s;'''
    cursor.execute(sql, (order_id, ))
    order_to_create = cursor.fetchone() # order = []
    
    print("Generate ACreatePackage")
    ACommand = amazon_ups_pb2.ACommand()
    ACreatePackage = ACommand.create.add()
    
    ACreatePackage.hid = order_to_create[1]
    ACreatePackage.packageid = order_to_create[0]
    ACreatePackage.location_x = order_to_create[3]
    ACreatePackage.location_y = order_to_create[4]
    ACreatePackage.seqnum = seq_num
    ACreatePackage.email = order_to_create[5]

    AItem = ACreatePackage.itemInfo.add()
    AItem.itemid = order_to_create[6]
    AItem.num = order_to_create[7]
    AItem.name = order_to_create[8]
    AItem.desc = order_to_create[9]

    return ACommand

# consider the warehouse id
def generate_APickupReq():
    print("Generate APickupReq")
    ACommand = amazon_ups_pb2.ACommand()

    APickupReq = ACommand.pickups.add()
    APickupReq.hid = 1
    APickupReq.seqnum = seq_num

    return ACommand

# @parameter:
# list order: (web_order.id, warehouse_id, truck_id, status, address_x, address_y, ups_username, 
#                            web_product.id, count, web_product.name, web_product.description)
def generate_ALoad(order):
    print("Generate ALoad")
    ACommand = amazon_ups_pb2.ACommand()
    ALoad = ACommand.toload.add()
    
    ALoad.truckid = order[2]
    ALoad.packageid = order[0]
    ALoad.seqnum = seq_num
   
    return ACommand

# @parameter: truck_id is a integer
def generate_ALoadComplete(truck_id):
    print("Generate ALoadComplete")
    
    ACommand = amazon_ups_pb2.ACommand()
    
    ALoadComplete = ACommand.comp.add()
    ALoadComplete.truckid = truck_id
    ALoadComplete.seqnum = seq_num
    
    return ACommand


######################### UCommand Handler ############################

def UCommandHandler(ups_command, dbConn):
    cursor = dbConn.cursor()
    
    if len(ups_command.uarrived)>0:
        for arrivedTruck in ups_command.uarrived:
            print("Message from UPS: received UArrived!")
            
            # find is there any unassigned package
            order_lock_db.acquire()
            sql = '''SELECT *
                    FROM web_order
                    WHERE warehouse_id = %s AND is_truck_requested = TRUE AND is_truck_assigned=FALSE;'''
            cursor.execute(sql, (arrivedTruck.whid, ))
            unassigned_order = cursor.fetchone() # orders = []
            
            # if there is no unassigned order
            # send ALoadComplete to UPS
            if unassigned_order is None:
                with seq_lock:
                    ALoadComplete = generate_ALoadComplete(arrivedTruck.truckid)
                    add_messageToUPS(ALoadComplete)
                    print("Add to UPS: ALoadComplete - in TruckArrived")
                order_lock_db.release()
                continue

            # update db tuples with the truckid
            # assign the truck to the current truck if there is any package unassigned
            sql = '''UPDATE web_order SET truck_id = %s, is_truck_assigned=TRUE WHERE warehouse_id = %s AND is_truck_requested = TRUE AND is_truck_assigned=FALSE;'''
            cursor.execute(sql,(arrivedTruck.truckid, arrivedTruck.whid))
            dbConn.commit()

            sql = '''UPDATE web_order SET is_truck_arrived = TRUE WHERE is_truck_arrived = FALSE AND truck_id = %s;'''
            cursor.execute(sql, (arrivedTruck.truckid,))
            dbConn.commit()
                
            #if order is packed, generate a APutOnTruck Acommand and send it to world'
            sql = '''SELECT web_order.id, warehouse_id, truck_id, status, address_x, address_y, ups_username, 
                    web_product.id, count, web_product.name, web_product.description 
                    FROM web_order, web_product 
                    WHERE web_order.product_id=web_product.id AND is_truck_arrived = TRUE AND truck_id = %s;'''
            cursor.execute(sql, (arrivedTruck.truckid, ))
            orders = cursor.fetchall() # orders = [][]

            order_lock_db.release()
            
            for order in orders:
                if order[3] == 'packed':
                    with order_lock_db:
                        sql = '''UPDATE web_order SET is_loaded=TRUE, status='loading' WHERE id = %s;'''
                        cursor.execute(sql, (order[0],))
                        dbConn.commit()
                        
                    with seq_lock:
                        APutOnTruck = generate_APutOnTruck(order)
                        add_toWorld(APutOnTruck)
                        print("Add to World: APutOnTruck - In received TruckArriced from UPS")
                    
                        # send ALoad to UPS
                        ALoad = generate_ALoad(order)
                        add_messageToUPS(ALoad)
                        print("Add to UPS: ALoad - In received TruckArriced from UPS")
    
    if len(ups_command.udelivered)>0:
        for deliver in ups_command.udelivered:
                print("Message from UPS: received UDelivered")
                
                # update the corresponding order status to be delivered whose id is packgeid
                with order_lock_db:
                    sql = '''UPDATE web_order SET status = 'delivered' WHERE id = %s;'''
                    cursor.execute(sql, (deliver.packageid,))
                    dbConn.commit()
                    
