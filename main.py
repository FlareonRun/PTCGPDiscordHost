from adbutils import adb
import configparser
from host import Host
from crawler import Crawler


if __name__ == '__main__':
    # 获取配置
    conf = configparser.ConfigParser()
    conf.read('config.ini', encoding='utf-8')
    # adb端口
    adbPort = conf.get('HostSetting','AdbPort')
    # 登录凭证
    token = conf.get('HostSetting','Token')
    # 网络代理
    proxy = conf.get('HostSetting', 'Proxy')
    proxies = None
    if len(proxy) != 0:
        proxies = {
            'http': proxy,
            'https': proxy,
        }
    # 连接模拟器
    adb.connect('127.0.0.1:'+adbPort)
    device = adb.device('127.0.0.1:'+adbPort)

    # 获取帖子配置
    _list_sections = conf.sections()
    _list_channels = filter(lambda section: section.startswith('channel'), _list_sections)

    for channel in _list_channels:
        # 启动爬虫定时任务，定时爬取帖子回复
        channel_id = conf.get(channel,'ID')
        last_message_id = conf.get(channel,'LastMessageID')
        limit = conf.get(channel,'Limit')
        Crawler(channel_id,last_message_id,token,limit,proxies).start()


    # host线程启动 开始处理消息
    Host(device,conf,token,proxies).handle()