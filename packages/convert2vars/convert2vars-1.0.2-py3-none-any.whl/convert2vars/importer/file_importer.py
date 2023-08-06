# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from convert2vars.util.logging import Logging


class FileImporter(object):
    @classmethod
    def import_file(cls, app_config, file_path, logger):
        Logging.debug(logger, "FileImporter.{0}: start".format(
            sys._getframe().f_code.co_name))

        try:
            with open(file_path, "r") as f:
                file_data = f.read()
        except IOError:
            Logging.error(
                logger, u"Failed to read parameter file({0})".format(file_path))
            return None

        Logging.debug(logger, "FileImporter.{0}: end".format(
            sys._getframe().f_code.co_name))
        return file_data
