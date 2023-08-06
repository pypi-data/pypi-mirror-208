#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import click
import pathlib

base_path = (pathlib.Path(__file__)).parent.parent
from convert2vars.app.app_impl import AppImpl

__appname__ = 'convert2vars'
__version__ = '1.0.0'


@click.group(help=u'テンプレートを読み込み、環境変数や任意の変数の値を埋め込んで出力する')
@click.option(
    '--config-file',
    '-c',
    type=str,
    metavar='CONFIG_FILE',
    # default=str(base_path) + '/config/convert2vars.yml',
    default='',
    show_default=True,
    help=u'設定ファイルを指定する')
@click.option(
    '--debug/--no-debug',
    '-d',
    is_flag=True,
    metavar='DEBUG',
    default=False,
    show_default=True,
    help=u'デバッグ出力を有効にする(標準出力のみ適用)')
@click.pass_context
def cli(ctx, config_file, debug):
    ctx.obj['config_file'] = config_file
    ctx.obj['debug'] = debug
    ctx.obj['base_path'] = base_path

@cli.command(help=u'環境変数や任意の変数の値を埋め込んで出力する')
@click.option(
    '--vars',
    '-e',
    type=str,
    multiple=True,
    metavar='VARS',
    show_default=True,
    help=u'変数とその値を指定する（ex. -e var1=X -e var2=y）')
@click.option(
    '--use-environment',
    '-E',
    is_flag=True,
    metavar='USE_ENVIRONMENT',
    default=False,
    show_default=True,
    help=u'環境変数を入力とするかどうかを指定する')
@click.option(
    '--input-file',
    '-i',
    type=str,
    metavar='INPUT_FILE',
    default='',
    show_default=True,
    help=u'パラメータファイル名を指定する')
@click.option(
    '--output-file',
    '-o',
    type=str,
    metavar='OUTPUT_FILE',
    default='',
    show_default=True,
    help=u'出力するファイル名を指定する（指定しない場合は、標準出力に出力する）')
@click.option(
    '--input-format',
    '-F',
    type=click.Choice(['ini', 'json', 'yaml'], case_sensitive=False),
    # metavar='FORMAT',
    default=None,
    show_default=True,
    help=u'パラメータファイルのフォーマットを指定する')
@click.option(
    '--section',
    '-S',
    type=str,
    metavar='PARAMETER_SECTION',
    default='DEFAULT',
    show_default=True,
    help=u'パラメータファイルのセクション名を指定する')
@click.option(
    '--output-format',
    '-f',
    type=click.Choice(['json', 'yaml'], case_sensitive=False),
    # metavar='FORMAT',
    default='json',
    show_default=True,
    help=u'出力する際のフォーマットを指定する(テンプレートを利用しない場合のみ有効)')
@click.option(
    '--template-file',
    '-t',
    type=str,
    metavar='TEMPLATE_FILE',
    default='',
    show_default=True,
    help=u'出力する際に利用するテンプレートのファイル名を指定する')
@click.pass_context
def convert(
    ctx, vars, use_environment, input_file, output_file,
    input_format, section, output_format, template_file):

    ctx.obj['vars'] = vars
    ctx.obj['use_environment'] = use_environment
    ctx.obj['input_file'] = input_file
    ctx.obj['output_file'] = output_file
    ctx.obj['input_format'] = input_format
    ctx.obj['section'] = section
    ctx.obj['output_format'] = output_format
    ctx.obj['template_file'] = template_file
    AppImpl.app_convert(ctx)

def main():
    cli(obj={})

#if __name__ == '__main__':
#    main()
