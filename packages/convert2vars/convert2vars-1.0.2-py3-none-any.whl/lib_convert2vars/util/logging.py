# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import glob
import os
import logging.config
from logging import (CRITICAL, DEBUG, ERROR, INFO, WARN, Formatter,
                     StreamHandler, getLogger)

__version__ = "1.0"


class Logging(object):
    @classmethod
    def get_logger(cls, config, enableDebug, logger_name):
        # configを指定されていれば、設定をロード
        if config:
            logging.config.dictConfig(config)
            return getLogger(logger_name)
        else:
            if enableDebug:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format="%(message)s"
                )
            else:
                logging.basicConfig(
                    level=logging.INFO,
                    format="%(message)s"
                )
            return getLogger()

    @classmethod
    def info(cls, logger, message):
        return logger.info(message) if logger is not None else None

    @classmethod
    def warn(cls, logger, message):
        return logger.warn(message) if logger is not None else None

    @classmethod
    def error(cls, logger, message):
        return logger.error(message) if logger is not None else None

    @classmethod
    def debug(cls, logger, message):
        return logger.debug('DEBUG: ' + str(message)) if logger is not None else None

    @classmethod
    def get_last_log(cls, config):
        log_filename_base = config['handlers']['file']['filename']

        # ローテーション前のログファイルが存在する場合は、
        # 最新のファイルとみなす
        if os.path.isfile(log_filename_base) and os.path.getsize(log_filename_base) != 0:
            return log_filename_base
        # ローテーション前のログファイルが存在しない場合は、
        # ファイル名で昇順にソートした最後のファイルを最新とみなす
        else:
            log_files = glob.glob(log_filename_base + '*')
            if log_files:
                log_files.sort()
                return log_files[-1]
            else:
                return None
