# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys
import json

from convert2vars.util.logging import Logging


class JsonFormatter(object):
    @classmethod
    def format(cls, parameters, logger):
        Logging.debug(logger, "JsonFormatter.{0}: start".format(
            sys._getframe().f_code.co_name))

        result = json.dumps(parameters)

        Logging.debug(logger, "JsonFormatter.{0}: end".format(
            sys._getframe().f_code.co_name))
        return result
