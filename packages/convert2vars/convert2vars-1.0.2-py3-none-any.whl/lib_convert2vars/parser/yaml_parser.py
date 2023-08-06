# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys
import yaml

from convert2vars.util.logging import Logging
from convert2vars.parser.parse_helper import ParseHelper

__version__ = "1.0"


class YamlParser(object):
    @classmethod
    def parse(cls, runtime_config, content_data, logger):
        Logging.debug(logger, "YamlParser.{0}: start".format(
            sys._getframe().f_code.co_name))
        parameters = None

        try:
            parameters = yaml.safe_load(content_data)
        except Exception as e:
            Logging.error(
                logger, u"パラメータファイルのパースに失敗しました({0})".format(content_data))
            Logging.error(logger, u"例外クラス: {0}".format(type(e)))
            Logging.error(logger, u"ARGS: {0}".format(e.args))
            Logging.debug(logger, u"例外詳細: {0}".format(e.message))
            return None

        parameters = ParseHelper.parse_values(dict(parameters), logger)

        Logging.debug(logger, "YamlParser.{0}: end".format(
            sys._getframe().f_code.co_name))
        return parameters
