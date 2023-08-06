# -*- coding: utf-8 -*-
# @Time    : 2023/3/3 9:23:56
# @Author  : Pane Li
# @File    : inrequest.py
"""
封装request， 使设备和平台都能来正常调用，统一入口，token过期时也能自动更新

"""
import base64
import logging
import os
import re
import sys
import time
from typing import List
import urllib3
import requests
from inhandtest.exception import ParameterValueError, UsernameOrPasswordError, TimeOutError, UpgradeFailedError, \
    ResourceNotFoundError
from inhandtest.file import file_hash
from inhandtest.tools import dict_in, dict_merge, replace_str, DotDict, loop_inspector


class DnInterface:
    def __init__(self, username, password, host='c.inhand.com.cn'):
        """
        :param username  平台用户名
        :param password  平台密码
        :param host: 'c.inhand.com.cn'
        """
        self.host = host
        self.username = username
        self.api = InRequest(self.host, username, password, 'dn4')

    def add_device(self, sn: str, mac: str, model: str) -> None:
        """添加设备，

        :param sn: 设备序列号
        :param mac: 设备mac地址
        :param model: 设备型号 IR6XX_EVDO  IR300
        :return:
        """

        def get_model_id(model_name: str) -> str:
            models = self.api.send_request('api/models', method='get', param={'limit': 0, 'verbose': 1}).json().get(
                'result')
            for model_ in models:
                if model_.get('name').upper() == model_name.upper():
                    return model_.get('_id')
            else:
                raise ResourceNotFoundError(f"the model {model_name} not found")

        for i in range(3):
            response = self.api.send_request('api/devices', method='get',
                                             param={"verbose": 100, "limit": 10, "cursor": 0,
                                                    'serial_number': sn, 'plc_id': 0})
            if response.json().get('total') == 0:
                body = {"deviceConfig": {"maxHeartbeatLost": 6, "heartbeatInterval": 120, "heartbeatTimeout": 10,
                                         "resendLogin": 60}, "siteName": "", "siteId": None, "name": sn,
                        "businessState": "0", "modelId": get_model_id(model), "model": model.upper(),
                        "serialNumber": sn, "mac": mac.upper(), "mobileNumber": "", "plcId": 0,
                        "config": {"timeout": "300000", "ackTimeout": "120000", "ackRetries": "3", "sync": "2"}}
                self.api.send_request('api/devices', 'post', param={"create_site": 0}, body=body)
                logging.info(f"the {sn} device add success")
            else:
                break

    @loop_inspector('device online')
    def assert_device_online(self, sn: str, timeout=120, interval=5) -> int:
        """ 校验设备基本状态

        :param sn: 序列号
        :param timeout: 校验信息，最大超时时间
        :param interval: 校验信息，校验间隔时间
        :return: True or False
        """
        response = self.api.send_request('api/devices', method='get',
                                         param={"verbose": 100, "limit": 10, "cursor": 0,
                                                'serial_number': sn, 'plc_id': 0})
        if response.json().get('total') == 1:
            device_id = response.json().get('result')[0].get('_id')
            response = self.api.send_request(f'api/devices/{device_id}', method='get', param={"verbose": 100}).json()
            return response.get('result').get('online')
        else:
            return 0

    def delete_device(self, sn):
        response = self.api.send_request('api/devices', method='get',
                                         param={"verbose": 100, "limit": 10, "cursor": 0,
                                                'serial_number': sn, 'plc_id': 0}).json()
        if response.get('total') == 1:
            self.api.send_request(f'api/devices/{response.get("result")[0].get("_id")}', method='delete')
            logging.info(f"the {sn} device delete success")


