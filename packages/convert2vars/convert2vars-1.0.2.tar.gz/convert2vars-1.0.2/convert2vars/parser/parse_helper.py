# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys
import re
import json

from collections import OrderedDict

from convert2vars.util.logging import Logging


class ParseHelper(object):
    @classmethod
    def parse_values(cls, parameters, logger):
        Logging.debug(logger, "ParserHelper.{0}: start".format(
            sys._getframe().f_code.co_name))

        for key in parameters:
            # If the value is None, convert to ''.
            if parameters[key] is None:
                parameters[key] = ''
                continue

            # If string is Jinja2 template, skip processing (String starting with '{{' '{%')
            if (re.match(r'^\{{', str(parameters[key])) or re.match(r'^\{%', str(parameters[key]))):
                continue

            # Structured values in Json format are parsed
            if (re.match(r'^\[', str(parameters[key])) or re.match(r'^\{', str(parameters[key]))):
                try:
                    if type(parameters[key]) is dict or type(parameters[key]) is list:
                        continue
                    parameters[key] = json.loads(
                        str(parameters[key]))
                    # If less than Python 3.7, dict elements are not guaranteed to be ordered,
                    # so deal with it.
                    # parameters[key] = json.loads(
                    #     str(parameters[key]), object_pairs_hook=OrderedDict)
                except json.decoder.JSONDecodeError as e:
                    Logging.error(
                        logger, "Failed to parse parameter value(Name: {0})".format(key))
                    Logging.error(
                        logger, "Edit the parameter file and specify values in the correct JSON format")
                    return None
        Logging.debug(logger, "ParserHelper.{0}: end".format(
            sys._getframe().f_code.co_name))
        return parameters
