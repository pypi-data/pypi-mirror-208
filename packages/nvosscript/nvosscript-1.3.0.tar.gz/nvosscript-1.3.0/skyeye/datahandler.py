import os
import re
import logging

# 导入全局日志记录器
logger = logging.getLogger(__name__)
def filter_effective_log(path):
    if path is None:
        print("please upload correct path")
        return
    logger.info(f" start filter_effective_log {path}")
    logger_list = []
    if not os.path.exists(path) or os.path.isdir(path):
        print(f"{path} not exists or this path is directory,please upload a logger file ")
        return

    with open(path, 'r') as f:
        for line in f:
            matchObj = re.match("\d|\d+|\d+|.*", line, re.M | re.I)
            if matchObj:
                logger_list.append(line)

    logger.info(f"filter logger info data is {logger_list}")
    



