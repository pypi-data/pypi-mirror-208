# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import pathlib
import sys

from jinja2 import Environment, FileSystemLoader

from convert2vars.util.logging import Logging


class TemplateLoader(object):
    @classmethod
    def load(cls, template_file, encoding, logger):
        Logging.debug(logger, "TemplateLoader.{0}: start".format(
            sys._getframe().f_code.co_name))
        Logging.debug(logger, "TemplateLoader.{0}: read template({1}) / start".format(
            sys._getframe().f_code.co_name, template_file))

        template_base_dir = (pathlib.Path(template_file)).parent.resolve()
        template_file_basename = (pathlib.Path(template_file)).name
        jinja_env = Environment(loader=FileSystemLoader(
            str(template_base_dir), encoding=encoding))

        try:
            tmpl = jinja_env.get_template(template_file_basename)
            Logging.debug(logger, "TemplateLoader.{0}: read template({1}) / end".format(
                sys._getframe().f_code.co_name, template_file))
        except Exception as e:
            Logging.error(
                logger, "Failed to load template file({0})".format(template_file))
            Logging.error(logger, u"Exception Class: {0}".format(type(e)))
            Logging.error(logger, u"ARGS: {0}".format(e.args))
            return None

        Logging.debug(logger, "TemplateLoader.{0}: end".format(
            sys._getframe().f_code.co_name))
        return tmpl
