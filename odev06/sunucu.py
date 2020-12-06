import socket
import sys
import threading
from datetime import datetime
import time
from typing import Counter
import queue

outputQ = queue.Queue()
Qlock = threading.Lock()
dictLock = threading.Lock()
usersWithConnections = {}

class userListenerThread(threading.Thread):
    def __init__(self, threadID, conn, c_addr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conn = conn
        self.c_adrr = c_addr
        self.userName = "NOT_AUTHORIZED"
        self.authorization = False
    
    def run(self):
        print(self.threadID + " starting.")
        self.listen()
            
    def listen(self):
        while True:
            data = self.conn.recv(1024)
            data_str = data.decode().strip()
            print(" '{0}': '{1}'".format(self.c_adrr, data_str))
            print("istemci: " + data_str + "\n")
            data_arg = data_str.split()[0]
            msgToSend = [self.conn]
            
            if data_arg == "NIC":
                usrname = data_str.split()[1]
                if usrname not in usersWithConnections.keys():
                    self.userName = usrname
                    self.authorization = True
                    dictLock.acquire()
                    usersWithConnections[usrname] = self.conn
                    dictLock.release()
                    msgToSend.append("WEL" + " " + usrname + "\n")                
                else:
                    msgToSend.append("REJ" + " " + usrname + "\n")
                self.sendMsg(msgToSend)

            elif data_arg == "QUI":
                if self.userName != "NOT_AUTHORIZED":
                    msgToSend.append("BYE" + " " + self.userName + "\n")
                else:
                    msgToSend.append("BYE\n")
                self.sendMsg(msgToSend)
                break
                 
            elif data_arg == "GLS":
                if self.checkAuthorization():
                    user_list = ""
                    for user in usersWithConnections.keys():
                        user_list += user + ":"
                    msgToSend.append("LST" + " " + user_list + "\n")
                    self.sendMsg(msgToSend)                
               
            elif data_arg == "PIN":
                msgToSend.append("PON\n")
                self.sendMsg(msgToSend)

            elif data_arg == "GNL":
                if self.checkAuthorization():
                    msgToSend.append("OKG\n")
                    self.sendMsg(msgToSend)
                    msgToSend = [self.conn, "GNL"]
                    msgToSend.append(self.userName)
                    message = data_str.split()[1:] + "\n"
                    msgToSend.append(message)
                    self.sendMsg(msgToSend)
            
            elif data_arg == "PRV":
                if self.checkAuthorization():
                    msgToSend.append("OKP\n")
                    self.sendMsg(msgToSend)
                    msgToSend = [self.conn, "PRV"]
                    param = data_str.split()[1:]
                    nick = param.split(":")[0]
                    message = param.split(":")[1] + "\n"
                    msgToSend.append(self.userName)
                    msgToSend.append(nick)
                    msgToSend.append(message)
                    self.sendMsg(msgToSend)
                
            elif data_arg == "OKG":
                pass
            elif data_arg == "OKP":
                pass
            elif data_arg == "OKW":
                pass
            elif data_arg == "TON":
                pass
            else:
                msgToSend.append("ERR\n")
                self.sendMsg(msgToSend)
        
        self.conn.close()
        print("Thread %s kapanıyor" % self.threadID)
    
    
    def sendMsg(self,message):
        Qlock.acquire()
        outputQ.put(message)
        Qlock.release()


    def checkAuthorization(self):
        if self.authorization:
            return True
        else:
            msg = [self.conn, "LRR\n"]
            self.sendMsg(msg)
            return False



class msgSenderThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        while True:
            if not outputQ.empty():
                message = self.getNextMessage()
                user_conn = message[0]
                
                if message[1] == "GNL":
                    for user, connection in usersWithConnections.items():
                        user_name = message[2]
                        msg = message[3]
                        data = "(General) " + user_name + ": " + msg
                        connection.send(data.encode()) 
                    
                elif message[1] == "PRV":
                    user_name = message[2]
                    dest_user = message[3]
                    msg = message[4]
                    if dest_user in usersWithConnections.keys():
                        data = "(Private) " + user_name + ": " + msg
                        usersWithConnections[dest_user].send(data.encode())
                    else:
                        data = "NOP " + dest_user + "\n"
                        user_conn.send(data.encode())          
                else:
                    user_conn.send(message[1].encode())
            
            else:
                time.sleep(1)
      
    def getNextMessage(self):
        Qlock.acquire()
        msg = outputQ.get()
        Qlock.release()
        return msg
        
def pingClient():
    data = "TIN\n"
    for user, connection in usersWithConnections.items():
        connection.send(data(encode))
        

s = socket.socket()
ip = "0.0.0.0"
port = 6666

s.bind((ip, port))
s.listen(5)

counter = 0
threads = []

senderThread = msgSenderThread()
senderThread.start()

threading.Timer(10, pingClient).start()

while True:
    conn, addr = s.accept() #blocking
    newListener = userListenerThread(counter,conn,addr)
    threads.append(newListener)
    newListener.start()
    counter += 1
    newListener.join()

s.close()