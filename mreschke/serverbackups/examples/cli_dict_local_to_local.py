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
    'prune': {
        # Keep all daily up to X days back, last snapshot in a week X weeks back, last snapshot in a month X months back...
        # 'keepDaily': 30,
        # 'keepWeekly': 24,
        # 'keepMonthly': 60,
        # 'keepYearly': 10,

        'keepDaily': 5,
        'keepWeekly': 8,
        'keepMonthly': 6,
        'keepYearly': 1,
    },
    'rsync': {
        'verbose': True,
    },
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
    'backup': {
        # Pre scripts run on destination before this servers backups, a good place to prep files for backup
        'preScripts': {
            'gitlab': {'script': 'sudo gitlab-backup create', 'output': 'gitlab-backup.txt', 'enabled': False},
        },
        # Files to backup on the destination.  Use extra in your actual server definition for extra files.
        # Arrays are merged with defaults, so you could append to common and exclude as well
        'files': {
            'common': [
                #'/etc/',
                #'/usr/local/bin/',
                #'/root/',
                #'/home/',
                #'/var/log/',
                #'/var/spool/cron/',
            ],
            'extra': [],
            'exclude': [
                'lost+found',
                '.Trash-1000',
            ],
        },
        'mysql': {
            'enabled': False,
            'mysqlCmd': 'mysql',
            #'mysqlCmd': 'docker exec -i mysql mysql',
            'dumpCmd': 'mysqldump',
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
            #     {'name': 'db2', 'tables': ['table1', 'table2']},
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
            #'path': '/Users/mreschke/Backups'  # Mac
            'path': '/home/mreschke/Backups'  # Linux
        },
        'backup': {
            'preScripts': {
                #'gitlab': {'enabled': True}
                # Example of capturing script output to snapshot
                #'test2': {'script': 'ls -Hhal /etc/', 'output': 'etc.txt', 'enabled': True},
            },

            'files': {
                'extra': [
                    "/etc/profile.d/"
                ],
            },
            'mysql': {
                'enabled': False,
                #'mysqlCmd': 'mysql',
                'mysqlCmd': 'docker exec -i mysql mysql',
                #'dumpCmd': 'mysqldump',
                'dumpCmd': 'docker exec -i mysql mysqldump',
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': 'techie',
                #'dbs': '*',
                'dbs': ['wiki'],
            },
            'postScripts': {
                'dpkg': {'enabled': False}
            }
        },
    },
}

# Run backups
backups = Backups(servers=servers, defaults=defaults)
cli.start(backups)


# Custom backups
if not cli.allowcustom(): cli.handle(); exit()
log.header("Running custom backups from " + __file__)
#################################################
# Add your custom backups code here
#################################################
print('custom stuff here')


# Handle CLI requests
cli.handle()
