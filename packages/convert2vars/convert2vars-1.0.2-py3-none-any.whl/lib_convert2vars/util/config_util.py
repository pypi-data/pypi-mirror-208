# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import yaml

__version__ = "1.0"


class ConfigUtil(object):
    @classmethod
    def parse_config(cls, config_file):
        yaml_obj = None
        with open(config_file) as f:
            yaml_obj = yaml.safe_load(f)

        return yaml_obj
