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
"""Inventory module."""


from os import path
from ansible.inventory.manager import InventoryManager
from ansible.module_utils._text import to_bytes
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import VaultSecret
from chainedci.config import Config, getConfig
from chainedci.log import log, add_tokens_to_log_filter


class Inventory():
    """Inventory object."""

    def __init__(self, inventory_file):
        """Init Inventory."""
        self.config = None
        self.inventory_file = inventory_file
        self.get_inventory_manager()
        self.scenario_name = None
        self.job = None

    def load(self, scenario_name, job_name):
        """Load inventory files and hide tokens."""
        self.scenario_name = scenario_name
        self.job = job_name
        self.load_config(scenario_name, job_name)
        run = getConfig('run')
        add_tokens_to_log_filter(self.config, [run.get('key')])
        config = getConfig('chainedci')
        config.update_key(self.config)

    def get_inventory_manager(self, key_id='default'):
        """Load ansible inventory manager."""
        # all needs loader
        loader = DataLoader()
        run = getConfig('run')

        if run.get('key'):
            secret = [(key_id,
                       VaultSecret(to_bytes(run['key'], encoding='utf-8')))]
            loader.set_vault_secrets(secret)

        self.inventory = InventoryManager(loader=loader,
                                          sources=[self.inventory_file])

    def load_config(self, scenario_name, job_name):
        """Load all config files depending on inventory file."""
        self.config = Config(load_env=False, init_scenarios=True)
        self.load_vault_key()

        # load configs
        host = self.inventory.hosts[scenario_name]
        inv_folder = host.vars['inventory_dir']
        self.load_groups(inv_folder, host)
        self.load_host_file(inv_folder, host)

        # set some run param in run config
        run = getConfig('run')
        run['name'] = scenario_name
        run['job'] = job_name
        self.config.simplify()

    def load_groups(self, inv_folder, host):
        """Load group files."""
        groups_to_load = host.get_groups()
        all_file = f"{inv_folder}/group_vars/all.yml"
        log.info('Load global group file "%s"', all_file)
        self.config.load_file(all_file, 'defaults')
        for grp in groups_to_load:
            if grp.name not in ['ungrouped', 'all']:
                self.load_group(inv_folder, grp.name)

    def load_group(self, inv_folder, group_name):
        """Load a group file."""
        file = f"{inv_folder}/group_vars/{group_name}.yml"
        if path.exists(file):
            log.info('Load group file "%s"', file)
            self.config.merge(file, 'defaults')
        else:
            log.info('No group file "%s"', file)

    def load_host_file(self, inv_folder, host):
        """Load host file."""
        host_file = f"{inv_folder}/host_vars/{host.name}.yml"
        log.info('Load scenario file "%s"', host_file)
        self.config.load_file(host_file, f'scenarios.{host.name}')

    def load_vault_key(self):
        """Load vault key if needed."""
        run = getConfig('run')
        if run.get('key'):
            log.debug('load vault key')
            self.config.set_vault_key(run['key'])
        else:
            self.config.clean_vault_keys()

    @property
    def scenarios(self):
        """List hosts extracted from inventory."""
        return self.inventory.hosts
