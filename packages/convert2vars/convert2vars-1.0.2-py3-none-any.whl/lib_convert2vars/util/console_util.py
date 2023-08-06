# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import click

__version__ = "1.0"


class ConsoleUtil(object):
    @classmethod
    def print_diffs(cls, diffs, diff_stat):
        modified_files = 0
        modified_file_names = []
        added_lines = 0
        deleted_lines = 0

        click.secho("変更差分:", fg='blue', bold=True)

        if type(diffs) is str:
            diffs_list = diffs.split('\n')
            for diff in diffs_list:
                ConsoleUtil._print_diff_color(diff)
        elif type(diffs) is list:
            print('x')
            for diff in diffs:
                diffs_list = diff.split('\n')
                for diff2 in diffs_list:
                    ConsoleUtil._print_diff_color(diff2)
        ConsoleUtil._print_diff_stat(diff_stat)

    @classmethod
    def _print_diff_color(cls, message):
        if message.startswith('+++'):
            click.secho(message, fg='yellow')
        elif message.startswith('---'):
            click.secho(message, fg='yellow')
        elif message.startswith('+'):
            click.secho(message, fg='green')
        elif message.startswith('-'):
            click.secho(message, fg='red')
        elif message.startswith('diff --git '):
            click.secho(message, fg='yellow')
        else:
            click.echo(message)

    @classmethod
    def _print_diff_stat(cls, diff_stat):
        click.echo('\n==========================================')
        click.secho("変更概要", bg='black', fg='blue', bold=True)
        click.echo(diff_stat)

    @classmethod
    def confirm_key_input(cls, prompt1, prompt2=''):
        click.secho(prompt1, fg='blue', bold=True)
        click.secho(prompt2, fg='blue', bold=True)
        click.getchar()
