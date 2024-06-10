def sanitize_dirname(filename):
    '''### 目录名消毒
    将无法用于目录名中的字符替换为下划线。'''
    for c in ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]:
        filename = filename.replace(c, "_")
    return filename
