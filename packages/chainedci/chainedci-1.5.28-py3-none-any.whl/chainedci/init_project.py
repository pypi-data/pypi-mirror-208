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
"""Init_project module."""

import os
import re
import shutil
import pkg_resources
import git
from jinja2 import Environment, FileSystemLoader
from chainedci.config import getConfig
from chainedci.log import log


def init_project():
    """Init the chainedci structure."""
    ini = getConfig('ini')
    sc_folder = ini['init']['tree']['scenarios']['folder']
    cf_folder = ini['init']['tree']['config']
    create_folders(sc_folder, cf_folder)
    create_all_file(sc_folder)
    create_static_files(sc_folder, cf_folder)


def create_folders(sc_folder, cf_folder):
    """Create chained-ci folders."""
    ini = getConfig('ini')
    folders = [
        f"{sc_folder}",
        f"{sc_folder}/{ini['init']['tree']['scenarios']['group']}",
        f"{sc_folder}/{ini['init']['tree']['scenarios']['definitions']}",
        f"{cf_folder}",
        f"{cf_folder}/{ini['artifacts']['certificates']['src']}",
        f"{cf_folder}/{ini['artifacts']['ssh_creds']['src']}",
        f"{cf_folder}/{ini['artifacts']['pdfidf']['src']}",
        f"{cf_folder}/{ini['artifacts']['ssh_access']['src']}",
        f"{cf_folder}/{ini['artifacts']['static']['src']}",
    ]
    for folder in folders:
        log.info('create folder %s', folder)
        os.makedirs(folder, exist_ok=True)


def create_all_file(sc_folder):
    """Create all.yml configuration."""
    ini = getConfig('ini')
    file_loader = FileSystemLoader(
        pkg_resources.resource_filename('chainedci', 'templates/'))
    env = Environment(autoescape=True, loader=file_loader)
    ci_template = env.get_template('all.yml.tpl')
    remote = git.Repo('.').remotes['origin'].url
    match = re.search(r'.*@(.*):(.*)\.git', remote)
    # SET_PROJECT_TRIGGER_IF_NEEDED is a placeholder
    output = ci_template.render( # nosec B106
        current_chained_ci_version='master',
        project_long_name=match.group(2).replace('/', '_'),
        gitlab_server=match.group(1),
        config_step=ini['specific_steps']['config'],
        config_path=ini['init']['tree']['config'],
        trigger_step=ini['specific_steps']['trigger_myself'],
        trigger_token='SET_PROJECT_TRIGGER_IF_NEEDED',
        example_project='/'.join(match.group(2).split('/')[:-1])+'/project_A'
    )
    filename = (f"{sc_folder}/{ini['init']['tree']['scenarios']['group']}"
                "/all.yml")
    with open(filename, 'w', encoding="utf-8") as all_file:
        all_file.write(output)
        log.info("Write projects file to '%s'", filename)


def create_static_files(sc_folder, cf_folder):
    """Create static init files."""
    ini = getConfig('ini')
    root = pkg_resources.resource_filename('chainedci', 'static/')
    shutil.copyfile(f"{root}/projectA.yml",
                    (f"{sc_folder}/"
                     f"{ini['init']['tree']['scenarios']['definitions']}"
                     "/projectA.yml"))
    shutil.copyfile(f"{root}/inventory",
                    (f"{sc_folder}"
                     "/inventory"))
    shutil.copyfile(f"{root}/projectA_config1.yml",
                    (f"{cf_folder}/{ini['artifacts']['pdfidf']['src']}"
                     "/projectA_config1.yml"))
    shutil.copyfile(f"{root}/projectA_config2.yml",
                    (f"{cf_folder}/{ini['artifacts']['pdfidf']['src']}"
                     "/projectA_config2.yml"))
