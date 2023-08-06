#!/usr/bin/env python3

"""Chained CI Artifact source."""

from shutil import copy, copytree, rmtree, unpack_archive, ReadError
from tempfile import mkdtemp
from os import makedirs
from os.path import isdir, exists
import binascii
import requests
from schema import Schema, Or, Optional
from chainedci.config import getConfig
from chainedci.tools import token_selector, get_env_or_raise, raise_ex
from chainedci.log import log
from chainedci.http_adapter import Http
from chainedci.parser import JinjaParser


class ArtifactSrc(dict):
    """Artifact Source object."""

    def __init__(self, src):
        """
        Artifact src init.

        :param src: The source of the artifact
        :type src: dict
        :param artifact_folder: The destination folder
        :type artifact_folder: string
        """
        super().__init__()
        self.uuid = binascii.crc32(str(src).encode('ascii'))
        self._folder = None
        self.update(self._validate(src))
        log.debug("ArtifactSrc[%s]: init type '%s' with source '%s'",
                  self.uuid, self['type'], self['source'])

    def load(self, artifact_folder):
        """
        Pull the ArtifactSrc locally.

        :param artifact_folder: The destination folder
        :type artifact_folder: string
        """
        # First lookup and replace variables in source
        parser = JinjaParser()
        self['source'] = parser.parse(self['source'])
        # Start loading
        log.debug("ArtifactSrc[%s]: load %s", self.uuid, self['source'])
        self._folder = artifact_folder
        if self._folder is None:
            raise ValueError("Artifact folder was never set")
        if self['type'] == 'pipeline':
            self._load_from_pipeline(self._folder)
        elif self['type'] == 'remote':
            self._load_from_remote()
        elif self['type'] == 'local_archive':
            self.unpack(self._folder, remote=False)
        elif self['type'] == 'remote_archive':
            self.unpack(self._folder)
        else:
            self._load_from_local()

    def _validate(self, src):
        """Validate ArtifactSrc Schema."""
        log.debug("ArtifactSrc[%s]: validation", self.uuid)
        schema = Schema(Or({'type': 'local',
                            'source': str,
                            'destination': str},
                           {'type': 'remote',
                            'source': str,
                            'destination': str},
                           {'type': 'local_archive',
                            'source': str},
                           {'type': 'remote_archive',
                            'source': str},
                           {'type': 'pipeline',
                            'source': str,
                            Optional('limit_to'): [dict],
                            Optional('artifact_in_pipeline'): bool}))
        return schema.validate(src)

    def unpack(self, dest='./', remote=True):
        """
        Download remote archive and unpack in a local folder.

        :param dest: The destination folder
        :type dest: string
        """
        log.debug("ArtifactSrc[%s]: get file to unpack %s to %s", self.uuid,
                  self['source'], dest)
        tmp_folder = mkdtemp()
        if remote:
            self._load_from_remote(tmp_folder + "/archive.zip")
        else:
            self._load_from_local(tmp_folder + "/archive.zip")

        log.debug("ArtifactSrc[%s]: unpack %s to %s", self.uuid,
                  tmp_folder + "/archive.zip", dest)
        try:
            unpack_archive(tmp_folder + "/archive.zip", dest)
        except ReadError:
            raise_ex(ValueError, f"{self['source']} is not an archive file")

        rmtree(tmp_folder)

    def _load_from_local(self, destination=None, source=None):
        """Pull the ArtifactSrc locally."""
        src = source or self['source']
        dest = destination or f"{self._folder}/{self['destination']}"
        log.debug("ArtifactSrc[%s]: load '%s' from local to '%s'", self.uuid,
                  src, dest)
        if not isdir(self._folder):
            raise OSError(f'Folder {self._folder} does not exists')
        # create parent directory
        makedirs('/'.join(dest.split('/')[:-1]), exist_ok=True)
        if isdir(src):
            copytree(src, dest, dirs_exist_ok=True)
        else:
            copy(src, dest)

    def _download_file(self, dest):
        """Download the file from an url."""
        log.debug("ArtifactSrc[%s]: download file '%s' to '%s'", self.uuid,
                  self['source'], dest)
        headers = token_selector(self['source'])
        with Http().session.get(self['source'], headers=headers) as response, \
                open(dest, 'wb') as out_file:
            # pylint: disable=no-member
            if response.status_code != requests.codes.ok:
                raise_ex(requests.exceptions.HTTPError,
                         f"ArtifactSrc: error calling '{self['source']}':"
                         f" '{ response.status_code }'")
            out_file.write(response.content)
            log.debug("ArtifactSrc[%s]: download done", self.uuid)

    def _load_from_remote(self, dest=None):
        """Load a remote artifact."""
        log.debug("ArtifactSrc[%s]: load remote '%s'", self.uuid,
                  self['source'])
        if dest is None:
            dest = f"{self._folder}/{self['destination']}"
        self._download_file(dest)

    def _load_from_pipeline(self, artifact_folder=None):
        """Pull the pipeline artifact."""
        log.debug("ArtifactSrc[%s]: load from pipeline '%s' to '%s'",
                  self.uuid, self['source'], artifact_folder)
        if self.get('artifact_in_pipeline', True):
            self._load_from_my_pipeline(artifact_folder)
        else:
            self._load_from_another_pipeline(artifact_folder)

    def _api_get(self, url):
        """Call an API."""
        log.debug("ArtifactSrc[%s]: call api '%s'", self.uuid, url)
        headers = token_selector(url)
        with Http().session.get(url, headers=headers) as response:
            # pylint: disable=no-member
            if response.status_code != requests.codes.ok:
                raise_ex(requests.exceptions.HTTPError,
                         f"ArtifactSrc[{self.uuid}]: error calling '{url}':"
                         f" '{ response.status_code }'")
            return response.json()

    def _load_from_my_pipeline(self, destination):
        """Load files from a previous job in this pipeline."""
        run = getConfig('run')
        pipeline_data = self._get_pipeline_successful_jobs()
        # filter steps to get the last sucessful step id
        target_step = f"{ self['source'] }:{ run['name'] }"
        last_success = list(filter(lambda d: d['name'] in target_step,
                                   pipeline_data))
        if not last_success:
            raise_ex(ValueError, f"ArtifactSrc[{self.uuid}]"
                                 f"No job found with name '{target_step}'")
        last_success_id = last_success[-1]['id']
        if 'limit_to' in self:
            tmp_folder = mkdtemp()
            self._download_job_artifact(last_success_id, tmp_folder)
            self._limit_to(tmp_folder, destination)
        else:
            self._download_job_artifact(last_success_id, destination)

    def _get_pipeline_successful_jobs(self, pipeline_id=None, project_id=None):
        """Get the list of a pipeline sucessful jobs."""
        # Get ids from env vars
        log.debug("ArtifactSrc[%s]: Search for pipeline '%s' successful jobs",
                  self.uuid, pipeline_id)
        config = getConfig('chainedci')
        api = config['defaults']['gitlab']['api_url']
        project_id = project_id or get_env_or_raise('CI_PROJECT_ID')
        pipeline_id = pipeline_id or get_env_or_raise('CI_PIPELINE_ID')
        # set request url
        url = (f"{ api }/projects/{ project_id }/"
               f"pipelines/{ pipeline_id }/jobs?scope[]=success")
        return self._api_get(url)

    def _download_job_artifact(self, job_id, destination, project_id=None):
        """Download an artifact of a job."""
        log.debug("ArtifactSrc[%s]: Download job '%s'", self.uuid,
                  job_id)
        config = getConfig('chainedci')
        api = config['defaults']['gitlab']['api_url']
        project_id = project_id or get_env_or_raise('CI_PROJECT_ID')
        self['source'] = (f"{ api }/projects/{ project_id }/"
                          f"jobs/{ job_id }/artifacts")
        self.unpack(destination)

    def _limit_to(self, tmp_folder, destination):
        """Filter the files of an archive."""
        log.debug("ArtifactSrc[%s]: Filter files. Move from '%s' to '%s'",
                  self.uuid, tmp_folder, destination)
        for file_filter in self['limit_to']:
            file_src = next(iter(file_filter))
            if not exists(f'{tmp_folder}/{file_src}'):
                raise_ex(ValueError, f"The file '{file_src}' does not exists "
                         "in this artifact.")
            self._load_from_local(
                source=f'{tmp_folder}/{file_src}',
                destination=f'{destination}/{file_filter[file_src]}')

    def _load_from_another_pipeline(self, artifact_folder):
        return artifact_folder
