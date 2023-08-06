# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from convert2vars.util.logging import Logging


class TemplateRender(object):
    @classmethod
    def render(cls, template, parameters, logger):
        Logging.debug(logger, "TemplateRender.{0}: start".format(
            sys._getframe().f_code.co_name))

        try:
            rendered = template.render(parameters)
        except Exception as e:
            Logging.error(
                logger, 'Failed to generate converted file')
            Logging.error(logger, u"Exception Class: {0}".format(type(e)))
            Logging.error(logger, u"ARGS: {0}".format(e.args))
            return None

        Logging.debug(logger, "TemplateRender.{0}: end".format(
            sys._getframe().f_code.co_name))
        return rendered
