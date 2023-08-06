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

import string
import random
from chainedci.config import getConfig, init_ini
from chainedci.log import log

'''
Tests library.
'''


def force_ini_values():
    init_ini()
    ini = getConfig('ini')
    ini['log']['level'] = 'DEBUG'
    ini['log']['deprecation_warning'] = True
    ini['log']['exception_or_exit'] = True
    log.setLevel('DEBUG')


def fake_token_selector(url):
    return {'TOKEN_VAR_NAME': 'TOKEN_VALUE'}


def rand_str(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def clean_secrets():
    ini = getConfig('ini')
    ini.dl._vault.secrets = []
