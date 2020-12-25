'''
Dağıtık Sistemler TP06 lab ödevi:
Ali KAAN ÖZDEN - 16401781

Sunucu düzgün bir şekidle çalışmaktadır. Daha rahat yazdiğim için ingilizce yazdım.
Windows'ta test edince (putty ile) yeni satırlarda gereksiz boşluklar oluşabilmekte. Nedeninini tam bulamadım.
Örnek çıktılar "cikti.pdf" sayfasında bulunmaktadır.
'''

import socket
import threading
import queue
import sys



clientDictionnary = {} # clientConnection : [ReadThread, WriteThread, connectionQ]
userNames = {} # userName : clientConnection
userNamesLock = threading.Lock()
clientDictLock = threading.Lock()
loggerQ = queue.Queue()

class ReadThread(threading.Thread):
    
    def __init__(self, threadID, connection, c_addr, connectionQ):
        threading.Thread.__init__(self) 
        self.threadID = threadID
        self.connection = connection
        self.c_addr = c_addr
        self.connectionQ = connectionQ
        self.userName = 0 #used for authentication
        log = "Thread:" + self.threadID + " is handling a new client: " + str(self.connection) 
        loggerQ.put(log)

    def run(self):
        self.parser()
        #Thread is quitting

    def parser(self):
        while True:
            data = self.connection.recv(1024)
            data_str = data.decode().strip()
            log = "Thread: " + self.threadID + " has recieved data: " + data_str
            loggerQ.put(log)
            try:
                args = data_str.split() #Split command from data
            except:
                continue
            try:
                if args[0] == "NIC":
                    userName = args[1]
                    self.userName = userName
                    if userName not in userNames.keys():
                        userNamesLock.acquire()
                        userNames[userName] = self.connection
                        userNamesLock.release()
                        serverResponse = "WEL" + " " + self.userName + "\n"
                    else:
                        serverResponse = "REJ" + " " + self.userName + "\n"
                    log = "Thread: " + self.threadID + " response to client: " + serverResponse 
                    self.connectionQ.put(serverResponse)

                elif args[0] == "QUI":
                    if self.userName != 0:
                        serverResponse = "BYE" + " " + self.userName + "\n"
                    else:
                        serverResponse = "BYE\n"
                    self.connectionQ.put(serverResponse)
                    log = "Thread: " + self.threadID + " response to client: " + serverResponse
                    loggerQ.put(log)
                    log = "Thread: " + self.threadID  + " is quiting."
                    break
                
                elif args[0] == "GLS":
                    if self.userName != 0:
                        userList = ""
                        for userName in userNames.keys():
                            userList += userName + ":"
                        userList = userList[:-1]
                        serverResponse = "LST" + " " + userList + "\n"
                    else:
                        serverResponse = "LRR\n"
                    self.connectionQ.put(serverResponse)
                    log = "Thread: " + self.threadID + " response to client: " + serverResponse
                
                elif args[0] == "PIN":
                    serverResponse = "PON\n"
                    self.connectionQ.put(serverResponse)
                    log = "Thread: " + self.threadID + " response to client: " + serverResponse
                
                elif args[0] == "GNL":
                    if self.userName != 0:
                        message = data_str.split()[1:]
                        if (not message): #empty message 
                            serverResponse = "ERR\n"
                            self.connectionQ.put(serverResponse)
                            log = "Thread: " + self.threadID + " response to client: " + serverResponse
                        else:
                            strmessage = ""
                            strmessage = strmessage.join(message)
                            messageWithUN = "<" + self.userName + ">: " + strmessage + "\n"
                            for clientConnection in userNames.values():
                                clientDictionnary[clientConnection][2].put(messageWithUN)
                            serverResponse = "OKG\n"
                            self.connectionQ.put(serverResponse)
                            log = "Thread: " + self.threadID + " response to client: " + serverResponse
                    else:
                        serverResponse = "LRR\n"
                        self.connectionQ.put(serverResponse)
                        log = "Thread: " + self.threadID + " response to client: " + serverResponse
                
                elif args[0] == "PRV":
                    if self.userName != 0:  
                        parameters = data_str.split()[1:]
                        if (not parameters): #empty message 
                            serverResponse = "ERR\n"
                            self.connectionQ.put(serverResponse)  
                            log = "Thread: " + self.threadID + " response to client: " + serverResponse
                        else:
                            strparameters = ""
                            strparameters = strparameters.join(parameters)
                            if len(strparameters.split(":")) != 2: #Cannot find ":" or wrong entry of parameters
                                serverResponse = "ERR\n"
                                self.connectionQ.put(serverResponse)
                                log = "Thread: " + self.threadID + " response to client: " + serverResponse
                            else:
                                userName = strparameters.split(":")[0] #username of receiver
                                message = strparameters.split(":")[1]
                                if userName not in userNames:
                                    serverResponse = "NOP\n"
                                    self.connectionQ.put(serverResponse)
                                    log = "Thread: " + self.threadID + " response to client: " + serverResponse
                                else: 
                                    messageWithUN = "*" + self.userName + "*: " + message + "\n"
                                    clientDictionnary[userNames[userName]][2].put(messageWithUN)
                                    serverResponse = "OKP\n"
                                    self.connectionQ.put(serverResponse)   
                                    log = "Thread: " + self.threadID + " response to client: " + serverResponse
                    else:
                        serverResponse = "LRR\n"
                        self.connectionQ.put(serverResponse)
                        log = "Thread: " + self.threadID + " response to client: " + serverResponse
                    
                elif args[0] == "OKG":
                    pass
                elif args[0] == "OKP":
                    pass
                elif args[0] == "OKW":
                    pass
                elif args[0] == "TON":
                    pass

                else:
                    serverResponse = "ERR\n"
                    self.connectionQ.put(serverResponse)
                    log = "Thread: " + self.threadID + " response to client: " + serverResponse
                loggerQ.put(log)
            except:
                continue