class DmInterface:

    def __init__(self, username, password, host='iot.inhand.com.cn'):
        """
        :param username  平台用户名
        :param password  平台密码
        :param host: 'iot.inhand.com.cn'|'iot.inhandnetworks.com' 平台是哪个环境,
        """
        self.host = host
        self.username = username
        type_ = 'iot' if ('iot' in self.host) or ('elms' in self.host) else 'ics'
        self.api = InRequest(self.host, username, password, type_)

    def device_exist(self, sn: str, timeout=120, interval=5) -> None:
        """检查设备在平台账号下存在，如果超时都不存在就抛异常

        :param sn:
        :param timeout:
        :param interval:
        :return:
        """
        for i in range(0, timeout, interval):
            response = self.api.send_request('api/devices', method='get',
                                             param={"verbose": 100, "limit": 10, "cursor": 0,
                                                    'serial_number': sn})
            if response.json().get('total') == 1:
                logging.info(f'check {sn} device exist')
                break
            logging.info(f'check {sn} device is not exist, please wait for {interval}s')
            time.sleep(interval)
        else:
            raise TimeOutError(f'{self.host} {self.username} account not found device {sn}')

    def device_state(self, sn: list) -> List[dict]:
        """根据sn 转换属性 属性值有：  online: 在线|离线   1|0
                                       iccid:
                                       imei:
                                       imsi:
                                       model: 设备型号
                                       version: 固件版本
                                       hwVersion: 硬件版本 'V1.0'
                                       bootVersion:  Bootloader版本  '1.1.3.r4956'
                                       sn: 序列号
                                       address
                                       id: 设备id
                                       name: 设备名字
                                       ip: 设备连接平台的ip地址
                                       protocol: 设备连接平台的协议
                                       config_sync: 设备配置同步状态
        :param sn: 列表
        :return: [{'sn': $sn, 'online': 1, 'iccid': '', 'imei'}]
        """
        result = []
        for sn_ in sn:
            response = self.api.send_request('api/devices', method='get',
                                             param={"verbose": 100, "limit": 10, "cursor": 0,
                                                    'serial_number': sn_}).json()
            if response.get('total') == 1:
                res = response.get('result')[0]
                config_sync = res.get('config').get('sync') if res.get('config') else None
                result.append(
                    {'sn': sn_, 'online': res.get('online'), 'iccid': res.get('info').get('iccid'),
                     'imei': res.get('info').get('imei'), 'imsi': res.get('info').get('imsi'),
                     'version': res.get('info').get('swVersion'), 'hwVersion': res.get('info').get('hwVersion'),
                     'bootVersion': res.get('info').get('bootVersion'), 'address': res.get('address'),
                     'id': res.get('_id'), 'name': res.get('name'), 'ip': res.get('pubIp'),
                     'protocol': res.get('protocol'), 'config_sync': config_sync, 'model': res.get('model')})
            else:
                result.append(
                    {'sn': sn_, 'online': None, 'iccid': None, 'imei': None, 'imsi': None, 'version': None,
                     'hwVersion': None, 'bootVersion': None, 'address': None, 'id': None, 'name': None, 'ip': None,
                     'protocol': None, 'config_sync': None, 'model': None})
        return result

    def add_device(self, sn: str) -> None:
        """添加设备，

        :param sn: 设备序列号
        :return:
        """
        for i in range(5):
            response = self.api.send_request('api/devices', method='get',
                                             param={"verbose": 100, "limit": 10, "cursor": 0,
                                                    'serial_number': sn})
            if response.json().get('total') == 0:
                self.api.send_request('api/devices', 'post',
                                      body={"name": sn + str(int(time.time())), "serialNumber": sn})
                logging.info(f"the {sn} device add success")
            else:
                break

    def assert_device_state(self, sn: str, state: dict, timeout=120, interval=5) -> None:
        """校验设备基本状态

        :param sn: 序列号
        :param state:   支持表达式${value} ex: {'version': "'${value}' in 'V1.1.3.r4956'"}
                        online: 在线|离线   1|0
                        connected: true 只有ics 有该参数
                        model: 设备型号
                        iccid:
                        imei:
                        imsi:
                        version: 固件版本
                        hwVersion: 硬件版本 'V1.0'
                        bootVersion:  Bootloader版本  '1.1.3.r4956'
                        sn: 序列号
                        address
                        vip:  只能在ics里面使用
                        ip: 设备连接平台的ip地址
                        protocol: 设备连接平台的协议 ex: 'mqtt' or 'ovdp'
                        config_sync: 设备配置同步状态 ex: 2  同成功
        :param timeout: 校验信息，最大超时时间
        :param interval: 校验信息，校验间隔时间
        :return: True or False
        """
        if state:
            import ipaddress
            for i in range(0, timeout, interval):
                result = self.device_state([sn])[0]
                for key, value in state.items():
                    if '${value}' in value:
                        value = replace_str(value, {'${value}': result.get(key)})
                        logging.info(f'start assert {sn} state {key} {value}')
                        try:
                            if not eval(value, {'ipaddress': ipaddress}):
                                logging.info(f'the {sn} device {key} info eval {value} is false')
                                break
                        except Exception as e:
                            logging.error(e)
                            break
                    else:
                        logging.info(f'start assert {sn} state {key} {value}')
                        if result.get(key) != value:
                            logging.info(f'the {sn} device {key} info value is {result.get(key)} not {value}')
                            break
                else:
                    logging.info(f"check {sn} device all state success")
                    break
                logging.info(f"check {sn} device state failed, please wait for {interval}s")
                time.sleep(interval)
            else:
                raise TimeOutError(f"the {sn} state {state} check failed")

    def send_config_online(self, sn: str or list, config: str) -> List[str]:
        """下发配置， 多台时仍然是一台一台下发的， 注意逻辑 设备必须是在线的才能下发

        :param config: 配置命令，多个配置用'\n'隔开
        :param sn: 一台设备或多台设备
        :return: list 返回未成功下发配置的设备sn
        """
        body = {
            "deviceType": 0,
            "deviceContent": config,
            "deviceDesc": 'set running config'
        }
        sn = [sn] if isinstance(sn, str) else sn
        online_devices = list(filter(lambda x: x.get('online'), self.device_state(sn)))
        offline_devices = list(filter(lambda x: not x.get('online'), self.device_state(sn)))
        if online_devices:
            for on_device in online_devices:
                logging.info(f'the {on_device.get("sn")} device send config')
                self.api.send_request(f'/api/devices/{on_device.get("id")}/config/set', 'post', param={'timeout': 30},
                                      body=body)
        else:
            logging.warning(f"the {sn} all offline")
        return [offline_.get('sn') for offline_ in offline_devices]

    def get_config_online(self, sn: str, config: str = None) -> None:
        """平台获取配置 设备需要在线

        :param sn: 序列号
        :param config: 对获取到的配置做校验 多条配置使用'\n'隔开， 为None时仅获取
        """
        response = self.api.send_request('api/devices', method='get',
                                         param={"verbose": 100, "limit": 10, "cursor": 0,
                                                'serial_number': sn})
        if response.json().get('total') == 1 and response.json().get('result')[0].get('online') == 1:
            device_id = response.json().get('result')[0].get('_id')
            device_name = response.json().get('result')[0].get('name')
            for i in range(0, 3):
                try:
                    task_state = self.api.send_request('api2/tasks/run', 'post',
                                                       body={'name': "GET RUNNING CONFIG", 'objectId': device_id,
                                                             'priority': 30, 'objectName': device_name,
                                                             'timeout': 30000,
                                                             'type': "4"}).json().get('result').get('state')
                    assert task_state == 3, "GET RUNNING CONFIG task status error!"
                    break
                except Exception as e:
                    logging.error(f'get running config task status reason is {e}, try {i + 2} again')
            else:
                raise Exception(f'device {sn} get running config task status failed')
            config_content = self.api.send_request(f'api/devices/{device_id}/config', 'get').json().get('result').get(
                'content')
            if config:
                assert set(config.split('\n')).issubset(set(config_content.split('\n'))), f'config {config} not exist'
        else:
            raise ResourceNotFoundError(f'the {sn} device not exist or offline')

    def upgrade_firmware_online(self, sn: str, firmware: str, timeout=10 * 60, interval=10) -> None:
        """ 升级固件， 保障升级成功不然就会报错

        :param sn: 设备序列号
        :param firmware: 升级的固件，本地全路径
        :param timeout: 下发升级任务后，总体的升级超时时间， 单位秒 至少5分鐘
        :param interval: 升级任务检测间隔， 单位秒
        :return None or TimeOutError， 升级失败就报TimeOutError
        """

        def model(name):
            models = self.api.send_request('api/models', 'get',
                                           {'gateway': True, 'verbose': 100, 'limit': 0}).json().get('result')
            for model_ in models:
                if len(re.findall(model_.get('firmwareNamePattern'), name)) == 1:
                    return model_.get('name')

        def version(name):
            return 'V' + re.findall('V(.*).bin', name)[0]

        online_devices = list(filter(lambda x: x.get('online'), self.device_state([sn])))
        if online_devices:
            device_id = online_devices[0].get('id')
            device_name = online_devices[0].get('name')
            file_name = os.path.basename(firmware)
            if os.path.isfile(firmware):  # 只要升级文件存在就升级
                get_firmware = self.api.send_request('api/firmware', 'get', {'name': file_name}).json()
                if get_firmware.get('total') == 0:
                    if os.path.exists(firmware):
                        param = {'filename': firmware, 'oid': 'undefined'}
                        upload_file = self.api.send_request('api/file/form', method='post', param=param,
                                                            params_type='form', file_path=firmware).json().get('result')
                        body = {'fid': upload_file['_id'], 'jobTimeout': 30, 'model': model(file_name),
                                'name': file_name,
                                'version': version(file_name), 'desc': 'auto test upload firmware'}
                        firmware_id = self.api.send_request('api/firmware', 'post', body=body, ).json().get(
                            'result').get(
                            '_id')
                    else:
                        raise FileNotFoundError(f'{firmware} not exist')
                else:
                    logging.info(f'This file {firmware} already exists on the cloud {self.host} {self.username}')
                    firmware_id = get_firmware.get('result')[0].get('_id')
                # 已完成固件上传
                job_id = self.api.send_request(f'api/device/{device_id}/upgrade', method='post',
                                               body={'deviceName': device_name, 'firmwareId': firmware_id,
                                                     'timeout': int(timeout / 60)}).json().get('result').get('_id')
                for i in range(0, timeout, interval):
                    time.sleep(interval)
                    job_response = self.api.send_request(f'/api2/tasks', method='get',
                                                         param={"verbose": 50, 'types': 6, 'object_id': device_id,
                                                                'limit': 100, 'cursor': 0}).json().get('result')
                    job = [job for job in job_response if job.get('_id') == job_id]
                    if len(job) == 1:
                        if job[0].get('_id') == job_id:
                            if job[0].get('state') == 3:
                                logging.info(f"upgrade to {file_name} success!")
                                break
                            elif job[0].get('state') == -1:
                                raise UpgradeFailedError(f'upgrade to {file_name} failed!')
                    else:
                        raise UpgradeFailedError('create upgrade task failed!')
                else:
                    raise TimeOutError('upgrade job check timeout')
                self.assert_device_state(sn, state={'version': '"${value}" in ' + f'"{file_name}"'}, timeout=300)
            else:
                logging.info(f'{firmware} not is file or version of same ')
        else:
            raise Exception(f'the device {sn} is offline or not exist')

    def upgrade_firmware(self, sn: str or list, firmware: str) -> None:
        """ 升级固件，只管下发升级任务，不监督是否升级成功

        :param sn: 设备序列号
        :param firmware: 升级的固件，本地全路径
        :return None
        """

        def model(name):
            models = self.api.send_request('api/models', 'get',
                                           {'gateway': True, 'verbose': 100, 'limit': 0}).json().get('result')
            for model_ in models:
                if len(re.findall(model_.get('firmwareNamePattern'), name)) == 1:
                    return model_.get('name')

        def version(name):
            return 'V' + re.findall('V(.*).bin', name)[0]

        sn = [sn] if isinstance(sn, str) else sn
        devices = list(filter(lambda x: x.get('id'), self.device_state(sn)))
        if os.path.isfile(firmware) and devices:
            file_name = os.path.basename(firmware)
            get_firmware = self.api.send_request('api/firmware', 'get', {'name': file_name}).json()
            if get_firmware.get('total') == 0:
                if os.path.exists(firmware):
                    param = {'filename': firmware, 'oid': 'undefined'}
                    upload_file = self.api.send_request('api/file/form', method='post', param=param,
                                                        params_type='form', file_path=firmware).json().get('result')
                    body = {'fid': upload_file['_id'], 'jobTimeout': 30, 'model': model(file_name),
                            'name': file_name,
                            'version': version(file_name), 'desc': 'auto test upload firmware'}
                    firmware_id = self.api.send_request('api/firmware', 'post', body=body, ).json().get(
                        'result').get(
                        '_id')
                else:
                    raise FileNotFoundError(f'{firmware} not exist')
            else:
                logging.info(f'This file {firmware} already exists on the cloud {self.host} {self.username}')
                firmware_id = get_firmware.get('result')[0].get('_id')
            self.api.send_request(f'api/firmware/{firmware_id}/devices', method='post',
                                  body={'deviceIds': [device.get('id') for device in devices], 'deviceGroupIds': [], })
        else:
            logging.info(f'{firmware} not is file or device is not exist')

    def web_remote_online(self, sn: str) -> str:
        """封装远程web访问方法

        :param sn: str, 设备序列号
        :return: 远程web管理链接
        """
        if self.host == 'iot.inhand.com.cn':
            server = 'ngrok.iot.inhand.com.cn:4443'
        elif self.host == 'iot.inhandnetworks.com':
            server = 'iot.inhandnetworks.com:4443'
        elif self.host == 'ics.inhandiot.com':
            server = 'ics.inhandiot.com:4443'
        else:
            server = 'ngrok.ics.inhandnetworks.com:443'
        response = self.api.send_request('api/devices', method='get',
                                         param={"verbose": 100, "limit": 10, "cursor": 0,
                                                'serial_number': sn})
        if response.json().get('total') == 1 and response.json().get('result')[0].get('online') == 1:
            device_id = response.json().get('result')[0].get('_id')
            device_name = response.json().get('result')[0].get('name')
            body = {"priority": 30, "timeout": 20000, "objectId": device_id, "objectName": device_name,
                    "name": "ngrok connect", "type": "23", "data": {"server": server, "proto": 'http', "port": 80}}
            for i in range(0, 3):
                try:
                    ngrok = self.api.send_request('api2/tasks/run', method='post', body=body).json()
                    if ngrok["result"]["data"]["response"]:
                        return ngrok["result"]["data"]["response"]
                except Exception as e:
                    logging.error(f"ngrok request failed reason is {e}, try {i + 2} again")
            else:
                raise Exception(f'Device {sn} get ngrok failed.')
        else:
            raise ResourceNotFoundError(f'the {sn} is not exist or offline')

    def reboot_online(self, sn: str) -> None:
        """DM平台设备重启
        """
        response = self.api.send_request('api/devices', method='get',
                                         param={"verbose": 100, "limit": 10, "cursor": 0,
                                                'serial_number': sn})
        if response.json().get('total') == 1 and response.json().get('result')[0].get('online') == 1:
            device_id = response.json().get('result')[0].get('_id')
            logging.info(f'{self.host} send to {sn} reboot command')
            status = self.api.send_request(f'api/device/{device_id}/methods', 'post',
                                           body={'method': "reboot", 'timeout': 15000}).json().get('status')
            assert status == 'succeeded', 'reboot error!'
        else:
            raise ResourceNotFoundError(f'the {sn} is not exist or offline')

    def remote_maintenance_online(self, sn: str, protocol='http', port=80, local_host='192.168.2.1',
                                  action='connect') -> str or None:
        """封装dm远程维护方法

        :param sn，必须在线
        :param protocol: str, 本地主机服务的协议, 'http'| 'https'| 'tcp'
        :param port: 端口, 本地主机的端口
        :param local_host: str, 本地主机的ip地址
        :param action: str, 是否连接远程维护隧道, 'connect'| 'disconnect'| 'delete'| 当为connect 时如果隧道不存在则自动新增
        :return: 当action='connect' 时返回远程维护连接
        """
        device = list(filter(lambda x: x.get('id'), self.device_state([sn])))

        tunnel_des = f'{sn} tunnel {protocol}://{local_host}:{port} '

        def find_tunnel(device_id_):
            tunnels_ = self.api.send_request('/api/touch/tunnels', method='get',
                                             param={'verbose': 100, 'device_id': device_id_}).json().get('result')
            if tunnels_:
                for tunnel_ in tunnels_:
                    if tunnel_.get('proto') == protocol and tunnel_.get('localPort') == port and tunnel_.get(
                            'localAddress'):
                        return tunnel_.get('_id'), tunnel_.get('connected'), tunnel_.get('publicUrl')
            return None, None, None

        if device:
            device_id = device[0].get('id')
            add_tunnel_body = {'verbose': 100, 'proto': protocol, 'name': str(round(time.time() * 1000)),
                               'localAddress': local_host, 'localPort': port, 'deviceId': device_id}
            tunnel_id, tunnel_status, pub_url = find_tunnel(device_id)
            if action == 'connect' and device[0].get('online'):
                if not tunnel_id:
                    result = self.api.send_request('/api/touch/tunnels', method='post', body=add_tunnel_body).json()
                    tunnel_id = result.get('result').get('_id')
                    tunnel_status = False
                    logging.info(f'Add {tunnel_des} success, tunnel name is {add_tunnel_body["name"]}')
                if not tunnel_status:
                    for i in range(0, 3):
                        connect = self.api.send_request(f'/api/touch/tunnels/{tunnel_id}/connect', 'put').json()
                        if connect.get('result').get('connected'):
                            pub_url = connect.get('result').get('publicUrl')
                            logging.info(f'tunnel {tunnel_des} connect success')
                            break
                    else:
                        raise ConnectionError(f'tunnel {tunnel_des} connect failed')
                else:
                    logging.info(f'tunnel {tunnel_des} already connect')
                return pub_url
            elif action == 'disconnect' and device[0].get('online'):
                if tunnel_id and tunnel_status:
                    self.api.send_request(f'/api/touch/tunnels/{tunnel_id}/disconnect', 'put')
                    logging.info(f'tunnel {tunnel_des} disconnect success')
                else:
                    logging.info(f'tunnel {tunnel_des} not exist or already disconnect')
            elif action == 'delete':
                if tunnel_id:
                    self.api.send_request(f'/api/touch/tunnels/{tunnel_id}', 'delete')
                    logging.info(f'tunnel {tunnel_des} delete success')
                else:
                    logging.info(f'tunnel {tunnel_des} not exist')
        else:
            logging.error(f'the device {sn} not exist')

    def delete_device(self, sn: str or list) -> None:
        """

        :param sn: 设备序列号，一个或多个
        :return:
        """
        sn = [sn] if isinstance(sn, str) else sn
        device = list(filter(lambda x: x.get('id'), self.device_state(sn)))
        if device:
            for device_ in device:
                self.api.send_request(f'api/devices/{device_.get("id")}', 'delete')
                logging.info(f'the {device_.get("sn")} delete success')


