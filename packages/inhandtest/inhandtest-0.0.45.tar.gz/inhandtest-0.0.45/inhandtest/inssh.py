# -*- coding: utf-8 -*-
# @Time    : 2023/3/8 13:26:52
# @Author  : Pane Li
# @File    : inssh.py
"""
inssh

"""
import logging
import os.path

import paramiko
from paramiko.ssh_exception import *


class InSsh:
    def __init__(self, host: str, username: str, password: str, port=22):
        """

        :param host: ssh 连接主机地址
        :param username: ssh 连接主机用户名
        :param password: ssh 连接主机密码
        :param port: 端口， 默认22
        """
        self.__host = host
        self.__username = username
        self.__password = password
        self.__port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.transport = paramiko.Transport((host, port))
        try:
            logging.info(f"ssh connect {self.__host} by {self.__username}:{self.__password}")
            self.ssh.connect(self.__host, self.__port, self.__username, self.__password, timeout=5)
        except AuthenticationException:
            raise AuthenticationException(f"ssh connect {self.__host} Username or Password error")
        except Exception:
            raise ConnectionError(f"ssh connect {self.__host} connect error")
        self.transport.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def exec_command(self, command: str) -> str:
        """执行命令并返回结果

        :param command: 执行命令, 多条时使用分号隔开
        :return: 返回所有命令执行后的结果
        """
        result = None
        if command:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            logging.info(f'exec command 【{command}】')
            result = stdout.read().decode("utf-8")
            logging.info(f'command result 【{result}】')
        return result

    def download_file(self, remote_file, local_file) -> None:
        """
        从服务器上下载文件
        :param remote_file: 远端文件路径
        :param local_file: 本地文件路径
        :return:
        """
        try:
            self.sftp.get(remote_file, local_file)
            logging.info(f'{remote_file} download success')
        except Exception as e:
            logging.error(f'{remote_file} download failed, {e}')

    def upload_file(self, remote_file, local_file) -> None:
        """
        文件上传
        :param remote_file: 远端文件路径
        :param local_file: 本地文件路径
        :return:
        """
        try:
            self.sftp.put(local_file, remote_file)
            logging.info(f'{local_file} upload success')
        except Exception as e:
            logging.error(f'{remote_file} upload failed, {e}')

    def clear_dir_or_remove_file(self, dir_name_or_file_path: str) -> None:
        """ 清除远端目录下所有文件，或单个文件

        :param dir_name_or_file_path: 目录或者文件路径
        :return:
        """

        def remove_file(file_path):
            try:
                self.sftp.remove(file_path)
                logging.info(f'{file_path} remove success！')
            except Exception as e:
                logging.error(f'{file_path} remove failed! {e}')

        if os.path.isdir(dir_name_or_file_path):
            files = self.sftp.listdir(dir_name_or_file_path)
            [remove_file(os.path.join(dir_name_or_file_path, i)) for i in files]
        else:
            remove_file(dir_name_or_file_path)

    def get_file_content(self, file_path: str) -> str:
        """获取文件内容

        :param file_path:  文件路径  ex： 'D:\ecoer\sdf.sh'
        :return:
        """
        self.sftp.chdir(os.path.dirname(file_path))
        logging.info(f'read {file_path} content success')
        return self.sftp.file(os.path.basename(file_path), 'r').read().decode(encoding='utf-8')

    def write_file_content(self, file_path: str, content: str, mode='w') -> None:
        """像文件写入数据

        :param file_path: 文件全路径 ex: 'D:\ecoer\sdf.sh'
        :param content: 写入的文件内容，多行内容使用\n 连接
        :param mode: 'w' 替换文件内容写入， 'a' 追加内容
        :return:
        """
        self.sftp.chdir(os.path.dirname(file_path))
        with self.sftp.open(os.path.basename(file_path), mode) as f:
            f.write(content)
        logging.info(f'write {file_path} content success')

    def chmod(self, file_path: str, mode) -> None:
        """更改文件权限

        :param file_path:
        :param mode:
        :return:
        """
        self.sftp.chmod(file_path, mode)
        logging.info(f'chmod {file_path} success')

    def mkdir(self, path, mode=511) -> None:
        """创建文件夹

        :param path: 路径
        :param mode:  511 即 o777 权限，最大的
        :return:
        """
        self.sftp.mkdir(path, mode)
        logging.info(f'mkdir {path} success')

    def rmdir(self, path) -> None:
        """删除文件夹

        :param path: 路径
        :return:
        """
        self.sftp.rmdir(path)
        logging.info(f'remove {path} success')

    def rename(self, old_path, new_path) -> None:
        """文件重命名

        :param old_path:
        :param new_path:
        :return:
        """
        self.sftp.rename(old_path, new_path)
        logging.info(f'{old_path} rename success')

    def close(self) -> None:
        """断开连接

        :return:
        """
        self.ssh.close()
        self.sftp.close()
        self.transport.close()


if __name__ == '__main__':
    import sys

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, stream=sys.stdout)
