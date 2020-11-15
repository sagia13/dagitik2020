import socket
import sys
import threading
from datetime import datetime
from typing import Counter

class connThread(threading.Thread):
    def __init__(self, threadID, conn, c_addr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conn = conn
        self.c_adrr = c_addr
    
    def run(self):
        self.conn.send("Hosgeldiniz!\n".encode())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.conn.send(current_time.encode() + "\n".encode())
        print("Bağlantı kuruldu: %s" % str(self.c_adrr))
        
        
        while True:
            data = self.conn.recv(1024)
            data_str = data.decode().strip()
            print(" '{0}': '{1}'".format(self.c_adrr, data_str))
            if data_str == "Kapan":
                self.conn.send("Gule gule\n".encode())
                print("Baglanti Kapaniyor: %s" % str(self.c_adrr))
                break
            elif data_str == "Selam":
                self.conn.send("Selam\n".encode())
            elif data_str == "Naber":
                self.conn.send("Iyiyim sagol\n".encode())
            elif data_str == "Hava":
                self.conn.send("Yagmurlu\n".encode())
            elif data_str == "Haber":
                self.conn.send("Korona\n".encode())
            else:
                self.conn.send("Anlamadim\n".encode())
            
            
        self.conn.close()
        print("Thread %s kapanıyor" % self.threadID)
            

s = socket.socket()
ip = "0.0.0.0"
port = int(sys.argv[1])

s.bind((ip, port))
s.listen(5)

counter = 0
threads = []

while True:
    conn, addr = s.accept() #blocking
    newConnThread = connThread(counter,conn, addr)
    threads.append(newConnThread)
    newConnThread.start()
    counter += 1
    newConnThread.join()



s.close()