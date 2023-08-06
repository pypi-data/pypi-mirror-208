# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import re
import configparser
import json
from collections import OrderedDict

from convert2vars.util.logging import Logging


__version__ = "1.0"


class ParameterLoader(object):
    @classmethod
    def load(cls, parameter_file, parameter_section, logger):
        Logging.info(
            logger, u"パラメータファイルの読み込み({0})".format(parameter_file))

        inifile = configparser.SafeConfigParser()
        inifile.optionxform = str

        try:
            read_result = inifile.read(parameter_file)
            if not read_result:
                Logging.error(
                    logger, u"パラメータファイルが存在しないか、アクセスできません({0})".format(parameter_file))
                return None
        except Exception as e:
            Logging.error(
                logger, u"パラメータファイルの読み込みに失敗しました({0})".format(parameter_file))
            Logging.error(logger, u"例外クラス: {0}".format(type(e)))
            Logging.error(logger, u"ARGS: {0}".format(e.args))
            Logging.debug(logger, u"例外詳細: {0}".format(e.message))
            return None

        parameters = dict(inifile.items(parameter_section))
        for key in parameters:
            # Jinja2テンプレートの処理はスキップ {{ {%
            if (re.match(r'^\{{', parameters[key]) or re.match(r'^\{%', parameters[key])):
                continue

            # Json形式の構造化された値はパースする
            if (re.match(r'^\[', parameters[key]) or re.match(r'^\{', parameters[key])):
                try:
                    parameters[key] = json.loads(
                        parameters[key], object_pairs_hook=OrderedDict)
                except json.decoder.JSONDecodeError as e:
                    Logging.error(
                        logger, u"パラメータ値のパースに失敗しました(パラメータ名: {0})".format(key))
                    Logging.error(
                        logger, u"パラメータファイルを編集し、正しいJSON形式で値を指定してください")
                    return None

        Logging.info(
            logger, u"パラメータファイルの読み込み({0}): 成功".format(parameter_file))
        return parameters
