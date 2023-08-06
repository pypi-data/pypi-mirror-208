# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys
import re
import json

from collections import OrderedDict

from convert2vars.util.logging import Logging

__version__ = "1.0"


class ParseHelper(object):
    @classmethod
    def parse_values(cls, parameters, logger):
        Logging.debug(logger, "ParserHelper.{0}: start".format(
            sys._getframe().f_code.co_name))

        for key in parameters:
            # 値はNoneの場合は、''に変換
            if parameters[key] is None:
                parameters[key] = ''
                continue

            # Jinja2テンプレートの処理はスキップ {{ {%
            if (re.match(r'^\{{', str(parameters[key])) or re.match(r'^\{%', str(parameters[key]))):
                continue

            # Json形式の構造化された値はパースする
            if (re.match(r'^\[', str(parameters[key])) or re.match(r'^\{', str(parameters[key]))):
                try:
                    if type(parameters[key]) is dict or type(parameters[key]) is list:
                        continue
                    parameters[key] = json.loads(
                        str(parameters[key]))
                    # Python 3.7未満の場合は、dictの要素の順序性が保証されないため、対処を行う
                    # parameters[key] = json.loads(
                    #     str(parameters[key]), object_pairs_hook=OrderedDict)
                except json.decoder.JSONDecodeError as e:
                    Logging.error(
                        logger, u"パラメータ値のパースに失敗しました(パラメータ名: {0})".format(key))
                    Logging.error(
                        logger, u"パラメータファイルを編集し、正しいJSON形式で値を指定してください")
                    return None
        Logging.debug(logger, "ParserHelper.{0}: end".format(
            sys._getframe().f_code.co_name))
        return parameters