class IcsInterface(DmInterface):
    __slots__ = ['remote_maintenance_online']

    def __init__(self, username, password, host='ics.inhandiot.com'):
        """
        :param username  平台用户名
        :param password  平台密码
        :param host: 'ics.inhandiot.com'|'ics.inhandnetworks.com' 平台是哪个环境
        """
        super().__init__(username, password, host)
        self.oid = self.__oid()

    def __oid(self) -> str:
        return self.api.send_request('api/me', 'get', {'verbose': 100}).json().get('result').get('oid')

    def add_device(self, sn_model: dict):
        """添加设备，

        :param sn_model: {$sn: 'IR302', $sn1: 'IR305'}
                model: IR901|IR912|IG902|IR915-WiFi|IG902-WiFi|VG710|IR915|IR611|IR615|IR301|IR302|IR305|IG501|IG502|IG532|IG974|VG814,
                    型号内容必须填写正确，不然添加的时候下发OpenVpn的配置会出问题，导致不能正常连接
        :return:
        """
        if sn_model:
            not_add = list(filter(lambda x: x.get('id') is None, self.device_state(list(sn_model.keys()))))
            if not_add:
                models = self.api.send_request('api/invpn/routers/models', 'get').json().get('result').get('models')
                for not_a in not_add:
                    sn = not_a.get('sn')
                    model = sn_model.get(sn)
                    for model_ in models:
                        if model == model_.get('name'):
                            lan_interface = model_.get('lanInterface')
                            if len(re.findall(model_.get('serialNumberPattern'), sn)) == 1:
                                subnet = self.api.send_request('api/invpn/router/subnet', 'get').json().get('result')
                                body = {'serialNumber': sn, 'name': sn + str(int(time.time())),
                                        'lanInterface': lan_interface,
                                        'subnet': subnet}
                                self.api.send_request('api/invpn/router', 'post', {'oid': self.oid}, body=body)
                                logging.info(f'add device {sn} to cloud {self.host} successfully')
                            break
                    else:
                        raise Exception(f'the Serial number {sn} and model do not match ')

    def device_state(self, sn: list) -> List[dict]:
        """根据sn 转换属性 属性值有：  online: 在线|离线   1|0
                                       connected: true | None
                                       iccid:
                                       imei:
                                       imsi:
                                       version: 固件版本
                                       hwVersion: 硬件版本 'V1.0'
                                       bootVersion:  Bootloader版本  '1.1.3.r4956'
                                       sn: 序列号
                                       id: 设备id
                                       name: 设备名称
                                       vip: 虚拟IP
                                       ip: 设备连接平台的ip地址
                                       protocol: 设备连接平台的协议
                                       config_sync: 设备配置同步状态
        :param sn: 列表
        :return: [{'sn': $sn, 'online': 1, 'iccid': '', 'imei'}]
        """
        result = []
        for sn_ in sn:
            response = self.api.send_request('api/invpn/routers', method='get',
                                             param={"limit": 10, "cursor": 0, 'verbose': 100,
                                                    'serialNumber': sn_}).json()
            if response.get('total') == 1:
                logging.info(f'the device {sn_} exist on {self.host}')
                res = response.get('result')[0]
                res_info = self.api.send_request(f'api/devices/{res.get("id")}', method='get',
                                                 param={'verbose': 100}).json().get('result')
                config_sync = res_info.get('config').get('sync') if res_info.get('config') else None
                result.append(
                    {'sn': sn_, 'online': res.get('online'), 'iccid': res.get('metadata').get('iccid'),
                     'imei': res.get('metadata').get('imei'), 'imsi': res.get('metadata').get('imsi'),
                     'version': res.get('metadata').get('swVersion'), 'hwVersion': res.get('metadata').get('hwVersion'),
                     'bootVersion': res.get('metadata').get('bootVersion'), 'vip': res.get('vip'),
                     'id': res.get('id'), 'connected': res.get('connected'), 'name': res.get('name'),
                     'ip': res_info.get('pubIp'), 'protocol': res_info.get('protocol'), 'config_sync': config_sync})
            else:
                result.append(
                    {'sn': sn_, 'online': None, 'iccid': None, 'imei': None, 'imsi': None, 'version': None,
                     'hwVersion': None, 'bootVersion': None, 'id': None, 'connected': None, 'name': None, 'ip': None,
                     'protocol': None, 'config_sync': None, 'vip': None})
        return result

    def send_openvpn_config(self, sn: str) -> None:
        """每次把设备添加到平台上线后，openvpn要连半天，可以主动推送下配置让openvpn连接的更快，
           如果设备已经连接上了openvpn就不在下发了

        :param sn: 单个sn
        :return:
        """
        result = self.device_state([sn])[0]
        if result.get('online') and not result.get('connected'):
            self.api.send_request(f'api/invpn/router/{result.get("id")}/config/send', 'get', param={'oid': self.oid})
        elif not result.get('id'):
            logging.warning(f'the device {sn} not exist')
        elif not result.get('online'):
            logging.warning(f'the device {sn} offline')
        elif result.get('connected'):
            logging.warning(f'the device {sn} already connected')

    def delete_device(self, sn: str or list) -> None:
        """

        :param sn: 设备序列号，一个或多个
        :return:
        """
        sn = [sn] if isinstance(sn, str) else sn
        device = list(filter(lambda x: x.get('id'), self.device_state(sn)))
        if device:
            for device_ in device:
                self.api.send_request(f'api/invpn/router/{device_.get("id")}', 'delete', {'oid': self.oid})
                logging.info(f'the {device_.get("sn")} delete success')


