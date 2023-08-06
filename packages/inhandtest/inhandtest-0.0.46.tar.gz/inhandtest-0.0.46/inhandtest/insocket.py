# -*- coding: utf-8 -*-
# @Time    : 2023/4/4 17:15:10
# @Author  : Pane Li
# @File    : insocket.py
"""
insocket

"""

import logging
import threading
import time
import socket


def tcp_server_data(host, port, recv_content: str or list = None, connect_time=10,
                    send_msg_to_server: str or list = None, function=None, **kwargs):
    """ 开启tcp_server, 并且接收数据，对数据做验证, 该连接为阻塞式，所以要确保客户端能正常连接过来，还要确保防火墙是关闭的
        该连接使用with，所以不管是客户端还是服务端，还是在异常状态下都会正常关闭

    :param host:  server地址
    :param port:  server端口
    :param recv_content: 判断recv_content 在接收到的内容里面 也可以不做校验
    :param connect_time:  服务器和客户端建立连接后，需要连接的时间
    :param send_msg_to_server: 当客户端连接成功后，已连接客户端向服务端发送的内容
    :param function: tcp_server 连接上后做的操作
    :param kwargs:  function接入的参数
    :return: AssertionError or None
    """

    def client_send_msg_to_server(conn, addr, msg: str or list):
        if msg is not None:
            msg = [msg] if isinstance(msg, str) else [msg_ for msg_ in msg]
            for msg_ in msg:
                conn.send(msg_.encode('utf-8'))
                logging.info(f'tcp client {addr} send msg {msg_} to server {host}: {port}')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # 使用with， 不用担心没有关闭server
        s.bind((host, port))  # 绑定服务器IP地址和端口号
        s.listen()  # 等待客户端连接
        for i_ in range(0, 4):  # 有些端口错误的客户端会连接上来，导致收到的消息始终为空，需要过滤掉
            client = True
            logging.info(f'tcp server {host}:{port} start wait client connect')
            __conn, __addr = s.accept()
            if function is not None:
                threading.Thread(target=function, kwargs=kwargs).start()
            with __conn:
                logging.info(f'tcp server {host}:{port} connect from client {__addr}')
                datas = b''
                now_time = int(time.time())
                send_msg_status = False
                while int(time.time()) <= now_time + connect_time:
                    # 接收客户端数据
                    recv_data = __conn.recv(1024)
                    if not recv_data:
                        client = False
                        __conn.close()
                        logging.info(f'client {__addr} is a error client')
                        break
                    if not send_msg_status:
                        threading.Thread(target=client_send_msg_to_server,
                                         args=(__conn, __addr, send_msg_to_server)).start()
                        send_msg_status = True
                    logging.info(f'tcp server {host}:{port} recv data {recv_data}')
                    datas = datas + recv_data
                    if recv_content is not None:
                        contents = [recv_content.encode('utf-8')] if isinstance(recv_content, str) else [
                            c_.encode('utf-8') for c_ in recv_content]
                        # 校验数据内容

                        if not list(filter(lambda x: x not in datas, contents)):
                            break
                else:
                    __conn.close()
                    if recv_content is not None:
                        logging.error(f'recv all data is {datas}')
                        raise AssertionError('recv data error')
            if client:
                break


def tcp_client_data(server: tuple, client: tuple = None, recv_content: str or list = None, connect_time=10,
                    send_msg_to_server: str or list = None, function=None, **kwargs):
    """ 开启tcp_client, 并且接收数据，对数据做验证
        该连接使用with，所以不管是客户端还是服务端，还是在异常状态下都会正常关闭

    :param server: ($host, $port), 客户端需要连接的服务器地址和端口，使用元组，必填('192.168.2.1', 502)
    :param client:  ($host, $port) 绑定指定地址和端口，如果为None ，本机直接开启一个， 跟server参数一样
    :param recv_content: 判断客户端 在接收到的内容里面包含recv_content 也可以不做校验
    :param connect_time:  服务器和客户端建立连接后，需要连接的时间
    :param send_msg_to_server: 当客户端连接成功后，客户端向服务端发送的内容
    :param function: 当客户端 连接上后做的操作
    :param kwargs:  function接入的参数
    :return: AssertionError or None
    """

    def client_send_msg_to_server(client_, msg: str or list):
        if msg is not None:
            msg = [msg] if isinstance(msg, str) else [msg_ for msg_ in msg]
            for msg_ in msg:
                client_.send(msg_.encode("utf-8"))
                logging.info(f'tcp client send msg {msg_} to server {server}')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # 使用with， 不用担心没有关闭server
        if client:
            s.bind(client)  # 绑定客户端IP地址和端口号
        s.connect(server)  # 客户端连接服务端
        threading.Thread(target=client_send_msg_to_server, args=(s, send_msg_to_server)).start()
        threading.Thread(target=function, kwargs=kwargs).start()
        now_time = int(time.time())
        while int(time.time()) <= now_time + connect_time:
            # 接收客户端数据
            recv_data = s.recv(1024)
            logging.info(f'tcp client recv data from server {server}: {recv_data}')
            datas = datas + recv_data
            if recv_content is not None:
                contents = [recv_content.encode('utf-8')] if isinstance(recv_content, str) else [c_.encode('utf-8') for
                                                                                                 c_ in recv_content]
                # 校验数据内容
                if not list(filter(lambda x: x not in datas, contents)):
                    break
        else:
            if recv_content is not None:
                logging.error(f'recv all data is {datas}')
                raise AssertionError('recv data error')


