import os
import io
import yaml
from mreschke.serverbackups.backupserver import BackupServer


class Backups:
    """Backup a complete set of servers"""

    __author__ = "Matthew Reschke <mail@mreschke.com>"
    __license__ = "MIT"

    def __init__(self, servers, config_path=None):
        if config_path:
            # Using config directory
            self.config_path = config_path
        else:
            # Passing in a dictionary of servers
            self.servers = servers
            self.defaults = self.get_default_template()

    def run(self):
        for server, options in self.servers.items():
            BackupServer(server, options, self.defaults).run()

    def get_default_template(self):
        """Get default server backup YAML config"""
        file = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults.yml'
        default_config = ''
        with io.open(file, 'r') as stream:
            default_config = yaml.load(stream, Loader=yaml.SafeLoader)
        return default_config
