# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

from convert2vars.util.logging import Logging

__version__ = "1.0"


class GenericAppError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return "{0} (STATUS/{1})".format(self.message, self.status_code)


class TemplateLoadError(GenericAppError):
    def __init__(self, status_code):
        super(TemplateLoadError, self).__init__(status_code)
        self.message = "テンプレートファイルのロードに失敗"


class TemplateRenderError(GenericAppError):
    def __init__(self, status_code):
        super(TemplateRenderError, self).__init__(status_code)
        self.message = "テンプレートのレンダリング処理に失敗"


class ParameterLoadError(GenericAppError):
    def __init__(self, status_code):
        super(ParameterLoadError, self).__init__(status_code)
        self.message = "テンプレートファイルのロードに失敗"


class ParameterFileWriteError(GenericAppError):
    def __init__(self, status_code):
        super(ParameterFileWriteError, self).__init__(status_code)
        self.message = "パラメータファイルの書き込み処理に失敗"


class ConvertedFileExportError(GenericAppError):
    def __init__(self, status_code):
        super(ConvertedFileExportError, self).__init__(status_code)
        self.message = "変換済みファイルの出力に失敗"
