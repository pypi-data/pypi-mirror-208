# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import sys

from dotenv import load_dotenv
from convert2vars.app.constants import Constants as cs
from convert2vars.app.command.command_convert import CommandConvert
from convert2vars.util.config_util import ConfigUtil
from convert2vars.util.logging import Logging


class AppImpl(object):
    @classmethod
    def _initialize(cls, ctx):
        config = {}

        try:
            if os.path.isfile(ctx.obj['config_file']):
                config = ConfigUtil.parse_config(ctx.obj['config_file'])
        except Exception:
            sys.stderr.write(
                "[ERROR] app Could not read log output configuration file(STATUS/{0})\n".format(
                    cs.EXIT_ERR_LOAD_CONFIG))
            sys.exit(cs.EXIT_ERR_LOAD_CONFIG)

        if config:
            logger = Logging.get_logger(
                config['logging'], ctx.obj['output_file'], ctx.obj['debug'], 'default')
        else:
            logger = Logging.get_logger(
                {}, ctx.obj['output_file'], ctx.obj['debug'], __name__)

        if ctx.obj['dotenv_file'] != "":
            load_dotenv(ctx.obj['dotenv_file'])

        return config, logger

    @classmethod
    def app_convert(cls, ctx):
        config, logger = cls._initialize(ctx)
        ctx.obj['config'], ctx.obj['logger'] = config, logger

        # Perform the conversion
        result = CommandConvert.execute(ctx)
        if result != cs.EXIT_SUCCESS:
            Logging.error(logger, "Error occurred (STATUS/{0})".format(result))
            sys.exit(result)
