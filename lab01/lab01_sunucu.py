import socket
import sys
import threading

from typing import Counter
import random

class connThread(threading.Thread):
    def __init__(self, threadID, conn, c_addr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conn = conn
        self.c_adrr = c_addr

    def run(self):
            
            self.conn.send("Sayi bulmaca oyununa hosgeldiniz!\n".encode())
            #print("Bağlantı kuruldu: %s" % str(self.c_adrr))
            while True:
                data = self.conn.recv(1024)
                data_str = data.decode().strip()
                data_str = data_str.split(" ")
                #print(" '{0}': '{1}'".format(self.c_adrr, data_str))
                if data_str[0] == "STA":
                    print("Sta girildi")
                    quit_flag = False
                    n = random.randint(1, 99)
                    counter = 0
                    self.conn.send("RDY\n".encode())
                    self.conn.send(("{}\n".format(n).encode()))
                    while True:
                        guess = self.conn.recv(1024)
                        guess = guess.decode().strip()
                        guess_list = guess.split(" ")
                        if guess_list[0] == "TRY":
                        
                            try:
                                guess = int(guess_list[1])
                                break
                            except:
                                self.conn.send("PRR\n".encode())
                        elif guess_list[0] == "STA":
                            n = random.randint(1, 99)
                            self.conn.send("RDY\n".encode())
                            self.conn.send(("{}\n".format(n).encode()))
                        elif guess_list[0] == "QUI":
                            self.conn.send("BYE\n".encode())
                            quit_flag = True
                            break
                        else:
                            self.conn.send("ERR\n".encode())
                    
                    if not quit_flag:
                        
                        rdy_flag = False
                        while True:
                            
                            print(type(guess), guess)
                            if rdy_flag:
                                while True:
                                    guess = self.conn.recv(1024)
                                    guess = guess.decode().strip()
                                    guess_list = guess.split(" ")
                                    if guess_list[0] == "TRY":
                                    
                                        try:
                                            guess = int(guess_list[1])
                                            break
                                        except:
                                            self.conn.send("PRR\n".encode())
                                    elif guess_list[0] == "STA":
                                        n = random.randint(1, 99)
                                        self.conn.send("RDY\n".encode())
                                        self.conn.send(("{}\n".format(n).encode()))
                                    elif guess_list[0] == "QUI":
                                        self.conn.send("BYE\n".encode())
                                        quit_flag = True
                                        break
                                    else:
                                        self.conn.send("ERR\n".encode())
                            
                            rdy_flag = False

                            if guess < n:
                                
                                self.conn.send("LTH\n".encode())
                                counter +=1
                                self.conn.send(("Current Guess Number: {}\n".format(counter)).encode())
                                guess = self.conn.recv(1024)
                                guess = guess.decode().strip()
                                guess_list = guess.split(" ")
                                
                                if guess_list[0] == "TRY":
                                    try:
                                        guess = int(guess_list[1])
                                    except:
                                        self.conn.send("PRR\n".encode())
                                elif guess_list[0] == "STA":
                                    n = random.randint(1, 99)
                                    self.conn.send("RDY\n".encode())
                                    self.conn.send(("{}\n".format(n).encode()))
                                    counter = 0
                                    rdy_flag = True
                                elif guess_list[0] == "QUI":
                                    self.conn.send("BYE\n".encode())
                                    quit_flag = True
                                    break
                                else:
                                    self.conn.send("ERR\n".encode())
                                    rdy_flag = True
                                
                            elif guess > n:
                                
                                self.conn.send("GTH\n".encode())
                                counter +=1
                                self.conn.send(("Current Guess Number: {}\n".format(counter)).encode())
                                guess = self.conn.recv(1024)
                                guess = guess.decode().strip()
                                guess_list = guess.split(" ")
                                
                                if guess_list[0] == "TRY":
                                    try:
                                        guess = int(guess_list[1])
                                    except:
                                        self.conn.send("PRR\n".encode())
                                elif guess_list[0] == "STA":
                                    n = random.randint(1, 99)
                                    self.conn.send("RDY\n".encode())
                                    self.conn.send(("{}\n".format(n).encode()))
                                    counter = 0
                                    rdy_flag = True
                                elif guess_list[0] == "QUI":
                                    self.conn.send("BYE\n".encode())
                                    quit_flag = True
                                    break
                                else:
                                    self.conn.send("ERR\n".encode())
                                    rdy_flag = True
                            
                            else:
                                print("buraya girdi")
                                self.conn.send("WIN\n".encode())
                                self.conn.send(("Total Guess Number: {}\n".format(counter)).encode())   
                                break
                    if quit_flag:
                        break
                            
                elif data_str[0] == "QUI":
                    self.conn.send("BYE\n".encode())
                    break
                elif data_str[0] == "TIC":
                    self.conn.send("TOC\n".encode())
                elif data_str[0] == "TRY":
                    self.conn.send("GRR\n".encode())
                else:
                    self.conn.send("ERR\n".encode())
                
                
            self.conn.close()
            #print("Thread %s kapanıyor" % self.threadID)


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


