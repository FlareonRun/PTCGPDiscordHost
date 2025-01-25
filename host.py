import queue
import time
from configparser import ConfigParser
import pyautogui
import os
import requests
from adbutils import AdbDevice
import logging

LOGGER = logging.getLogger("Host")
message_queue = queue.Queue()

class Host:
    confidence = 0.9
    reset = False
    handle_message = None


    def __init__(self,device: AdbDevice,conf: ConfigParser,token,proxies):
        self.device = device
        self.conf = conf
        self.token = token
        self.proxies = proxies

    def handle(self):
        print("host started...")
        while True:
            # 游戏画面行动至填写用户ID
            is_ready = self.wait_for_add()
            if is_ready:
                # 从队列中提取消息
                message = message_queue.get()
                # 队列中无消息则等待30秒
                if message is None:
                    time.sleep(30)
                    continue
                print("Received message: ", message)
                # 记录当前处理中的消息
                self.handle_message = message
                # 输入好友ID
                self.device.click(270,790)
                time.sleep(1)
                self.device.send_keys(message['friend_code'])
                self.conf.set('channel-'+ message['channel_id'],'LastMessageID',message['message_id'])
                # 将消息ID写入配置文件
                with open('config.ini', 'w') as config_file:
                    self.conf.write(config_file)


    def wait_for_add(self):
        time.sleep(1)
        screenshot = self.device.screenshot()
        # 回到初始位置
        if self.reset:
            if self.image_search(self.get_image_path('cancel'), screenshot, region=(240, 875, 60, 60)):
                self.device.click(270, 900)
                return False
        # 等待输入ID位置
        if self.image_search(self.get_image_path('search'),screenshot,region=(330, 760, 160, 80)):
            return True
        if self.image_search(self.get_image_path('community'),screenshot,region=(245, 900, 60, 60)):
            self.device.click(270,930)
            return False
        if self.image_search(self.get_image_path('friends'),screenshot,region=(40, 790, 60, 60)):
            self.reset = False
            self.device.click(65, 830)
            return False
        if self.image_search(self.get_image_path('add'),screenshot,region=(455, 120, 60, 60)):
            self.device.click(480, 150)
            return False
        if self.image_search(self.get_image_path('ready'),screenshot,region=(420, 770, 60, 60)):
            self.device.click(450, 800)
            return False
        if self.image_search(self.get_image_path('request'),screenshot,region=(325, 405, 60, 60)):
            self.device.click(400, 430)
            return False
        # 已经是好友返回初始位置
        if self.image_search(self.get_image_path('already'),screenshot,region=(325, 405, 60, 60)):
            self.reset = True
            return False
        # 错误ID返回初始位置
        if self.image_search(self.get_image_path('error'),screenshot,region=(230, 200, 90, 90)):
            print("error!")
            self.device.click(270, 670)
            self.reset = True
            return False
        # 申请成功添加反应后回到初始位置
        if self.image_search(self.get_image_path('requested'),screenshot,region=(305, 400, 60, 60)):
            #self.add_reaction()
            self.reset = True
            return False
        return False


    # 添加反应
    #def add_reaction(self) :
        #url = 'https://discord.com/api/v9/channels/{}/messages/{}/reactions/%F0%9F%91%8C/%40me?location=Message%20Hover%20Bar&type=0'.format(self.handle_message['channel_id'],self.handle_message['message_id'])
        #requests.put(url,proxies=self.proxies,headers={'Authorization':self.token})

    # 抄的Sliverala大佬的方法
    def get_image_path(self, image_name):
        return os.path.join(os.curdir, "resource", f"{image_name}.png")

    # 抄的Sliverala大佬的方法
    def image_search(self, image_path, screenshot, region=None,confidence=confidence):
        """
        在图片中搜索指定图像
        """
        try:
            result = pyautogui.locate(
                image_path, screenshot, region=region, confidence=confidence
            )
            if result:
                LOGGER.info(
                        f"Found {image_path} at ({result.left}, {result.top}, {result.left + result.width}, {result.top + result.height})"
                )
            return result
        except pyautogui.ImageNotFoundException as e:
            LOGGER.debug(f"Image not found: {image_path}")
            return None
        except Exception as e:
            LOGGER.error(f"Error during image search: {e}")
            return None

