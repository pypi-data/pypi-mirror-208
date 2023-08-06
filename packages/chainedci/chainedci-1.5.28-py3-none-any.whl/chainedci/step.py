#!/usr/bin/env python3

"""Chained CI Scenario Step."""

from schema import Schema, Or, Optional
from ansible.parsing.yaml.objects import AnsibleVaultEncryptedUnicode
from chainedci.config import config, getConfig, merge_dicts
from chainedci.parser import JinjaParser
from chainedci.log import log, deprecation_warning
from chainedci.artifact import Artifact
from chainedci.artifact_src import ArtifactSrc
from chainedci.pipeline import Pipeline


def _get_config_step():
    """Get config step config if exists."""
    ini = getConfig('ini')
    config_step_name = ini['specific_steps']['config']
    scenario_name = getConfig('run')['name']
    if config_step_name in config[scenario_name]['scenario_steps']:
        return config[scenario_name]['scenario_steps'][config_step_name]
    return None


def _select_values_from_config_step(config_project):
    """
    Select values from config_project.

    Return project api (or url) and config path if exists
    """
    config_src = {}
    if 'api' in config_project:
        config_src['api'] = config_project['api']
    elif 'url' in config_project:
        config_src['url'] = config_project['url']
    if 'path' in config_project:
        config_src['path'] = config_project['path']
    return config_src


