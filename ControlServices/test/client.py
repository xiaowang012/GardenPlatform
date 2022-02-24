#coding=utf-8
import socket

s=socket.socket()
host = "127.0.0.1"
#connect
s.connect((host,1111))

#读取1024bit的数据
print('start connect')
while 1:
    command = input()
    if command == 'q':
        break
    s.sendall(bytes(command,encoding='utf8'))
s.close()