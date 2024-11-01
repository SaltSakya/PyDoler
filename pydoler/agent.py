import os
import time
from enum import Enum
from typing import List
from threading import Thread, Lock
from abc import ABC, abstractmethod

from pydoler.utils import *
from pydoler.define import *
from pydoler.downloader import download

class AgentState(Enum):
    NORMAL = 0
    FILLED = 1
    ERROR = 2

class Agent(ABC):
    def __init__(self, url,
                 headers:Dict[str, str] = HEADERS,
                 cookies = None,
                 stream = STREAM_MODE,
                 max_threads:int = MAX_THREADS,
                 download_dir:str = DOWNLOAD_DIR,
                 first_check_delay:str = FIRST_CHECK_DELAY,
                 list_check_interval:str = LIST_CHECK_INTERVAL,):
        self.url:str = url
        self.dirname:str = ""
        self.state:AgentState = AgentState.NORMAL

        self.headers:Dict[str, str] = headers
        self.cookies:Dict[str, str] = cookies
        self.stream:bool = stream

        self.max_threads:int = max_threads
        self.download_dir:str = download_dir
        self.first_check_delay:str = first_check_delay
        self.list_check_interval:str = list_check_interval

        self.cur_threads:int = 0

        self.lock:Lock = Lock()
        self.url_list:List[Tuple[str, str]] = list()

    def download(self):
        self.main_thread = Thread(target=self.download_thread)
        self.main_thread.start()

    def download_thread(self):
        '''### 下载线程'''
        self.url_preprocess()
        self.preprocess()
        self.mkdir()
        
        if self.state == AgentState.ERROR:
            return

        t = Thread(target=self.download_list)
        t.start()
        self.fill_list()
        self.state = AgentState.FILLED
        t.join()

    def url_preprocess(self):
        '''### url 预处理
        由于输入的 url 可能来自不同的相关 url，所以需要在此处进行预处理，以获取标准的 url。'''
        pass

    @abstractmethod
    def preprocess(self):
        '''### 预处理
        在此处进行预处理操作，并指定目录名（必需）。'''
        pass

    def mkdir(self):
        '''### 创建目录
        如果目录不存在，则递归创建目录。'''
        # 检查目录是否已定义
        if self.dirname == "":
            Log.Error("目录名未定义")
            self.state = AgentState.ERROR
            return
        
        # 目录名消毒
        self.dirname = sanitize_dirname(self.dirname)

        # 创建目录
        if not os.path.exists(os.path.join(self.download_dir, self.dirname)):
            os.makedirs(os.path.join(self.download_dir, self.dirname))

    def download_list(self):
        '''### 下载列表线程'''
        # 检查时刻
        t = time.time() + self.first_check_delay

        # 检查循环
        while True:
            # 若未到检查时刻，继续等待
            if time.time() < t: continue

            # 到达检查时刻，设定下次检查时间
            t = time.time() + self.list_check_interval

            # 检查当前线程数与 url 列表
            if self.cur_threads < self.max_threads and len(self.url_list):
                # 获取 url
                self.lock.acquire()
                filename, url, *retry = self.url_list.pop(0)
                self.cur_threads += 1 # 增加当前线程数
                self.lock.release()

                if len(retry): retry = retry[0]
                else: retry = 0

                # 下载 url 内容
                Thread(
                    target=download,
                    args=(url, os.path.join(self.download_dir, self.dirname)),
                    kwargs={
                        "filename": filename,
                        "headers": self.headers,
                        "cookies": self.cookies,
                        "stream": self.stream,
                        "retrys": retry,
                        "onfinish": self.revert_token
                    }).start()

            # 检查是否已全部下载完成
            if self.state == AgentState.FILLED and len(self.url_list) == 0 and self.cur_threads == 0:
                break

        self.postprocess()

    @abstractmethod
    def fill_list(self):
        '''### 填充任务 url 列表
        在此处填充 url 列表，并确保在添加 url 时加锁。'''
        pass

    def revert_token(self, retry:bool = False, filename:str = None, url:str = None, retryCount:int = 0):
        '''### 回调函数
        下载结束后的回调操作，减少当前线程数。'''
        self.lock.acquire()
        if retry:
            retryCount+=1
            if retryCount > RETRY_TIMES:
                Log.Error((">>> 重试次数已达上限，下载失败:\n"
                           f"\t文件名: {filename}\n"
                           f"\tURL: {url}"))
            else:
                Log.Warning((f">>> 下载失败，即将重试第{retryCount}次...\n"
                             f"\t文件名: {filename}\n"
                             f"\tURL: {url}"))
                self.url_list.append((filename, url, retryCount))
        self.cur_threads -= 1
        self.lock.release()

    def postprocess(self):
        '''### 后期处理
        在此处进行后期处理操作。'''
        pass

    def wait(self):
        self.main_thread.join()
