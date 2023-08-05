import logging
import os
from logging.handlers import RotatingFileHandler


def init(level=logging.INFO, logdir=None, filename="run.log", max_filesize=1024 * 1024 * 100) -> logging.Handler:
    """
    初始化日志框架
    :param level: 最低的日志level，如LogLevel.INFO
    :param logdir: 日志目录
    :param filename: 日志文件名
    :param max_filesize: 最大文件大小
    :return:
    """
    logging.basicConfig(level=level)
    logger = logging.getLogger()
    # 删除默认的handler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 设置日志格式
    # logging_format = logging.Formatter(
    #     "%(asctime)s %(levelname)s %(filename)s Line %(lineno)s %(funcName)s: %(message)s"
    # )
    time_format = "%Y-%m-%d %H:%M:%S"
    logging_format = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s Line %(lineno)s: %(message)s", datefmt=time_format
    )

    # 输出到控制台
    handler = logging.StreamHandler()
    handler.setFormatter(logging_format)
    logger.addHandler(handler)

    # 输出到文件
    if logdir:
        os.makedirs(logdir, exist_ok=True)
        # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
        file_handler = RotatingFileHandler(
            os.path.join(logdir, filename), maxBytes=max_filesize, backupCount=100, encoding="utf-8"
        )
        file_handler.setFormatter(logging_format)
        return file_handler
