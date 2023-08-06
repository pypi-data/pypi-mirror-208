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
from convert2vars.exporter.file_exporter import FileExporter
from convert2vars.util.logging import Logging

__version__ = "1.0"


class AppHelper(object):
    # Const
    GENERATE_SUCCESS = 0

    @classmethod
    def generate_parameters(cls, runtime_config, logger):
        parameter_parsed = {}
        Logging.debug(logger, "AppHelper.{0}: start".format(
            sys._getframe().f_code.co_name))

        # 環境変数、カスタムパラメータを元にパラメータリストを作成
        parameters = cls._generate_parameters(runtime_config, logger)

        # パラメータファイル中のパラメータを置換
        if runtime_config['input_file'] != '':
            parameter_rendered = cls._generate_rendered(
                runtime_config['input_file'], parameters, logger)

            # パラメータ置換に失敗した場合は、例外をスロー
            if parameter_rendered is None:
                raise TemplateRenderError(cs.EXIT_ERR_RENDER_PARAMETER)

            # デバッグ出力
            Logging.debug(logger, "AppHelper.{0}: Rendered parametes({1})".format(
                sys._getframe().f_code.co_name, parameter_rendered))

            # パラメータファイルのフォーマット判定
            cls._detect_input_format(runtime_config)

            # パラメータファイルの内容をパース
            parameter_parsed = cls._parse_parameter_file(
                runtime_config, parameter_rendered, logger)
        
            # デバッグ出力
            Logging.debug(logger, "AppHelper.{0}: Rendered parametes({1})".format(
                sys._getframe().f_code.co_name, parameter_parsed))
        else:
            parameter_parsed = parameters

        # 改行コードを統一
        # cls._post_generate_config(config, config['output_file'], logger)

        Logging.debug(logger, "AppHelper.{0}: end".format(
            sys._getframe().f_code.co_name))
        return parameter_parsed

    @classmethod
    def _detect_input_format(cls, runtime_config):
        # 明示的にパラメータファイルのフォーマットを指定していない場合、ファイルの拡張子を元に判定
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
            # テンプレートファイルのロード
            tmpl = TemplateLoader.load(template_path, 'utf8', logger)
            if tmpl is None:
                Logging.error(logger,
                              u"処理に失敗したため、異常終了しました(STATUS/{0})".format(cs.EXIT_ERR_LOAD_TEMPLATE))
                return None

            # テンプレートのパラメータ置換
            return TemplateRender.render(tmpl, parameters, logger)
        except Exception as e:
            raise e

    @classmethod
    def _generate_parameters(cls, runtime_config, logger):
        parameters = {}
        Logging.debug(logger, "AppHelper.{0}: start".format(
            sys._getframe().f_code.co_name))

        # 環境変数をパラメータとして利用する場合、パラメータリストに追加
        if runtime_config['use_environment']:
            parameters.update(dict(os.environ))

        # カスタムパラメータが指定された場合、パラメータリストに追加
        if runtime_config['vars']:
            for custom_var in runtime_config['vars']:
                key_value = custom_var.split('=')
                if len(key_value) == 2:
                    parameters.update({key_value[0]: key_value[1]})

        # パラメータファイルを指定していない場合、Json形式の構造化された値をパースする
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
            # iniファイルとして、パース
            return IniParser.parse(
                runtime_config, parameter_rendered, logger)
        elif runtime_config['input_format'] == 'json':
            # jsonファイルとして、パース
            return JsonParser.parse(
                runtime_config, parameter_rendered, logger)
        elif runtime_config['input_format'] == 'yaml':
            # yamlファイルとして、パース
            return YamlParser.parse(
                runtime_config, parameter_rendered, logger)
        else:
            return None

    @classmethod
    def generate_converted_with_template(cls, runtime_config, parameters, logger):
        # テンプレートファイルのロード
        tmpl = TemplateLoader.load(
            runtime_config['template_file'], 'utf8', logger)
        if tmpl is None:
            raise TemplateLoadError(cs.EXIT_ERR_LOAD_TEMPLATE)

        # テンプレート中のパラメータを置換
        converted_rendered = TemplateRender.render(tmpl, parameters, logger)
        if converted_rendered is None:
            raise TemplateRenderError(cs.EXIT_ERR_RENDER_TEMPLATE)

        return converted_rendered

    @classmethod
    def generate_converted_without_template(cls, runtime_config, parameters, logger):
        # 出力フォーマットに応じて整形
        if runtime_config['output_format'] == 'json':
            return JsonFormatter.format(parameters, logger)
        elif runtime_config['output_format'] == 'yaml':
            return YamlFormatter.format(parameters, logger)
        else:
            return None