def udp_server_data(host, port, recv_content: str or list = None, connect_time=10, send_msg_to_client: dict = None):
    """ 开启udp_server, 并且接收数据，对数据做验证, udp 校验数据时未区分客户端，所以保证接入时只有一个客户端
        该连接使用with，所以不管是客户端还是服务端，还是在异常状态下都会正常关闭

    :param host:  server地址
    :param port:  server端口
    :param recv_content: 判断recv_content 在接收到的内容里面 也可以不做校验
    :param connect_time:  服务器和客户端建立连接后，需要连接的时间
    :param send_msg_to_client: 开启udp server后， 向客户端发送的内容{($host, $port): $msg}
                               总体内容为字典， key值为元组类型， 总共长度为2位，第一位是客户端的地址， 第二位是端口
                               字典的value为需要给对应客户端发送的内容，可以是str 或list，
                               如需要给客户端192.168.3.2:6541 发送两条内容 'hello', 'word', 可以这样写
                               {('192.168.3.2', 6541): ['hello', 'word']}
                                确保对端服务和端口正常开启，不然要出问题
    :return: AssertionError or None
    """

    def server_send_msg_to_client(server, msg: dict):
        if msg:
            for key, value in msg.items():
                msg = [value] if isinstance(value, str) else [value_ for value_ in value]
                for msg_ in msg:
                    server.sendto(msg_.encode('utf-8'), key)
                    logging.info(f'udp server {host}: {port} send msg {msg_} to client {key}')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # 使用with， 不用担心没有关闭server
        s.bind((host, port))  # 绑定服务器IP地址和端口号
        logging.info(f'udp server {host}:{port} enable')
        threading.Thread(target=server_send_msg_to_client, args=(s, send_msg_to_client)).start()
        datas = b''
        now_time = int(time.time())
        while int(time.time()) <= now_time + connect_time:
            # 接收客户端数据
            data, addr = s.recvfrom(5024)
            logging.info(f'udp server {host}:{port} recv data from {addr}: {data}')
            datas = datas + data
            if recv_content is not None:
                contents = [recv_content.encode()] if isinstance(recv_content, str) else [c_.encode() for c_ in
                                                                                          recv_content]
                # 校验数据内容
                if not list(filter(lambda x: x not in datas, contents)):
                    break
        else:
            if recv_content is not None:
                logging.error(f'recv all data is {datas}')
                raise AssertionError('recv data error')


def udp_client_data(server: tuple, client: tuple = None, recv_content: str or list = None, connect_time=10,
                    send_msg_to_server: str or list = None):
    """ 开启udp_client, 并且接收数据，对数据做验证
        该连接使用with，所以不管是客户端还是服务端，还是在异常状态下都会正常关闭

    :param server: ($host, $port), 客户端需要连接的服务器地址和端口，使用元组，必填('192.168.2.1', 502)
    :param client:  ($host, $port) 绑定指定地址和端口，如果为None ，本机直接开启一个， 跟server参数一样
    :param recv_content: 判断客户端 在接收到的内容里面包含recv_content 也可以不做校验
    :param connect_time:  服务器和客户端建立连接后，需要连接的时间
    :param send_msg_to_server: 当客户端连接成功后，客户端向服务端发送的内容
    :return: AssertionError or None
    """

    def client_send_msg_to_server(client_, msg: str or list):
        if msg is not None:
            msg = [msg] if isinstance(msg, str) else [msg_ for msg_ in msg]
            for msg_ in msg:
                client_.sendto(msg_.encode("utf-8"), server)
                logging.info(f'udp client send msg {msg_} to server {server}')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # 使用with， 不用担心没有关闭server
        if client:
            s.bind(client)  # 绑定客户端IP地址和端口号
        threading.Thread(target=client_send_msg_to_server, args=(s, send_msg_to_server)).start()
        now_time = int(time.time())
        datas = b''
        while int(time.time()) <= now_time + connect_time:
            # 接收服务端数据
            data, server_addr = s.recvfrom(5024)
            logging.info(f'upd client recv data from server {server_addr}: {data}')
            datas = datas + data
            if recv_content is not None:
                contents = [recv_content.encode('utf-8')] if isinstance(recv_content, str) else [c_.encode('utf-8') for
                                                                                                 c_ in recv_content]
                # 校验数据内容
                if not list(filter(lambda x: x not in datas, contents)):
                    break
        else:
            if recv_content is not None:
                logging.error(f'recv all data is {datas}')
                raise AssertionError('recv data error')


if __name__ == '__main__':
    import sys

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO,
                        stream=sys.stdout)
    # udp_server_data('10.5.24.224', 1112, send_msg_to_client=None)
