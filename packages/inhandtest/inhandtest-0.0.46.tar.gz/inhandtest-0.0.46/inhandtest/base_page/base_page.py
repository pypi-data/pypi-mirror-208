# -*- coding: utf-8 -*-
# @Time    : 2023/3/8 17:54:32
# @Author  : Pane Li
# @File    : base_page.py
"""
base_page

"""
import os.path
import sys
from os import path
from inhandtest.base_page._ig_contents_locators import IGContentsLocators
from typing import List
from inhandtest.exception import ModelError
from inhandtest.tools import loop_inspector
from playwright.sync_api import Page, Locator, expect, TimeoutError, sync_playwright
from inhandtest.base_page._vg710_contents_locators import VGContentsLocators
from inhandtest.base_page._ir3XX_contents_locators import Ir3XXContentsLocators
from inhandtest.base_page.table_tr import Table
import allure
import logging
import re


class BasePage:

    def __init__(self, host: str, username: str, password: str, protocol='https',
                 port=443, model='VG710', language='en', page: Page = None, **kwargs):
        """

        :param host:  设备主机地址
        :param username: 用户名
        :param password: 密码
        :param protocol: 协议
        :param port: 端口
        :param model: 'VG710'|'ER805'|'ER605'|'IR302'|'IG502'|'IG902'|'IR305'|'IR615'
        :param page: 当page为None时，自动打开浏览器及页面，否则使用传入的page
        :param kwargs:
                      browser: 当没有传入page时，可以选择浏览器
                      locale: dict 国际化
        """
        self.page = page
        self.host = host
        self.model = model.upper()
        self.protocol = protocol
        self.port = port
        self.__username = username
        self.__password = password
        self.language = language
        self.__browser_type = kwargs.get('browser')
        self.__http_credentials_model = ('VG710',)  # 需要使用http认证的设备, 没有登录页面 只有登录弹窗
        if self.page is None:
            self.__new_page()
        if self.model == 'VG710':
            self.content_locator = VGContentsLocators(self.page, language).tags_menu
        elif self.model in ('IG902', 'IG502'):
            self.content_locator = IGContentsLocators(self.page, language).tags_menu
        elif self.model in ('IR302', 'IR305', 'IR615'):
            self.content_locator = Ir3XXContentsLocators(self.page, language).tags_menu
        else:
            raise ModelError(f'not support this mode {model}')
        self.locale = kwargs.get('locale').get(language) if kwargs.get('locale') else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def __login_locator(self) -> dict:
        if self.model == 'VG710':
            return {'wait_locator': self.page.locator('#logo')}
        elif self.model in ('ER805', 'ER605'):
            return {'username': self.page.locator('#username'), 'password': self.page.locator('#password'),
                    'submit': self.page.locator('button'),
                    'wait_locator': self.page.locator('.inStarCloud')}
        elif self.model in ('IG902', 'IG502'):
            return {'username': self.page.locator('#username'), 'password': self.page.locator('#password'),
                    'submit': self.page.locator('//button[@type="submit"]'),
                    'wait_locator': self.page.locator('#logo')}
        elif self.model == 'IR302':
            return {'username': self.page.locator('#username'), 'password': self.page.locator('#passwd'),
                    'submit': self.page.locator('.login_button'),
                    'wait_locator': self.page.locator('#logo')}
        else:
            raise Exception(f'not support this model {self.model}')

    def __new_page(self):
        def dialog_(dialog):
            logging.info(f'dialog message is {dialog.message}, accepted')
            dialog.accept()

        self.__playwright = sync_playwright().start()
        if self.__browser_type == 'firefox':
            browser = self.__playwright.firefox
        elif self.__browser_type == 'webkit':
            browser = self.__playwright.webkit
        else:
            browser = self.__playwright.chromium
        self.__browser = browser.launch(headless=False)
        if self.model in self.__http_credentials_model:
            http_credentials = {'username': self.__username, 'password': self.__password}
        else:
            http_credentials = None
        self.__context = self.__browser.new_context(ignore_https_errors=True, http_credentials=http_credentials)
        logging.info('Start your journey browser is chrome')
        self.page = self.__context.new_page()
        self.page.on("dialog", dialog_)

    @allure.step("用户登录")
    def login(self, username=None, password=None, status='success') -> None:
        """

        :param username:  如果不传使用默认的用户名
        :param password:  如果不传使用默认的密码
        :param status: 登录状态 'success'|'fail' 期望登录的状态是成功还是失败，失败了就会停留在登录页面，不做任何操作
        :return:
        """
        username = self.__username if not username else username
        password = self.__password if not password else password

        def goto_router():
            device = "{}://{}:{}".format(self.protocol, self.host, self.port)
            try:
                self.page.goto(device, timeout=120 * 1000)
            except Exception:
                raise
            self.page.bring_to_front()
            self.page.wait_for_timeout(500)
            if self.model in self.__http_credentials_model:
                logging.info(f'Open {self.host} device address {device} and login')
            else:
                logging.info(f'Open {self.host} device address {device}')

        def _login():
            if self.model not in self.__http_credentials_model:
                self.__login_locator.get('username').fill(username)
                logging.info('Device %s fill username %s' % (self.host, username))
                self.__login_locator.get('password').fill(password)
                logging.info('Device %s fill password %s' % (self.host, password))
                self.__login_locator.get('submit').click()
                logging.info("Device %s  login" % self.host)
                if status == 'success':
                    self.__login_locator.get('wait_locator').wait_for(state='visible')
                    self.page.wait_for_timeout(500)

        for i in range(0, 10):
            if self.__login_locator.get('username') and self.__login_locator.get(
                    'username').is_visible():
                _login()
                break
            elif self.__login_locator.get('wait_locator') and self.__login_locator.get(
                    'wait_locator').is_visible():
                # logging.info("Device %s already login in" % self.host)
                break
            elif self.page.url == 'about:blank':
                goto_router()
                _login()
                break
            else:
                try:
                    logging.info(f"Device %s refresh page {i + 1} times" % self.host)
                    self.page.reload()
                except TimeoutError:
                    pass
        else:
            raise Exception(f'Device {self.host} page error')

    @allure.step('页面抓取接口{url}返回结果')
    def wait_for_response(self, url: str, timeout=30) -> dict:
        """

        :param url:  pattern 匹配的正则表达式,
        :param timeout: 默认30秒
        :return: 返回结果
        """
        with self.page.expect_response(lambda response: re.search(url, response.url) and response.status == 200,
                                       timeout=timeout * 1000) as response_info:
            logging.info("Device %s fetch url %s " % (self.host, response_info.value.url))
        logging.info("Device %s the api response is  %s " % (self.host, response_info.value.json()))
        return response_info.value.json()

    @allure.step('进入菜单{menu}')
    def access_menu(self, menu: str, wait_time=None) -> None:
        """进入菜单，多个菜单使用点号隔开，不限多少层级   menu_locator 存放在 base_locators 里面，
            定义menu = {'system': {'locator': '#menu_id', 'wait_locator': '#wait_locator_id'},
                               'status':{'locator': '#status_id', 'wait_locator': '#wait_locator_id'}}
            定义菜单时所有菜单的点号都需要省略，如2.4g 写成24g；空格写成下划线，如wi-fi 2.4g 写成wi-fi_24g
            中划线写成下划线，如wi-fi-2.4g 写成wi_fi_24g


        :param menu: 'system'| 'system.status' 菜单名称全部来自与设备的英文版本，点号需要省略不写， 其他不变，大小写均可以
                     菜单中原有的点号都需要忽略，如wi-fi 2.4g 需要传入wi-fi_24g 或 wi-fi 2.4g 或 wi-fi_2.4g
        :param wait_time: 当操作完菜单后是否需要等待时间 单位毫秒
        :return:
        """

        def in_current_menu(locators: dict) -> bool:
            _in_current_menu = False
            if locators.get('visible_locator'):
                _in_current_menu = True
                for visible_locator in locators.get('visible_locator'):
                    if not visible_locator.is_visible():
                        _in_current_menu = False
                        break
            if locators.get('attributes'):
                for locator, value in locators.get('attributes').items():
                    if locator.is_visible():
                        for attr, expect_value in value.items():
                            if expect_value not in locator.get_attribute(attr):
                                _in_current_menu = False
                                break
                        else:
                            _in_current_menu = True
                            continue
                        break
                    else:
                        _in_current_menu = False
                        break
            return _in_current_menu

        def access_one_menu(menu_one: str, locators: dict, level: int):  # 进入某一个菜单
            if not in_current_menu(locators):
                menus = locators.get('menu') if isinstance(locators.get('menu'), list) else [locators.get('menu')]
                for menu_1 in menus:
                    self.click(menu_1)
                logging.info(f'select {level} level menu {menu_one}')
                if locators.get('mouse_move'):
                    self.page.mouse.move(locators.get('mouse_move')[0], locators.get('mouse_move')[1])
                if locators.get('wait_locator'):
                    for wait_locator in locators.get('wait_locator'):
                        wait_locator.wait_for(state='visible')
                    self.page.wait_for_timeout(500)  # 多等500ms

        def access(menus):  # 递归进入菜单
            new_menus = []
            click_menus = []
            menu_content = self.content_locator
            # 把菜单名、菜单的元素信息、以及菜单等级依次放入列表中
            for menu_s, level_ in zip(menus, range(1, len(menus) + 1)):
                menu_content = menu_content.get(menu_s)
                new_menus.append([menu_s, menu_content, level_])
            new_menus.reverse()  # 逆序查看是否在当前这个菜单的页面
            for menu_one, locators, level_ in new_menus:
                if not in_current_menu(locators):
                    # 找出需要点击的菜单
                    click_menus.append((menu_one, locators, level_))
                else:
                    break
            if click_menus:
                click_menus.reverse()  # 回归原来的顺序
                for menu_one, locators, level_ in click_menus:
                    access_one_menu(menu_one, locators, level_)
            else:
                logging.info(f'already in {".".join(menu)} menu')

        def default_change(menu_old, locators: dict) -> str:
            menu_old_s = menu_old.split('.')
            for menu_old_ in menu_old_s:
                locators = locators.get(menu_old_)
            default = locators.get('default')
            menu_new = menu_old + '.' + default if default else menu_old
            return menu_new

        if menu:
            self.page.bring_to_front()
            self.login()
            try:
                menu = menu.replace(' ', '_').replace('-', '_').lower()
                menu = default_change(menu, self.content_locator).split('.')
                access(menu)
            except Exception:
                raise f'not support this menu {menu}'
            if wait_time:
                self.page.wait_for_timeout(wait_time)

    @allure.step('{log_desc} 输入{value}')
    def fill(self, locator: Locator, value: str or int, log_desc=None, force=False) -> None:
        """ 封装公共的输入操作

        :param locator:  元素定位

        :param value: 输入的值
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :param force: 强制写入
        :return:
        """
        if value is not None:
            locator.clear()
            locator.fill(str(value), force=force)
            locator.blur()  # 鼠标移出输入框
            if log_desc:
                logging.info(f'Device {self.host} fill {log_desc} {value}')

    @allure.step('点击 {log_desc}')
    def click(self, locator: Locator, log_desc=None, dialog_message: str = None, tip_messages: str or list = None,
              wait_for_time: int = None, tip_messages_timeout=30) -> None:
        """ 封装公共的点击操作

        :param locator:  元素定位
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :param dialog_message: str  点击按钮后有dialog弹出，并且期望对信息做验证， 支持模糊匹配
        :param tip_messages: str or list 点击后等待该tip出现 再等待tip消失，如果有多个，使用列表传入
                            tip_messages 是支持模糊匹配
                            该项校验 页面元素必须停留时间1秒及更多时间，否则不容易检测到导致报错
        :param wait_for_time: ms  当做完所有操作后是否需要等待时间
        :param tip_messages_timeout: 默认30秒， 单位秒
        :return:
        """

        if not locator.is_disabled():
            if dialog_message:
                self.dialog_massage(locator.click, dialog_message)
            else:
                locator.click()
            if log_desc:
                logging.info(f'Device {self.host} click {log_desc}')
            self.tip_messages(tip_messages, tip_messages_timeout)
            if wait_for_time:
                self.page.wait_for_timeout(wait_for_time)

    @allure.step('{log_desc} {action}')
    def check(self, locator: Locator, action='check', log_desc=None, tip_messages: str or list = None) -> None:
        """ 封装公共的单选操作
        :param locator:  元素定位
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :param action: 'check'|'uncheck'| None | '是' | 'Yes'
        :param tip_messages: str or list 点击后等待该tip出现 再等待tip消失，如果有多个，使用列表传入
                            tip_messages 是支持模糊匹配
                            该项校验 页面元素必须停留时间1秒及更多时间，否则不容易检测到导致报错
        :return:
        """

        if action is not None:
            if action in ('check', 'Yes', '是', 'yes'):
                locator.check()
            else:
                locator.uncheck()
            if log_desc:
                logging.info(f'Device {self.host} {log_desc} {action}')
            self.tip_messages(tip_messages)

    @allure.step('下拉选择')
    def select_option(self, locator: Locator, value: str or int, log_desc=None) -> None:
        """ 封装公共的下拉选择操作

        :param locator:  元素定位
        :param value: str or int, 下拉选择option的value属性值、或label
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :return:
        """

        def scroll_into_view_action(all_option_: Locator, option_: Locator, times=100):
            select = False
            option_end = None
            for find_time in range(0, times):
                if option_.count() == 1:
                    option_.click()
                    select = True
                    break
                elif option_.count() == 0:
                    if option_end != all_option_.last.inner_text():
                        option_end = all_option_.last.inner_text()
                        all_option_.last.scroll_into_view_if_needed()
                        logging.info(f'scroll down the scroll bar {find_time + 1} tims')
                    else:
                        logging.info(f'scroll down the bottom')
                        break
                else:
                    raise Exception('found more option elements')
            if not select:
                for find_time in range(0, times):
                    if option_.count() == 1:
                        option_.click()
                        break
                    elif option_.count() == 0:
                        if option_end != all_option_.first.inner_text():
                            option_end = all_option_.first.inner_text()
                            all_option_.first.scroll_into_view_if_needed()
                            logging.info(f'scroll up the scroll bar {find_time + 1}')
                        else:
                            logging.info(f'scroll up the top')
                            break
                    else:
                        raise Exception('found more option elements')
                else:
                    raise Exception('scroll bar too lang, more 100 times')

        if value is not None:
            locator.wait_for(state='visible')
            if locator.get_attribute('aria-controls') or locator.locator('.ant-select-selection').get_attribute(
                    'aria-controls'):
                if locator.get_attribute("aria-controls"):  # ER805 设备的下拉选择
                    now_option = locator.locator('../..').locator('.ant-select-selection-item').inner_text()
                    option_p = self.page.locator(f'//div[@id="{locator.get_attribute("aria-controls")}"]').locator(
                        '..').locator('//div[@class="rc-virtual-list-holder-inner"]')
                    option = option_p.locator(f'//div[@title="{value}"]')
                    all_option = option_p.locator('.ant-select-item.ant-select-item-option')
                else:  # IG902 设备的下拉选择
                    now_option = locator.locator(
                        '//div/div/div[@class="ant-select-selection-selected-value"]').inner_text()
                    option_p = self.page.locator(
                        f'//div[@id="{locator.locator(".ant-select-selection").get_attribute("aria-controls")}"]').locator(
                        '//ul[@role="listbox"]')
                    option = option_p.get_by_text(re.compile(value, re.IGNORECASE))
                    all_option = option_p.locator('//li')
                if now_option != value:
                    locator.scroll_into_view_if_needed()
                    if not locator.is_editable():
                        locator.click(force=True)
                    else:
                        locator.click()
                    scroll_into_view_action(all_option, option)
            else:  # IR300 等设备的下拉选择
                locator.select_option(str(value))  # value 可以为label 或者value
                if locator.locator(f'//option[@value="{value}"]').count() == 1:
                    value = locator.locator(f'//option[@value="{value}"]').inner_text()
            if log_desc:
                logging.info(f"Device {self.host} select {log_desc} of {value}")

    @allure.step('{log_desc} {action}')
    def switch_button(self, locator: Locator, action: str = 'enable', log_desc=None) -> None:
        """控制通用开关按钮开关， 如拨号的开关

        :param locator:  开关按钮元素
        :param action: enable, disable, None 可以开启或关闭，但是并没有提交，只是点击了下
        :param log_desc:  开关功能描述
        :return: None
        """
        if action is not None:
            locator.wait_for(state='visible')
            if action.lower() == 'enable':
                if locator.get_attribute('aria-checked') == 'false' or not locator.get_attribute('aria-checked'):
                    locator.click(force=True)
                    if log_desc:
                        logging.info(f"Device {self.host} {log_desc} enabled")
            else:
                if locator.get_attribute('aria-checked') == 'false' or not locator.get_attribute('aria-checked'):
                    pass
                else:
                    locator.click(force=True)
                    if log_desc:
                        logging.info(f"Device {self.host} {log_desc} disabled")

    @allure.step('伸缩按钮')
    def expand(self, left_text: str, action: str = 'expand') -> None:
        """ 伸缩按钮

        :param left_text: 伸缩按钮 左边的文本，需要注意国际化
        :param action: expand|close|None
        :return:
        """
        text_locator = self.page.get_by_text(left_text, exact=True)
        if action is not None:
            text_locator.wait_for(state='visible')
            if text_locator.count() > 1:
                raise
            else:
                if text_locator.locator('..').get_attribute('type') == 'button':  # IG 产品
                    if 'right' in text_locator.locator('..').locator('//span/i').get_attribute('aria-label'):
                        if action.lower() == 'expand':
                            self.click(text_locator.locator('..'), f'expand {left_text}')
                    else:
                        if action.lower() == 'close':
                            self.click(text_locator.locator('..'), f'closed {left_text}')
                elif text_locator.locator('..').get_attribute('role') == 'button' or not text_locator.locator(
                        '..').get_attribute('role'):  # ER805
                    locator = self.page.locator(f'svg[data-icon="right"]:right-of(:text-is("{left_text}"))').first
                    if action.lower() == 'expand':
                        if not locator.get_attribute('style'):
                            self.click(locator, f'expand {left_text}')
                    else:
                        if locator.get_attribute('style') == 'transform: rotate(90deg);':
                            self.click(locator, f'closed {left_text}')
                else:
                    raise Exception("not support this expand")

    @allure.step('上传文件')
    def upload_file(self, locator: Locator, path_, dialog_massage=None) -> None:
        """

        :param locator:
        :param path_:
        :param dialog_massage
        :return:
        """

        def upload():
            if path_:
                if os.path.isfile(path_) and os.path.exists(path_):
                    with self.page.expect_file_chooser() as fc:
                        locator.click()
                    file_chooser = fc.value
                    file_chooser.set_files(path_)
                    logging.info(f'Device {self.host} upload file Successful')
                else:
                    logging.error(f'{path_} Does Not Exist.')

        if dialog_massage:
            self.dialog_massage(upload, dialog_massage)
        else:
            upload()

    @allure.step('下载文件')
    def download_file(self, locator: Locator, file_path, file_name=None) -> None:
        """默认为日志路径

        :param locator: 下载按钮元素
        :param file_path: 下载文件的路径, 不需要跟文件名，
        :param file_name: 如果文件名
        :return:
        """
        if file_path is not None:
            if os.path.isdir(file_path) and os.path.exists(file_path):
                with self.page.expect_download() as download_info:
                    locator.click()
                download = download_info.value
                file_name = download.suggested_filename if file_name is not None else file_name
                download.save_as(path.join(file_path, file_name))
                logging.info(
                    f'Device {self.host} download {download.suggested_filename} to path {file_path} successful')
            else:
                logging.error(f'{file_path} Does Not Exist.')

    @allure.step("校验dialog message")
    def dialog_massage(self, f, message: str = '') -> None:
        """对话框提示进行校验， 使用时需要在base_locator 里面定义dialog_massage 且返回字典数据

        :param f:  是一个操作函数，执行后会有dialog弹窗出现
        :param message: 校验的信息, 支持模糊匹配
        :return:
        """
        if message:
            with self.page.expect_event('dialog') as dialog_info:
                f()
            assert self.locale.get(message) in dialog_info.value.message, \
                f'{self.host} assert {message} dialog error'

    @allure.step("校验tip messages")
    def tip_messages(self, messages: str or list = None, timeout=30) -> None:
        """ 某些提交操作会出现文本的提示，提示在过几秒钟后会消失，对于该类消息的验证使用该方法，
            使用时需要在base_locator tip_messages 且返回字典数据

        :param messages: str or list 点击后等待该tip出现 再等待tip消失，如果有多个，使用列表传入
                            tip_messages 是支持模糊匹配
                            该项校验 页面元素必须停留时间1秒及更多时间，否则不容易检测到导致报错
        :param timeout: 校验超时时间
        :return:
        """
        if messages:
            tip_messages = [messages] if isinstance(messages, str) else messages
            for message in tip_messages:
                message = self.locale.get(message)  # 国际化转换
                expect(self.page.get_by_text(re.compile(message, re.IGNORECASE))).to_be_visible(timeout=timeout * 1000)
                expect(self.page.get_by_text(re.compile(message, re.IGNORECASE))).to_be_hidden(timeout=timeout * 1000)

    @allure.step("校验text messages")
    def text_messages(self, messages: str or list = None, timeout=10) -> None:
        """ 对文本内容做验证，如在输入框输入错误内容时出现的文本，该类文本会一直存在
        :param messages: str or list 文本内容，如果有多个，使用列表传入
        :param timeout: 校验超时时间
        :return:
        """
        if messages:
            text_messages = [messages] if isinstance(messages, str) else messages
            for message in text_messages:
                message = self.locale.get(message)  # 国际化转换
                expect(self.page.get_by_text(re.compile(message, re.IGNORECASE))).to_be_visible(timeout=timeout * 1000)

    @allure.step("校验元素Title")
    def title_messages(self, messages: str or list = None, timeout=10) -> None:
        """ 对元素的属性title做内容验证，
        :param messages: str or list 文本内容，如果有多个，使用列表传入
        :param timeout: 校验超时时间
        :return:
        """
        if messages:
            text_messages = [messages] if isinstance(messages, str) else messages
            for message in text_messages:
                message = self.locale.get(message)  # 国际化转换
                expect(self.page.get_by_title(re.compile(message, re.IGNORECASE))).to_be_visible(timeout=timeout * 1000)

    @allure.step('设置页面翻页')
    def page_refresh(self, refresh_time: str, select_locator: Locator) -> None:
        """
        :param refresh_time: str
                        '0'|'3'|'4'|'5'|'10'|'15'|'30'|'60'|'120'|'180'|'240'|'300'|'600'|'900'|'1200'|'1800'
        :param select_locator: 元素定位
        :return:
        """
        # 待完善
        if self.model in ('VG710', 'IR302'):
            if select_locator.evaluate("el => el.value") == str(
                    refresh_time) and select_locator.is_disabled():
                pass
            else:
                if select_locator.is_disabled():
                    self.click(select_locator.locator('..').locator('#refresh-button'), 'refresh button')
                    self.page.wait_for_timeout(500)
                self.select_option(select_locator, refresh_time, 'refresh time select')
                self.click(select_locator.locator('..').locator('#refresh-button'), 'refresh button ok')

    @staticmethod
    @allure.step("Table tr action")
    def table_tr(locators: dict, value: list, log_desc=None) -> List[int or None] or None:
        """

        :param locators: {"locator": $locator2, "param": {$key2: $value2}, "columns": list, 'unique_columns': list}
        :param value: [($action,{**kwarg})] ex: [('delete_all', )],  [('edit', $old, $new)]多个操作时使用列表 [('add',{}), ('add',{})]
        :param log_desc: 日志描述
        :return:
        """
        tr = Table(locators.get('columns'), locators.get('locator'),
                   locators.get('unique_columns'), locators.get('param'), log_desc)
        exist_tr = []
        if value:
            for value_ in value:
                if value_[0] == 'add':
                    tr.add(**value[1])
                elif value_[0] == 'delete_all':
                    tr.delete_all()
                elif value_[0] == 'delete':
                    tr.delete(**value[1])
                elif value_[0] == 'exist':
                    exist_tr.append(tr.exist(**value[1]))
                elif value_[0] == 'edit':
                    tr.edit(value[1], value[2])
            return exist_tr

    def agg_in(self, locators: list, action_dict: dict) -> None:
        """封装公共的整合输入操作
                :param locators:  列表 嵌套 长度为2的元组，元组的第一项为操作项名称， 第二项为对应的一个字典
                    [($param1, {"locator": $locator1, "type": $type1, "relation": [($param2, $value2)], "param": {$key1: $value1}}),
                    ($param2, {"locator": $locator2, "type": $type2, "relation": [($param3, $value3),……], "param": {$key2: $value2}}),
                    ($param3, {"locator": $locator2, "type": 'table_tr', "relation": [($param3, $value3),……], "param": {$key2: $value2},
                                "columns": list, 'unique_columns': list}),]
                    $param: 操作项的名称，如 'language'|'sim'|'status'
                    $locator: 操作项的元素定位， locator or [locator,locator,...]
                    $type: 操作项的类型 fill|select|button|check|upload_file|download_file|text_visible|error_tips|locators_title|
                                     multi_select|multi_check|multi_fill|table_tr,
                            select value值可以是label|Value
                            multi_select指一个参数有多个select, 对应操作项的多个locator及value用[]传入
                    "relation":[($param, $value)]: 操作项的关联项，若有多个则首个为最先操作的关联项，其中$param为关联项的名称，$value为关联项的预期值
                    "param":{$key, $value}: 参数转换，如大小写转换{"ab":"AB"} {"wan":"Wan"}等.
                :param action_dict: 要做操作的参数名称与对应的值{$param1: $value1, $param2: $value2}
                :return:
                """
        relations = []

        def operation(param, param_locator, value):
            if param_locator.get('type') == 'text':
                self.fill(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'select':
                if param_locator.get('param') and value in param_locator.get('param').keys():
                    value = param_locator.get('param').get(value)
                self.select_option(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'button':
                if value:
                    dialog_message, tip_messages, wait_for_time, tip_messages_timeout = None, None, None, 30
                    if isinstance(value, dict):
                        dialog_message = value.get('dialog_message')
                        tip_messages = value.get('tip_messages')
                        wait_for_time = value.get('wait_for_time')
                        tip_messages_timeout = value.get('tip_messages_timeout') if value.get(
                            'tip_messages_timeout') is not None else 30
                    self.click(param_locator.get('locator'), param, dialog_message, tip_messages, wait_for_time,
                               tip_messages_timeout)
            elif param_locator.get('type') == 'check':
                if value:
                    value_, tip_messages = value, None
                    if isinstance(value, dict):
                        value_ = value.get('value')
                        tip_messages = value.get('tip_messages')
                    self.check(param_locator.get('locator'), value_, param, tip_messages)
            elif param_locator.get('type') == 'table_tr':
                if isinstance(value, list):  # value按照table_tr()的传参方式传参,
                    self.table_tr(param_locator, value, param)
                else:
                    logging.error(f'value {value} should be a list, not {type(value)}')
            elif param_locator.get('type').startswith('multi_'):
                if len(param_locator.get('locator')) == len(value):
                    for locator_, value_ in dict(zip(param_locator.get('locator'), value)):
                        if 'select' in param_locator.get('type'):
                            if param_locator.get('param') and value_ in param_locator.get('param').keys():
                                value_ = param_locator.get('param').get(value_)
                            self.select_option(locator_, value_, param)
                        elif param_locator.get('type').endswith('check'):
                            self.check(locator_, value_, param)
                        elif param_locator.get('type').endswith('fill'):
                            self.fill(locator_, value_, param)
                        else:
                            logging.error(f"not support this param type {param_locator.get('type')}")
                else:
                    logging.error('Wrong length or type of locator or value!')
            elif param_locator.get('type') == 'upload_file':
                if value:
                    file_path, dialog_message = value, None
                    if isinstance(value, dict):
                        file_path, dialog_message = value.get('file_path'), value.get('dialog_message')
                    elif isinstance(value, str):
                        pass
                    self.upload_file(param_locator.get('locator'), file_path, dialog_message)
            elif param_locator.get('type') == 'download_file':
                if value:
                    file_path, file_name = value, None
                    if isinstance(value, dict):
                        file_path, file_name = value.get('file_path'), value.get('file_name')
                    elif isinstance(value, str):
                        pass
                    self.download_file(param_locator.get('locator'), file_path, file_name)
            elif param_locator.get('type') == 'tip_messages':
                if value:
                    messages, timeout = value, 10
                    if isinstance(value, dict):
                        timeout = value.get('timeout') if value.get('timeout') else 10
                        messages = value.get('messages')
                    self.tip_messages(messages, timeout)
            elif param_locator.get('type') == 'text_messages':  # 用逗号分解多个
                if value:
                    messages, timeout = value, 10
                    if isinstance(value, dict):
                        timeout = value.get('timeout') if value.get('timeout') else 10
                        messages = value.get('messages')
                    self.text_messages(messages, timeout)
            elif param_locator.get('type') == 'title_messages':
                if value:
                    messages, timeout = value, 10
                    if isinstance(value, dict):
                        timeout = value.get('timeout') if value.get('timeout') else 10
                        messages = value.get('messages')
                    self.title_messages(messages, timeout)
            else:
                raise Exception(f"not support this param type {param_locator.get('type')}")

        if action_dict:
            for option in locators:
                assert type(option) in (tuple, list) and len(option) == 2, "type of option is incorrect"
                if option[0] in [key for key, value in action_dict.items() if value is not None]:
                    if option[1].get("relation") and option[1].get("relation") not in relations:
                        # 对关系项操作之前检查关系项
                        for relation_ in option[1].get("relation"):
                            relation_locator = [i[1] for i in locators if i[0] == relation_[0]][0]
                            operation(relation_[0], relation_locator, relation_[1])  # 关系项操作
                        relations.append(option[1].get("relation"))
                    operation(option[0], option[1], action_dict.get(option[0]))  # 本身操作

    @allure.step("计算判断表达式{expect_}")
    def eval_inner_text(self, expect_: dict, locators: list) -> bool:
        """对页面特定元素值做判断

        :param expect_: {$status: $expressions}
                        status: 状态名称， 比如可以传定义好的 current_sim
                        expressions: 完整表达式, 当判断int型的关系时${value}和期望值可加"",而当需要调用str型的关系时${value}和期望值都要加"",
                         例:（'${value}==1', '${value}!=1', '${value}>1', '${value}>=1', '${value}<1', '${value}<=1', "${value}"=="abc"
                        '"${value}".startswith("123")', '"${value}".endswith("23")', '"${value}" in a', '"${value}" not in b',
                        '"${value}".__contains__("234")', 'time.strptime("${value}}", "%Y-%m-%d %H:%M:%S")'）
                        ex: '${value}==8' 多个使用元组或者列表，注意期望值是字符串时需要带上引号， 如'${value}=="sim1"'
        :param locators: [($param1, {"locator": $locator1, "type": $type1, "relation": [($param2, $value2)], "param": {$key1: $value1}}),
                          ($param2, {"locator": $locator2, "type": $type2, "relation": [($param3, $value3),……], "param": {$key2: $value2}}),
                          ($param3, {"locator": $locator2, "type": 'table_tr', "relation": [($param3, $value3),……], "param": {$key2: $value2},
                                "columns": list, 'unique_columns': list}),]
        :return: 只返回True or False 不做断言
        """
        if expect_:
            for key in expect_.keys():
                filter_key = list(filter(lambda x: x[0] == key, locators))
                if len(filter_key) == 1:
                    option = filter_key[0]
                    locator = option[1].get('locator')
                    if isinstance(locator, Locator):
                        value = locator.first.inner_text() if locator.count() != 0 else 'None'
                    else:
                        value = str(locator)
                    try:
                        expression = expect_.get(key).replace('${value}', value).replace('\n', ' ')
                        if option[1].get('param'):
                            for replace_k, replace_v in option[1].get('param').items():
                                expression = expression.replace(replace_k, replace_v)
                        if eval(expression, {'repr': repr}):
                            logging.info(f'Check {option[0]} , {expression} is true')
                        else:
                            logging.info(f'Check {option[0]} , {expression} is false')
                            return False
                    except TypeError:
                        logging.info(f'get {key} inner_text failed')
                        return False
                else:
                    raise KeyError(f'not support the key {key}')
        return True

    @allure.step("获取页面元素文本值")
    def get_text(self, keys: str or list or tuple, locators: list) -> str or dict or None:
        """获取页面元素文本值

        :param keys: None or str or list or tuple, 需要获取对应文本的元素的关键字
        :param locators: [($param1, {"locator": $locator1, "type": $type1}),
                         type: 支持的类型有：'text'|'fill'|'select'
                         该select 为select标签的文本值， ER805 和ER605 直接使用text
        :return: 当key为None时，返回None
                 当key为str时，只能获取某一个字段的信息，同时使用str返回
                 当key为列表或者元组时， 使用字典返回相关关键字的信息
        """
        result = {}
        if keys:
            keys = [keys] if isinstance(keys, str) else keys
            for key in keys:
                filter_key = list(filter(lambda x: x[0] == key, locators))
                if len(filter_key) == 1:
                    option = filter_key[0]
                    locator = option[1].get('locator')
                    if isinstance(locator, Locator):
                        if locator.count() != 0:
                            if option[1].get('type') == 'select':
                                value = locator.first.text_content()
                            elif option[1].get('type') == 'fill':
                                value = locator.first.input_value()
                            else:
                                value = locator.first.inner_text()
                        else:
                            raise
                    else:
                        value = str(locator)
                    result[key] = value
                else:
                    raise KeyError(f'not support the key {key}')
        if result:
            if len(result.keys()) == 1:
                return result.get(keys[0])
            else:
                return result
        else:
            return None

    @allure.step("PC Ping")
    @loop_inspector('PC Ping', timeout=120, interval=10)
    def pc_ping(self, host_or_ip: str or list or tuple = 'www.baidu.com', number: int = 4, src=None,
                lost_packets=False, assert_result=True) -> bool:
        """ 验证在PC机上ping某个地址是否丢包， 仅判断丢包

        :param lost_packets:
        :param src: 验证的源IP地址 '192.168.2.100'
        :param host_or_ip: 验证的目的IP地址, 可使用元组或列表接收多个地址
        :param number: 包数量
        :param lost_packets: True|False 如果为True判断会丢包，如果为False判断不丢包
        :param assert_result: True|False 是否对 lost_packets 的结果做判断
        :return:
        """
        tag_result = True
        if host_or_ip:
            host_or_ip = [host_or_ip] if isinstance(host_or_ip, str) else host_or_ip
            for host in host_or_ip:
                command = f'ping {host} -n {number}' if src is None else f'ping -S {src} {host} -n {number}'
                logging.info(command)
                if assert_result:
                    result = os.popen(command).read()
                    logging.info(result)
                    if lost_packets:  # 判断需要丢包
                        send = re.findall(r'已发送 = (.*?)，', result, re.S)[0]
                        accept = re.findall(r'已接收 = (.*?)，', result, re.S)[0]
                        if send == accept:
                            if '无法访问' not in result:
                                logging.info(f'PC {src} ping {host} does not loss packet')
                                tag_result = False
                    else:  # 判断不丢包
                        if '丢失 = 0' not in result:
                            logging.info(f'PC {src} ping {host} loss packet')
                            tag_result = False
                        else:
                            if '无法访问' in result:
                                logging.info(f'PC {src} ping {host} loss packet')
                                tag_result = False
                else:
                    os.popen(command)
                if not tag_result:
                    break
        return tag_result

    def close(self) -> None:
        if self.__context and self.__browser and self.__playwright:
            self.__context.close()
            self.__browser.close()
            self.__playwright.stop()
            logging.info('close browser and playwright')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO,
                        stream=sys.stdout)
    with BasePage('10.5.24.96', 'adm', '123456', 'https', 443, model='ig902') as my_page:
        # system = (
        #     '3rd party notification', '3rd party notification', 'cloud edge computing.azure iot edge',
        #     'cloud edge computing.aws iot greengrass',
        #     'device supervisor',
        #     'device supervisor.measure monitor.group', 'device supervisor.alarm', 'device supervisor.alarm.alarm rules',
        #     'device supervisor.alarm.history alarms', 'device supervisor.alarm.alarm label', 'device supervisor.cloud',
        #     'device supervisor.cloud.whitehawk energy manager',
        #     'device supervisor.protocol', 'device supervisor.protocol.iec 104 server',
        #     'device supervisor.protocol.opcua server',
        #     'device supervisor.protocol.modbus rtu slave', 'device supervisor.parameter settings',
        #     'device supervisor.custom quickfunctions',
        #     'device supervisor.cloud.whitehawk energy manager',
        #     'device supervisor.protocol.iec 104 server',)
        for i in range(0, 1):
            my_page.access_menu(f'system.inhand_cloud.inhand connect service')
            my_page.page.wait_for_timeout(2 * 1000)
            my_page.access_menu(f'system.inhand_cloud.inhand device manager')
            my_page.access_menu(f'system.inhand_cloud.inhand device manager')
            my_page.access_menu(f'system.inhand_cloud.inhand iscada cloud')
            my_page.access_menu(f'system.inhand_cloud.inhand iscada cloud')
        # a = my_page.get_text('language', [('language', {'locator': my_page.page.frame_locator('#window_content').locator('#_f_hostname'), 'type': 'fill'})])
        # print(a)
    # with BasePage('10.5.24.96', 'adm', '123456', model='IG902') as my_page:
    #     my_page.access_menu('edge_computing.device_supervisor.measure_monitor')
    #     my_page.page.wait_for_timeout(1000)
    #     my_page.access_menu('edge_computing.device_supervisor.protocol')
    #     my_page.page.wait_for_timeout(1000)
    # user_table = Table(
    #     [('mode', 'input'), ('status', 'input'), ('ssid', 'input'),  ('mac', 'input'),
    #      ('auth', 'input'), ('encry', 'input'), ('network', 'input'), ('gateway', 'input'), ('dns', 'input'), ('time', 'input')],
    #     my_base.page.frame_locator('#window_content').locator('#wifi-2g-grid'),
    #     ['mode', 'status', 'ssid', 'mac', 'auth', 'encry', 'network', 'gateway', 'dns', 'time'], None)
    # a = user_table.exists([{'mode': "'${value}'!='AP'", 'ssid': 'inhand-visitor-2g'}])
    # print(a)
    # print(user_table.exist(locale={'disable': 'Disabled'}, mode="'${value}'!='AP'", ssid='inhand-visitor-2g', status='disable'))
    # user_table.delete(name='test2', value='222')
    # my_base.page.wait_for_timeout(5 * 1000)
