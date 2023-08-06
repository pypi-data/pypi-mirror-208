#!/usr/bin/env python3

"""Chained CI config wrapper."""

import sys
from schema import Schema, Or, Optional
from chainedci.tools import raise_ex
from chainedci.log import log
from chainedci.step import Step
from chainedci.config import config, getConfig


def _run_status_exit_signal(status):
    """Select the exit signal depending on status."""
    switcher = {
        'critical': 5,
        'failed': 3,
        'canceled': 2,
        'skipped': 1
    }
    return switcher.get(status, 0)


class Scenario(dict):
    """Scenario Object."""

    def __init__(self, name):
        """
        Prepare the scenario object.

        :param name: The name of the scenario
        :type key: string
        """
        super().__init__()
        self.name = name
        self.steps = {}
        log.info("Scenario[%s]: initialization", self.name)
        if name in config['scenarios']:
            self.update(self._validate_sc(config['scenarios'][name]))
            config_run = getConfig('run')
            if 'job' in config_run:
                step_name = config_run['job']
                self.load_step(step_name, self['scenario_steps'][step_name])
            else:
                for step_name, step_config in self['scenario_steps'].items():
                    self.load_step(step_name, step_config)
        else:
            raise_ex(AttributeError, "No such scenario: " + name)

    def load_step(self, step_name, step_config):
        """Add a new step in the Scenario."""
        default = self._validate_all(config['defaults'])
        log.debug("Scenario[%s]: loading step '%s'", self.name,
                  step_name)
        cfg = default['gitlab']['git_projects'][step_config['project']]
        cfg.update(step_config)
        if 'ssh_access' in default:
            log.debug("Scenario[%s]: push group ssh_access '%s'", self.name,
                      step_name)
            cfg.update(
                {'group_ssh_access': default['ssh_access']})
        if 'ansible_ssh_creds' in default:
            log.debug("Scenario[%s]: push group ssh_creds '%s'", self.name,
                      step_name)
            cfg.update(
                {'group_ssh_creds': default['ansible_ssh_creds']})
        if 'certificates' in default:
            log.debug("Scenario[%s]: push group certificates '%s'", self.name,
                      step_name)
            cfg.update(
                {'group_certificates': default['certificates']})
        extra = {'pod': self.name, 'jumphost': self['jumphost']}
        self.steps[step_name] = Step(step_name, cfg, extra, self.name)

    def run(self, step_name):
        """
        Run the step pipeline.

        :param step_name: The name of the step
        :type step_name: string
        """
        if step_name not in self.steps:
            raise_ex(ValueError, f"Scenario - Step name '{step_name}' unknown")
        try:
            run_status = self.steps[step_name].run()
            log.info("Scenario[%s]: run finished wth status '%s'",
                     self.name, run_status)
        # pylint: disable=broad-except
        except Exception as err:
            log.critical("Here is the exception:\n %s", err)
            log.critical("Scenario[%s]: Run crash, please check previous "
                         "message", self.name)
            run_status = 'critical'
        sys.exit(_run_status_exit_signal(run_status))

    def _validate_all(self, src):
        log.debug("Scenario[%s]: validation of global config", self.name)
        src = dict(src)
        schema = Schema({
            Optional('disable_pages'): bool,
            Optional('protected_pods'): [str],
            Optional('tokens'): [
                {
                    'name': str,
                    'filter': str,
                    'id': str,
                    'value': str}
            ],
            'stages': [str],
            'runner': {
                'tags': [str],
                'env_vars': Or(dict, None),
                Optional('docker_proxy'): Or(str, None),
                'images': dict,
            },
            'gitlab': {
                Optional('pipeline'): {'delay': int},
                'base_url': str,
                'api_url': str,
                'private_token': str,
                Optional('healthchecks_url'): str,
                'git_projects': dict
            },
            Optional('certificates'): str,
            Optional('ansible_ssh_creds'): str,
            Optional('ssh_access'): str,
        })
        return schema.validate(src)

    def _validate_sc(self, src):
        log.debug("Scenario[%s]: validation of scenario", self.name)
        schema = Schema({
            'jumphost': Or({
                'server': str,
                'user': str}, None, {}),
            Optional('environment'): str,
            'scenario_steps': dict})
        return schema.validate(src)
