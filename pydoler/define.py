from typing import *

DOWNLOAD_DIR:str = 'downloads' # 默认下载路径

FIRST_CHECK_DELAY:float = 0.5 # 默认首次检查延迟
LIST_CHECK_INTERVAL:float = 3 # 默认检查间隔
RETRY_TIMES:int = 5 # 默认重试次数
MAX_THREADS:int = 4 # 默认最大下载线程数
STREAM_MODE:bool = False # 是否开启流式下载模式

HEADERS:Dict[str, str]= {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
}

COOKIES:Dict[str, str] = {}
