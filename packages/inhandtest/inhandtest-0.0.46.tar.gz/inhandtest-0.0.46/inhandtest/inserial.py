# -*- coding: utf-8 -*-
# @Time    : 2023/5/6 9:24:33
# @Author  : Pane Li
# @File    : inserial.py
"""
inserial

"""
import logging
from threading import Thread
from inhandtest.tools import check_windows_process
from serial import *
from serial.tools import list_ports
from inhandtest.exception import *


class InSerial:

    def __init__(self, com='', baud_rate=115200, data_bits=8, parity='none', stop_bit=1, flow_control=False,
                 timeout=1, username='adm', password='123456'):
        """ 在使用串口做功能配置时需关闭日志服务器，避免影响功能，如果在接收日志时可不登录, 使用with 语句主动关闭串口

        :param com: com口，如不传系统自动查找, com1|com2
        :param baud_rate: 波特率
        :param data_bits: 8|7 只能是這兩個选项
        :param parity: none|even|odd
        :param stop_bit: 1|2
        :param flow_control: True|False
        :param timeout: 控制read函数读取超时时间
        :param username: 登录账号
        :param password: 登录密码
        """
        self.com = com.upper()
        self.baud_rate = baud_rate
        self.data_bits = data_bits
        self.parity = parity[0].upper()
        self.stop_bit = stop_bit
        self.flow_control = flow_control
        self.timeout = timeout
        self.username = username
        self.password = password
        self.__user_flag = 'Router#'
        self.__super_flag = '/www #'
        self.__config_flag = '(config)#'
        self.__normal_flag = 'Router>'
        self.serial = Serial()
        self.__auto_find_com()
        self.logs_number = []
        self.__open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __auto_find_com(self):
        if not self.com:
            port_list = list(list_ports.comports())
            logging.info(port_list)
            if len(port_list) <= 0:
                logging.error("The Serial port can't find!")
            else:
                # 找到第一个可用的串口
                port_list_0 = list(port_list[0])
                self.com = port_list_0[0]

    def login(self, username=None, password=None):
        username = self.username if not username else username
        password = self.password if not password else password
        try:
            self.serial.write("\n".encode("gbk"))
            flag = self.serial.readlines(2)
            logging.info(f'{flag[1].decode()}')
            flag = flag[1].decode("gbk").strip()
            if flag in (self.__config_flag, self.__super_flag, self.__normal_flag, self.__user_flag):
                pass
            elif 'login:' in flag:
                self.send_cli({username: ":"})
                self.serial.write((password + '\n').encode('gbk'))
                login_flag = self.serial.read_until('>'.encode("gbk")).decode("gbk")
                if ' \r\n' == login_flag:
                    raise UsernameOrPasswordError
                else:
                    tag = login_flag.split('\r\n')[-1].strip().replace('>', '')
                    self.__user_flag = f'{tag}#'
                    self.__normal_flag = f'{tag}>'
                    logging.info(login_flag)
                    pass
            else:
                logging.error(f'Serial Connect {self.com} Failed')
                raise ConnectionError
            logging.info(f'Serial Connect {self.com} Successful')
        except Exception:
            raise ConnectionError

    def __open(self):
        try:
            check_windows_process('sscom', True)
            time.sleep(2)
        except:
            pass
        self.serial.port = self.com
        self.serial.baudrate = self.baud_rate
        self.serial.bytesize = self.data_bits
        self.serial.parity = self.parity
        self.serial.stopbits = self.stop_bit
        self.serial.xonxoff = self.flow_control
        self.serial.timeout = self.timeout
        if not self.serial.is_open:
            self.serial.open()

    def receive_log(self, timeout=20, logs_number=1):
        """接收日志

        :param timeout: 接收超时时间
        :param logs_number
        :return:
        """
        self.serial.timeout = 1
        for i in range(0, timeout, 1):
            data = self.serial.readline()  # 获取串口内容
            logging.info(f'serial com {self.com} read str <{data.decode()}>')
            if data:
                self.logs_number.append(data.decode())
            if logs_number == len(self.logs_number):
                break
            else:
                time.sleep(1)
        else:
            raise Exception('can not receive logs')

    def logout(self):
        self.send_cli({"exit": "[Y|N]", "y": "Press"})

    def send_cli(self, command: dict):
        """发送命令，支持多条，

        @param command: 支持发送多条命令，命令为key，期望返回为value, 先执行的命令写前面
        {"first_command": "first_flag", "second_command": "second_flag"}
        @return: 当发送一条命令时直接返回结果，发送多条时返回结果列表
        """
        flag_reacts = []
        if command:
            for com, flag in command.items():
                self.serial.write(bytes((com + "\r\n").encode("gbk")))
                flag_react = self.serial.read_until(flag.encode("gbk")).decode("gbk").strip()
                logging.info(flag_react)
                flag_reacts.append(flag_react)
        if len(flag_reacts) == 1:
            return flag_reacts[0]
        else:
            return flag_reacts

    def close(self):
        if self.serial.is_open:
            try:
                self.serial.close()
            except SerialException:
                logging.error(f'Serial Close {self.com} Failed')

    def assert_recv_data(self, action, length, timeout=10, content=None):
        """
        :param action: 操作函数
        :param length: 期望接受到的数据长度
        :param timeout: 最大超时时间
        :param content: 期望校验接受到的数据的内容
        """
        serial_thread = Thread(target=self.receive_log, args=(timeout, length))
        serial_thread.daemon = True
        serial_thread.start()
        time.sleep(1)
        action()
        for x in range(0, timeout, 1):
            if length and not content:
                command = 'length == len(self.logs_number)'
            elif not length and content:
                command = "content in ','.join(self.logs_number)"
            else:
                command = "length == len(self.logs_number) and content in ','.join(self.logs_number)"
            if eval(command):
                logging.info(f"assert data {self.logs_number} ok")
                break
            else:
                time.sleep(1)
        else:
            raise Exception('serial not receive data')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, stream=sys.stdout)
    # ss.login(password='123456')
    # ss.logout()
    # ss.login()
    # ss.read_all_and_write()
    # for i in range(0, 50):
    #     logging.info(ss.read_all_data)
    #     time.sleep(1)
    # ss.read_all_data
    # ss.config_mode()
    # result = ss.send_cli({"": "#"})
    # logging.info(f'1111 {result[0]}')
    # ss.close()
