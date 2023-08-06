#!/usr/bin/env python
# -*- coding: utf-8 -*-

from convert2vars.app.app_impl import AppImpl
import click
import pathlib

base_path = (pathlib.Path(__file__)).parent.parent

__appname__ = 'convert2vars'
__version__ = '1.0.2'


@click.group(help='Load a template, embed the value of a variable, and output it.')
@click.option(
    '--config-file',
    '-c',
    type=str,
    metavar='CONFIG_FILE',
    default='',
    show_default=True,
    help='Specify a configuration file')
@click.option(
    '--debug/--no-debug',
    '-d',
    is_flag=True,
    metavar='DEBUG',
    default=False,
    show_default=True,
    help='Enable debug output (applies to standard output only)')
@click.pass_context
def cli(ctx, config_file, debug):
    ctx.obj['config_file'] = config_file
    ctx.obj['debug'] = debug
    ctx.obj['base_path'] = base_path


@cli.command(help='Embed and output the values of environment variables and various variables')
@click.option(
    '--vars',
    '-e',
    type=str,
    multiple=True,
    metavar='VARS',
    show_default=True,
    help='Specify a variable and its value (ex. -e var1=X -e var2=y)')
@click.option(
    '--use-environment',
    '-E',
    is_flag=True,
    metavar='USE_ENVIRONMENT',
    default=False,
    show_default=True,
    help='Specify whether environment variables are input or not')
@click.option(
    '--input-file',
    '-i',
    type=str,
    metavar='INPUT_FILE',
    default='',
    show_default=True,
    help='Specify parameter file name')
@click.option(
    '--output-file',
    '-o',
    type=str,
    metavar='OUTPUT_FILE',
    default='',
    show_default=True,
    help='Specify the name of the file to output (if not specified, output to standard output)')
@click.option(
    '--input-format',
    '-F',
    type=click.Choice(['ini', 'json', 'yaml'], case_sensitive=False),
    # metavar='FORMAT',
    default=None,
    show_default=True,
    help='Specify the format of the parameter file')
@click.option(
    '--section',
    '-S',
    type=str,
    metavar='PARAMETER_SECTION',
    default='DEFAULT',
    show_default=True,
    help='Specify section name for parameter file (valid only for ini files)')
@click.option(
    '--output-format',
    '-f',
    type=click.Choice(['json', 'yaml'], case_sensitive=False),
    # metavar='FORMAT',
    default='json',
    show_default=True,
    help='Specify format for output (valid only if template is not used)')
@click.option(
    '--template-file',
    '-t',
    type=str,
    metavar='TEMPLATE_FILE',
    default='',
    show_default=True,
    help='Specify the file name of the template to be used for output')
@click.option(
    '--dotenv-file',
    type=str,
    metavar='DOTENV_FILE',
    default='',
    show_default=True,
    help='Specify the name of the dotenv file to be used as an environment variable')
@click.pass_context
def convert(
        ctx, vars, use_environment, input_file, output_file,
        input_format, section, output_format, template_file, dotenv_file):

    ctx.obj['vars'] = vars
    ctx.obj['use_environment'] = use_environment
    ctx.obj['input_file'] = input_file
    ctx.obj['output_file'] = output_file
    ctx.obj['input_format'] = input_format
    ctx.obj['section'] = section
    ctx.obj['output_format'] = output_format
    ctx.obj['template_file'] = template_file
    ctx.obj['dotenv_file'] = dotenv_file
    AppImpl.app_convert(ctx)


def main():
    cli(obj={})
