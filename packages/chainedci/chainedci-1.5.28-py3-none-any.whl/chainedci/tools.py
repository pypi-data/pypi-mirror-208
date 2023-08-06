#!/usr/bin/env python3

"""Config and Logging usefull scripts and vars."""

import logging
import sys
from time import sleep
from chainedci.config import getConfig, config
from chainedci.parser import JinjaParser


def raise_ex(exception, message):
    """Raise an exception after logging it."""
    log = logging.getLogger('chainedci')
    log.critical(message)
    ini = getConfig('ini')
    if ini['log']['exception_or_exit']:
        raise exception(message)
    sys.exit(message)


def get_env_or_raise(env):
    """Return a env var or raise an exception."""
    ini = getConfig('ini')
    if env not in ini['env']:
        raise_ex(ValueError, f"Environmnent variable '{env}' MUST be set")
    return ini['env'][env]


def token_selector(url):
    """
    Return a token based on domain name.

    If no domain is found, return none.
    """
    log = logging.getLogger('chainedci')
    if 'tokens' not in config['defaults']:
        log.debug("token_selector - none found")
        return {}
    log.debug("token_selector - check in the %s token(s)",
              len(config['defaults']['tokens']))
    for token in config['defaults']['tokens']:
        log.debug("token_selector - check token '%s' with filter '%s'",
                  token['name'], token['filter'])
        if token['filter'] in url:
            log.debug("token_selector - it match")
            parser = JinjaParser()
            log.debug("token_selector - type of token value: %s",
                      type(str(parser.parse(token['value']))))

            token_name = str(token['id'])
            log.debug("token_selector - type of token key: %s",
                      type(token_name))
            return {token_name: str(parser.parse(token['value']))}
    log.debug("token_selector - none found")
    return {}


def waiting_cursor(sleep_time=15, micro_step=5, end=''):
    """
    Print a waiting cursor.

    :param sleep_time: time wainting in seconds
    :type sleep_time: int
    :param micro_step: time between a dot print in seconds
    :type micro_step: int
    """
    ini = getConfig('ini')
    if ini['log']['level'] == 'INFO':
        for elapsed in range(0, sleep_time):
            print_one_on(elapsed, micro_step)
            sleep(1)
        print('#', end=end, flush=True)
    else:
        sleep(sleep_time)


def print_one_on(index, micro_step, string='.', end=''):
    """
    Print a string only if index can be devided by micro_step.

    :param index: one index
    :type sleep_time: int
    :param micro_step: a step when we can print the string
    :type micro_step: int
    :param string: the string to print
    :type string: string
    :param end: end of line
    :type end: string
    """
    if index % micro_step == 0:
        print(string, end=end, flush=True)
