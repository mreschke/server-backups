from mreschke.serverbackups import Backups, cli, log

# Configure logger
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
cli.start(backups)


# Custom backups
if not cli.allowcustom(): cli.handle(); exit()
log.header("Running custom backups from " + __file__)
#################################################
# Add your custom backups code here
#################################################
log.info('custom stuff here')


# Handle CLI requests
cli.handle()
