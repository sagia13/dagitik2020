'''
Dağıtık Sistemler proje kodu:
Ali KAAN ÖZDEN - 16401781

Sunucu düzgün bir şekilde çalışmaktadır. Daha rahat yazdiğim için ingilizce yazdım.
Windows'ta test edince (putty ile) yeni satırlarda gereksiz boşluklar oluşabilmekte. Nedeninini tam bulamadım. 
Linux terminalden Telnet ile bağlantı yapmanızı öneririm.
'''

import socket
import threading
import queue
import sys



clientDictionnary = {} # clientConnection : [ReadThread, WriteThread, connectionQ]
userNames = {} # userName : clientConnection
user_authentication = {} #{username:password}
users_with_connections = {} #{username:clientConnection}
room_dict = {} #{room_name: [owner, user_list]}
clientDictLock = threading.Lock()
user_auth_lock = threading.Lock()
users_with_conn_lock = threading.Lock()
room_dict_lock =  threading.Lock()


class ReadThread(threading.Thread):
    
    def __init__(self, threadID, connection, c_addr, connectionQ):
        threading.Thread.__init__(self) 
        self.threadID = threadID
        self.connection = connection
        self.c_addr = c_addr
        self.connectionQ = connectionQ
        self.userName = 0 #used for authentication
       
    def run(self):
        self.parser()
        #Thread is quitting

    def parser(self):
        while True:
            data = self.connection.recv(1024)
            data_str = data.decode().strip()
            try:
                args = data_str.split() #Split command from data
            except:
                continue
            try:
                if args[0] == "QUI":
                    if self.userName != 0:
                        serverResponse = "BYEQ" + " " + self.userName + "\n"
                        users_with_conn_lock.acquire()
                        users_with_connections.pop(self.userName)
                        users_with_conn_lock.release()
                    else:
                        serverResponse = "BYEQ\n"
                    self.connectionQ.put(serverResponse)
                    break
                
                elif args[0] == "GLS":
                    if self.userName != 0:
                        try:
                            roomName = args[1]
                            if self.userName in room_dict[roomName][1]:
                                serverResponse = "LSTU: owner(" + room_dict[roomName][0] + ") users: "
                                for user in room_dict[roomName][1]:
                                    serverResponse += user + " "
                                serverResponse += "\n"
                            else:
                                serverResponse  = "NENT " + roomName + "\n"
                        except:
                            serverResponse = "ERR\n"
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)
                
                elif args[0] == "PIN":
                    serverResponse = "PON\n"
                    self.connectionQ.put(serverResponse)
                
                elif args[0] == "GNL":
                    if self.userName != 0:
                        try:
                            roomName = args[1]
                            message = args[2:]
                            if roomName not in room_dict.keys():
                                serverResponse = "NOPR\n"
                            else:
                                if self.userName in room_dict[roomName][1]:
                                    strmessage = roomName + "/" + self.userName + ": "
                                    for item in message:
                                        strmessage += (item + " ")
                                    strmessage += "\n"
                                    for user in room_dict[roomName][1]:
                                        try:
                                            clientDictionnary[(users_with_connections[user])][2].put(strmessage)
                                        except: #useroffline
                                            continue
                                    serverResponse = "OKG\n"
                                else:
                                    serverResponse = "NAR\n"
                        except:
                            serverResponse = "ERR\n"
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)
                
                elif args[0] == "PRV":
                    if self.userName != 0:  
                        parameters = data_str.split()[1:]
                        if (not parameters): #empty message 
                            serverResponse = "ERR\n"
                            self.connectionQ.put(serverResponse)  
                        else:
                            strparameters = ""
                            strparameters = strparameters.join(parameters)
                            if len(strparameters.split(":")) != 2: #Cannot find ":" or wrong entry of parameters
                                serverResponse = "ERR\n"
                                self.connectionQ.put(serverResponse)
                            else:
                                userName = strparameters.split(":")[0] #username of receiver
                                message =  ""
                                firstWord = parameters[0].split(":")[1]
                                message += firstWord
                                parameters = parameters[1:]
                                for word in parameters:
                                    message += (word + " ")
                                if userName not in users_with_connections.keys():
                                    serverResponse = "NOP\n"
                                    self.connectionQ.put(serverResponse)
                                    
                                else: 
                                    messageWithUN = "*" + self.userName + "*: " + message + "\n"
                                    clientDictionnary[users_with_connections[userName]][2].put(messageWithUN)
                                    serverResponse = "OKP\n"
                                    self.connectionQ.put(serverResponse)                      
                    else:
                        serverResponse = "LRR\n"
                        self.connectionQ.put(serverResponse)
                    
                elif args[0] == "REG":
                    if self.userName == 0:
                        try:
                            userName = args[1] 
                            password = args[2]
                            self.userName = userName
                            if userName in user_authentication.keys():
                                serverResponse = "REJ " + userName + "\n"
                                self.userName = 0
                            else:
                                if password.isdigit():
                                    serverResponse = "REGOK " + self.userName + "\n" + "WEL " + self.userName + "\n"
                                    user_auth_lock.acquire()
                                    user_authentication[userName] = password
                                    user_auth_lock.release()
                                    users_with_conn_lock.acquire()
                                    users_with_connections[userName] = self.connection
                                    users_with_conn_lock.release()
                                else:
                                    serverResponse = "REJPSW " + password + "\n"
                                    self.userName = 0
                        except:
                            serverResponse = "ERR\n"   
                    else:
                        password = args[1]
                        if password.isdigit():
                            user_auth_lock.acquire()
                            user_authentication[self.userName] = password
                            user_auth_lock.release()
                            serverResponse = "REGOK " + password + "\n"
                        else:
                            serverResponse = "REJPSW " + password + "\n"
                    self.connectionQ.put(serverResponse)
                            
                elif args[0] == "LOGIN":
                    if self.userName == 0:
                        try:
                            userName = args[1]
                            password = args[2]
                            if userName in user_authentication.keys():
                                if user_authentication[userName] == password:
                                    self.userName = userName
                                    users_with_conn_lock.acquire()
                                    users_with_connections[userName] = self.connection
                                    users_with_conn_lock.release()
                                    serverResponse = "WEL " + userName + "\n"
                                else:
                                    serverResponse = "REJ\n"
                            else:
                                serverResponse = "REJ\n"
                        except:
                            serverResponse = "ERR\n"
                    else:
                        users_with_conn_lock.acquire()
                        users_with_connections.pop(self.userName)
                        users_with_conn_lock.release()
                        serverResponse = "BYE " + self.userName + "\n"
                        self.connectionQ.put(serverResponse)
                        self.userName = 0
                        try:
                            userName = args[1]
                            password = args[2]
                            if userName in user_authentication.keys():
                                if user_authentication[userName] == password:
                                    self.userName = userName
                                    users_with_conn_lock.acquire()
                                    users_with_connections[userName] = self.connection
                                    users_with_conn_lock.release()
                                    serverResponse = "WEL " + userName + "\n"
                                else:
                                    serverResponse = "REJ\n"
                            else:
                                serverResponse = "REJ\n"
                        except:
                            serverResponse = "ERR\n"
                    self.connectionQ.put(serverResponse)
    
                elif args[0] == "LOGOFF":
                    if self.userName == 0:
                        self.connectionQ.put("NACC\n")
                    else:
                        users_with_conn_lock.acquire()
                        users_with_connections.pop(self.userName)
                        users_with_conn_lock.release()
                        serverResponse = "OKL\n"
                        self.connectionQ.put(serverResponse)
                        self.userName = 0

                elif args[0] == "RLS":
                    serverResponse = "LSTR "
                    for room in room_dict.keys():
                        serverResponse += (room + ":")
                    serverResponse = serverResponse[:-1] + "\n"
                    self.connectionQ.put(serverResponse)
                        
                elif args[0] == "ENTER":
                    if self.userName != 0:
                        try:
                            roomName = args[1]
                            if roomName in room_dict.keys():
                                room_dict_lock.acquire()
                                if self.userName in room_dict[roomName][1]:
                                    serverResponse = "INR\n"
                                    room_dict_lock.release()
                                else:
                                    room_dict[roomName][1].append(self.userName)
                                    room_dict_lock.release()
                                    strmessage = "NTF: " + self.userName + " entered " + roomName + "\n"
                                    for user in room_dict[roomName][1]:
                                        if user != self.userName:
                                            try:
                                                clientDictionnary[(users_with_connections[user])][2].put(strmessage)
                                            except:
                                                continue
                                    serverResponse = "OKEN\n"
                            else:
                                serverResponse = "NOPR " + roomName + "\n"
                        except:
                            serverResponse = "ERR\n"
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)
                                
                elif args[0] == "EXIT":
                    if self.userName != 0:
                        try:
                            roomName = args[1]
                            if self.userName not in room_dict[roomName][1]:
                                serverResponse = "NENT " + roomName + "\n"
                            else:
                                room_dict_lock.acquire()
                                index = room_dict[roomName][1].index(self.userName)
                                room_dict[roomName][1].pop(index)
                                room_dict_lock.release()
                                strmessage = "NTF: " + self.userName + " exited " + roomName + "\n"
                                for user in room_dict[roomName][1]:
                                    try:
                                        clientDictionnary[(users_with_connections[user])][2].put(strmessage)
                                    except:#user is offline
                                        continue #do not notify
                                serverResponse = "OKEX " + roomName + "\n"
                        except:
                            serverResponse = "ERR\n"
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)

                elif args[0] == "RLSE":
                    if self.userName != 0:
                        serverResponse = "LSTRE "
                        for roomName in room_dict.keys():
                            if self.userName in room_dict[roomName][1]:
                                serverResponse += roomName + ":"
                        serverResponse = serverResponse[:-1] + "\n"            
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)
                
                elif args[0] == "CREATR":
                    if self.userName != 0:
                        try:
                            roomName = args[1]
                            if roomName in room_dict.keys():
                                serverResponse = "REJ\n"
                            else:
                                room_dict_lock.acquire()
                                room_dict[roomName] = [self.userName,[self.userName]]
                                room_dict_lock.release()
                                serverResponse = "OKCR " + roomName + "\n"
                        except:
                            serverResponse = "ERR\n"
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)
                
                elif args[0] == "KICK":
                    if self.userName != 0:
                        try:
                            roomName = args[1]
                            userName = args[2]
                            if roomName in room_dict.keys():
                                if self.userName == room_dict[roomName][0]:
                                    if userName in room_dict[roomName][1]:
                                        room_dict_lock.acquire()
                                        index = room_dict[roomName][1].index(userName)
                                        room_dict[roomName][1].pop(index)
                                        room_dict_lock.release()
                                        messagetouser = "KICKED " + roomName + "\n"
                                        try:
                                            clientDictionnary[users_with_connections[userName]][2].put(messagetouser)
                                        except: #user is offline
                                            pass #do not notify
                                        notification = "NTF " + userName + " is kicked from " + roomName + "\n"
                                        for user in room_dict[roomName][1]:
                                            try:
                                                clientDictionnary[(users_with_connections[user])][2].put(notification)
                                            except:#user is offline
                                                continue #do not notify
                                        serverResponse = "OKKICK " + userName + "\n"
                                    else:
                                        serverResponse = "NOP\n"
                                else:
                                    serverResponse = "NOWN " + roomName + "\n"
                            else:
                                serverResponse = "NOPR " + roomName + "\n"
                        except:
                            serverResponse = "ERR\n"
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)
                
                elif args[0] == "CLSR":
                    if self.userName != 0:
                        try:
                            roomName = args[1]
                            if roomName in room_dict.keys():
                                if self.userName == room_dict[roomName][0]:
                                    notification = "NTF " + roomName + " is closed by " + self.userName + "\n" + "EXITED " + roomName + "\n"
                                    for user in room_dict[roomName][1]:
                                        if user != self.userName:
                                            try:
                                                clientDictionnary[(users_with_connections[user])][2].put(notification)
                                            except:
                                                continue
                                    room_dict_lock.acquire()
                                    room_dict.pop(roomName)
                                    room_dict_lock.release()
                                    serverResponse = "OKCLS " + roomName + "\n"
                                else:
                                    serverResponse = "NOWN " + roomName + "\n"
                            else:
                                serverResponse = "NOPR " + roomName + "\n" 
                        except:
                            serverResponse = "ERR\n"         
                    else:
                        serverResponse = "NACC\n"
                    self.connectionQ.put(serverResponse)


                else:
                    serverResponse = "ERR\n"
                    self.connectionQ.put(serverResponse)
                    
            except:
                continue

