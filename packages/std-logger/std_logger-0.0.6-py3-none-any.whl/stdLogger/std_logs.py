#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   std_logs.py
@Time    :   2023/02/09 11:19:47
@Author  :   Wei.fu 
@Version :   1.0
@Contact :   wei.fw
@Desc    :   None
'''

# here put the import lib
from flask_log_request_id import current_request_id
from flask import g
import sys, traceback, os
from loguru import logger as _logger


def current_account_name():
    """
    获取当登陆的用户
    """
    try:
        account_name = g.get('account_name', None)
        return account_name
    except Exception:
        return None


_FORMAT_CONFIG = '<green>{time:YYYY-MM-DD hh:mm:ss}</green> | <level>{level}</level> | {message}'


class StdLogger(object):
    """
    自定义日志类
    """

    def __init__(self):
        try:
            is_exists = os.path.exists("./runtime")
            if not is_exists:
                os.mkdir("./runtime")
        except Exception as err:
            print(err)

        _logger.remove()
        _logger.add(sys.stdout, format=_FORMAT_CONFIG)
        #只记录INFO级别日志
        _logger.add("./runtime/app.log",
                    rotation="500 MB",
                    format=_FORMAT_CONFIG,
                    level=10
                    )
        # 记录warning以上的日志
        _logger.add(
            "./runtime/app_error.log",
            level=30,
            format=_FORMAT_CONFIG,
            rotation="500 MB",
        )

    def info_only(self, record):
        return record["level"].name == "INFO"

    def custom_message_context(self):
        """
        追加自定义的内容
        """
        account_name = current_account_name()
        request_id = current_request_id()
        result = traceback.extract_stack()
        caller = result[len(result) - 3]
        caller_list = str(caller).split(',')
        file_path_of_caller = caller_list[0].lstrip('<FrameSummary file ')

        _line = caller_list[1].split()[1]
        _base_dir = os.getcwd()
        module_line = "%s:%s" % (file_path_of_caller[len(_base_dir):], _line)
        msg = "%s | %s | %s" % (request_id, module_line, account_name)
        return msg

    def trace(self, __message: str, *args, **kwargs) -> None:
        """
          level 5
        """
        account_name = current_account_name()
        request_id = current_request_id()
        msg = "%s | %s | %s " % (request_id, account_name, __message)
        _logger.trace(msg, *args, **kwargs)

    def debug(self, __message: str, *args, **kwargs) -> None:
        """
        level 10
        """
        _msg = self.custom_message_context()
        print(type(__message))
        #message = "%s | %s" % (_msg, __message)
        #_logger.debug(message, *args, **kwargs)

    def info(self, __message: str, *args, **kwargs) -> None:
        """
        level 20
        """

        _msg = self.custom_message_context()
        message = "%s | %s" % (_msg, __message)
        _logger.info(message, *args, **kwargs)

    def success(self, __message: str, *args, **kwargs) -> None:
        """level 25"""
        _msg = self.custom_message_context()
        message = "%s | %s" % (_msg, __message)
        _logger.debug(message, *args, **kwargs)

    def warning(self, __message: str, *args, **kwargs) -> None:
        """level 30"""
        _msg = self.custom_message_context()
        message = "%s | %s" % (_msg, __message)
        _logger.warning(message, *args, **kwargs)

    def error(self, __message: str, *args, **kwargs) -> None:
        """level 40"""
        _msg = self.custom_message_context()
        message = "%s | %s" % (_msg, __message)
        _logger.error(message, *args, **kwargs)

    def exception(self, __message: str, *args, **kwargs) -> None:
        """level 50"""
        _msg = self.custom_message_context()
        message = "%s | %s" % (_msg, __message)
        _logger.exception(message, *args, **kwargs)


std_logger=logger = StdLogger()