class StarInterface:

    def __init__(self, username, password, host='star.inhandcloud.cn'):
        """ 须确保用户关闭了多因素认证

        :param username  平台用户名
        :param password  平台密码
        :param host: 'star.inhandcloud.cn'|'star.inhandcloud.cn'|'star.nezha.inhand.dev'|'star.nezha.inhand.design' 平台是哪个环境,
        """
        self.host = host
        self.username = username
        self.api = InRequest(self.host, username, password, 'star')
        self.me = self.__get_me()

    def __get_me(self) -> DotDict:
        """ 获取me的各种信息 包括oid

        :return:
        """
        response = DotDict(
            self.api.send_request('/api/v1/users/me', method='get', param={"expand": 'org'}).json().get('result'))
        return response

    def device_state(self, sn: list) -> List[dict]:
        """根据sn 转换属性 属性值有：  online: 在线|离线   True|False
                                       iccid:
                                       imei:
                                       imsi:
                                       version: 固件版本
                                       licenseStatus: 'licensed'
                                       sn: 序列号
                                       address
                                       id: 设备id
                                       name: 设备名字
        :param sn: 列表
        :return: [{'sn': $sn, 'online': 1, 'iccid': '', 'imei'}]
        """
        result = []
        for sn_ in sn:
            response = self.api.send_request('/api/v1/devices', method='get',
                                             param={"expand": 'firmwareUpgradeStatus,compatibilities,org', "limit": 10,
                                                    "compatibilities": 'nezha_device_config,nezha_device_webui',
                                                    'serialNumber': sn_}).json()
            if response.get('total') == 1:
                res = response.get('result')[0]
                state = res.get('state') if res.get('state') else None
                result.append(
                    {'sn': sn_, 'online': res.get('online'),
                     'iccid': state.get('iccid') if state else None,
                     'imei': state.get('imei') if state else None,
                     'imsi': state.get('imsi') if state else None,
                     'version': res.get('firmware'),
                     'licenseStatus': res.get('licenseStatus'),
                     'address': res.get('address'),
                     'id': res.get('_id'),
                     'name': res.get('name')})
            else:
                result.append(
                    {'sn': sn_, 'online': None, 'iccid': None, 'imei': None, 'imsi': None,
                     'version': None, 'licenseStatus': None, 'address': None, 'id': None, 'name': None})
        return result

    def add_device(self, sn: str, mac_or_imei: str) -> None:
        """添加设备，

        :param sn: 设备序列号
        :param mac_or_imei: 添加设备时需要依赖设备的mac地址或者IMEI号，去生产库查询该设备是否是映翰通设备
        :return:
        """
        for i in range(5):
            validated_field = self.api.send_request(f'api/v1/serialnumber/{sn}/validate', method='post').json().get(
                'result').get('validatedField')
            if not list(filter(lambda x: x.get('id'), self.device_state([sn]))):
                self.api.send_request('api/v1/devices', 'post',
                                      body={"name": sn + str(int(time.time())), "serialNumber": sn, 'oid': self.me.oid,
                                            validated_field: mac_or_imei})
                logging.info(f"the {sn} device add success")
            else:
                break

    def assert_device_state(self, sn: str, state: dict, timeout=120, interval=5) -> None:
        """校验设备基本状态

        :param sn: 序列号
        :param state:   支持表达式${value} ex: {'version': "'${value}' in 'V1.1.3.r4956'"}
                        online: 在线|离线   True|False
                        iccid:
                        imei:
                        imsi:
                        version: 固件版本
                        licenseStatus: 'licensed'
                        sn: 序列号
                        address
        :param timeout: 校验信息，最大超时时间
        :param interval: 校验信息，校验间隔时间
        :return: True or False
        """
        if state:
            for i in range(0, timeout, interval):
                result = self.device_state([sn])[0]
                for key, value in state.items():
                    if '${value}' in value:
                        value = replace_str(value, {'${value}': result.get(key)})
                        logging.info(f'start assert {sn} state {key} {value}')
                        try:
                            if not eval(value):
                                logging.info(f'the {sn} device {key} info eval {value} is false')
                                break
                        except Exception as e:
                            logging.error(e)
                            break
                    else:
                        logging.info(f'start assert {sn} state {key} {value}')
                        if result.get(key) != value:
                            logging.info(f'the {sn} device {key} info value is {result.get(key)} not {value}')
                            break
                else:
                    logging.info(f"check {sn} device all state success")
                    break
                logging.info(f"check {sn} device state failed, please wait for {interval}s")
                time.sleep(interval)
            else:
                raise TimeOutError(f"the {sn} state {state} check failed")

    def delete_device(self, sn: str or list) -> None:
        """

        :param sn: 设备序列号，一个或多个
        :return:
        """
        sn = [sn] if isinstance(sn, str) else sn
        device = list(filter(lambda x: x.get('id'), self.device_state(sn)))
        if device:
            for device_ in device:
                self.api.send_request(f'api/devices/{device_.get("id")}', 'delete')
                logging.info(f'the {device_.get("sn")} delete success')


