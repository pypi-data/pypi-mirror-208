# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys
import yaml

from collections import OrderedDict
from convert2vars.util.logging import Logging

__version__ = "1.0"


class YamlFormatter(object):
    @classmethod
    def format(cls, parameters, logger):
        Logging.debug(logger, "YamlFormatter.{0}: start".format(
            sys._getframe().f_code.co_name))

        # PyYAMLのOrderedDict対応
        def _represent_odict(dumper, instance):
            return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

        def _construct_odict(loader, node):
            return OrderedDict(loader.construct_pairs(node))

        yaml.add_representer(OrderedDict, _represent_odict)
        yaml.add_constructor('tag:yaml.org,2002:map', _construct_odict)
        result = yaml.dump(parameters)

        Logging.debug(logger, "YamlFormatter.{0}: end".format(
            sys._getframe().f_code.co_name))
        return result