class Step(dict):
    """Scenario step object."""

    def __init__(self, name, step_config, extra, scenario):
        """
        Prepare the step object.

        :param name: The name of the step
        :type name: string
        :param step_config: The step config
        :type step_config: dict
        :param extra: Extra parameters to send to the remote pipeline
        :type extra: dict
        :param scenario: Scenario name
        :type scenario: string
        :return: a Step object
        :rtype: Step class
        """
        super().__init__()
        self.name = name
        self.extra = extra
        self.pipeline = None
        self.scenario = scenario
        self.artifact = None
        self.artifact_input = {'encrypt': False}
        log.info("Step[%s]: initialization", self.name)
        self.update(self._validate(step_config))
        self._prepare_artifact()
        self._prepare_parameters()

    def run(self):
        """
        Run the pipeline.

        :return: Run result
        :rtype: string

        Depending on step name,
        Get the artifact if it is a config step
        OR run another chainedci pipeline
        OR call the remote pipeline trigger
        """
        return (self._run_skip()
                or self._run_config()
                or self._run_trigger_myself()
                or self._run_project())

    def _run_skip(self):
        log.debug("Step[%s]: check if we run this step", self.name)
        if not self.only_except_check():
            log.info("Step[%s]: Skip due to only/except reason")
            return "skipped"
        return None

    def _run_config(self):
        """Run a config step.

        :return: Run result
        :rtype: string
        """
        ini = getConfig('ini')
        if self.name == ini['specific_steps']['config']:
            log.info("Step[%s]: run - Specific step 'Config'", self.name)
            if self.artifact:
                self.artifact.get_local()
                return "ok"
            log.error("Step[%s]: run - no artifact, nothing to do", self.name)
            return "skipped"
        return None

    def _run_trigger_myself(self):
        """Run a trigger to the same chained-ci.

        :return: Run result
        :rtype: string
        """
        ini = getConfig('ini')
        if self.name == ini['specific_steps']['trigger_myself']:
            parser = JinjaParser()
            log.info("Step[%s]: run - Specific step 'Trigger'",
                     self.name)
            self.extra['INPOD'] = self.extra['pod']
            self.extra['triggered_from'] = ini['env']['CI_JOB_NAME']
            self['api'] = (f"{config['gitlab']['api_url']}"
                           f"/projects/{ini['env']['CI_PROJECT_ID']}"
                           "/trigger/pipeline")
            self.pipeline = Pipeline(self['api'],
                                     self['trigger_token'],
                                     self.parameters,
                                     (parser.parse(self['branch'])
                                      if ('branch' in self) else 'master')
                                     )
            self.pipeline.start()
            log.info("Step[%s]: trigger started", self.name)
            return self.pipeline.status['status']
        return None

    def _run_project(self):
        """Run a project pipeline.

        :return: Run result
        :rtype: string
        """
        parser = JinjaParser()
        if self.artifact:
            self.parameters['artifacts_bin'] = self.artifact.bin
        self.pipeline = Pipeline(self['api'],
                                 self['trigger_token'],
                                 self.parameters,
                                 (parser.parse(self['branch'])
                                  if ('branch' in self) else 'master')
                                 )
        if self.get('timeout', None):
            log.debug("Step[%s]: set pipeline timeout to custom value"
                      " '%s'", self.name, self['timeout'])
            self.pipeline.set_custom_timeout(self['timeout'])
        self.pipeline.loop()
        if self.get('pull_artifacts', False):
            self._pull_artifact()
        log.info("Step[%s]: run finished", self.name)
        return self.pipeline.status['status']

    def only_except_check(self):
        """
        Check if run conditions are present.

        Eval each "only" and "except" conditions on env vars and return the
        result with formula: any(except[]) and all(only[])
        """
        ini = getConfig('ini')
        if 'only' not in self and 'except' not in self:
            log.debug("Step[%s]: No only/except rules", self.name)
            return True
        # pylint: disable=R1729
        excpt = (any([ini['env'].eval(rule)
                      for rule in self['except']])
                 if 'except' in self else False)
        # pylint: disable=R1729
        only = (all([ini['env'].eval(rule)
                     for rule in self['only']])
                if 'only' in self else True)
        return not excpt and only

    def _prepare_artifact(self):
        """Prepare the artifact to send."""
        log.debug("Step[%s]: prepare input artifact", self.name)
        if 'input_artifact' in list(self.keys()):
            self.artifact_input = self['input_artifact']
        else:
            deprecation_warning(f"please update step '{self.name}' with new "
                                "'input_artifact' structure")
            self._prepare_artifact_deprecated()
        self._prepare_artificat_input_security_values()
        self._prepare_artifact_from_input()

    def _prepare_artificat_input_security_values(self):
        """Prepare security fields linked to security."""
        self._prepare_artificat_input_encrypt()
        self._prepare_artificat_input_group_ssh_access()
        self._prepare_artificat_input_group_ssh_creds()
        self._prepare_artificat_input_group_certificates()

    def _prepare_artificat_input_encrypt(self):
        """Set default 'encrypt' value in artifact input."""
        if ('encrypt' not in self.artifact_input
                and self.artifact_input):
            log.debug("Step[%s]: option: do not encrypt artifact", self.name)
            self.artifact_input['encrypt'] = False

    def _prepare_artificat_input_group_ssh_access(self):
        """Inherit ssh_access from group."""
        if ('group_ssh_access' in self
                and 'ssh_access' not in self.artifact_input):
            log.debug("Step[%s]: option: use group ssh access '%s'",
                      self.name, self['group_ssh_access'])
            self.artifact_input['ssh_access'] = self['group_ssh_access']

    def _prepare_artificat_input_group_ssh_creds(self):
        """Inherit ssh_access from group."""
        if ('group_ssh_creds' in self
                and 'ssh_creds' not in self.artifact_input):
            log.debug("Step[%s]: option: use group ssh_creds '%s'",
                      self.name, self['group_ssh_creds'])
            self.artifact_input['ssh_creds'] = self['group_ssh_creds']

    def _prepare_artificat_input_group_certificates(self):
        """Inherit certificates from group."""
        if ('group_certificates' in self
                and 'certificates' not in self.artifact_input):
            log.debug("Step[%s]: option: use group certificate '%s'",
                      self.name, self['group_certificates'])
            self.artifact_input['certificates'] = self['group_certificates']

    def _prepare_artifact_from_input(self):
        """Prepare the artifact object."""
        if self.artifact_input:
            config_step = _get_config_step()
            if config_step:
                config_src = self._enrich_config_src_with_config_step()
            else:
                config_src = {'branch':
                              self._prepare_artifact_default_branch()}
            self.artifact = Artifact(
                self.artifact_input, self.name, config_src)
        else:
            self.artifact = None

    def _enrich_config_src_with_config_step(self):
        """Enrich artifact input src from 'config' step.

        If a config step is in the scenario, we reuse the config to
        fetch the artifacts.
        """
        config_src = {}
        config_step = _get_config_step()
        log.debug("Step[%s]: prepare config_src", self.name)
        config_project_name = config_step['project']
        config_project = config['defaults']['gitlab']['git_projects'][
            config_project_name]
        config_project = merge_dicts(config_project, config_step)
        config_src = _select_values_from_config_step(config_project)
        # Always set the branch, from config step branch or from
        # env vars
        ini = getConfig('ini')
        config_src['branch'] = \
            config_project.get('branch',
                               ini['env'].get('CI_COMMIT_BRANCH',
                                              'master'))
        return config_src

    def _prepare_artifact_default_branch(self):
        """Set a default branch to artifact src."""
        ini = getConfig('ini')
        return self.get('branch',
                        ini['env'].get('CI_COMMIT_BRANCH',
                                       'master'))

    def _prepare_artifact_deprecated(self):
        """Prepare artifact from deprecated inputs."""
        self.artifact_input = {}
        self._prepare_artifact_deprecated_files()
        self._prepare_artifact_deprecated_infra()
        self._prepare_artifact_deprecated_secu()

    def _prepare_artifact_deprecated_files(self):
        if 'get_artifacts' in self:
            self.artifact_input['get_artifacts'] = self['get_artifacts']
        if 'local_files' in self:
            self.artifact_input['local_files'] = self['local_files']
        if 'remote_files' in self:
            self.artifact_input['remote_files'] = self['remote_files']

    def _prepare_artifact_deprecated_infra(self):
        ini = getConfig('ini')
        if self.name == ini['specific_steps']['config']:
            if self.get('infra', '').lower() == 'none':
                log.debug("Step[%s]: No infra file added", self.name)
            else:
                self.artifact_input['infra_pdfidf'] = self.get('infra',
                                                               self.scenario)

    def _prepare_artifact_deprecated_secu(self):
        if 'certificates' in self:
            self.artifact_input['certificates'] = self['certificates']
        if 'ssh_access' in self:
            self.artifact_input['ssh_access'] = self['ssh_access']
        if 'ansible_ssh_creds' in self:
            self.artifact_input['ssh_creds'] = self['ansible_ssh_creds']
        if 'get_encrypt' in self:
            self.artifact_input['encrypt'] = self['get_encrypt']

    def _prepare_parameters(self):
        """Prepare the parameters to send."""
        log.debug("Step[%s]: prepare pipeline parameters", self.name)
        params = self._prepare_parameters_get_and_parse('parameters')
        params |= self._prepare_parameters_get_and_parse('extra_parameters')
        if 'novault' in self:
            params['NOVAULT_LIST'] = '\\n'.join(self['novault'])
        params['source_job_name'] = self.name
        for p_name, p_value in self.extra.items():
            params[p_name] = p_value
        self.parameters = params

    def _prepare_parameters_get_and_parse(self, param_type):
        """Get and parse params."""
        params = {}
        parser = JinjaParser()
        if param_type in self:
            for k, val in self[param_type].items():
                params[k] = parser.parse(val)
        return params

    def _pull_artifact(self):
        """Download the project pipeline artifact."""
        url = self.pipeline.artifact_url(self['pull_artifacts'])
        artifact_src = ArtifactSrc({'type': 'remote_archive', 'source': url})
        artifact_src.unpack()

    def _validate(self, src):
        src = dict(src)
        log.debug("Step[%s]: validation", self.name)
        schema = Schema({'project': str,
                         'stage': str,
                         Optional('url'): str,
                         Optional('api'): str,
                         Optional('path'): str,
                         Optional('token'): str,
                         Optional('infra'): str,
                         Optional('branch'): str,
                         Optional('novault'): [str],
                         Optional('get_encrypt'): bool,
                         Optional('get_bin'): bool,
                         Optional('input_artifact'): dict,
                         Optional('get_artifacts'): Or(str, list),
                         Optional('only'): [str],
                         Optional('except'): [str],
                         Optional('local_files'): [dict],
                         Optional('remote_files'): [dict],
                         Optional('certificates'): str,
                         Optional('group_certificates'): str,
                         Optional('ansible_ssh_creds'): str,
                         Optional('group_ssh_creds'): str,
                         Optional('ssh_access'): str,
                         Optional('group_ssh_access'): str,
                         Optional('parameters'): dict,
                         Optional('extra_parameters'): dict,
                         Optional('pull_artifacts'): Or(str, None),
                         Optional('trigger_token'): Or(
                             str, AnsibleVaultEncryptedUnicode),
                         Optional('timeout'): int})
        return schema.validate(src)
