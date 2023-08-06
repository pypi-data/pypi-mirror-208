#!/usr/bin/env python3

"""Chained CI config wrapper."""
import copy
import os
import pkg_resources
from yaml import load, SafeLoader, add_constructor
import ansible.parsing.yaml.objects
from ansible.module_utils._text import to_bytes
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import VaultSecret
from chainedci.env_vars import EnvVars


# pylint: disable=invalid-name
__configDict = {}


def getConfig(name, load_env=True, init_scenarios=False, reset=False):
    """
    Get the config object with its name.

    :param name: The name of the config to get
    :type name: string
    :param load_env: Load or not environment variables if config does not
                     exists
    :type load_env: Boolean
    :param init_scenarios: Load or not scenarios if config does not exists
    :type init_scenarios: Boolean
    :return: a Config Class
    :rtype: Config object
    """
    if name in __configDict and not reset:
        return __configDict[name]
    __configDict[name] = Config(load_env, init_scenarios)
    return __configDict[name]


def merge_dicts(default, user):
    """Overload default dictionnary with the user one."""
    default = copy.deepcopy(default)
    user = copy.deepcopy(user)
    if isinstance(user, dict) and isinstance(default, dict):
        for k, v in default.items():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge_dicts(v, user[k])
    return user


def init_ini(default_config_file='default_chainedci.yml',
             user_config_file='chainedci.yml'):
    """Initialize the ini config.

    with the defaults overloaded with the user config.
    """
    ini = getConfig('ini', reset=True)
    default_config = pkg_resources.resource_string('chainedci',
                                                   default_config_file)
    ini.load_content(default_config)
    if os.path.exists(user_config_file):
        ini.merge(user_config_file)


def simple_dict(data):
    """Recursive function to parse AnsibleVaultEncryptedUnicode as str."""
    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = simple_dict(v)
    elif isinstance(data, list):
        # pylint: disable=consider-using-enumerate
        for i in range(0, len(data)):
            data[i] = simple_dict(data[i])
    elif isinstance(data,
                    ansible.parsing.yaml.objects.AnsibleVaultEncryptedUnicode):
        data = str(data)
    return data


def _create_vault_construct(loader, node):
    """Yaml constructor for vault."""
    loader.construct_scalar(node)
    return "__VAULTED_VALUE__"


def _load_yaml_data(data):
    """Load data without ansible loader. Assiming it is YAML."""
    add_constructor(
        '!vault', _create_vault_construct, SafeLoader)
    return load(data, SafeLoader)


class Config(dict):
    """Config class compatible with ansible vaulted files."""

    dl = DataLoader()

    def __init__(self, load_env=True, init_scenarios=False):
        """
        Init config class.

        Add a env attribute to access Env Vars
        """
        super().__init__()
        if load_env:
            self['env'] = EnvVars()
        if init_scenarios:
            self['defaults'] = None
            self['scenarios'] = {}

    def load_vault_key(self, filename):
        """
        Set vault secret from file.

        :param filename: the file name to load with path
        :type filename: string

        :Example:
        >>> c = Config()
        >>> c.load_vault_key('tests/config/config_example_vault_file')
        """
        with open(filename, encoding="utf-8") as f:
            content = f.readlines()
            self.set_vault_key(content[0].rstrip())

    def get_vault_key(self):
        """
        Get vault secret.

        :return: the vault key
        :rtype: VaultLib

        :Example:
        >>> c = Config()
        >>> c.load_vault_key('tests/config/config_example_vault_file')
        >>> type(c.get_vault_key())
        <class 'ansible.parsing.vault.VaultLib'>
        """
        # pylint: disable=protected-access
        return self.__class__.dl._vault

    def set_vault_key(self, key, key_id='default'):
        """
        Set vault secret.

        :param key: the vault key
        :type key: string

        :param key_id: the vault key name
        :type key_id: string

        :Example:
        >>> c = Config()
        >>> c.set_vault_key('fake')
        """
        secret = [(key_id, VaultSecret(to_bytes(key, encoding='utf-8')))]
        self.__class__.dl.set_vault_secrets(secret)

    def clean_vault_keys(self):
        """Remove all vault keys."""
        # pylint: disable=protected-access
        type(self).dl = DataLoader()

    def load_file(self, filename, key_name=None):
        """
        Load config file.

        :param filename: the file name to load with path
        :type filename: string

        :Example:
        >>> c = Config()
        >>> c.load_file('tests/config/config_example.yml')
        """
        if self.get_vault_key().secrets:
            content = self.__class__.dl.load_from_file(filename)
        else:
            with open(filename, encoding="utf-8") as f:
                content = _load_yaml_data(f)
        self.update_key(content, key_name)

    def load_content(self, content, key_name=None):
        """
        Load config file.

        :param content: the config content to load
        :type content: string
        """
        if self.get_vault_key().secrets:
            content = self.__class__.dl.load(content)
        else:
            content = _load_yaml_data(content)
        self.update_key(content, key_name)

    def update_key(self, content, key_name=None):
        """
        Update content with an optional key_name.

        :param content: the config content to load
        :type content: string
        :param key_name: the optionan key to update, if none, update self
        :type content: string
        """
        if key_name is not None:
            dic = self
            keys = key_name.split('.')
            for key in keys[:-1]:
                dic = dic.setdefault(key, {})
            dic[keys[-1]] = content
            self.update(dic)
        else:
            self.update(content)

    def merge(self, newfile, key_name=None):
        """Merge a config from a file to this object."""
        new = self.__class__.dl.load_from_file(newfile) or {}
        actual = self[key_name] if key_name else self
        self.update_key(merge_dicts(actual, new), key_name)

    def simplify(self):
        """Remove ansible objects in this object."""
        self.update(simple_dict(self))


# Load ini file
# pylint: disable=invalid-name
config = getConfig('chainedci', load_env=False)
run = getConfig('run', load_env=False)
