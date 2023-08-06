# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from convert2vars.app.app_exception import *
from convert2vars.app.app_helper import AppHelper
from convert2vars.app.constants import Constants as cs
from convert2vars.util.logging import Logging

__version__ = "1.0"


class CommandConvert(object):
    @classmethod
    def execute(cls, ctx):
        base_path = ctx.obj['base_path']
        config = ctx.obj['config']
        config['runtime'] = {
            'section': ctx.obj['section'],
            'vars': ctx.obj['vars'],
            'use_environment': ctx.obj['use_environment'],
            'input_file': ctx.obj['input_file'],
            'output_file': ctx.obj['output_file'],
            'input_format': ctx.obj['input_format'],
            'output_format': ctx.obj['output_format'],
            'template_file': ctx.obj['template_file']
        }
        logger = ctx.obj['logger']
        Logging.debug(logger, "CommandConvert.{0}: start".format(
            sys._getframe().f_code.co_name))

        # パラメータファイル、環境変数、カスタムパラメータからパラメータリストを作成
        parameters_parsed = AppHelper.generate_parameters(
            config['runtime'], logger)

        Logging.debug(logger, parameters_parsed)

        # 指定したフォーマットに変換
        if config['runtime']['template_file'] != '':
            converted_rendered = AppHelper.generate_converted_with_template(
                config['runtime'], parameters_parsed, logger)
        else:
            converted_rendered = AppHelper.generate_converted_without_template(
                config['runtime'], parameters_parsed, logger)

        Logging.info(logger, converted_rendered)

        Logging.debug(logger, "CommandConvert.{0}: end".format(
            sys._getframe().f_code.co_name))
        return cs.EXIT_SUCCESS
