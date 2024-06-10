import os

import zipfile

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
            
