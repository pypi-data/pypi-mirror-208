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
"""Options module."""


import argparse
import textwrap
from os import path
from chainedci.log import log, deprecation_warning
from chainedci.tools import raise_ex
from chainedci.config import getConfig
from chainedci.version import __version__


class Options():
    """Get options from args."""

    def __init__(self):
        """Init Inventory."""
        self.get_options()
        self.check_options()
        self.check_required_parameters()

    def get_options(self):
        """Define and parse the command line arguments."""
        description = textwrap.dedent(f'''\
            chainedci {__version__}
            ---------------------------

                Mode: 'run'
                Prepare and trigger a specific step of a chainedci scenario.
                Parameters are backward compatible with legacy ansible version.
                Required parameters: '--scenario', '--job', '--inventory'

                Mode: 'generate'
                Prepare a .gitlab-ci.yml file from inventory
                Required parameters: '--inventory'

                Mode: 'init'
                Init the chained-ci project structure
                Required parameters: None

            ''')
        parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('mode',
                            help="mode in 'run', 'generate'",
                            choices=['run', 'generate', 'init'])
        parser.add_argument('-i', '--inventory',
                            dest='inventory',
                            help="inventory of scenarios")
        parser.add_argument('-s', '--scenario', '-l', '--limit',
                            dest='scenario_name',
                            help="limit inventory to one scenario")
        parser.add_argument('-j', '--job',
                            dest='job',
                            help="job name to execute")
        parser.add_argument('-p', '--vault-password-file',
                            help="path to the ansible vault password file",
                            dest='vault_password_file')
        parser.add_argument('-e', '--extra_vars',
                            help="backward compatible argument, please use "
                                 "--job parameter. This parameter must be "
                                 "formatted like this: 'step=xxxxx'")
        self.opts = parser.parse_args()

    def check_options(self):
        """
        Check all arguments.

        - ensure retro-compatibility
        - check file presence
        """
        # Check job parameter in case of retrocompatibility
        if self.opts.mode == 'run':
            if not self.opts.job:
                if 'step=' not in (self.opts.extra_vars or ''):
                    raise_ex(ValueError, "Please set --job parameter or "
                             "--extra_vars parameter with "
                             "'step=xxxx' "
                             "value")
                else:
                    extra = self.opts.extra_vars.split("=")
                    self.opts.job = extra[1]
                    deprecation_warning("Please consider using option --job "
                                        "to replace '-e step=xxx' parameter")
        # store vault key if exists
        self.store_vault_key()
        # crash if inventory does not exists in run or generate mode
        if (self.opts.mode in ['generate', 'run'] and
                not path.exists(self.opts.inventory)):
            raise_ex(ValueError, f"Inventory file '{self.opts.inventory}' "
                                 "does not exists.")

    def store_vault_key(self):
        """Store vault key in 'run' config."""
        ini = getConfig('ini')
        run = getConfig('run')
        if self.opts.vault_password_file:
            if not path.exists(self.opts.vault_password_file):
                raise_ex(ValueError, "Vault password file "
                                     f"'{self.opts.vault_password_file}' "
                                     "does not exists.")
            with open(self.opts.vault_password_file,
                      encoding="utf-8") as vault_file:
                content = vault_file.readlines()
                run['key'] = content[0].rstrip().encode("utf-8")
                log.warning("Vault password set with file %s",
                            self.opts.vault_password_file)
        elif ini['encryption']['key_env_name'] in ini['env']:
            log.warning("Vault password set with ENV VAR")
            run['key'] = ini['env'][ini['encryption']
                                    ['key_env_name']].encode("utf-8")
        else:
            log.warning("No vault password is set, assume all the "
                        "configuration is readable without ansible vault")

    def check_required_parameters(self):
        """Check parameters depending on 'mode'."""
        if self.opts.mode == 'run':
            if (not self.opts.job
                    or not self.opts.scenario_name):
                raise_ex(ValueError, "'Run' mode requires following "
                                     "parameters: '--scenario', "
                                     "'--job', and '--inventory'")
