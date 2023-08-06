# -*- coding: utf-8 -*-
# @Time   : 2023/3/31 14:40
# @Author : zhangzhongtian
# @File   : _ig_contents_locators.py
"""
_ig_contents_locators

"""
from playwright.sync_api import Locator, Page


class IGContentsLocators:

    def __init__(self, page: Page, language='en', model='IG902'):
        """

        :param page:
        :param language:
        :param model: 当前匹配IG902  IG502
        """
        self.page = page
        self.language = language
        self.model = model.upper()
        if language == 'en':
            self.__locale: dict = {'network': 'Network', 'network_interface': 'Network Interface',
                                   'cellular': 'Cellular', 'ethernet': 'Ethernet',
                                   'performance': 'Performance And Storage',
                                   'bridge': 'Bridge', 'loopback': 'Loopback',
                                   'network_service': 'Network Services', 'dhcp': 'DHCP',
                                   'dns': 'DNS', "gps_configure": "GPS Configure", 'gps': 'Status',
                                   "gps_ip_forwarding": "GPS IP Forwarding",
                                   "gps_serial_forwarding": "GPS Serial Forwarding",
                                   'host_list': 'Host List', 'routing': 'Routing',
                                   'routing_status': 'Routing Status',
                                   'routing_static': 'Static Routing', 'firewall': 'Firewall',
                                   'acl': 'ACL', 'nat': 'NAT',
                                   'status': 'Status', 'l2tp_client': 'L2TP Client',
                                   'l2tp_service': 'L2TP Service',
                                   'edge': 'Edge Computing', 'python_edge': 'Python Edge Computing',
                                   'docker_manager': 'Docker Manager', 'cloud_edge_computing': 'Cloud Edge Computing',
                                   'device_supervisor': 'Device Supervisor', 'measure_monitor': 'Measure Monitor',
                                   'monitoring_list': 'Monitoring List', 'group': 'Group',
                                   'alarm': 'Alarm', 'realtime_alarms': 'Realtime Alarms', 'alarm_rules': 'Alarm Rules',
                                   'history_alarms': 'History Alarms', 'alarm_label': 'Alarm Label',
                                   'cloud': 'Cloud', 'mqtt_cloud_service': 'MQTT Cloud Service',
                                   'whitehawk_energy_manager': 'Whitehawk Energy Manager', 'protocol': 'Protocol',
                                   'parameter_settings': 'Parameter Settings',
                                   'custom_quickfunctions': 'Custom QuickFunctions',
                                   'system': 'System', 'system_time': 'System Time', 'system_log': 'Log',
                                   'system_config': 'Configuration Management', 'system_cloud': 'InHand Cloud',
                                   'system_firmware': 'Firmware Upgrade', 'system_tools': 'Access Tools',
                                   'system_user_management': 'User Management', 'system_reboot': 'Reboot',
                                   'system_network_tools': 'Network Tools',
                                   'system_3rd_party': '3rd Party Notification',
                                   'configuration': ' Configuration', 'trigger_condition': 'Trigger Condition',
                                   'gigabitethernet': 'Gigabitethernet', 'flow_usage_day': 'Flow Usage Monitoring(Day)',
                                   'flow_usage_month': 'Flow Usage Monitoring(Month)'
                                   }
        else:
            self.__locale: dict = {'network': '网络', 'network_interface': '网络接口', 'performance': '性能与存储',
                                   'cellular': '蜂窝网', 'ethernet': '以太网',
                                   'bridge': '桥接口', 'loopback': '环回接口',
                                   'network_service': '网络服务', 'dhcp': 'DHCP服务',
                                   'dns': 'DNS服务', "gps_configure": "GPS 配置", 'gps': 'GPS',
                                   "gps_ip_forwarding": "GPS IP转发",
                                   "gps_serial_forwarding": "GPS 串口转发", 'host_list': '主机列表',
                                   'routing': '路由', 'routing_status': '路由状态',
                                   'routing_static': '静态路由', 'firewall': '防火墙',
                                   'acl': '访问控制列表', 'nat': '网络地址转换',
                                   'status': '状态', 'l2tp_client': 'L2TP客户端', 'l2tp_service': 'L2TP服务器',
                                   'edge': '边缘计算', 'python_edge': 'Python边缘计算', 'docker_manager': 'Docker 管理',
                                   'cloud_edge_computing': '公有云边缘计算', 'device_supervisor': '设备监控',
                                   'measure_monitor': '测点监控', 'monitoring_list': '监控列表', 'group': '分组',
                                   'alarm': '告警', 'realtime_alarms': '实时告警', 'alarm_rules': '告警规则',
                                   'history_alarms': '历史告警', 'alarm_label': '告警标签',
                                   'cloud': '云服务', 'mqtt_cloud_service': 'MQTT云服务',
                                   'whitehawk_energy_manager': '白鹰能源管家', 'protocol': '协议转换',
                                   'parameter_settings': '参数设置', 'custom_quickfunctions': '自定义快函数',
                                   'system': '系统管理', 'system_time': '系统时间', 'system_log': '系统日志',
                                   'system_config': '配置管理', 'system_cloud': '设备云平台',
                                   'system_firmware': '固件升级', 'system_tools': '管理工具',
                                   'system_user_management': '用户管理', 'system_reboot': '重启',
                                   'system_network_tools': '工具', 'system_3rd_party': '第三方软件声明',
                                   'configuration': '配置',
                                   'trigger_condition': '触发条件', 'gigabitethernet': '千兆以太网口',
                                   'flow_usage_day': '流量使用监测（当天）', 'flow_usage_month': '流量使用监测（当月）'
                                   }

    def content_target(self, locale) -> Locator:
        if self.__locale.get(locale):
            locale = self.__locale.get(locale)
        return self.page.locator(f'//span[@class="ant-breadcrumb-link"]/span[text()="{locale}"]')

    @property
    def overview_menu(self) -> Locator:
        return self.page.locator('//a[@href="/overview"]')

    @property
    def network_menu(self) -> Locator:
        return self.page.locator('//a[@href="/network"]')

    @property
    def edge_menu(self) -> Locator:
        return self.page.locator('//li[@role="menuitem"]/a[@href="/edge-computing"]')

    @property
    def system_menu(self) -> Locator:
        return self.page.locator('//li[@role="menuitem"]/a[@href="/system"]')

    @property
    def network_interface_menu(self) -> Locator:
        return self.page.locator(f'div:text-is("{self.__locale.get("network_interface")}")')

    @property
    def cellular_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("cellular")}")')

    @property
    def ethernet_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("ethernet")}")')

    @property
    def bridge_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("bridge")}")')

    @property
    def wlan_menu(self) -> Locator:
        return self.page.locator('a:has-text("WLAN")')

    @property
    def loopback_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("loopback")}")')

    @property
    def wan_menu_502(self) -> Locator:
        return self.page.locator('a:has-text("WAN")')

    @property
    def lan_menu_502(self) -> Locator:
        return self.page.locator('a:has-text("LAN")')

    @property
    def network_service_menu(self) -> Locator:
        return self.page.locator(f'div:text-is("{self.__locale.get("network_service")}")')

    @property
    def dhcp_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("dhcp")}")')

    @property
    def dns_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("dns")}")')

    @property
    def gps_menu(self) -> Locator:
        return self.page.locator('a:has-text("GPS")')

    @property
    def host_list_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("host_list")}")')

    @property
    def routing_menu(self) -> Locator:
        return self.page.locator(f'div:text-is("{self.__locale.get("routing")}")')

    @property
    def routing_status_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("routing_status")}")')

    @property
    def routing_static_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("routing_static")}")')

    @property
    def firewall_menu(self) -> Locator:
        return self.page.locator(f'div:text-is("{self.__locale.get("firewall")}")')

    @property
    def acl_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("acl")}")')

    @property
    def nat_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("nat")}")')

    @property
    def vpn_menu(self) -> Locator:
        return self.page.locator('div:text-is("VPN")')

    @property
    def l2tp_menu(self) -> Locator:
        return self.page.locator('a:has-text("L2TP")')

    @property
    def python_edge_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("python_edge")}")')

    @property
    def docker_manager_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("docker_manager")}")')

    @property
    def cloud_edge_computing_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("cloud_edge_computing")}")')

    @property
    def azure_iot_edge_menu(self) -> Locator:
        return self.page.locator('div:text-is("Azure IoT Edge")')

    @property
    def aws_iot_greengrass_menu(self) -> Locator:
        return self.page.locator('div:text-is("AWS IoT Greengrass")')

    @property
    def device_supervisor_menu(self) -> Locator:
        return self.page.locator(f'div:text-is("{self.__locale.get("device_supervisor")}")')

    @property
    def measure_monitor_menu(self) -> Locator:
        return self.page.locator(
            f'.ant-menu.ant-menu-sub.ant-menu-inline >> a:has-text("{self.__locale.get("measure_monitor")}")')

    @property
    def alarm_menu(self) -> Locator:
        return self.page.locator(
            f'.ant-menu.ant-menu-sub.ant-menu-inline >> a:has-text("{self.__locale.get("alarm")}")')

    @property
    def cloud_menu(self) -> Locator:
        return self.page.locator(
            f'.ant-menu.ant-menu-sub.ant-menu-inline >> a:has-text("{self.__locale.get("cloud")}")')

    @property
    def protocol_menu(self) -> Locator:
        return self.page.locator(
            f'.ant-menu.ant-menu-sub.ant-menu-inline >> a:has-text("{self.__locale.get("protocol")}")')

    @property
    def parameter_settings_menu(self) -> Locator:
        return self.page.locator(
            f'.ant-menu.ant-menu-sub.ant-menu-inline >> a:has-text("{self.__locale.get("parameter_settings")}")')

    @property
    def custom_quickfunctions_menu(self) -> Locator:
        return self.page.locator(
            f'.ant-menu.ant-menu-sub.ant-menu-inline >> a:has-text("{self.__locale.get("custom_quickfunctions")}")')

    @property
    def system_time_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_time")}")')

    @property
    def system_log_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_log")}")')

    @property
    def system_config_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_config")}")')

    @property
    def system_cloud_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_cloud")}")')

    @property
    def system_firmware_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_firmware")}")')

    @property
    def system_tools_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_tools")}")')

    @property
    def system_user_management_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_user_management")}")')

    @property
    def system_reboot_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_reboot")}")')

    @property
    def system_network_tools_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_network_tools")}")')

    @property
    def system_3rd_party_menu(self) -> Locator:
        return self.page.locator(f'a:has-text("{self.__locale.get("system_3rd_party")}")')

    @property
    def tags_menu(self) -> dict:
        return {
            'overview': {
                'default': 'flow_usage_monitoring(day)',
                'menu': self.overview_menu,
                'visible_locator': [self.page.locator(f'//div[text()="{self.__locale.get("performance")}"]')],
                'wait_locator': [self.page.locator(f'//div[text()="{self.__locale.get("performance")}"]')],
                'flow_usage_monitoring(day)': {
                    'menu': self.page.locator(f'div:text-is("{self.__locale.get("flow_usage_day")}")'),
                    'attributes': {
                        self.page.locator(f'div:text-is("{self.__locale.get("flow_usage_day")}")'): {
                            'aria-selected': 'true'}},
                },
                'flow_usage_monitoring(month)': {
                    'menu': self.page.locator(f'div:text-is("{self.__locale.get("flow_usage_month")}")'),
                    'attributes': {
                        self.page.locator(f'div:text-is("{self.__locale.get("flow_usage_month")}")'): {
                            'aria-selected': 'true'}},
                }
            },
            'network': {
                'default': 'network_interface.cellular',
                'menu': self.network_menu,
                'visible_locator': [self.page.locator('//span[@class="ant-breadcrumb-link"]/a[@href="/network"]')],
                'wait_locator': [self.content_target('cellular')],
                'network_interface': {
                    'default': 'cellular',
                    'menu': self.network_interface_menu,
                    'visible_locator': [self.cellular_menu],
                    'wait_locator': [self.cellular_menu],
                    'cellular': {
                        'menu': self.cellular_menu,
                        'visible_locator': [self.content_target('cellular')],
                        'wait_locator': [self.content_target('cellular')]},
                    'ethernet': {
                        'default': 'gigabitethernet_0/1',
                        'menu': self.ethernet_menu,
                        'visible_locator': [self.content_target('ethernet')],
                        'wait_locator': [self.content_target('ethernet')],
                        'gigabitethernet_0/1': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("gigabitethernet")} 0/1")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("gigabitethernet")} 0/1")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('#internet')],
                        },
                        'gigabitethernet_0/2': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("gigabitethernet")} 0/2")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("gigabitethernet")} 0/2")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [
                                self.page.locator('.antd-pro-components-description-list-index-term').first],
                        }
                    },
                    'bridge': {
                        'menu': self.bridge_menu,
                        'visible_locator': [self.content_target('bridge')],
                        'wait_locator': [self.content_target('bridge')]},
                    'wlan': {
                        'menu': self.wlan_menu,
                        'visible_locator': [self.content_target('WLAN')],
                        'wait_locator': [self.content_target('WLAN')]},
                    'wan': {
                        'menu': self.wan_menu_502,
                        'visible_locator': [self.content_target('WAN')],
                        'wait_locator': [self.content_target('WAN')]},
                    'lan': {
                        'menu': self.lan_menu_502,
                        'visible_locator': [self.content_target('LAN')],
                        'wait_locator': [self.content_target('LAN')]},
                    'loopback': {
                        'menu': self.loopback_menu,
                        'visible_locator': [self.content_target('loopback')],
                        'wait_locator': [self.content_target('loopback')]}},
                # Network Services
                'network_services': {
                    'menu': self.network_service_menu,
                    'visible_locator': [self.dhcp_menu],
                    'wait_locator': [self.dhcp_menu],
                    'dhcp': {
                        'menu': self.dhcp_menu,
                        'visible_locator': [self.content_target('dhcp')],
                        'wait_locator': [self.content_target('dhcp')]},
                    'dns': {
                        'menu': self.dns_menu,
                        'visible_locator': [self.content_target('dns')],
                        'wait_locator': [self.content_target('dns')]},
                    'gps': {
                        'default': 'gps_configure',
                        'menu': self.gps_menu,
                        'visible_locator': [self.content_target('gps')],
                        'wait_locator': [self.content_target('gps')],
                        'gps_configure': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("gps_configure")}")'),
                            'attributes': {self.page.locator(f'div:text-is("{self.__locale.get("gps_configure")}")'): {
                                'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('.ant-form-item-no-colon')],
                        },
                        'gps_ip_forwarding': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("gps_ip_forwarding")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("gps_ip_forwarding")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('#enable')],
                        },
                        'gps_serial_forwarding': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("gps_serial_forwarding")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("gps_serial_forwarding")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('#enable')],
                        },
                    },
                    'host_list': {
                        'menu': self.host_list_menu,
                        'visible_locator': [self.content_target('host_list')],
                        'wait_locator': [self.content_target('host_list')]}},
                # Routing
                'routing': {
                    'menu': self.routing_menu,
                    'visible_locator': [self.routing_status_menu],
                    'wait_locator': [self.routing_status_menu],
                    'routing_status': {
                        'menu': self.routing_status_menu,
                        'visible_locator': [self.content_target('routing_status')],
                        'wait_locator': [self.content_target('routing_status')]},
                    'static_routing': {
                        'menu': self.routing_static_menu,
                        'visible_locator': [self.content_target('routing_static')],
                        'wait_locator': [self.content_target('routing_static')]}},
                # Firewall
                'firewall': {
                    'menu': self.firewall_menu,
                    'visible_locator': [self.acl_menu],
                    'wait_locator': [self.acl_menu],
                    'acl': {
                        'menu': self.acl_menu,
                        'visible_locator': [self.content_target('acl')],
                        'wait_locator': [self.content_target('acl')]},
                    'nat': {
                        'menu': self.nat_menu,
                        'visible_locator': [self.content_target('nat')],
                        'wait_locator': [self.content_target('nat')]}},
                # VPN
                'vpn': {
                    'menu': self.vpn_menu,
                    'visible_locator': [self.l2tp_menu],
                    'wait_locator': [self.l2tp_menu],
                    'l2tp': {
                        'default': 'status',
                        'menu': self.l2tp_menu,
                        'status': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("status")}")'),
                            'attributes': {self.page.locator(f'div:text-is("{self.__locale.get("status")}")'): {
                                'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('.ant-spin-container').first],
                        },
                        'l2tp_client': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("l2tp_client")}")'),
                            'attributes': {self.page.locator(f'div:text-is("{self.__locale.get("l2tp_client")}")'): {
                                'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('.ant-spin-container').first]
                        },
                        'l2tp_service': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("l2tp_service")}")'),
                            'attributes': {self.page.locator(f'div:text-is("{self.__locale.get("l2tp_service")}")'): {
                                'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('.ant-spin-container').first]}
                    }
                }
            },
            'edge_computing': {
                'default': 'python_edge_computing',
                'menu': self.edge_menu,
                'visible_locator': [
                    self.page.locator('//span[@class="ant-breadcrumb-link"]/a[@href="/edge-computing"]').last],
                'wait_locator': [self.content_target('python_edge').nth(1)],
                'python_edge_computing': {
                    'menu': self.python_edge_menu,
                    'visible_locator': [self.content_target('python_edge').nth(1)],
                    'wait_locator': [self.content_target('python_edge').nth(1)]
                },
                'docker_manager': {
                    'menu': self.docker_manager_menu,
                    'visible_locator': [self.content_target('docker_manager').nth(1)],
                    'wait_locator': [self.content_target('docker_manager').nth(1)]
                },
                'cloud_edge_computing': {
                    'default': 'azure_iot_edge',
                    'menu': self.cloud_edge_computing_menu,
                    'visible_locator': [self.content_target('cloud_edge_computing').nth(1)],
                    'wait_locator': [self.content_target('cloud_edge_computing').nth(1)],
                    'azure_iot_edge': {
                        'menu': self.azure_iot_edge_menu,
                        'attributes': {self.azure_iot_edge_menu: {'aria-selected': 'true'}},
                        'wait_locator': [self.page.locator('//button[@id="enable"]').first],
                    },
                    'aws_iot_greengrass': {
                        'menu': self.aws_iot_greengrass_menu,
                        'attributes': {
                            self.aws_iot_greengrass_menu: {'aria-selected': 'true'}},
                        'wait_locator': [self.page.locator('//button[@id="enable"]').first],
                    }
                },
                # Device Supervisor
                'device_supervisor': {
                    'default': 'measure_monitor.monitoring_list',
                    'menu': self.device_supervisor_menu,
                    'visible_locator': [self.measure_monitor_menu],
                    'wait_locator': [self.measure_monitor_menu],
                    'measure_monitor': {
                        'default': 'monitoring_list',
                        'menu': self.measure_monitor_menu,
                        'visible_locator': [self.content_target('measure_monitor')],
                        'monitoring_list': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("monitoring_list")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("monitoring_list")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('.ant-input-search-button').first],
                        },
                        'group': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("group")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("group")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('//i[@class="anticon anticon-plus-circle"]')],
                        },
                    },
                    'alarm': {
                        'default': 'realtime_alarms',
                        'menu': self.alarm_menu,
                        'visible_locator': [self.content_target('alarm')],
                        'wait_locator': [self.content_target('alarm')],
                        'realtime_alarms': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("realtime_alarms")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("realtime_alarms")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('.ant-table-header.ant-table-hide-scrollbar')]
                        },
                        'alarm_rules': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("alarm_rules")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("alarm_rules")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [
                                self.page.locator(f'span:text-is("{self.__locale.get("trigger_condition")}")')]
                        },
                        'history_alarms': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("history_alarms")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("history_alarms")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('span:text-is("~")')]
                        },
                        'alarm_label': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("alarm_label")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("alarm_label")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('.ant-table-selection-column >> nth=0')]
                        },
                    },
                    'cloud': {
                        'default': 'mqtt_cloud_service',
                        'menu': self.cloud_menu,
                        'visible_locator': [self.content_target('cloud')],
                        'wait_locator': [self.content_target('cloud')],
                        'mqtt_cloud_service': {
                            'menu': self.page.locator(f'div:text-is("{self.__locale.get("mqtt_cloud_service")}")'),
                            'attributes': {
                                self.page.locator(f'div:text-is("{self.__locale.get("mqtt_cloud_service")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('//label[@for="enable.form"]')]
                        },
                        'whitehawk_energy_manager': {
                            'menu': self.page.locator(
                                f'div:text-is("{self.__locale.get("whitehawk_energy_manager")}")'),
                            'attributes': {
                                self.page.locator(
                                    f'div:text-is("{self.__locale.get("whitehawk_energy_manager")}")'): {
                                    'aria-selected': 'true'}},
                            'wait_locator': [self.page.locator('//label[@for="enable.form"]')]
                        }
                    },
                    'protocol': {
                        'default': 'modbus_tcp_slave',
                        'menu': self.protocol_menu,
                        'visible_locator': [self.content_target('protocol')],
                        'wait_locator': [self.content_target('protocol')],
                        'modbus_tcp_slave': {
                            'menu': self.page.locator(f'div:text-is("Modbus TCP Slave")'),
                            'visible_locator': [
                                self.page.locator(f'text=Modbus TCP Slave{self.__locale.get("configuration")}')],
                            'wait_locator': [
                                self.page.locator(f'text=Modbus TCP Slave{self.__locale.get("configuration")}')],
                        },
                        'iec_104_server': {
                            'menu': self.page.locator(f'div:text-is("IEC 104 Server")'),
                            'visible_locator': [
                                self.page.locator(f'text=IEC 104 Server{self.__locale.get("configuration")}')],
                            'wait_locator': [
                                self.page.locator(f'text=IEC 104 Server{self.__locale.get("configuration")}')],
                        },
                        'opcua_server': {
                            'menu': self.page.locator(f'div:text-is("OPCUA Server")'),
                            'visible_locator': [
                                self.page.locator(f'text=OPCUA Server{self.__locale.get("configuration")}')],
                            'wait_locator': [
                                self.page.locator(f'text=OPCUA Server{self.__locale.get("configuration")}')],
                        },
                        'modbus_rtu_slave': {
                            'menu': self.page.locator(f'div:text-is("Modbus RTU Slave")'),
                            'visible_locator': [
                                self.page.locator(f'text=Modbus RTU Slave{self.__locale.get("configuration")}')],
                            'wait_locator': [
                                self.page.locator(f'text=Modbus RTU Slave{self.__locale.get("configuration")}')],
                        },
                    },
                    'parameter_settings': {
                        'menu': self.parameter_settings_menu,
                        'visible_locator': [self.content_target('parameter_settings')],
                        'wait_locator': [self.content_target('parameter_settings')]
                    },
                    'custom_quickfunctions': {
                        'menu': self.custom_quickfunctions_menu,
                        'visible_locator': [self.content_target('custom_quickfunctions')],
                        'wait_locator': [self.content_target('custom_quickfunctions')]}
                }
            },
            'system': {
                'default': 'system_time',
                'menu': self.system_menu,
                'visible_locator': [self.page.locator('//span[@class="ant-breadcrumb-link"]/a[@href="/system"]')],
                'wait_locator': [self.content_target('system_time')],
                'system_time': {
                    'menu': self.system_time_menu,
                    'visible_locator': [self.content_target('system_time')],
                    'wait_locator': [self.content_target('system_time')],
                },
                'log': {
                    'default': 'log',
                    'menu': self.system_log_menu,
                    'visible_locator': [self.content_target('system_log')],
                    'wait_locator': [self.content_target('system_log')],
                    'log': {
                        'menu': self.page.locator('.ant-tabs-tab >> nth=0'),
                        'attributes': {
                            self.page.locator('.ant-tabs-tab >> nth=0'): {'aria-selected': 'true'}},
                        'wait_locator': [self.page.locator('//button[@class="ant-btn"]').first],
                    },
                    'configure': {
                        'menu': self.page.locator('.ant-tabs-tab >> nth=1'),
                        'attributes': {
                            self.page.locator('.ant-tabs-tab >> nth=1'): {'aria-selected': 'true'}},
                        'wait_locator': [self.page.locator('#log_to_remote_enable')],
                    }
                },
                'configuration_management': {
                    'menu': self.system_config_menu,
                    'visible_locator': [self.content_target('system_config')],
                    'wait_locator': [self.content_target('system_config')],
                },
                'inhand_cloud': {
                    'default': 'inhand_connect_service',
                    'menu': self.system_cloud_menu,
                    'visible_locator': [self.content_target('system_cloud')],
                    'wait_locator': [self.content_target('system_cloud')],
                    'inhand_connect_service': {
                        'menu': self.page.locator(f'div:text-is("InHand Connect Service")'),
                        'attributes': {
                            self.page.locator(f'div:text-is("InHand Connect Service")'): {'aria-selected': 'true'}},
                        'wait_locator': [self.page.locator('//button[@id="enable"]')],
                    },
                    'inhand_device_manager': {
                        'menu': self.page.locator(f'div:text-is("InHand Device Manager")'),
                        'attributes': {
                            self.page.locator(f'div:text-is("InHand Device Manager")'): {'aria-selected': 'true'}},
                        'wait_locator': [self.page.locator('//button[@id="enable"]')],
                    },
                    'inhand_iscada_cloud': {
                        'menu': self.page.locator(f'div:text-is("InHand iSCADA Cloud")'),
                        'attributes': {
                            self.page.locator(f'div:text-is("InHand iSCADA Cloud")'): {'aria-selected': 'true'}},
                        'wait_locator': [self.page.locator('//button[@id="mode"]')],
                    }
                },
                'firmware_upgrade': {
                    'menu': self.system_firmware_menu,
                    'visible_locator': [self.content_target('system_firmware')],
                    'wait_locator': [self.content_target('system_firmware')],
                },
                'access_tools': {
                    'menu': self.system_tools_menu,
                    'visible_locator': [self.content_target('system_tools')],
                    'wait_locator': [self.content_target('system_tools')],
                },
                'user_management': {
                    'menu': self.system_user_management_menu,
                    'visible_locator': [self.content_target('system_user_management')],
                    'wait_locator': [self.content_target('system_user_management')],
                },
                'reboot': {
                    'menu': self.system_reboot_menu,
                    'visible_locator': [self.content_target('system_reboot')],
                    'wait_locator': [self.content_target('system_reboot')],
                },
                'network_tools': {
                    'menu': self.system_network_tools_menu,
                    'visible_locator': [self.content_target('system_network_tools')],
                    'wait_locator': [self.content_target('system_network_tools')],
                },
                '3rd_party_notification': {
                    'menu': self.system_3rd_party_menu,
                    'attributes': {self.system_3rd_party_menu.locator('..'): {'class': 'ant-menu-item-selected'}},
                    'wait_locator': [self.content_target('system_3rd_party')],
                }
            },
        }
