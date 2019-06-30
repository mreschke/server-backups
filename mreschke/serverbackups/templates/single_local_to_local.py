#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups import cli

# Backup servers defined in /etc/mreschke/serverbackups configurations
servers = {
    'localhost': {
        'enabled': True,
        'destination': {
            'path': '~/Backups'
        },
    }
}
cli.backupservers(servers=servers)

# Custom backups
if not cli.allowcustom(): cli.handle(); exit()
cli.log("Running custom backups from backups.py")

# Run mreschke.serverbackups package
cli.handle()
