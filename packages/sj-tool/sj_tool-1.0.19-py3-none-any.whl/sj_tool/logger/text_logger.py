"""
This text_logger is wrapped from loguru: https://github.com/Delgan/loguru
"""

import os
import sys

import loguru
from loguru import logger
from datetime import datetime


class LogLevel:
    """
    TRACE：最低级别的日志，通常用于调试和追踪代码的执行过程。

    DEBUG：用于详细输出程序执行过程中的变量、状态和异常信息等，通常用于调试和问题定位。

    INFO：用于输出程序的正常运行信息，例如程序启动、停止等，可以用于了解程序的整体运行情况。

    SUCCESS：用于输出操作成功的信息，例如操作完成、数据保存成功等，可以用于展示程序的功能和成果。

    WARNING：用于输出警告信息，例如操作失败、数据异常等，可以用于提示用户注意问题。

    ERROR：用于输出错误信息，例如程序崩溃、异常退出等，可以用于帮助用户定位问题。

    CRITICAL：最高级别的日志，用于输出致命错误信息，例如系统故障、硬件故障等，需要及时采取紧急措施。
    """

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def init(level: str, save_log=True, logdir=None, comment="", filename="text.log", max_filesize=None) -> loguru.logger:
    """
    初始化日志框架
    :param level: 最低的日志level，如LogLevel.INFO
    :param save_log: 是否保存log到文件
    :param logdir: 日志目录
    :param comment: log文件夹名后缀(仅在logdir为None时有效)
    :param filename: 日志文件名
    :param max_filesize: 最大文件大小
    :param replace: 是否替换已有文件（如果文件存在）
    :return:
    """
    logger.remove()
    logger.add(sys.stdout, level=level)

    if not logdir:
        current_time = datetime.now().strftime("%b%d_%H-%M-%S")
        if "" != comment:
            comment = "." + comment
        logdir = os.path.join("runs", current_time + comment)

    if save_log:
        logger.add(os.path.join(logdir, filename), rotation=max_filesize, level=level)

    return logger
