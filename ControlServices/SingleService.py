#coding=utf-8
import socket
import json
import time
import os
basedir = os.path.abspath(os.path.dirname(__file__))


file_path = basedir +os.sep  + 'datas.json'
file_path_log = basedir +os.sep  + 'logs.txt'

#control commands
control_instruction = {
    "on": {
        "0": "fe050000ff009835",
        "1": "fe050001ff00c9f5",
        "2": "fe050002ff0039f5",
        "3": "fe050003ff006835",
        "4": "fe050004ff00d9f4",
        "5": "fe050005ff008834",
        "6": "fe050006ff007834",
        "7": "fe050007ff0029f4",
        "8": "fe050008ff0019f7",
        "9": "fe050009ff004837",
        "10": "fe05000aff00b837",
        "11": "fe05000bff00e9f7",
        "12": "fe05000cff005836",
        "13": "fe05000dff0009f6",
        "14": "fe05000eff00f9f6",
        "15": "fe05000fff00a836"
    },
    "off": {
        "0": "fe0500000000d9c5",
        "1": "fe05000100008805",
        "2": "fe05000200007805",
        "3": "fe050003000029c5",
        "4": "fe05000400009804",
        "5": "fe0500050000c9c4",
        "6": "fe050006000039c4",
        "7": "fe05000700006804",
        "8": "fe05000800005807",
        "9": "fe050009000009c7",
        "10": "fe05000a0000f9c7",
        "11": "fe05000b0000a807",
        "12": "fe05000c000019c6",
        "13": "fe05000d00004806",
        "14": "fe05000e0000b806",
        "15": "fe05000f0000e9c6"
    }
}

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

