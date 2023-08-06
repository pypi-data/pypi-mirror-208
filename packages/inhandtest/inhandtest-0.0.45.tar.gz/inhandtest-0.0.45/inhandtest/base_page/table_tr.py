# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 10:13:10
# @Author  : Pane Li
# @File    : table_tr.py
"""
table_tr

"""
import logging
from typing import List
from inhandtest.tools import replace_str
from playwright.sync_api import Locator


class Table:

    def __init__(self, columns: list, table_locator: Locator, unique_columns: list, locale: dict = None, log_desc=None):
        """


        :param columns: [("acl_name", 'input'), ('action', 'select')] 说明列的表名以及 类型， 类型现在只支持三种('input'、'select'、'check')
                        eg:[("列名称变量","列字段对应类型"), ...]
                        在选择时只接收label, 不支持value选择， 因为查找时也使用的label，
                        在表格只有查找功能是时，只要列属性不定义为check 都可以
        :param table_locator: table_locator 定位
        :param unique_columns:  list, 确认唯一的列资源名称, eg: ["列名称变量1", "列名称变量2"...]， 当表只有查找功能时，该项为列的所有值。
        :param locale: dict, 国际化文件,
        """
        self.columns = columns  # 列名要与实际的列相对应，不能多也不能少 [("acl_name", 'input'), ('action', 'select')]
        self.table_locator = table_locator
        self.unique_columns = unique_columns  # 重复列名
        self.tr = self.table_locator.locator('//tbody').locator('//tr')
        self.locale = locale
        self.log_desc = log_desc

    def __filter_td_index(self, contain_check=False, **kwargs):
        self.table_locator.wait_for(state='visible')
        expect_result = []
        for input_key, input_value in kwargs.items():
            if not contain_check:
                result = list(filter(lambda a: a[0] == input_key and a[1] != 'check' and a[0] in self.unique_columns,
                                     self.columns))  # 排除掉check
            else:
                result = list(filter(lambda a: a[0] == input_key, self.columns))
            if len(result) == 1:
                expect_result.append((self.columns.index(result[0]), input_value, result[0][1]))  # 找出td是第几个，也及值
        return expect_result

    def __edit_add(self, **kwargs):
        for column in self.__filter_td_index(True, **kwargs):
            if column[1] is not None:
                if column[2] == 'input':
                    self.tr.locator('//td').locator(f'.fi{column[0] + 1}').first.clear()
                    self.tr.locator('//td').locator(f'.fi{column[0] + 1}').first.fill(str(column[1]))
                elif column[2] == 'select':
                    option = self.locale.get(
                        column[1]) if self.locale and self.locale.get(
                        column[1]) else str(column[1])
                    self.tr.locator('//td').locator(f'.fi{column[0] + 1}').first.select_option(option)
                elif column[2] == 'check':
                    if column[1] in ('check', 'Yes', '是', 'yes'):
                        self.tr.locator('//td').locator(f'.fi{column[0] + 1}').first.check()
                    else:
                        self.tr.locator('//td').locator(f'.fi{column[0] + 1}').first.uncheck()
                else:
                    raise Exception(f'not support this type {column[2]}')

    def exist(self, find_one=True, locale=None, **kwargs) -> int or None or List[int]:
        """ 传入的资源是否存在, 对于check 项是不计入重复选项的，因为勾选其实只是开启功能而已


        :param find_one: 是否只查询一个，当查询一个时返回的是int值，索引从0 开始， 当没查询到时返回的是None
                         当查询多个时，如果没有找到返回的是[], 如果找到了是列表包含了多个索引值

        :param locale: dict 国际化， 默认为类初始化的locale, 也可以单独传入
        :param kwargs: 支持传入表达式， 如 acl_name='${value} == '2''
        :return: int or list or None
        """
        search_tr = []
        one_tr = None
        expect_result = self.__filter_td_index(**kwargs)
        locale = self.locale if locale is None else locale
        if expect_result:
            for tr_nth in range(0, self.tr.count()):
                if self.tr.nth(tr_nth).locator('//td').count() == len(self.columns):  # 要求td里面的项跟最初定义的是一样的长度，不然就认为不是内容项
                    for result_ in expect_result:
                        text_n = self.tr.nth(tr_nth).locator('//td').nth(result_[0]).inner_text()  # 现在的值
                        text_e = replace_str(str(result_[1]), locale)  # 期望的值
                        if '${value}' in text_e:
                            text_e = text_e.replace('${value}', text_n)
                            try:
                                if not eval(text_e):
                                    break
                            except Exception as e:
                                logging.error(e)
                                break
                        else:
                            if text_n != text_e:
                                break
                    else:
                        search_tr.append(tr_nth)
                        if find_one:
                            one_tr = tr_nth
                            break
        if find_one:
            return one_tr
        else:
            return search_tr

    def add(self, **kwargs) -> None:
        """ add 前是不查找是否存在的，直接加
        :param kwargs str, 待添加列 及对应值
        :return:
        """
        self.__edit_add(**kwargs)
        for i in range(0, self.tr.get_by_role('button').count()):
            action_attribute = self.tr.get_by_role('button').nth(i).get_attribute('onclick')
            if action_attribute in (
                'TGO(this).onAdd()', 'TGO(this).footerAdd()', 'footerAdd()') and self.tr.get_by_role(
                    'button').nth(i).is_enabled():
                self.tr.get_by_role('button').nth(i).click()
                if self.log_desc is not None:
                    logging.info(f'add table {self.log_desc} success')
                break

    def delete(self, **kwargs) -> None:
        """
        :param kwargs str, 待删除列 及对应值
        :return:
        """
        find_tr = self.exist(find_one=True, **kwargs)
        if find_tr is not None:
            self.tr.nth(find_tr).locator('//td').nth(0).click()
            for i in range(0, self.tr.get_by_role('button').count()):
                action_attribute = self.tr.get_by_role('button').nth(i).get_attribute('onclick')
                if action_attribute in ("TGO(this).onDelete()", "TGO(this).footerDel()", "footerDel()", 'delete_save(this)'):
                    if not self.tr.get_by_role('button').nth(i).is_disabled():
                        self.tr.get_by_role('button').nth(i).click()
                        if self.log_desc is not None:
                            logging.info(f'delete table {self.log_desc} success')
                        break
                    else:
                        logging.error(f'the data in the row {find_tr} cannot be deleted')
        else:
            logging.warning(f'not found the resource {kwargs}')

    def delete_all(self) -> None:
        nth = 1
        while self.tr.count() >= nth + 2:
            self.tr.nth(nth).locator('//td').nth(0).click()
            try:
                for i in range(0, self.tr.get_by_role('button').count()):
                    action_attribute = self.tr.get_by_role('button').nth(i).get_attribute('onclick')
                    if action_attribute in ("TGO(this).onDelete()", "TGO(this).footerDel()", 'footerDel()', 'delete_save(this)'):
                        if not self.tr.get_by_role('button').nth(i).is_disabled():
                            self.tr.get_by_role('button').nth(i).click()
                            break
                        else:
                            raise TimeoutError  # 第一行的数据不能删除，走到第二行去
                else:
                    break  # 所有行都走完了却没有删除按钮，也需要退出去
            except TimeoutError:
                nth = nth + 1
        logging.info('table resource all delete')

    def edit(self, old: dict, new: dict) -> None:
        """
        :param old ,dict, 待变更列数据
        :param new ,dict, 变更数据
        :return:
        """
        find_tr = self.exist(find_one=True, **old)
        if find_tr is not None:
            self.tr.nth(find_tr).locator('//td').nth(0).click()
            self.__edit_add(**new)
            for i in range(0, self.tr.get_by_role('button').count()):
                action_attribute = self.tr.get_by_role('button').nth(i).get_attribute('onclick')

                if action_attribute in ("TGO(this).onOK()", "TGO(this).footerOK()", 'footerOK()', 'footerModify()',
                                        "TGO(this).footerModify()",) and self.tr.get_by_role(
                        'button').nth(i).is_enabled():
                    self.tr.get_by_role('button').nth(i).click()
                    if self.log_desc is not None:
                        logging.info(f'edit table {self.log_desc} success')
                    break
        else:
            logging.warning(f'not found the resource {old}')

    def exists(self, value: list, find_one=True, locale=None) -> List[int] or List[list]:
        """查找多条记录

        :param value: list [{}, {}], 每组信息使用字典传输
        :param find_one: 是否只查询一个
        :param locale: 国际化，默认使用self.locale
        :return: 返回列表
        """
        result = []
        for value_ in value:
            result.append(self.exist(find_one, locale, **value_))
        return result

    def adds(self, value: list) -> None:
        """添加多列资源

        :param value: 列表， 套字典[{'acl_name': 'pl'}]
        :return:
        """
        if value:
            for value_ in value:
                self.add(**value_)

    def deletes(self, value: list) -> None:
        """删除多列资源

        :param value: 列表， 套字典[{'acl_name': 'pl'}]
        :return:
        """
        if value:
            for value_ in value:
                self.delete(**value_)

    def edits(self, value: list) -> None:
        """编辑多列资源

        :param value: 列表， 套字典[($old, $new)]  old 和new 都是字典
        :return:
        """
        if value:
            for value_ in value:
                self.edit(**value_[0], **value_[1])
