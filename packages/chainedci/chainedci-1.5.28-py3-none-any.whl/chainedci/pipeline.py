#!/usr/bin/env python3

"""Chained CI Pipeline Manager."""

import json
import time
import urllib.parse
from chainedci.config import getConfig
from chainedci.http_adapter import Http
from chainedci.log import log
from chainedci.tools import (raise_ex, get_env_or_raise, token_selector,
                             waiting_cursor)


def _prepare_variables(parameters):
    """Prepare variable list to be sent to gitlab trigger API."""
    return {f'variables[{var}]': val for (var, val) in parameters.items()}


class Pipeline():
    """Pipeline manager."""

    def __init__(self, base_url, token, parameters, ref='master'):
        """Prepare the pipeline."""
        self.base_url = base_url
        self.parameters = _prepare_variables(parameters)
        self.parameters['token'] = token
        self.parameters['ref'] = ref
        self.pipeline_id = None
        self.status = {'status': None,
                       'start': None,
                       'timeout': None,
                       'custom_timeout': None,
                       'previous_time': None,
                       'step_running_timeout': None,
                       'last_response': None}
        self.web_url = None
        self.stop = False

    def loop(self):
        """Start the pipeline and wait for the end."""
        self.start()
        self.wait_for_remote_pipeline()

    def set_custom_timeout(self, timeout):
        """
        Set pipeline specific running timeout.

        :param timeout: The time to wait in running status before
                        stopping with timeout alert
        :type timeout: int
        """
        ini = getConfig('ini')
        if ini['timers']['timeout_retrocompatibility']:
            self.status['step_running_timeout'] = (
                timeout * ini['timers']['retries_sleep'])
        else:
            self.status['step_running_timeout'] = timeout

    def start(self):
        """
        Start the remote pipeline.

        :return: Run result
        :rtype: string
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Send the POST
        url = self.base_url+"/trigger/pipeline"
        log.debug("Pipeline: start - POST to '%s'", url)
        log.debug("Pipeline: start - POST with params '%s'",
                  dict(self.parameters))
        with Http().session.post(url,
                                 data=urllib.parse.urlencode(self.parameters),
                                 headers=headers) as response:

            # Handle success
            if response.status_code == 201:
                last_response = json.loads(response.content)
                self.pipeline_id = last_response['id']
                self._set_status('pending')
                log.debug("Pipeline: start - Pipeline successfully created "
                          "at '%s' (Gitlab server time) "
                          "with id [%s] and status '%s'",
                          last_response['created_at'],
                          last_response['id'],
                          last_response['status'])
                log.info("Pipeline: start - Pipeline created: '%s'",
                         last_response['web_url'])
                self.status['last_response'] = last_response

            # Handle Failure
            elif response.status_code == 404:
                raise_ex(ValueError,
                         (f"Pipeline: run - Failed to start "
                          f"'{url}' with code [404]. "
                          "This may be an issue with 'api' or 'trigger_token' "
                          "values"))
            else:
                raise_ex(ValueError,
                         (f"Pipeline: run - Failed to start "
                          f"'{url}' with code "
                          f"[{response.status_code}] and message "
                          f"'{response.content}'"))

    def get_remote_pipeline_info(self):
        """Get the remote pipeline info."""
        url = f"{self.base_url}/pipelines/{self.pipeline_id}"
        headers = token_selector(url)
        log.debug("Pipeline: get status from '%s'", url)
        with Http().session.get(url, headers=headers) as response:
            # Manage non 200 answers
            if response.status_code not in [200, 401]:
                raise_ex(ValueError,
                         (f"Pipeline: run - Failed to get status at "
                          f"'{url}' with code "
                          f"[{response.status_code}] and message "
                          f"'{response.content}'"))
            # Manage some exceptions where there is no content, it can happen
            if ((response.content == b'' or response.status_code == 401)
                    and self.status['status'] != 'unknown'):
                log.debug("Pipeline: status changed from 'pending' "
                          "to 'unknown'")
                return 'unknown'
            return json.loads(response.content)

    def get_remote_pipeline_status(self):
        """
        Get the remote pipeline status and handle response.

        Possible return of Gitlab CI are: created, waiting_for_resource,
        preparing, pending, running, success, failed, canceled, skipped,
        manual, scheduled.

        For now, created, waiting_for_resource, preparing, skipped, manual,
        and scheduled, are not managed.
        """
        resp = self.get_remote_pipeline_info()
        if resp == 'unknown':
            self._set_status('unknown')
        else:
            log.debug("Pipeline: last status = '%s'", resp['status'])
            if resp['status'] == 'running':
                # Rollback on timer if we are in unknown state
                if self.status['status'] == 'unknown':
                    log.debug("Pipeline: status changed from 'unknown' "
                              "to 'running'")
                    self._set_status('running',
                                     self.status['previous_time'])
                # Reset timers if we move from pending to running
                elif self.status['status'] == 'pending':
                    log.debug("Pipeline: status changed from 'pending' "
                              "to 'running'")
                    self._set_status('running')
            elif resp['status'] in ['failed', 'success', 'canceled']:
                ini = getConfig('ini')
                if ini['log']['level'] == 'INFO':
                    print('\n')
                log.info("Pipeline: stopping, status changed to '%s'",
                         resp['status'])
                self.stop = True
            self.status['last_response'] = resp
            self.status['status'] = resp['status']

    def _set_status(self, status, start_time=None):
        """
        Update status state and time.

        :param status: The status
        :type name: string
        :param start_time: The epoch to force for the start time
        :type name: float
        """
        ini = getConfig('ini')
        if status == 'unknown':
            self.status['previous_time'] = self.status['start']
        start_time = start_time or time.time()
        status_timer = (self.status['step_running_timeout']
                        if (status == 'running' and
                            self.status['step_running_timeout']) else
                        ini['timers'][status])
        self.status['start'] = start_time
        self.status['timeout'] = start_time + status_timer
        self.status['status'] = status

    def wait_for_remote_pipeline(self):
        """Loop to wait pipeline end."""
        log.debug("Pipeline - Loop start")
        ini = getConfig('ini')
        while not self.stop:
            if time.time() < self.status['timeout']:
                log.debug("Pipeline - Wait %s seconds",
                          ini['timers']['retries_sleep'])
                waiting_cursor(ini['timers']['retries_sleep'])
                self.get_remote_pipeline_status()
            else:
                raise_ex(
                    TimeoutError,
                    (f"Pipeline: Timeout, pipeline {self.web_url} "
                     f"seems stucked in status '{self.status['status']}' "
                     f"from {self.status['timeout'] - self.status['start']} "
                     "seconds")
                )
        log.info("Pipeline - Loop ended with status '%s'",
                 self.status['status'])

    def artifact_url(self, job_name):
        """Get the remote artifact url."""
        ini = getConfig('ini')
        # Warning if not a successful pipeline
        if self.status['status'] != 'success':
            raise_ex(ValueError,
                     "Pipeline - no artifact will be available with "
                     f"that '{self.status['status']}' pipeline")
        headers = {"PRIVATE-TOKEN":
                   get_env_or_raise(ini['auth']['private_token_env'])}
        url = (f"{self.base_url}/pipelines/{self.pipeline_id}/jobs/"
               "?scope[]=success")
        log.debug("Pipeline: get successful jobs from '%s'", url)
        with Http().session.get(url, headers=headers) as response:
            # Manage non 200 answers
            if response.status_code not in [200]:
                raise_ex(ValueError,
                         (f"Pipeline: artifact_url - Failed to get jobs at "
                          f"'{url}' with code "
                          f"[{response.status_code}] and message "
                          f"'{response.content}'"))
            resp = json.loads(response.content)
            log.debug("Pipeline - Job list = %s",
                      [{key: job[key] for key in ['id', 'name', 'status']}
                       for job in resp])
            jobs = sorted(filter(lambda d: d['name'] == job_name, resp),
                          key=lambda i: i['id'])
            if len(jobs) < 1:
                raise_ex(ValueError,
                         (f"Pipeline: artifact_url - Failed to get the jobs "
                          f"list with name '{job_name}'. Get {len(jobs)}, but "
                          "shall have more than '1'."))
            if 'artifacts_file' not in jobs[-1].keys():
                raise_ex(ValueError,
                         (f"Pipeline: artifact_url - No artifact file linked "
                          f"with this job ({jobs[-1]})"))
            url = f"{self.base_url}/jobs/{jobs[-1]['id']}/artifacts"
            log.info("Pipeline - artifact is here '%s'", url)
            return url