class WriteThread(threading.Thread):
    
    def __init__(self, threadID, connection, c_addr, connectionQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.connection = connection
        self.c_addr = c_addr
        self.connectionQ = connectionQ
        log = "Thread:" + self.threadID + " is handling (write) a new client: " + str(self.connection) 
        loggerQ.put(log)

    def run(self):
        while True:
            message = self.connectionQ.get()
            self.connection.send(message.encode())
            if "BYE " in message: #means ReadThread is done with client
                self.connection.close()
                userNamesLock.acquire()
                UserNameList = list(userNames.keys())
                clientConnectionList = list(userNames.values())                
                index = clientConnectionList.index(self.connection)
                userNames.pop(UserNameList[index])
                userNamesLock.release()
                clientDictLock.acquire()
                clientDictionnary.pop(self.connection)
                clientDictLock.release()
                log = "Thread:" + self.threadID + " is handling quiting."
                loggerQ.put(log)
                break
            #WriteThread is also done.
        

class LoggerThread(threading.Thread):
    
    def __init__(self, loggerQ):
        threading.Thread.__init__(self)
        self.loggerQ = loggerQ
        
    
    def run(self):
        while True:
            log = self.loggerQ.get()
            logfile = open("logfile.txt", "w+")
            logfile.write(log)
            logfile.close()
        
        
                
#MAIN()

#Socket creation
try:
    s = socket.socket()
    ip = sys.argv[1]
    port = int(sys.argv[2])
    s.bind((ip, port))
    s.listen(5)

except: #Wrong parameters
    print("Please re-run the server with correct paramaters, Ex: python odev06_sunucu.py <IP> <PORT>")
    sys.exit(1)


#Variables for thread management
id = 0
threads = []

#Logger thread initialization
newlogger = LoggerThread(loggerQ)
newlogger.start()

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

