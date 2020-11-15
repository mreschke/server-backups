#!/usr/bin/env python
from datetime import date
from mreschke.serverbackups import Backups, cli, log

# Configure logger
log.init({
    'console': {
        'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    },
    'file': {
        'enabled': True,
        'file': '/tmp/backups-{}.log'.format(date.today().strftime('%Y-%m-%d')),
    }
})

# Set per server defaults.  Each server can override parts of this default.
defaults = {
    'enabled': True,
    'cluster': None,

    # Keep all daily up to X days back, last snapshot in a week X weeks back, last snapshot in a month X months back...
    'prune': {
        'keepDaily': 30,
        'keepWeekly': 24,
        'keepMonthly': 60,
        'keepYearly': 10,
    },

    # Rsync options
    'rsync': {
        'verbose': True,
    },

    # Source server connection details
    'source': {
        'location': 'local',  # local, ssh,
        'ssh': {
            # Only used with location=ssh
            'host': 'server.example.com',  # or IP address,
            'port': 22,
            'user': 'root',
            'key': '~/.ssh/id_rsa',
        },
    },

    # Destination server connection details
    'destination': {
        'location': 'local',  # local, ssh,
        'path': '/mnt/backups',
        'ssh': {
            # Only used with location=ssh
            'host': 'server.example.com',  # or IP address,
            'port': 22,
            'user': 'root',
            'key': '~/.ssh/id_rsa',
        },
    },

    # Backup items
    'backup': {
        # Pre scripts run on destination before this servers backups, a good place to prep files for backup
        'preScripts': {
            'gitlab': {'script': 'sudo gitlab-backup create', 'output': 'gitlab-backup.txt', 'enabled': False},
        },

        # Files to backup on the destination.  Use extra in your actual server definition for extra files.
        # Arrays are merged with defaults, so you could append to common and exclude as well
        'files': {
            'common': [
                '/etc/',
                '/usr/local/bin/',
                '/root/',
                '/home/',
                '/var/log/',
                '/var/spool/cron/',
            ],
            'extra': [],
            'exclude': [
                'lost+found',
                '.Trash-1000',
            ],
        },

        # MySQL Databases and Tables
        # Host and port are relative inside the server itself via ssh, not remote
        'mysql': {
            'enabled': False,
            'mysqlCmd': 'mysql',
            #'mysqlCmd': 'docker exec -i mysql mysql',
            'dumpCmd': 'mysqldump',
            'dumpFlags': '--quick --single-transaction --flush-logs',
            #'dumpCmd': 'docker exec -i mysql mysqldump',
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'unknown',
            # All databases minus exclusions
            'dbs': '*',
            # A list of databases (all tables)
            # 'dbs': ['db1', 'db2'],
            # A list of database with a selection of tables
            # 'dbs': [
            #     {'name': 'db1', 'tables': ['table1', 'table2']},
            #     {'name': 'db2', 'tables': '*'},
            # ],
            'excludeDbs': [
                'information_schema',
                'performance_schema',
                'lost+found',
                '#mysql50#lost+found',
            ],
        },

        # Post scripts run on destination after this servers backups, a good place to cleanup files
        'postScripts': {
            'dpkg': {'script': 'dpkg -l | gzip', 'output': 'dpkg.gz', 'enabled': False},
        },
    },
}

# Define each server to backup (each will be merged with defaults config)
servers = {
    'myserver.example.com': {
        'enabled': True,
        'cluster': 'localhost',
        # Example of local -> local backup
        'source': {
            'location': 'local',
        },
        'destination': {
            'location': 'local',
        },
        'backup': {
            'preScripts': {
                #'gitlab': {'enabled': True}
            },
            'mysql': {
                'enabled': True,
                'mysqlCmd': 'mysql',
                #'mysqlCmd': 'docker exec -i mysql mysql',
                'dumpCmd': 'mysqldump',
                #'dumpCmd': 'docker exec -i mysql mysqldump',
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': 'password',
                'dbs': '*',
            },
            'postScripts': {
                # Export dpkg package list of Linux Debian
                'dpkg': {'enabled': True},
                # Example of backing up postgres database
                #'fusionauth': {'script': 'cd /tmp/ && sudo -u postgres pg_dump fusionauth | gzip', 'output': 'fusionauth.sql.gz', 'enabled': True},
                # Example of capturing script output to snapshot
                #'test2': {'script': 'ls -Hhal /etc/', 'output': 'etc.txt', 'enabled': True},
            }
        },
    },
}

# Initialize Backup Class
# If you are defining servers in a dictionary above, without a separate defaults
#backups = Backups(servers=servers)

# If you are defining both servers and defaults above
backups = Backups(servers=servers, defaults=defaults)

# If you are using a config.d directory (/etc/serverbackups by default)
#backups = Backups()
#backups = Backups(config_path='/etc/alternative/dir')

# Run Backups
cli.start(backups)


# Custom backups
if not cli.allowcustom(): cli.handle(); exit()
log.header("Running custom backups from " + __file__)
#################################################
# Add your custom backups code here
#################################################
print('custom stuff here, any python code you want')


# Handle CLI requests
cli.handle()
