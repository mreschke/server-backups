#import io
import os
from glob import glob

import yaml

from .backupserver import BackupServer
from .utils import dd, dump


class Backups:
    """Backup a complete set of servers
    """
    __author__ = "Matthew Reschke <mail@mreschke.com>"
    __license__ = "MIT"

    def __init__(self, *, servers=None, defaults=None, config_path='/etc/serverbackups'):
        # NOTICE: Do NOT log anything in this class.  Too early or it will log even during --help

        # Blank attributes
        self.config_path = None
        self.configd_path = None
        self.defaults_file = None

        # Get defaults from parameter, or config path defaults.yml
        self.defaults = self.__get_defaults(servers, defaults, config_path)

        # Get servers from parameter or config path .d folder
        servers = self.__get_servers(servers)

        # Build complete servers dictionary by merging each server with defaults
        self.servers = {}
        for server in servers:
            self.servers[server] = self.__merge_defaults(servers[server], self.defaults)

    def run(self, server=None, cluster=None):
        if server:
            # Backup a single server from the config
            if server in self.servers:
                BackupServer(server, self.servers[server], self.defaults).run()
        elif cluster:
            # Backup all servers marked with this cluster
            for server, options in self.servers.items():
                if options['cluster'] == cluster:
                    BackupServer(server, options, self.defaults).run()
        else:
            for server, options in self.servers.items():
                BackupServer(server, options, self.defaults).run()

    def __get_defaults(self, servers, defaults, config_path):
        """Get defaults from parameter, or config path defaults.yml
        """
        if servers and defaults:
            # Using passed in defaults
            return defaults
        elif servers and not defaults:
            # No defaults, so everything is self-contained in servers
            # But still need to create a blank defaults so our merge works properly

            # Using serverbackup builtint default.yml
            file = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults_blank.yml'
            default_config = ''
            with open(file, 'r') as stream:
                default_config = yaml.safe_load(stream)
            return default_config
        else:
            # No servers defined, using config path
            self.config_path = config_path
            self.configd_path = config_path + '/config.d'
            self.defaults_file = config_path + '/defaults.yml'

            # Read defaults.yml file
            if os.path.exists(self.defaults_file):
                defaults = {}
                with open(self.defaults_file, 'r') as stream:
                    defaults = yaml.safe_load(stream)
                return defaults
            else:
                print("Defaults file " + self.defaults_file + " does not exist")
                exit(1)

    def __get_servers(self, servers):
        """Get servers from parameter or config path .d folder
        """
        if not servers:
            # Read each servers .yml config in config.d folder
            servers = {}
            files = glob(self.configd_path + "/*.yml")
            for file in files:
                with open(file, 'r') as stream:
                    servers = {**servers, **yaml.safe_load(stream)}
        return servers

    def __merge_defaults(self, options, defaults):
        """Properly merge or replace options with defaults"""

        # Ensure options has all keys
        options.setdefault('cluster', '')
        options.setdefault('prune', {})
        options.setdefault('rsync', {})
        options.setdefault('source', {})
        options.setdefault('destination', {})
        options['source'].setdefault('ssh', {})
        options['destination'].setdefault('ssh', {})
        options.setdefault('backup', {})
        options['backup'].setdefault('preScripts', {})
        options['backup'].setdefault('files', {})
        options['backup'].setdefault('mysql', {})
        options['backup'].setdefault('postScripts', {})
        options['backup']['files'].setdefault('common', [])
        options['backup']['files'].setdefault('extra', [])
        options['backup']['files'].setdefault('exclude', [])
        options['backup']['mysql'].setdefault('excludeDbs', [])

        # Merge arrays
        options['backup']['files']['common'] = defaults['backup']['files']['common'] + options['backup']['files']['common']
        options['backup']['files']['extra'] = defaults['backup']['files']['extra'] + options['backup']['files']['extra']
        options['backup']['files']['exclude'] = defaults['backup']['files']['exclude'] + options['backup']['files']['exclude']
        options['backup']['mysql']['excludeDbs'] = defaults['backup']['mysql']['excludeDbs'] + options['backup']['mysql']['excludeDbs']

        # Replace dictionaries
        options['prune'] = {**defaults['prune'], **options['prune']}
        options['rsync'] = {**defaults['rsync'], **options['rsync']}
        options['source']['ssh'] = {**defaults['source']['ssh'], **options['source']['ssh']}
        options['source'] = {**defaults['source'], **options['source']}
        options['destination']['ssh'] = {**defaults['destination']['ssh'], **options['destination']['ssh']}
        options['destination'] = {**defaults['destination'], **options['destination']}

        options['backup']['mysql'] = {**defaults['backup']['mysql'], **options['backup']['mysql']}

        options['backup']['preScripts'] = {**defaults['backup']['preScripts'], **options['backup']['preScripts']}
        for script in options['backup']['preScripts'].keys():
            if script in defaults['backup']['preScripts'].keys():
                options['backup']['preScripts'][script] = {**defaults['backup']['preScripts'][script], **options['backup']['preScripts'][script]}

        options['backup']['postScripts'] = {**defaults['backup']['postScripts'], **options['backup']['postScripts']}
        for script in options['backup']['postScripts'].keys():
            if script in defaults['backup']['postScripts'].keys():
                options['backup']['postScripts'][script] = {**defaults['backup']['postScripts'][script], **options['backup']['postScripts'][script]}

        # Finally replace remaining flat values
        options = {**defaults, **options}
        return options