class WriteThread(threading.Thread):
    
    def __init__(self, threadID, connection, c_addr, connectionQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.connection = connection
        self.c_addr = c_addr
        self.connectionQ = connectionQ
        
    def run(self):
        while True:
            message = self.connectionQ.get()
            self.connection.send(message.encode())
            if "BYEQ " in message: #means ReadThread is done with client
                break
            #WriteThread is also done. 
        self.connection.close()
        clientDictLock.acquire()
        clientDictionnary.pop(self.connection)
        clientDictLock.release()
               
#MAIN()

#Socket creation
try:
    s = socket.socket()
    ip = sys.argv[1]
    port = int(sys.argv[2])
    s.bind((ip, port))
    s.listen(5)

except: #Wrong parameters
    print("Please re-run the server with correct paramaters, Ex: proje.py <IP> <PORT>")
    sys.exit(1)

#Variables for thread management
id = 0
threads = []

#Infinite while loop
while True:
    connection, address = s.accept() #blocking
    newconnectionQ = queue.Queue() 
    strID = str(id) + ".0"
    newReadThread = ReadThread(strID, connection, address, newconnectionQ)
    strID = str(id) + ".1"
    newWriteThread = WriteThread(strID, connection, address, newconnectionQ)
    clientDictLock.acquire()
    clientDictionnary[connection] = [newReadThread, newWriteThread, newconnectionQ]
    clientDictLock.release()
    threads.append([newReadThread, newWriteThread])
    newReadThread.start()
    newWriteThread.start()
    id += 1

