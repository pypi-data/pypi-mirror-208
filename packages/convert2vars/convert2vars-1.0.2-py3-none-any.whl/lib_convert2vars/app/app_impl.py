# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import sys

from convert2vars.app.constants import Constants as cs
from convert2vars.app.command.command_convert import CommandConvert
from convert2vars.util.config_util import ConfigUtil
from convert2vars.util.logging import Logging

__version__ = "1.0"


class AppImpl(object):
    @classmethod
    def _initialize(cls, ctx):
        config = {}

        try:
            if os.path.isfile(ctx.obj['config_file']):
                config = ConfigUtil.parse_config(ctx.obj['config_file'])
        except Exception:
            sys.stderr.write(
                u"[ERROR] app ログ出力の設定ファイルを読み込めませんでした(STATUS/{0})\n".format(
                    cs.EXIT_ERR_LOAD_CONFIG))
            sys.exit(cs.EXIT_ERR_LOAD_CONFIG)


        if config:
            logger = Logging.get_logger(config["logging"], ctx.obj['debug'], 'default')
        else:
            logger = Logging.get_logger({}, ctx.obj['debug'], __name__)
  
        return config, logger

    @classmethod
    def app_convert(cls, ctx):
        config, logger = cls._initialize(ctx)
        ctx.obj['config'], ctx.obj['logger'] = config, logger
        # 変換結果を取得する
        result = CommandConvert.execute(ctx)
        if result != cs.EXIT_SUCCESS:
            Logging.error(logger, "異常終了 ステータスコード: " + str(result))
            sys.exit(result)
