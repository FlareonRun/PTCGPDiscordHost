import requests
import host
import re
import threading
import time
import logging
import operator

LOGGER = logging.getLogger("Crawler")

class Crawler(threading.Thread):

    def __init__(self,channel_id,last_message_id,token,limit,proxies):
        threading.Thread.__init__(self, name=channel_id)
        self.token = token
        self.channel_id = channel_id
        self.last_message_id = last_message_id
        self.limit = limit
        self.proxies = proxies
        # 生成帖子URL
        self.url = "https://discord.com/api/v9/channels/{}/messages?limit=10".format(channel_id)
        print('Crawler',channel_id, 'init finished')

    def run(self):
        # 每分钟爬取一次数据
        while True:
            self.crawl()
            time.sleep(60)


    def crawl(self):
        # 拼接翻页
        page = ''
        if len(self.last_message_id) != 0:
            page = '&after={}'.format(self.last_message_id)
        LOGGER.info('Crawler crawling {}...'.format(self.url))
        # 大陆需要使用代理才能访问
        try:
            response = requests.get(self.url+page,proxies=self.proxies,headers={'Authorization':self.token})
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Error request: {e}")
            return
        if response.status_code == 200:
            # 使用 .json() 方法解析 JSON 响应体并转化为 Python 字典
            data = response.json()
            sort_data = sorted(data,key=operator.itemgetter('timestamp'),reverse=False)
            # 匹配16位数字
            fc_pattern = re.compile(r'\d{16}')
            for message in sort_data:
                matcher = fc_pattern.search(message['content'])
                self.last_message_id = message['id']
                if matcher:
                    friend_code = matcher.group()
                    # 获取帖子ID 消息ID 好友码 用户ID
                    fc_message = {'channel_id':self.channel_id,'message_id':message['id'],'friend_code':friend_code,'user_id':message['author']['id']}
                    LOGGER.info(fc_message)
                    # 放入队列 等待host处理
                    host.message_queue.put(fc_message)


