#!/usr/bin/env python3

"""Simple Jinja-like parser."""

import re
import logging
from chainedci.config import getConfig


class JinjaParser():
    """Ultra light ansible jinja parser."""

    def __init__(self):
        """Prepare the regex."""
        # pylint: disable=anomalous-backslash-in-string
        self.re_tag = re.compile(".*\\{\\{(.*?)\\}\\}.*")
        # pylint: disable=anomalous-backslash-in-string
        self.re_lookup = re.compile(
            "\\s*lookup\\(\\s*'env'\\s*,\\s*'(.*?)'\\s*\\)")
        # pylint: disable=anomalous-backslash-in-string
        self.re_default = re.compile("\\s*default\\(\\s*'(.*?)'\\s*")

    def parse(self, data, hide_value=False):
        """
        Parse the string.

        :param data: The String to parse
        :type data: string
        :param hide_value: Hide the replaced value
        :type hide_value: boolean
        :return: the string with replaced part
        :rtype: string
        """
        if isinstance(data, str):
            while self.re_tag.match(data):
                log = logging.getLogger('chainedci')
                log.debug("JinjaParser - Complex variable found in '%s'", data)
                matchs = self.re_tag.findall(data)
                for expr in matchs:
                    data = data.replace("{{" + expr + "}}",
                                        str(self.parse_expr(expr, log, hide_value)))
        return data

    def parse_expr(self, expr, log, hide_value):
        """
        Parse one expression.

        :param expr: The epxression to parse
        :type expr: string
        :param log: The logging of object
        :type log: logging
        :param hide_value: Hide the replaced value
        :type hide_value: boolean
        :return: replacement of the expression
        :rtype: string
        """
        ret = ''
        log.debug("JinjaParser - Try to parse '%s'", expr)
        expr_parts = expr.split('|')
        for part in expr_parts:
            if self.re_lookup.match(part):
                ret = self.lookup_env(part, hide_value)
            elif self.re_default.match(part):
                ret = self.default(ret, part, hide_value)
            else:
                raise ValueError(f'Can not parse {part} in {expr}')
        return ret

    def lookup_env(self, part, hide_value=False):
        """
        Lookup for variable in env variables.

        :param part: the lookup('env', 'var') part
        :type part: string
        :param hide_value: Hide the replaced value
        :type hide_value: boolean
        :return: the replaced string
        :rtype: string
        """
        ini = getConfig('ini')
        log = logging.getLogger('chainedci')
        log.debug("JinjaParser - Match lookup in '%s'", part)
        matchs = self.re_lookup.findall(part)
        if matchs[0] in ini['env']:
            log.debug("JinjaParser - Match lookup replace with '%s'",
                      '*****' if hide_value else ini['env'][matchs[0]])
            return ini['env'][matchs[0]]
        log.debug("JinjaParser - No value found, set to ''")
        return ''

    def default(self, prev, part, hide_value=False):
        """
        Set default value.

        :param prev: the default('value', ) part
        :type prev: the previous value
        :param part: the lookup('env', 'var') part
        :type part: string
        :param hide_value: Hide the replaced value
        :type hide_value: boolean
        :return: the replaced string
        :rtype: string
        """
        log = logging.getLogger('chainedci')
        log.debug("JinjaParser - Match default in '%s'", part)
        matchs = self.re_default.findall(part)
        if prev == '' or prev is None:
            log.debug("JinjaParser - set value to default '%s'",
                      '*****' if hide_value else matchs[0])
            return matchs[0]
        return prev
