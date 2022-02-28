#coding=utf-8
import socket
import json
import time
import os
basedir = os.path.abspath(os.path.dirname(__file__))

#file path 
file_path = basedir +os.sep  + 'datas.json'
file_path_log = basedir +os.sep  + 'logs.txt'
file_path_control_commands = basedir +os.sep  + 'control_commands.json'

#control commands
try:
    with open(file_path_control_commands,'r',encoding='utf-8') as f:
        control_instruction = json.load(f)
except:
    raise Exception('read control commands error!')


host = '0.0.0.0'
port = 1111
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
print('listen')
server.listen(10)

while 1:
    while 1:
        if os.path.getsize(file_path) > 0:
            break
    with open(file_path,'r',encoding='utf-8') as f:
        data = json.load(f)
    while True:
        device1,addr = server.accept()
        print('connect:',addr)
        recv_info = device1.recv(1024).decode('utf-8')
        if recv_info:
            if data["device"] in str(recv_info):
                #命令转码
                command_list = data["command"].split('#')
                command_send = control_instruction[command_list[0]][str(int(command_list[1])-1)]
                device1.sendall(bytes.fromhex(command_send))
                return_recv = device1.recv(1024).hex()
                if return_recv == command_send:
                    print('send Success!')
                    with open(file_path,'w',encoding='utf-8') as f:
                        f.truncate()
                    device1.close()
                    #write success message
                    time_str = data["time"]
                    with open(file_path_log,'a',encoding='utf-8') as f:
                        f.write('\n'+time_str + ' send: '+ command_send+' recv: '+ return_recv +'status: ok '+ 'current time: ' + str(time.strftime("%Y-%m-%d %H:%M:%S")))
                    break
                else:
                    with open(file_path_log,'a',encoding='utf-8') as f:
                        f.write('\n'+' send: '+ command_send+' recv: '+ return_recv +'status: error '+ 'current time: ' + str(time.strftime("%Y-%m-%d %H:%M:%S")))
                    device1.close()
            else:
                with open(file_path_log,'a',encoding='utf-8') as f:
                    f.write('\n'+ ' send: None'+' recv: None ' +'status: reject client '+ 'current time: ' + str(time.strftime("%Y-%m-%d %H:%M:%S")))
                device1.close()  
        else:
            with open(file_path_log,'a',encoding='utf-8') as f:
                f.write('\n'+ ' send: None'+' recv: None' +'status: no data reject client '+ 'current time: ' + str(time.strftime("%Y-%m-%d %H:%M:%S")))
            device1.close()

