from mreschke.serverbackups import log
from mreschke.serverbackups import Backups
from mreschke.serverbackups.utils import dump, dd

# Optionally configure logger, but this app may have its own log settings
log.init({
    'console': {
        'level': 'DEBUG',
    },
    'file': {
        'enabled': True,
        'file': '/tmp/backups.log',
    }
})

# Define each server to backup (each will be merged with defaults config)
servers = {
    'sunmac.mreschke.net': {
        'enabled': True,
        'cluster': 'localhost',
        'source': {
            'location': 'local',
        },
        'destination': {
            'location': 'ssh',
            'path': '/store/backups',
            'ssh': {
                'host': 'linstore.mreschke.net',
                'user': 'toor',
                'key': '/home/mreschke/.ssh/id_rsa'
            }
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

backups = Backups(servers=servers)
#backups = Backups(servers=servers, defaults=defaults)
#backups = Backups()

# Backups API Explorer
# dump("DEFAULTS", backups.defaults)
#dump("SERVERS", backups.servers)
# dump(backups.config_path)
# dump(backups.configd_path)
# dump(backups.defaults_file)

# Can just run them all
backups.run()

# Or can flip through each
#for server in backups.servers:
    #backups.run(server)
