#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2019 Orange
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Chained CI environment variables wrapper."""

import os
import re
import logging


class EnvVars(dict):
    """Class to access environment variables."""

    def __init__(self, load=True):
        """
        Show Environmnent variable as a dict with object access.

        :param load: Load or not env vars at init
        :type load: boolean
        :return: a EnvVars object
        :rtype: EnvVars class

        >>> env = EnvVars()
        >>> env['PATH']
        '.../usr/bin:...'
        >>> env.PATH
        '.../usr/bin:...'
        >>> env
        {...'PATH': .../usr/bin:...}
        >>> 'HOME' in env
        True
        >>> 'Zorglub' in env
        False
        >>> env.PATH
        '.../usr/bin:...'
        """
        if load:
            super().__init__(dict(os.environ))
        else:
            super()

    def eval(self, condition):
        """
        Eval a condition string on the environment vars.

        :param condition: The condition to eval
            The condition can be:
            - a variable presence check: 'VAR_NAME'
            - an equality: 'VAR_NAME == VALUE'
            - a difference: 'VAR_NAME != VALUE'
            - a test the value is in a list 'VAR_NAME in [VAL1, VAL2]'
            In any case, if the variable does not exists, the result is false.
        :type condition: string
        :return: the eval result
        :rtype: boolean

        >>> env = EnvVars()
        >>> env['USER']
        johndoe
        >>> env.eval('USER')
        True
        >>> env.eval('USER == johndoe')
        True
        >>> env.eval('USER == janedoe')
        False
        >>> env.eval('USER != janedoe')
        True
        >>> env.eval('USER in [johndoe, janedoe]')
        True
        >>> env.eval('USER in [janedoe, bobdoe]')
        False
        """
        log = logging.getLogger('chainedci')
        if all(sep not in condition for sep in [' ', '=']):
            ret = condition in self
            log.debug('env_condition_parser - check if %s in env -> %s',
                      condition, ret)
        elif '=' in condition:
            (var, equ, val) = re.findall(r'^(.*[^\s])\s*([=\!]=)\s*([^\s].*)$',
                                         condition)[0]
            if var not in self:
                log.debug('env_condition_parser - %s not in env -> %s',
                          var, False)
                return False
            ret = (self[var] == val) if (equ == '==') else (self[var] != val)
            log.debug('env_condition_parser - eval equality '
                      '"%s" %s "%s" -> %s', var, equ, val, ret)
        elif ' in ' in condition:
            (var, val) = re.findall(r'^(.*[^\s])\s* in '
                                    r'\s*\[\s*([^\s].*[^\s])\s*\]$',
                                    condition)[0]
            val = re.sub(r'\s*,\s*', ',', val).split(',')
            if var not in self:
                log.debug('env_condition_parser - %s not in env -> %s',
                          var, False)
                return False
            ret = self[var] in val
            log.debug('env_condition_parser - eval '
                      '"%s" in %s -> %s', var, val, ret)
        else:
            log.warning('condition not parsed: %s', condition)
            ret = False
        return ret
