# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

from convert2vars.util.logging import Logging

__version__ = "1.0"


class ParameterRender(object):
    @classmethod
    def render(cls, template, parameters, logger):
        Logging.info(logger, u"パラメータファイルを生成")

        try:
            rendered = template.render(parameters)
        except Exception as e:
            Logging.error(
                logger, u"パラメータファイルの生成に失敗しました")
            Logging.error(logger, u"例外クラス: {0}".format(type(e)))
            Logging.error(logger, u"ARGS: {0}".format(e.args))
            Logging.debug(logger, u"例外詳細: {0}".format(e.message))
            return None

        Logging.info(logger, u"パラメータファイルを生成: 成功")
        return rendered
