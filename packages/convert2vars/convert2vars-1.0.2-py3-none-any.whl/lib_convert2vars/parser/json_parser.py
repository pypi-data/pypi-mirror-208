# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys
import json

from convert2vars.util.logging import Logging
from convert2vars.parser.parse_helper import ParseHelper

__version__ = "1.0"


class JsonParser(object):
    @classmethod
    def parse(cls, runtime_config, content_data, logger):
        Logging.debug(logger, "JsonParser.{0}: start".format(
            sys._getframe().f_code.co_name))
        parameters = None

        try:
            parameters = json.loads(content_data)
        except Exception as e:
            Logging.error(
                logger, u"パラメータファイルのパースに失敗しました({0})".format(content_data))
            Logging.error(logger, u"例外クラス: {0}".format(type(e)))
            Logging.error(logger, u"ARGS: {0}".format(e.args))
            return None

        parameters = ParseHelper.parse_values(dict(parameters), logger)

        Logging.debug(logger, "JsonParser.{0}: end".format(
            sys._getframe().f_code.co_name))
        return parameters
