# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 14:41:08
# @Author  : Pane Li
# @File    : ip.py
"""
ip

"""
import ipaddress
import re


def ip_range(ip: str = '192.168.2.3', start_ip: str = '192.168.2.1', end_ip: str = '192.168.2.254', assertion=True) -> bool:
    """验证IP地址是否在约定的范围

    :param ip: 验证的IP地址
    :param start_ip: IP地址起始
    :param end_ip: IP地址结束
    :param assertion: 为True 时直接断言，为False时返回判断结果
    :return:
    """
    if ip and start_ip and end_ip:
        start_address = ipaddress.ip_address(start_ip)
        end_address = ipaddress.ip_address(end_ip)
        ip_address = ipaddress.ip_address(ip)
        if assertion:
            assert end_address >= ip_address >= start_address, 'ip is not in the specified range'
        else:
            return end_address >= ip_address >= start_address


def validate_mac(mac) -> None:
    assert re.match(r"^\s*([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}\s*$", mac), f'"{mac}" is not mac'


def is_private_ip(ip) -> bool:
    return ipaddress.ip_address(ip).is_private