class InRequest:

    def __init__(self, host: str, username: str, password: str, type_='device', protocol='https', port=443):
        """支持设备，平台登录及操作API, 自动识别地址

        :param host:  主机地址，如果是平台的就填写平台server，如果是设备就填写设备的地址
        :param username:  用户名
        :param password: 密码
        :param type_: device|iot|ics|star|iscada|iwos|dn4  区分平台和设备
        :param protocol: 协议，当前只支持http https
        :param port: 端口
        """
        self.protocol = protocol
        self.host = host
        self.username = username
        self.password = password
        self.headers = {}
        self.type_ = type_
        self.port = port
        self.__login()

    def __url_pre(self, path: str):
        """host+path

        :param path:  请求路径
        :return:
        """
        if path.startswith('/'):
            return self.protocol + '://' + self.host + ':' + str(self.port) + path
        else:
            return self.protocol + '://' + self.host + ':' + str(self.port) + '/' + path

    def __login(self):
        if self.type_ in ('iot', 'ics', 'iwos', 'dn4'):
            self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
            param = {
                'client_id': '17953450251798098136',
                'client_secret': '08E9EC6793345759456CB8BAE52615F3',
                'grant_type': 'password',
                'type': 'account',
                'autoLogin': 'true',
                'password_type': 2,
                'pwdType': 'pwd',
                "username": self.username,
                "password": file_hash(self.password)}
            response = self.send_request('/oauth2/access_token', method='post', param=param).json()
            self.headers = {'Authorization': 'Bearer ' + response['access_token']}
        elif self.type_ in ('iscada', 'star'):
            settings_url = '/api/v1/erlang/frontend/settings' if self.type_ == 'iscada' else '/api/v1/frontend/settings'
            res_setting = self.send_request(settings_url, 'get', expect='result').json()
            # erlang 登录地址不一样，需要重新指向
            authority = res_setting['result']['authProvider']['authority']
            protocol_re = self.protocol
            host_re = self.host
            self.protocol = authority.split('://')[0]
            self.host = authority.split('://')[-1]
            param = {
                'client_id': res_setting['result']['authProvider']['clientId'],
                'client_secret': res_setting['result']['authProvider']['clientSecret'],
                'grant_type': 'password',
                'scope': 'offline',
                "username": self.username,
                "password": self.password,
                # "type": 'account'
            }
            response = self.send_request('/oauth2/token', method='post', param=param, params_type='form').json()
            self.headers = {'Authorization': 'Bearer ' + response['access_token']}
            self.protocol = protocol_re
            self.host = host_re
        elif self.type_ == 'device':
            username_password = '%s:%s' % (self.username, self.password)
            base_auth = base64.b64encode(username_password.encode()).decode()
            self.headers = {'Authorization': 'Basic %s' % base_auth}
            resp = self.send_request('v1/user/login', 'post').json()
            self.headers['Authorization'] = 'Bearer ' + resp['results']['web_session']

    def send_request(self, path, method, param=None, body=None, expect=None, file_path=None,
                     params_type='json', header=None, code=200, auth=True):
        """封装http请求，根据请求方式及参数类型自动判断使用哪些参数来发送请求

        :param path: 请求路径
        :param method: 请求方法
        :param param: 请求中的参数,
        :param body: post请求中的body，当消息体为json时使用
        :param expect: 期望包含的结果
        :param file_path: 文件路径，用于文件上传或者下载文件
        :param params_type: 参数类型，用于post请求，参数值：form|json
        :param header: 请求头 只支持字典
        :param code: 验证返回code
        :param auth: 是否认证， 默认需要的
        :return:
        """
        header = dict_merge(self.headers, header) if auth else header
        urllib3.disable_warnings()  # 去除https warnings提示
        method = method.upper()
        params_type = params_type.upper()
        url = self.__url_pre(path)
        if method == 'GET':
            res = requests.get(url=url, params=param, headers=header, verify=False)
            if file_path:
                with open(file_path, 'w', encoding='UTF-8') as f:
                    f.write(res.text)
        elif method == 'POST':
            if params_type == 'FORM':
                if file_path:
                    if self.type_ == 'device':
                        files = {
                            'file': (
                                os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream')}
                        res = requests.post(url, params=param, files=files, headers=header, verify=False)
                    else:
                        with open(file_path, 'rb') as f:
                            file_info = {"file": f}
                            res = requests.post(url, data=param, files=file_info, headers=header, verify=False)
                else:
                    res = requests.post(url=url, data=param, headers=header, verify=False)
            elif params_type == 'JSON':
                res = requests.post(url=url, params=param, json=body, headers=header, verify=False)
            else:
                res = requests.post(url=url, headers=header, verify=False)
        elif method == 'DELETE':
            if body:
                if params_type == 'JSON':
                    res = requests.delete(url, headers=header, json=body, verify=False)
                else:
                    res = requests.delete(url, headers=header, data=body, verify=False)
            else:
                res = requests.delete(url, params=param, headers=header, verify=False)
        elif method == 'PUT':
            if params_type == 'JSON':
                res = requests.put(url, json=body, params=param, headers=header, verify=False)
            else:
                res = requests.put(url, data=param, headers=header, verify=False)
        else:
            raise ParameterValueError(f"requests method {method} not support")
        logging.info(f'Requests Method:[{method}] Code: {res.status_code} URL: {url}, Param: {param}, Body: {body}')
        if res.status_code != 401:
            if self.type_ == 'device':
                if res.status_code == 404:
                    raise Exception('not support API login')
                if res.status_code == 200 and 'login' in path:
                    if 'error' in res.json().keys():
                        raise UsernameOrPasswordError
            res.encoding = 'utf-8'  # 如返回内容有中文的需要编码正确
            try:
                logging.info(f'Requests Response json is {res.json()}')
            except Exception:
                logging.warning(f'Requests Response json is None')
        else:
            # 当token过期时，统一重新登录后再次调API
            self.__login()
            res = self.send_request(path, method, param, body, expect, file_path, params_type, header, code)
        if code:
            assert res.status_code == code, '返回状态不一致'
        if expect:
            if isinstance(expect, list):
                if len(expect) > 0:
                    for i in expect:
                        if isinstance(i, str) or isinstance(i, int):
                            assert str(i) in res.text, f"Response text {res.text} Does not contain {i}"
                        elif isinstance(i, dict):
                            dict_in(res.json(), i)
            elif isinstance(expect, dict):
                dict_in(res.json(), expect)
            elif isinstance(expect, str) or isinstance(expect, int):
                assert str(expect) in res.text, f"Response text {res.text} Does not contain {expect}"
            else:
                raise ValueError('expect param type error！')
        return res


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, stream=sys.stdout)
    # testApi = StarInterface('liwei@inhand.com.cn', '123456', 'star.nezha.inhand.dev')
    api = DnInterface('smoke@inhand.com.cn', 'smoke@inhand', 'c.inhand.com.cn', )
    api.add_device('RL6152315576161', '00:18:05:29:12:AB', 'IR6XX_EVDO')
    api.delete_device('RL6152315576161')
    # testApi.remote_maintenance_online('RF3052213006490', )
    # testApi.add_device({'RF3052213006490': 'IR305'})
    # print(testApi.web_remote_online('RF3052213006490'))
    # testApi.device_exist('VG7512022009918')
    # testApi.get_config_online('VG7512022009918', 'hello\r\nword')
    # testApi.send_config_online('VG7512022009918', 'hello\nword')
    # testApi.send_openvpn_config('RF3022206089272')
    # print(testApi.remote_maintenance_online('RF3052213006490', action='delete'))
    # print(re.findall('V(.*).bin', 'IR9-V1.0.0.r10190.bin')[0])
    # # testApi.get_config_online('RF3052213006490', 'dhcpd_start=192.168.2.3')
    # testApi.assert_device_state('RF3022206089272', state={'online': 1, 'connected': True})
