#!/usr/bin/env python3

"""Logging functions and vars."""

import logging
import sys
from chainedci.config import getConfig
from chainedci.parser import JinjaParser
from chainedci.tools import raise_ex


def init_log(ini):
    """Config the default logging."""
    console_handler = logging.StreamHandler(sys.stdout)
    log_handlers = [console_handler]
    if ini['log']['file']:
        file_handler = logging.FileHandler(ini['log']['file']['name'])
        log_handlers.append(file_handler)
    logging.basicConfig(format=ini['log']['format'],
                        handlers=log_handlers,
                        level=ini['log']['level'])


def deprecation_warning(msg):
    """Print a deprecation message."""
    ini = getConfig('ini')
    if ini['log']['deprecation_warning']:
        log.warning("DEPRECATION: %s", msg)
        print(f"DEPRECATION: {msg}")


class TokenFilter(logging.Filter):
    """Logging filter to avoid token leaking."""

    def __init__(self, patterns):
        """
        Init with a list of patterns to hide.

        :param patterns: Patterns to hide
        :type patterns: list
        """
        super().__init__()
        self._patterns = patterns

    def filter(self, record):
        """Filter the message."""
        record.msg = self.redact(record.msg)
        if isinstance(record.args, dict):
            for k in record.args.keys():
                record.args[k] = self.redact(record.args[k])
        else:
            record.args = tuple(self.redact(arg) for arg in record.args)
        return True

    def redact(self, msg):
        """Replace patterns with a message."""
        msg = msg if isinstance(msg, str) else str(msg)
        for pattern in self._patterns:
            if isinstance(pattern, (bytes, bytearray)):
                pattern = pattern.decode("utf-8")
            msg = msg.replace(pattern, "__HIDDEN__")
        return msg


def add_tokens_to_log_filter(conf, additional_tokens=None):
    """
    Add all tokens to the log filter.

    This will fetch all tokens in all.yml and add them to log filter.
    Token from env vars can be added by setting the list of the vars setting
    the param additional_env_tokens_names.

    If the values of one of the tokens is empty it will raise an exception.

    :param conf: a config object
    :type conf: Config object
    :param additional_tokens: the list of tokens to hide
    :type additional_tokens: list of string
    """
    ini = getConfig('ini')
    if not ini['log']['hide_tokens']:
        log.info("NO filter added to the log system due to log/hide_tokens "
                 "bypass")
        return
    log.info("Add filters to the log system")
    token_list = []
    # Add global tokens to filters
    if 'defaults' in conf:
        if 'tokens' in conf['defaults']:
            for token in conf['defaults']['tokens']:
                log.debug("add_tokens_to_log_filter - Add %s to token log "
                          "filter", token['name'])
                parser = JinjaParser()
                token_value = parser.parse(token['value'], True)
                if token_value == '':  # nosec B105
                    raise_ex(ValueError, f"Please set a value for token "
                                         f"{token['name']} in config file "
                                         "all.yml")
                log.debug("add_tokens_to_log_filter - type of token value: %s",
                          type(token_value))
                token_list.append(token_value)
        # Add project tokens to filters
        if 'gitlab' in conf['defaults']:
            for project_name in conf['defaults']['gitlab']['git_projects']:
                project = conf['defaults']['gitlab']['git_projects'][
                    project_name]
                if 'trigger_token' in project:
                    parser = JinjaParser()
                    token_value = parser.parse(str(project['trigger_token']),
                                               True)
                    if token_value == '':  # nosec B105
                        raise_ex(ValueError,
                                 "Please set a value for 'trigger_token' "
                                 f"of project {project_name} in config "
                                 "file all.yml")
                    log.debug("add_tokens_to_log_filter - Add project '%s' "
                              "trigger_token to token log filter",
                              project_name)
                    token_list.append(token_value)
    # Add additional tokens
    for token in additional_tokens or []:
        log.debug("add_tokens_to_log_filter - "
                  "Add additional token to log filter")
        token_list.append(token)
    log.addFilter(TokenFilter(token_list))


# pylint: disable=invalid-name
log = logging.getLogger('chainedci')
