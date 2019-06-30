#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups import cli

# Backup servers defined in /etc/mreschke/serverbackups configurations
# =============================================================================
#cli.log("Running server backups from YAML configs")

servers = {
    'enabled': True,
    'source': {
        'location': 'remote',
        'ssh': {
            'address': 'linprox.mreschke.net'
        }
    },
    'server': {
        'location': 'local'
    },
}
cli.backupservers(servers=servers)
# backupservers(defaultYaml=defaultYaml, serversYaml=serversYaml)
# backupservers(config_path='/etc/mreschke/serverbackups')
# ALSO pass in python dict instead of yaml
# backupserfvers(servers=servers, default=default)

# Custom backupsYour custom backups here
# =============================================================================
if not cli.allowcustom():
    cli.done()
    exit()
cli.log("Running custom backups from backups.py")

# Run mreschke.serverbackups package
# =============================================================================
cli.done()
