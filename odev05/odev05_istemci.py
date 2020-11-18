import socket
import sys
s = socket.socket()
ip = sys.argv[1]
port = int(sys.argv[2])
s.connect((ip,port))
print(s.recv(1024).decode())
print(s.recv(1024).decode())

while True:
    user = input()
    s.send(user.encode())
    print(s.recv(1024).decode())
    if user == "QUI":
        break

s.close()