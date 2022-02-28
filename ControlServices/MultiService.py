#coding=utf-8
import select
import socket
import sys
import queue

#控制指令
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

server = socket.socket()
server.setblocking(0)

server_addr = ('127.0.0.1',11111)

print('starting up on %s port %s' % server_addr)
server.bind(server_addr)

server.listen(5)

inputs = [server, ] #自己也要监测呀,因为server本身也是个fd
outputs = []

message_queues = {}

while True:
    print("waiting for next event...")

    readable, writeable, exeptional = select.select(inputs,outputs,inputs) #如果没有任何fd就绪,那程序就会一直阻塞在这里

    for s in readable: #每个s就是一个socket
        if s is server: #别忘记,上面我们server自己也当做一个fd放在了inputs列表里,传给了select,如果这个s是server,代表server这个fd就绪了,
            #就是有活动了, 什么情况下它才有活动? 当然 是有新连接进来的时候 呀
            #新连接进来了,接受这个连接
            conn, client_addr = s.accept()
            print("new connection from",client_addr)
            conn.setblocking(0)
            inputs.append(conn) #为了不阻塞整个程序,我们不会立刻在这里开始接收客户端发来的数据, 把它放到inputs里, 下一次loop时,这个新连接
            #就会被交给select去监听,如果这个连接的客户端发来了数据 ,那这个连接的fd在server端就会变成就续的,select就会把这个连接返回,返回到
            #readable 列表里,然后你就可以loop readable列表,取出这个连接,开始接收数据了, 下面就是这么干 的
            message_queues[conn] = queue.Queue() #接收到客户端的数据后,不立刻返回 ,暂存在队列里,以后发送

        else: #s不是server的话,那就只能是一个 与客户端建立的连接的fd了
            #客户端的数据过来了,在这接收
            data = s.recv(1024)
            if data:
                print("收到来自[%s]的数据:" % s.getpeername()[0], data)
                message_queues[s].put(data) #收到的数据先放到queue里,一会返回给客户端
                if s not  in outputs:
                    outputs.append(s) #为了不影响处理与其它客户端的连接 , 这里不立刻返回数据给客户端


            else:#如果收不到data代表什么呢? 代表客户端断开了呀
                print("客户端断开了",s)

                if s in outputs:
                    outputs.remove(s) #清理已断开的连接

                inputs.remove(s) #清理已断开的连接

                del message_queues[s] ##清理已断开的连接


    for s in writeable:
        try :
            next_msg = message_queues[s].get_nowait()

        except queue.Empty:
            print("client [%s]" %s.getpeername()[0], "queue is empty..")
            outputs.remove(s)

        else:
            print("sending msg to [%s]"%s.getpeername()[0], next_msg)
            s.send(next_msg.upper())


    for s in exeptional:
        print("handling exception for ",s.getpeername())
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        del message_queues[s]