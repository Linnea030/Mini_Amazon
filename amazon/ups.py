import socket
import threading
import select
import psycopg2

import world_amazon_pb2
import amazon_ups_pb2

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

UPSHOST, UPSPORT = "vcm-30971.vm.duke.edu", 22222
WHOST, WPORT = "vcm-30971.vm.duke.edu", 23456
# for setting up socket as server
AmazonHOST, AmazonPORT = "vcm-30971.vm.duke.edu", 11111

# connect with UPS server as client and return the socket set up
def connectA():
    sk_A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    A_ip = socket.gethostbyname(AmazonHOST)
    
    ip_port = (A_ip, AmazonPORT)
    sk_A.connect(ip_port)

    print("UPSmini: connected with Amazon")
    
    return sk_A

# set up the socket server to connect with UPS
# return the socket_amazon
# use socket_amazon to accept connection
def setUpUPSServer():
    ip_port = (UPSHOST, UPSPORT)
               
    sk_ups = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk_ups.bind(ip_port)
    sk_ups.listen(20)

    print("UPSmini: Server with Amazon set up")
    
    return sk_ups
    
# send google protocol buffer message through socket
# args: (socket, protocol buffer object)
# return: None
def send_msg(socket,msg):
    to_send = msg.SerializeToString()
    _EncodeVarint(socket.sendall,len(to_send))
    socket.sendall(to_send)

# recv serialized message through socket
# args: (socket)
# return: a serialized string
def recv_msg(socket):
    var_int_buff = []
    while True:
        buf = socket.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = socket.recv(msg_len)
    print("=====Recv message:\n"+str(whole_message))
    return whole_message

def recvMsgFromUPS():
    
    # set up socket as a server
    sk_ups = setUpUPSServer()
    
    # keep trying to accept UPS connection
    while True:
        print("UPS Sercer: Waiting to be connected")
        connWithAmazon, address = sk_ups.accept()
        print("UPS Server: Accept connection from Amazon")
        
        # recv msg from UPS
        mssgFromAmazon = recv_msg(connWithAmazon)
        if mssgFromAmazon == "":
            print("Received from Amazon: blank string!!!")
            connWithAmazon.close()
            continue
        
        amazon_command = amazon_ups_pb2.ACommand()
        amazon_command.ParseFromString(mssgFromAmazon)
        
        print("----- Receive from Amazon -----")
        print(str(amazon_command))
        
        print("UPS Server: close socket")
        connWithAmazon.close()

if __name__ == '__main__':
    recvMsgFromUPS()