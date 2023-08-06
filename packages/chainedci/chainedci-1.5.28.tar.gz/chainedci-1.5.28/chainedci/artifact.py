#!/usr/bin/env python3

"""Chained CI Artifact."""
import urllib.parse
import base64
from os import walk
from shutil import rmtree, make_archive
# pylint: disable-next=deprecated-module
from distutils.dir_util import copy_tree
from tempfile import mkdtemp, NamedTemporaryFile
from schema import Schema, Or, Optional
from ansible.parsing.vault import VaultSecret, VaultEditor
from ansible.errors import AnsibleError
from chainedci.config import getConfig
from chainedci.log import log
from chainedci.artifact_src import ArtifactSrc
from chainedci.parser import JinjaParser


class Artifact(dict):
    """
    Object representing the artifact to send to the remote pipeline.

    This object:
    - stores the Artifact sources
    - encrypt all sources
    - generate the zip file
    - generate the bin value of the Artifact
    """

    def __init__(self, src, step_name, config_source):
        """Artifact class.

        :param src: The artifact sources
        :type src: dict
        :param ini: The chainedci ini config
        :type ini: dict
        """
        super().__init__()
        self.sources = []
        self.step_name = step_name
        self.folder = None
        self.vault_ed = None
        self.config_source = config_source
        log.info("Artifact[%s]: initialization", self.step_name)
        self.update(self._validate(src))
        self.import_src()

    def import_src(self):
        """Import artifact sources."""
        ini = getConfig('ini')
        if 'get_artifacts' in self:
            log.debug("Artifact[%s]: load 'get_artifacts'", self.step_name)
            if isinstance(self['get_artifacts'], str):
                self._add_source({'type': 'pipeline',
                                  'source': self['get_artifacts']})
            else:
                for artifact in self['get_artifacts']:
                    if 'static_src' in artifact:
                        (artifact_type, base, final) = self._get_source(
                            extension=ini['artifacts']['static']['extension'],
                            folder=ini['artifacts']['static']['src'])
                        artifact['type'] = f'{artifact_type}_archive'
                        artifact['source'] = (
                            f"{base}/{artifact['name']}{final}")
                        del artifact['static_src']
                    else:
                        artifact['type'] = 'pipeline'
                        artifact['source'] = artifact['name']
                    del artifact['name']
                    self._add_source(artifact)
        if 'local_files' in self:
            log.debug("Artifact[%s]: load 'local_files'", self.step_name)
            for file in self['local_files']:
                (source_file, local_file) = list(file.items())[0]
                self._add_source({'type': 'local',
                                  'source': source_file,
                                  'destination': local_file})
        if 'remote_files' in self:
            log.debug("Artifact[%s]: load 'remote_files'", self.step_name)
            for file in self['remote_files']:
                (source_file, remote_file) = list(file.items())[0]
                self._add_source({'type': 'remote',
                                  'source': source_file,
                                  'destination': remote_file})
        if 'infra_pdfidf' in self:
            log.debug("Artifact[%s]: load 'infra_pdfidf'", self.step_name)
            self._import_infra_pdfidf(self['infra_pdfidf'])
        if ('certificates' in self
                or 'ssh_access' in self
                or 'ssh_creds' in self):
            self._import_certs()

    def _import_certs(self):
        ini = getConfig('ini')
        if 'certificates' in self:
            # pylint: disable=unused-variable
            (artifact_type, base, final) = self._get_source(
                extension='',
                folder=ini['artifacts']['certificates']['src'])
            log.debug("Artifact[%s]: load 'certificates'", self.step_name)
            self._add_source(
                {'type': artifact_type,
                 'destination': ini['artifacts']['certificates']['dest'],
                 'source': f"{base}/{self['certificates']}"})
        if 'ssh_creds' in self:
            # pylint: disable=unused-variable
            (artifact_type, base, final) = self._get_source(
                extension='',
                folder=ini['artifacts']['ssh_creds']['src'])
            log.debug("Artifact[%s]: load 'ssh_creds'", self.step_name)
            self._add_source(
                {'type': artifact_type,
                 'destination': ini['artifacts']['ssh_creds']['dest'],
                 'source': f"{base}/{self['ssh_creds']}"})
        if 'ssh_access' in self:
            # pylint: disable=unused-variable
            (artifact_type, base, final) = self._get_source(
                extension='',
                folder=ini['artifacts']['ssh_access']['src'])
            log.debug("Artifact[%s]: load 'ssh_access'", self.step_name)
            self._add_source(
                {'type': artifact_type,
                 'destination': ini['artifacts']['ssh_access']['dest'],
                 'source': f"{base}/{self['ssh_access']}"})

    def _import_infra_pdfidf(self, infra):
        """Import PDF/IDF."""
        ini = getConfig('ini')
        (artifact_type, base, final) = self._get_source(
            extension=ini['artifacts']['pdfidf']['extension'],
            folder=ini['artifacts']['pdfidf']['src'])
        idf_prefix = ini['artifacts']['pdfidf']['idf_prefix']
        self._add_source({
            'type': artifact_type,
            'source': f"{base}/{infra}{final}",
            'destination': ini['artifacts']['pdfidf']['pdf_dest']})
        self._add_source({
            'type': artifact_type,
            'source': f"{base}/{idf_prefix}{infra}{final}",
            'destination': ini['artifacts']['pdfidf']['idf_dest']})

    def _get_source(self, extension, folder):
        """Get source parameters from config_src.

        for 'static_src' and 'infra_pdfidf' source can be remote from url, api
        or can be local.
        """
        parser = JinjaParser()
        branch = parser.parse(self.config_source['branch'])
        path = (parser.parse(self.config_source['path'])+f'/{folder}'
                if 'path' in self.config_source else folder)
        # in case of remote config
        if 'api' in self.config_source:
            artifact_type = "remote"
            base = (f"{ self.config_source['api'] }/repository/files/"
                    f"{ urllib.parse.quote(path) }")
            final = f"{extension}?ref={ branch }"
        elif 'url' in self.config_source:
            artifact_type = "remote"
            base = (f"{ self.config_source['url'] }/raw/{ branch }/"
                    f"{ urllib.parse.quote(path) }")
            final = extension
        else:
            artifact_type = "local"
            base = f"{ path }"
            final = extension
        return(artifact_type, base, final)

    @property
    def bin(self):
        """Get the base64 encoded binary value of the artifact."""
        log.info("Artifact[%s]: generate bin", self.step_name)
        self._load_artifactfolder()
        self._encrypt_artifactfolder()
        content = self._zip_artifactfolder()
        self._clean_artifactfolder()
        return base64.b64encode(content)

    def get_local(self, dest='./'):
        """Copy the artifact file to a specific folder."""
        log.info("Artifact[%s]: get artifacts to '%s'", self.step_name, dest)
        self._load_artifactfolder()
        self._encrypt_artifactfolder()
        copy_tree(self.folder, dest)
        self._clean_artifactfolder()

    def _zip_artifactfolder(self):
        """Zip the artifact folder."""
        log.debug("Artifact[%s]: zip artifact folder", self.step_name)
        # pylint: disable=R1732
        tmp_file = NamedTemporaryFile(suffix='.zip')
        zip_name = tmp_file.name.replace('.zip', '')
        # Archive the folder
        zip_file = make_archive(zip_name,
                                'zip',
                                root_dir=self.folder)
        # Get the binary content of the file
        with open(zip_file, mode='rb') as file:
            content = file.read()
        tmp_file.close()
        return content

    def _clean_artifactfolder(self):
        """Clean artifact folder."""
        rmtree(self.folder)

    def _load_artifactfolder(self):
        """Load all the artifactSrc."""
        log.debug("Artifact[%s]: load artifact folder", self.step_name)
        # Create temp folder
        self.folder = mkdtemp()
        # Get all sources to this folder
        for artifact_src in self.sources:
            artifact_src.load(self.folder)

    def _encrypt_artifactfolder(self):
        """Encrypt all files of the temporary folder."""
        ini = getConfig('ini')
        if self['encrypt']:
            log.debug("Artifact[%s]: encrypt artifact archive", self.step_name)
            if ini['encryption']['method'] == 'ansible_vault':
                self._load_vault_lib()
            else:
                raise ValueError(
                    "Config encryption:method' must be in "
                    f"'{['ansible_vault']}' not "
                    f"'{ini['encryption']['method']}'")
            # pylint: disable=unused-variable
            for root, dirs, files in walk(self.folder):
                for file in files:
                    self._encrypt_artifact_file(f'{root}/{file}')

    def _encrypt_artifact_file(self, filepath):
        """Encrypt on file of the temporary folder."""
        ini = getConfig('ini')
        if ini['encryption']['method'] == 'ansible_vault':
            self._encrypt_artifact_file_vault(filepath)

    def _load_vault_lib(self):
        """Load VaultLib to encypt files."""
        ini = getConfig('ini')
        run = getConfig('run')
        if not run.get('key'):
            raise ValueError(
                f"'{ini['encryption']['key_env_name']}' variable must be set")
        self.vault_ed = VaultEditor()

    def _encrypt_artifact_file_vault(self, filepath):
        """Encrypt file with ansible vault."""
        run = getConfig('run')
        log.debug("Artifact[%s]: vault file '%s'", self.step_name, filepath)
        vault_key = run.get('key')
        try:
            self.vault_ed.encrypt_file(filepath, VaultSecret(vault_key))
        except AnsibleError as excpt:
            if f"{excpt}" == "input is already encrypted":
                log.info("%s is already encrypted, continue", filepath)
            else:
                raise excpt
        except Exception as excpt:
            log.error("Unexpected error")
            raise excpt

    def _add_source(self, src):
        """Add a source to the artifact."""
        self.sources.append(ArtifactSrc(src))

    def _validate(self, src):
        """Validate the artifact config."""
        log.debug("Artifact[%s]: validation", self.step_name)
        schema = Schema({
            Optional('get_artifacts'): Or(str, [dict]),
            Optional('local_files'): [dict],
            Optional('remote_files'): [dict],
            Optional('certificates'): str,
            Optional('ssh_creds'): str,
            Optional('ssh_access'): str,
            Optional('infra_pdfidf'): str,
            'encrypt': bool})
        return schema.validate(dict(src))
