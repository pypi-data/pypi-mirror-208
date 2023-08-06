# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import sys

from convert2vars.app.app_exception import *
from convert2vars.app.constants import Constants as cs
from convert2vars.template.template_loader import TemplateLoader
from convert2vars.template.template_render import TemplateRender
from convert2vars.parser.ini_parser import IniParser
from convert2vars.parser.json_parser import JsonParser
from convert2vars.parser.yaml_parser import YamlParser
from convert2vars.parser.parse_helper import ParseHelper
from convert2vars.formatter.json_formatter import JsonFormatter
from convert2vars.formatter.yaml_formatter import YamlFormatter
from convert2vars.util.logging import Logging


class AppHelper(object):
    # Const
    GENERATE_SUCCESS = 0

    @classmethod
    def generate_parameters(cls, runtime_config, logger):
        parameter_parsed = {}
        Logging.debug(logger, "AppHelper.{0}: start".format(
            sys._getframe().f_code.co_name))

        # Create parameter lists based on environment variables and custom parameters
        parameters = cls._generate_parameters(runtime_config, logger)

        # Replace parameters in parameter file
        if runtime_config['input_file'] != '':
            parameter_rendered = cls._generate_rendered(
                runtime_config['input_file'], parameters, logger)

            # Throws exception if parameter substitution fails
            if parameter_rendered is None:
                raise TemplateRenderError(cs.EXIT_ERR_RENDER_PARAMETER)

            # debug output
            Logging.debug(logger, "AppHelper.{0}: Rendered parametes({1})".format(
                sys._getframe().f_code.co_name, parameter_rendered))

            # Parameter file format determination
            cls._detect_input_format(runtime_config)

            # Parse the contents of the parameter file
            parameter_parsed = cls._parse_parameter_file(
                runtime_config, parameter_rendered, logger)

            # debug output
            Logging.debug(logger, "AppHelper.{0}: Rendered parametes({1})".format(
                sys._getframe().f_code.co_name, parameter_parsed))
        else:
            parameter_parsed = parameters

        Logging.debug(logger, "AppHelper.{0}: end".format(
            sys._getframe().f_code.co_name))
        return parameter_parsed

    @classmethod
    def _detect_input_format(cls, runtime_config):
        # If the format of the parameter file is not explicitly specified,
        # the decision is based on the file extension
        if runtime_config['input_format'] is None:
            file_ext = os.path.splitext(runtime_config['input_file'])
            if file_ext[1][1:] == 'ini':
                runtime_config['input_format'] = 'ini'
            elif file_ext[1][1:] == 'json':
                runtime_config['input_format'] = 'json'
            elif file_ext[1][1:] == 'yaml' or file_ext[1][1:] == 'yml':
                runtime_config['input_format'] = 'yaml'

    @classmethod
    def _generate_rendered(cls, template_path, parameters, logger):
        try:
            # Load template files
            tmpl = TemplateLoader.load(template_path, 'utf8', logger)
            if tmpl is None:
                Logging.error(logger,
                              "Abnormal termination due to processing failure(STATUS/{0})".format(cs.EXIT_ERR_LOAD_TEMPLATE))
                return None

            # Template Parameter Substitution
            return TemplateRender.render(tmpl, parameters, logger)
        except Exception as e:
            raise e

    @classmethod
    def _generate_parameters(cls, runtime_config, logger):
        parameters = {}
        Logging.debug(logger, "AppHelper.{0}: start".format(
            sys._getframe().f_code.co_name))

        # If environment variables are used as parameters, add them to the parameter list
        if runtime_config['use_environment']:
            parameters.update(dict(os.environ))

        # If custom parameters are specified, add them to the parameter list
        if runtime_config['vars']:
            for custom_var in runtime_config['vars']:
                key_value = custom_var.split('=')
                if len(key_value) == 2:
                    parameters.update({key_value[0]: key_value[1]})

        # Parses structured values in Json format if no parameter file is specified
        if runtime_config['input_file'] == '':
            parameters = ParseHelper.parse_values(parameters, logger)

        Logging.debug(logger, "AppHelper.{0}: parameters¥n{1}".format(
            sys._getframe().f_code.co_name, parameters))

        Logging.debug(logger, "AppHelper.{0}: end".format(
            sys._getframe().f_code.co_name))
        return parameters

    @classmethod
    def _parse_parameter_file(cls, runtime_config, parameter_rendered, logger):
        if runtime_config['input_format'] == 'ini':
            # As an ini file, parse
            return IniParser.parse(
                runtime_config, parameter_rendered, logger)
        elif runtime_config['input_format'] == 'json':
            # As an JSON file, parse
            return JsonParser.parse(
                runtime_config, parameter_rendered, logger)
        elif runtime_config['input_format'] == 'yaml':
            # As an YAML file, parse
            return YamlParser.parse(
                runtime_config, parameter_rendered, logger)
        else:
            return None

    @classmethod
    def generate_converted_with_template(cls, runtime_config, parameters, logger):
        # Load template files
        tmpl = TemplateLoader.load(
            runtime_config['template_file'], 'utf8', logger)
        if tmpl is None:
            raise TemplateLoadError(cs.EXIT_ERR_LOAD_TEMPLATE)

        # Replace parameters in the template
        converted_rendered = TemplateRender.render(tmpl, parameters, logger)
        if converted_rendered is None:
            raise TemplateRenderError(cs.EXIT_ERR_RENDER_TEMPLATE)

        return converted_rendered

    @classmethod
    def generate_converted_without_template(cls, runtime_config, parameters, logger):
        # Formatted according to output format
        if runtime_config['output_format'] == 'json':
            return JsonFormatter.format(parameters, logger)
        elif runtime_config['output_format'] == 'yaml':
            return YamlFormatter.format(parameters, logger)
        else:
            return None
