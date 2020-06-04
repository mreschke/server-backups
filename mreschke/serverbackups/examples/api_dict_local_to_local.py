from datetime import date
from mreschke.serverbackups import Backups, log
from mreschke.serverbackups.utils import dump, dd

# Optionally configure logger, but this app may have its own log settings
log.init({
    'console': {
        'level': 'DEBUG',
    },
    'file': {
        'enabled': True,
        'file': '/tmp/backups-{}.log'.format(date.today().strftime('%Y-%m-%d')),
    }
})

# Set per server defaults
defaults = {
    'enabled': True,
    'cluster': None,
    'prune': {
        'keepDaily': 30,
        'keepWeekly': 24,
        'keepMonthly': 60,
        'keepYearly': 10,
    },
    'rsync': {
        'verbose': True,
    },
    'source': {
        'location': 'local',  # local, ssh,
        'ssh': {
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
            'host': 'server.example.com',  # or IP address,
            'port': 22,
            'user': 'root',
            'key': '~/.ssh/id_rsa',
        },
    },
    'backup': {
        'preScripts': {
            'dpkg': {'script': 'dpkg -l | gzip', 'output': 'dpkg.gz', 'enabled': False},
        },
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
            'dbs': '*',
            'excludeDbs': [
                'information_schema',
                'performance_schema',
                'lost+found',
                '#mysql50#lost+found',
            ],
        },
        'postScripts': {
            'dpkg': {'script': 'dpkg -l | gzip', 'output': 'dpkg.gz', 'enabled': False},
        },
    },
}

# Define each server to backup (each will be merged with defaults config)
serversX = {
    'sunmac.mreschke.net': {
        'enabled': True,
        'cluster': 'localhost',
        'source': {
            'location': 'local',
        },
        'destination': {
            'location': 'local',
            'path': '/Users/mreschke/Backups'
        },
        'backup': {
            'preScripts': {
                'test': {
                    'enabled': True,
                    'script': 'cat /etc/hosts',
                    'output': 'hosts.txt'
                },
                'test2': {
                    'enabled': True,
                    'script': 'ls -Hhal /etc/',
                    'output': 'etc.txt'
                },
            },
            'mysql': {
                'enabled': True,
                'mysqlCmd': 'docker exec -i mysql mysql',
                'dumpCmd': 'docker exec -i mysql mysqldump',
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': 'techie',
                #'dbs': '*',
                'dbs': ['wiki'],
                # 'dbs': [
                #     {'name': 'blog', 'tables': ['test1', 'test2']},
                # ]
            },
        },
    },
}




# Define each server to backup (each will be merged with defaults config)
servers = {
    'sunmac.mreschke.net': {
        'enabled': True,
        'source': {
            'location': 'local',
        },
        'destination': {
            'location': 'local',
            'path': '/Users/mreschke/Backups'
        },
        'backup': {
            'files': {
                'common': [
                    '/etc/',
                ],
                'exclude': [
                    'lost+found',
                    '.Trash-1000',
                ],
            },
        },
    },
}



# Test by passing in servers, using builtin defaults
backups = Backups(servers=servers)

# Test by passing in servers and defaults
#backups = Backups(servers=servers, defaults=defaults)

# Test by using /etc/serverbackups
#backups = Backups()

# Backups API Explorer
# dump("DEFAULTS", backups.defaults)
#dump("SERVERS", backups.servers)
# dump(backups.config_path)
# dump(backups.configd_path)
# dump(backups.defaults_file)

# Can just run them all
backups.run()

# Or can flip through each and add your own logic per server if needed
#for server in backups.servers:
    #backups.run(server)

