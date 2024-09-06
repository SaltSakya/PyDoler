import os
from threading import Thread, Lock
from typing import List, Tuple, Any

import imageio
import zipfile

class Log:
    __thread: Thread = None
    __lock: Lock = Lock()
    __queue: List[Tuple[Tuple, dict[str, Any]]] = list()

    @staticmethod
    def printLog():
        print("Log thread started...")
        while Log.__queue:
            args, kwargs = Log.__queue.pop(0)
            print(*args, **kwargs)
        Log.__thread = None

    @staticmethod
    def print(*args, **kwargs):
        Log.__queue.append((args, kwargs))
        Log.__lock.acquire()
        if Log.__thread is None:
            Log.__thread = Thread(target=Log.printLog)
            Log.__thread.start()
        Log.__lock.release()
        

def sanitize_dirname(filename:str):
    '''### 目录名消毒
    将无法用于目录名中的字符替换为下划线。'''
    for c in ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]:
        filename = filename.replace(c, "_")
    return filename

def zip_dir(dir_path:str, zip_file_path:str=None, 
            compression:int=zipfile.ZIP_DEFLATED):
    '''### 压缩目录
    将指定目录压缩为zip文件。
    :param dir_path: 目录路径
    :param zip_file_path: 压缩文件路径，不指定则使用目录路径加上.zip后缀
    '''
    if zip_file_path is None:
        zip_file_path = dir_path + ".zip"

    with zipfile.ZipFile(zip_file_path, "w", compression=compression) as zf:
        for root, _, files in os.walk(dir_path):
            for file in files:
                filename = os.path.join(root, file)
                arcname = os.path.join(os.path.basename(root), file)
                zf.write(filename, arcname)

def unzip_file(zip_file_path:str, extract_dir:str):
    '''### 解压文件
    将指定zip文件解压到指定目录。
    :param zip_file_path: zip文件路径
    :param extract_dir: 解压目录
    '''
    with zipfile.ZipFile(zip_file_path, "r") as zf:
        zf.extractall(extract_dir)
            
def pack_gif(dir:str, gif_name:str, images:List[str], delays:List[int]|int = 30):
    '''### 打包gif
    将指定目录下的图片打包成gif。
    :param dir: 目录路径
    :param gif_name: 打包后的gif文件名
    :param images: 图片文件名列表
    :param delays: 每张图片的显示时间，单位毫秒
    '''

    if not gif_name.endswith(".gif"):
        gif_name += '.gif'

    if delays is int:
        fps = 1 / delays
    else:
        fps = len(delays)/sum(delays)

    fps *= 1000

    frames = [imageio.imread(os.path.join(dir, file)) for file in images]
    
    imageio.mimsave(os.path.join(dir, gif_name), frames, fps=fps)
