# -*- coding: utf-8 -*-
# @Time    : 2023/2/7 15:56:30
# @Author  : Pane Li
# @File    : telnet.py
"""
telnet

"""
import logging
import re
import telnetlib
import time
from typing import List

from inhandtest.tools import loop_inspector, replace_str


class Telnet:
    __doc__ = '使用telnet连接设备，封装下面命令'

    def __init__(self, model: str, host: str, super_user: str, super_password: str, user='adm', password='123456',
                 port=23, **kwargs):
        """使用telnet连接设备

        :param model: 设备型号，VG710'|'IR302'|'ER805'|'ER605'|'IG902'|'IG502'|'IR915'
        :param host: 设备lan ip， 192.168.2.1
        :param super_user: 超级管理员的用户名称
        :param super_password:  超级管理员的密码
        :param user: 用户名
        :param password: 用户密码
        :param port: 端口
        :param kwargs: interface_replace, 字典类型，只替换输入命令 {'wan': 'wan0', 'wifi_sta': 'wan2', 'cellular1': 'wwan0'}
                       在telnet里面接口名称转换，使得输入命令时接口名称统一。
                       factory_username:  工厂用户名
                       factory_password: 工厂用户密码

        """
        self.model = model.upper()
        self.host = host
        self.super_user = super_user
        self.super_password = super_password
        self.user = user
        self.password = password
        self.port = port
        self.host_name = ''
        self.super_tag = '/www #'
        self.config_tag = '(config)#'
        self.user_tag = '#'
        self.normal_tag = '>'
        self.factory_tag = '(factory)#'  # 仅部分设备支持工厂模式
        self.factory_username = kwargs.get('factory_username')
        self.factory_password = kwargs.get('factory_password')
        self.interface_replace: dict = kwargs.get('interface_replace')
        if self.model not in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
            raise Exception(f'Not support this device model {self.model}')
        self.tn: telnetlib.Telnet
        self.__login()

    def update_hostname(self, hostname: str) -> None:
        """更新hostname 后对应的telnet也需要更新

        :param hostname: str
        :return:
        """
        self.host_name = hostname
        self.user_tag = f'{hostname}#'
        self.normal_tag = f'{hostname}>'

    def __login(self):
        """


        :return:
        """
        login_spe = {"VG710": '#', 'IR302': '>', 'ER805': '#', 'ER605': '#', 'IG902': '#', 'IG502': '#', 'IR915': '#'}
        try:
            # 连接telnet服务器
            logging.info("Start telnet 【%s:%s】" % (self.host, self.port))
            self.tn = telnetlib.Telnet(self.host, self.port, timeout=10)
        except:
            raise ConnectionError(f'Device【{self.host}:{self.port} connect failed】')
        logging.info("Telnet 【%s:%s】 connected" % (self.host, self.port))
        logging.info(self.tn.read_until('login:'.encode("cp936")).decode("cp936").strip())
        # 登录路由器
        self.tn.write("{}\n".format(self.user).encode("cp936"))
        logging.info(self.tn.read_until('Password:'.encode("cp936")).decode("cp936").strip())
        self.tn.write("{}\n".format(self.password).encode("cp936"))
        login_result = self.tn.read_until(login_spe.get(self.model).encode("cp936"), timeout=20).decode("cp936").strip()
        logging.info(login_result)
        if 'Login incorrect' in login_result:
            raise Exception('UsernameOrPasswordError')
        self.update_hostname(login_result.split('\r\n')[-1].split(' ')[-1][:-1])
        logging.info(f"Device {self.host} login success. user_tag: {self.user_tag}")
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __auto_login(function):
        """自动重新登录, 只能当装饰器使用， 不对外使用

        :param function:
        :return:
        """

        def __auto_login(self, *args, **kwargs):
            try:
                res = function(self, *args, **kwargs)
            except (ConnectionResetError, ConnectionAbortedError):
                self.__login()
                res = function(self, *args, **kwargs)
            return res

        return __auto_login

    @__auto_login
    def super_mode(self) -> None:
        """进入路由器的超级模式

        @return:
        """
        self.tn.write(("\003" + "\r").encode("cp936"))
        time.sleep(1)
        read_contents = self.tn.read_very_eager().decode('cp936').strip()
        logging.info(read_contents)
        if self.config_tag in read_contents:
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["exit", self.super_user + " " + self.super_password])
            elif self.model == 'IR302':
                self.send_cli(["exit", "exit", "support enable", self.super_user, self.super_password])
        elif self.super_tag in read_contents or (('/' in read_contents) and (' #' in read_contents)):
            self.send_cli(['cd /www'])
        elif self.user_tag in read_contents:
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli([self.super_user + " " + self.super_password])
            elif self.model == 'IR302':
                self.send_cli(["exit", "support enable", self.super_user, self.super_password])
        elif self.normal_tag in read_contents:
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["enable", self.password, self.super_user + ' ' + self.super_password])
            elif self.model == 'IR302':
                self.send_cli(["support enable", self.super_user, self.super_password])
        elif self.factory_tag in read_contents:
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["exit", self.super_user + " " + self.super_password])
            elif self.model == 'IR302':
                self.send_cli(["exit", "exit", "support enable", self.super_user, self.super_password])
        else:
            logging.warning(f'not support this mode. telnet return contents: {read_contents}')
            self.close()
            self.__login()
            self.super_mode()
        logging.info(f"Device {self.host} access in super mode")

    @__auto_login
    def config_mode(self) -> None:
        """配置模式

        :return:
        """
        self.tn.write(("\003" + "\r").encode("cp936"))
        time.sleep(1)
        read_contents = self.tn.read_very_eager().decode('cp936').strip()
        logging.info(read_contents)
        if self.config_tag in read_contents:
            pass
        elif self.super_tag in read_contents or (('/' in read_contents) and (' #' in read_contents)):
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["cli", "con t"], [self.user_tag, None])
            elif self.model == 'IR302':
                self.send_cli(["console", "enable", self.password, 'con t'])
        elif self.user_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['con t'])
        elif self.normal_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["enable", self.password, 'con t'])
        elif self.factory_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['exit', 'con t'])
        else:
            logging.warning(f'not support this mode, last content:{read_contents}')
            self.close()
            self.__login()
            self.config_mode()
        logging.info(f"Device {self.host} access in config mode")

    @__auto_login
    def user_mode(self) -> None:
        """用户特权模式， 默认进入就是用户特权模式

        :return:
        """
        self.tn.write(("\003" + "\r").encode("cp936"))
        time.sleep(1)
        read_contents = self.tn.read_very_eager().decode('cp936').strip()
        logging.info(read_contents)
        if self.config_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['exit'])
        elif self.super_tag in read_contents or (('/' in read_contents) and (' #' in read_contents)):
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["cli"], [self.user_tag])
            elif self.model in ['IR302']:
                self.send_cli(["console", "enable", self.password])
        elif self.user_tag in read_contents:
            pass
        elif self.normal_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["enable", self.password])
        elif self.factory_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['exit'])
        else:
            logging.warning(f'not support this mode. telnet return contents: {read_contents}')
            self.close()
            self.__login()
            self.user_mode()
        logging.info(f"Device {self.host} access in user mode")

    @__auto_login
    def normal_mode(self) -> None:
        """普通模式

        :return:
        """
        self.tn.write(("\003" + "\r").encode("cp936"))  # 普通模式下输入ctrl+c会返回  % Command is not supported!
        time.sleep(1)
        read_contents = self.tn.read_very_eager().decode('cp936').strip()
        logging.info(read_contents)
        if self.config_tag in read_contents:
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['exit', 'disable'])
            elif self.model in ['IR302']:
                self.send_cli(['exit', 'exit'])
        elif self.super_tag in read_contents or (('/' in read_contents) and (' #' in read_contents)):
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["cli", "disable"], [self.user_tag, None])
            elif self.model in ['IR302']:
                self.send_cli(["console"])
        elif self.user_tag in read_contents:
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['disable'])
            elif self.model in ['IR302']:
                self.send_cli(['exit'])
        elif self.normal_tag in read_contents:
            pass
        elif self.factory_tag in read_contents:
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['exit', 'disable'])
            elif self.model in ['IR302']:
                self.send_cli(['exit', 'exit'])
        else:
            logging.warning(
                f'not support this mode. telnet return contents: {read_contents} normal_tag: {self.normal_tag}')
            self.close()
            self.__login()
            self.normal_mode()
        logging.info(f"Device {self.host} access in normal mode")

    @__auto_login
    def factory_mode(self) -> None:
        """工厂模式， 仅部分机型支持该模式，使用时需注意

        :return:
        """
        if not self.factory_username or not self.factory_password:
            raise Exception("sure this device support factory mode, and init factory_username、factory_password")
        self.tn.write(("\003" + "\r").encode("cp936"))
        time.sleep(1)
        read_contents = self.tn.read_very_eager().decode('cp936').strip()
        logging.info(read_contents)
        if self.config_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(['exit', self.factory_username + " " + self.factory_password])
        elif self.super_tag in read_contents or (('/' in read_contents) and (' #' in read_contents)):
            if self.model in ['VG710', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["cli", self.factory_username + " " + self.factory_password], [self.user_tag, None])
            elif self.model in ['IR302']:
                self.send_cli(["console", "enable", self.password, self.factory_username + " " + self.factory_password])
        elif self.user_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli([self.factory_username + " " + self.factory_password])
        elif self.normal_tag in read_contents:
            if self.model in ['VG710', 'IR302', 'ER805', 'ER605', 'IG902', 'IG502', 'IR915']:
                self.send_cli(["enable", self.password, self.factory_username + " " + self.factory_password])
        elif self.factory_tag in read_contents:
            pass
        else:
            logging.warning(f'not support this mode. telnet return contents: {read_contents}')
            self.close()
            self.__login()
            self.factory_mode()
        logging.info(f"Device {self.host} access in factory mode")

    @__auto_login
    def send_cli(self, command: list or str, read_until=None, type_=None, **kwargs) -> str:
        """发送命令，支持多条，返回最后一条命令输入后的结果

        :param command: 支持发送多条命令["first_command", "second_command"] or 'command'
        :param read_until: str or list, 直至返回结果终止， 与command相呼应，如None的情况表示输入命令后等待1s， ['/www', None]
        :param type_: 'super'|'config'|'user'|'normal'|'factory'|None
        :param kwargs
               timeout: 当有read_until时， timeout参数生效， 读取超时时间 默认30秒
               key_replace: 字典, 需将固定字符替换为另一字符则填写该参数, 例: {'\r\n': '', ' ': ''}等
               key_replace_type: 'cli'|'last_read'|'cli_last_read'，仅在key_replace 有值时生效，默认last_read
                                 'cli': 仅替换发出去的命令
                                 'last_read': 仅替换最后读取到的内容
                                 'cli_last_read': 既要替换cli 也要替换最后读取到的内容
               interface_replace_type: 'cli'|'last_read'|'cli_last_read'，仅在interface_replace 有值时生效，默认cli
                                 'cli': 仅替换发出去的命令
                                 'last_read': 仅替换最后读取到的内容
                                 'cli_last_read': 既要替换cli 也要替换最后读取到的内容

        :return: 读取超时时返回Exception， 如果命令执行正确，返回最后一条命令输入后的结果
        """
        interface_replace_type = kwargs.get('interface_replace_type') if kwargs.get('interface_replace_type') else 'cli'
        key_replace_type = kwargs.get('key_replace_type') if kwargs.get('key_replace_type') else 'last_read'
        if kwargs.get('key_replace') and 'cli' in key_replace_type:  # 替换方法的关键字
            command = replace_str(command, kwargs.get('key_replace'))
        if self.interface_replace and 'cli' in interface_replace_type:  # 替换接口的关键字
            command = replace_str(command, self.interface_replace)
        timeout = kwargs.get('timeout') if kwargs.get('timeout') else 30
        result = ''
        if type_ == 'super':
            self.super_mode()
        elif type_ == 'config':
            self.config_mode()
        elif type_ == 'user':
            self.user_mode()
        elif type_ == 'normal':
            self.normal_mode()
        elif type_ == 'factory':
            self.factory_mode()
        logging.info(f"Device {self.host} send cli {command}")
        if command:
            command = [command] if isinstance(command, str) else command
            if read_until:
                read_until = [read_until] if isinstance(read_until, str) else read_until
                if len(read_until) != len(command):
                    raise Exception('The read_until params is error')
            else:
                read_until = [None for i in range(0, len(command))]
            for com, read_until_ in zip(command, read_until):
                self.tn.write((com + "\n").encode("cp936"))
                until_result = []
                for i in range(0, timeout, 1):  # 30秒没有找到期望的就主动断开
                    time.sleep(1)
                    result = self.tn.read_very_eager().decode('cp936', "ignore").strip()
                    if result:
                        logging.info(result)
                        result = result.split(com + "\r\n")[-1]
                    if read_until_:
                        until_result.append(result)
                        if isinstance(read_until_, str):
                            if read_until_ in ''.join(until_result):
                                result = ''.join(until_result)
                                break
                        elif isinstance(read_until_, list):
                            if not [read_until_one for read_until_one in read_until_ if
                                    read_until_one not in ''.join(until_result)]:
                                result = ''.join(until_result)
                                break
                    else:
                        # 如果没有readuntil 直接返回
                        break
                else:
                    self.tn.write(("\003" + "\r").encode("cp936"))
                    time.sleep(1)
                    raise Exception('ReadUntilTimeOutError')
        if kwargs.get('key_replace') and 'last_read' in key_replace_type:
            result = replace_str(result, kwargs.get('key_replace'))
        if self.interface_replace and 'last_read' in interface_replace_type:  # 替换接口的关键字
            result = replace_str(result, self.interface_replace)
        return result

    @__auto_login
    def assert_cli(self, cli=None, expect=None, timeout=20, interval=5, type_='super', key_replace=None,
                   key_replace_type='last_read', interface_replace_type='cli', read_until=None) -> None:

        """在某个模式下支持输入一条或多条命令, 且支持对执行时最后一条命令返回的结果做断言
           该方法对ping tcpdump命令 无效

        :param cli: str or list, 发送的命令 一条或者多条
        :param read_until: str or list, 直至返回结果终止， 与cli相呼应，如None的情况表示输入命令后等待1s， ['/www', None]
        :param expect: str or list or dict, 一条或多条希望校验的存在的结果，如需要判断不存在时，可以使用字典{$expect: False}
                       同时校验时可以是{$expect1: True, $expect: False}, str或者list时都是判断存在
        :param timeout: 检测超时时间  秒
        :param interval: 检测间隔时间 秒
        :param type_: 'super'|'config'|'user'|'normal'|'factory'|None
        :param key_replace: 字典, 需将固定字符替换为另一字符则填写该参数, 例: {'\r\n': '', ' ': ''}等 默认去掉换行
        :param key_replace_type: 'cli'|'last_read'|'cli_last_read'，仅在key_replace 有值时生效，默认last_read
                                 'cli': 仅替换发出去的命令
                                 'last_read': 仅替换最后读取到的内容
                                 'expect': 仅替换期望校验的值
                                 'cli_last_read'|'cli_expect'|'last_read_expect' 任意两种组合
                                 'cli_expect_last_read': 既要替换cli 也要替换最后读取到的内容还有校验的值
        :param interface_replace_type: 'cli'|'last_read'|'cli_last_read'，仅在interface_replace 有值时生效，默认cli
                                 'cli': 仅替换发出去的命令
                                 'last_read': 仅替换最后读取到的内容
                                 'expect': 仅替换期望校验的值
                                 'cli_last_read'|'cli_expect'|'last_read_expect' 任意两种组合

                                 'cli_expect_last_read': 既要替换cli 也要替换最后读取到的内容还有校验的值
        :return: None|Exception
        """

        if key_replace is None:
            key_replace = {'\r\n': ''}
        if cli is not None:
            for i in range(0, timeout, interval):
                if key_replace and 'cli' in key_replace_type:
                    cli = replace_str(cli, key_replace)
                    key_replace_type = key_replace_type.replace('cli', '')
                result = self.send_cli(cli, read_until, type_=type_, key_replace=key_replace, key_replace_type=key_replace_type,
                                       interface_replace_type=interface_replace_type)
                expect = str(expect) if isinstance(expect, int) else expect
                check_ = True
                if expect:
                    if 'expect' in key_replace_type:
                        expect = replace_str(expect, key_replace)
                    if 'expect' in interface_replace_type:
                        expect = replace_str(expect, self.interface_replace)
                    logging.info(f'start assert cli expect {expect}')
                    if isinstance(expect, str):
                        if expect not in result:
                            check_ = False
                    elif isinstance(expect, list):
                        if [expect_ for expect_ in expect if expect_ not in result]:
                            check_ = False
                    elif isinstance(expect, dict):
                        for k, v in expect.items():
                            if v:
                                if k not in result:
                                    check_ = False
                                    break
                            else:
                                if k in result:
                                    check_ = False
                                    break
                    else:
                        raise Exception('parameter expect is error')
                if check_:
                    break
                else:
                    time.sleep(interval)
                    logging.info(f"{expect} assert failure, wait for {interval}s inspection")
            else:
                raise Exception(f'{expect} not found timeout')
            logging.info(f'assert cli normal')

    @__auto_login
    @loop_inspector('Telnet ping', timeout=30)
    def ping(self, address='www.baidu.com', packets_number=4, params='', key_replace=None, lost_packets=False) -> bool:
        """设备里面ping地址

        :param address: 域名或者IP
        :param packets_number, ping 包的个数，默认都是4个
        :param params: 参数 如'-I cellular1'、'-s 32'
        :param key_replace: 字典类型， 传入的参数转换关系表{$old: $new}
        :param lost_packets: True|False 如果为True判断会丢包，如果为False判断不丢包
        :return:
        """
        self.super_mode()
        params = params if params.startswith(' ') else ' ' + params
        x = True
        result = self.send_cli("ping " + address + params + f' -c {packets_number}', self.super_tag,
                               key_replace=key_replace, key_replace_type='cli', )
        if lost_packets:
            # 判断需要丢包
            if 'received, 0% packet loss' in result:
                x = False
        else:
            # 当判断不为丢包时
            if 'received, 0% packet loss' not in result:
                x = False
        return x

    @__auto_login
    def tcpdump(self, expect: str or list or dict, key_replace=None, timeout=30, interval=5, **kwargs) -> None:
        """

        :param expect: str or list or dict,
                       一条或多条希望校验的存在的结果，如需要判断不存在时，可以使用字典{$expect: False}
                       str或者list时都是判断存在
        :param kwargs: 命令参数, str, interface| param| cat_num
                        interface: 接口名称, wan| wifi_24g| wifi_5g| lan| cellular1
                        param: 抓包过滤关键字, None, 'icmp', 'http', 'port 21', 'host 1.1.1.1 and icmp'
                        catch_num: 抓包数量, int
        :param key_replace: 字典类型， 传入的参数转换关系表{$old: $new}
        :param timeout: 校验超时时间, int
        :param interval: 5
        :return:
        """
        flag = {'interface': '-i', 'param': '', 'catch_num': '-c'}
        command = 'tcpdump'
        if kwargs:
            for k, v in kwargs.items():
                for k_, v_ in flag.items():
                    if k == k_:
                        command = command + f' {v_} ' + f'{v}'
        for i in range(0, timeout, interval):
            tag_not = False
            if isinstance(expect, dict):
                for k, v in expect.items():
                    if not v:
                        tag_not = True
                        break
                expect = [_ for _ in expect.keys()]
            else:
                pass
            if not tag_not:  # 判断需要抓到
                try:
                    self.send_cli(command, [expect], timeout=15, type_='super', key_replace=key_replace,
                                  key_replace_type='cli')
                    logging.info('find the exception in tcpdump result.')
                    self.tn.write(("\003" + "\r").encode("cp936"))
                    break
                except:
                    time.sleep(interval)
                    continue
            else:  # 判断不需要抓到
                try:
                    self.send_cli(command, [expect], timeout=10, type_='super', key_replace=key_replace,
                                  key_replace_type='cli')
                    self.tn.write(("\003" + "\r").encode("cp936"))
                    time.sleep(interval)
                    continue
                except:
                    break
        else:
            raise Exception('TcpdumpTimeOutError')

    @__auto_login
    @loop_inspector('Telnet regular match content', timeout=20)
    def re_match(self, command: str or list, regular: str or list, type_='super',
                 key_replace=None, key_replace_type='last_read') -> str or List[str]:
        """根据表达式获取最后一次执行命令的匹配值

        :param command: 发送命令，可以是一条或多条
        :param regular: 正则表达式，对执行的最后一次命令返回内容进行正则查询，必须要查询到，
                        如果查不到，直至查询超时并报错
                        如果查到不止一个，返回每个正则表达式的第一个
                        列子：硬件地址 r'HWaddr(.*)inet6'， '(([0-9a-fA-F]{2}[:]){5}([0-9a-fA-F]{2})|([0-9a-fA-F]{2}[-]){5}([0-9a-fA-F]{2}))'
        :param type_: 'super'|'config'|'user'|'normal'|'factory'|None
        :param key_replace: dict 替换最后一次命令返回内容的值 默认：{'\r\n':'', ' ': ''}
        :param key_replace_type: 'cli'|'last_read'|'cli_last_read'，仅在key_replace 有值时生效，默认last_read
                                 'cli': 仅替换发出去的命令
                                 'last_read': 仅替换最后读取到的内容
                                 'cli_last_read': 既要替换cli 也要替换最后读取到的内容
        :return: str or list ，根据正则表达式的个数返回值
        """
        key_replace = {'\r\n': '', ' ': ''} if key_replace is None else key_replace
        key_replace_type = 'last_read' if key_replace_type is None else key_replace_type
        result = self.send_cli(command, type_=type_, key_replace=key_replace, key_replace_type=key_replace_type)
        if isinstance(regular, str):
            re_list = re.findall(regular, result)
            if re_list:
                for i in re_list:
                    if isinstance(i, str):
                        return re.findall(regular, result)[0]
                    else:
                        return re.findall(regular, result)[0]
            else:
                logging.info(f'regular {regular} match content None')
                return False
        elif isinstance(regular, list):
            result_ = []
            for regular_ in regular:
                re_list = re.findall(regular_, result)
                if re_list:
                    for i in re_list:
                        if isinstance(i, str):
                            result_.append(re.findall(regular_, result)[0])
                        else:
                            result_.append(re.findall(regular_, result)[0][0])
                else:
                    logging.info(f'regular {regular_} match content None')
                    return False
            else:
                return result_

    # intools 实现获取信息更改信息
    @__auto_login
    def in_tools(self, get_info: str or list) -> str or List[str] or None:
        """在超级模式下可以获取或者设置相关intools的属性

        :param get_info: 常用属性可能会有productnumber,oem_name,等intools里面的属性
                       列： get_info='productnumber'，需要获取多个属性时采用列表传入

        :return: 返回需要获取的信息
        """
        if get_info:
            if isinstance(get_info, str):
                regular = f'{get_info}=(.*)\\r\\n'
            else:
                regular = [f'{info}=(.*)\\r\\n' for info in get_info]
            return self.re_match('intools', regular, key_replace={})

    @__auto_login
    def kill_process(self, name: str) -> None:
        """使用kill杀死对应进程

        :param name: 进程相关名称
        :return:
        """
        result = self.send_cli(f'ps auxww|grep {name}', type_='super')
        pids = []
        for process in result.split('\r\n'):
            process = re.sub(' +', ' ', process)
            if f'grep {name}' not in process and len(process.split(' ')) >= 11:
                pids.append(process.split(' ')[1])
        if pids:
            self.send_cli('kill -9 ' + ' '.join(pids))

    @__auto_login
    def reboot(self) -> None:
        """直接重启设备

        @return:
        """
        self.user_mode()
        self.send_cli(['reboot', 'y'])
        logging.info("【%s】Device is rebooting, wait for 120s" % self.host)
        time.sleep(120)

    @__auto_login
    def close(self) -> None:
        """关闭连接

        @return:
        """
        self.tn.close()
        logging.info("Telnet 【%s:%s】 close connect session" % (self.host, self.port))


if __name__ == '__main__':
    import sys

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, stream=sys.stdout)
    device = Telnet('IG902', '10.5.24.96', 'inhand', '64391099@inhand')
    # device.send_cli('ifconfig', '/www #', 'super')

        # device = Telnet('IG902', '
    # device = Telnet('VG710', '10.5.24.206', 'inhand', '64391099@inhand')
    # a = device.send_cli('ping www.baidu.com -c 4', '/www #', 'super')
    # print(eval('1==2'))
    # device.assert_cli('ifconfig |grep wifi', expect='Local', interface_replace_type='cli_expect_last_read')
    # print(device.re_match('ifconfig eth0', r'HWaddr(.*)inet6', key_replace={'\r\n':'', ' ': ''}))
