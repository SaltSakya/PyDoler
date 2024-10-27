import os
import re

from requests import get, post, Response

from .utils import Log

def get_name_type(r: Response):
    '''
    获取文件名和文件类型
    :param r: 请求响应
    :return: 文件名, 文件类型'''
    if r.history:
        filename_in_url = r.history[0].url.split('/')[-1].split('?')[0]
    else:
        filename_in_url = r.url.split('/')[-1].split('?')[0]
    
    filename = "_".join(filename_in_url.split('.')[:-1])
    filetype_in_url = filename_in_url.split('.')[-1]

    filetype = re.search(r'^[a-zA-Z]*?/([^;]+);?(.*?)$', r.headers["Content-Type"]).group(1)
    if filetype == "jpeg" and filetype_in_url == "jpg":
        filetype = "jpg"
    return filename, filetype

def download(url:str, path:str, filename:str=None, headers=None, params=None, cookies=None, stream=False, retrys=0, onfinish=None):
    """
    下载文件
    :param url: 文件URL
    :param path: 保存路径
    :param headers: 请求头
    :param params: 请求参数
    :param cookies: 请求Cookie
    :param stream: 是否流式下载
    :param retrys: 重试次数
    :return: 文件保存路径
    """

    Log.Log(f">>> {url} 开始下载...")
    
    for i in range(retrys + 1):
        try:
            response = get(url, headers=headers, params=params, cookies=cookies, stream=stream)
            response.raise_for_status()

        except Exception as e:
            Log.Error((f">>> 打开文件链接失败\n"
                       f"\turl：{url}\n"
                       f"\t错误信息：{e}, {e.__traceback__}"))
            onfinish(True, filename, url, retrys)
            return
        
        try:
            n, t = get_name_type(response)

            if filename is None or filename == "":
                filename = f"{n}.{t}"
            elif len(filename.split('.')) > 0 and filename.split('.')[-1] != t:
                filename = ".".join(filename.split('.')[:-1] + [t])

            with open(os.path.join(path, filename), 'wb') as f:
                if stream:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                else:
                    f.write(response.content)
            break
        except Exception as e:
            Log.Error((f">>> 下载文件失败\n"
                       f"\t文件名：{filename}\n"
                       f"\turl：{url}\n"
                       f"\t错误信息：{e}, {e.__traceback__}"))
            
            onfinish(True, filename, url, retrys)
            return
    
    Log.Success(f">>> {url} 下载完成！")
    onfinish()
    return
