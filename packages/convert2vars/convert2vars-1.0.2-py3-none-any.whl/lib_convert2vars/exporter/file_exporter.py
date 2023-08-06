# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

from convert2vars.formatter.yaml_formatter import YamlFormatter
from convert2vars.util.logging import Logging


__version__ = "1.0"


class FileExporter(object):
    @classmethod
    def export_resource(cls, parsed_data, app_config, logger):
        header = [u'# Gerarated by Squid ACL Generator for Office365 Sites']
        is_succeed = False

        url_acls = YamlFormatter.format(parsed_data['URL'],
                                        'URL', False, header, logger)

        url_output_text = "\n".join(url_acls)
        url_acl_file = app_config['working_acl_dir'] + \
            '/' + app_config['working_acl_host_file']
        url_write_result = FileExporter._export_file(
            url_acl_file, url_output_text, logger)
        if not url_write_result:
            return is_succeed

        ip_output_text = "\n".join(ip_acls)
        ip_acl_file = app_config['working_acl_dir'] + \
            '/' + app_config['working_acl_ip_file']
        ip_write_result = FileExporter._export_file(
            ip_acl_file, ip_output_text, logger)
        if not ip_write_result:
            return is_succeed

        is_succeed = True
        return is_succeed

    @classmethod
    def _export_file(cls, file_path, file_data, logger):
        Logging.info(
            logger, u"Squid ACLのエクスポート({0}): start".format(file_path))
        try:
            with open(file_path, "w") as f:
                f.write(file_data)
        except IOError:
            Logging.error(
                logger, u"Squid ACLの書き込みに失敗しました({0})".format(file_path))
            return False
        Logging.info(
            logger, u"Squid ACLのエクスポート({0}): end".format(file_path))
        return True
