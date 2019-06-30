import os
import io
import yaml
from mreschke.serverbackups import backups


def from_dict(servers, defaults):
    x = backups()


def defaults():
    """Get default server backup YAML config"""
    file = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults.yml'
    default_config = ''
    with io.open(file, 'r') as stream:
        default_config = yaml.load(stream, Loader=yaml.SafeLoader)
    return default_config
