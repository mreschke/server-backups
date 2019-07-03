#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups import cli
from mreschke.serverbackups.backups import Backups


# Backup servers defined in dictionary
servers = {
    'localhost': {
        'enabled': True,
        'destination': {
            'path': '~/Backups'
        },
    }
}
backups = Backups(servers)
cli.load(backups)


# Custom backups
if not cli.allowcustom(): cli.handle(); exit()
cli.log("Running custom backups from backups.py")
#################################################
# Add your custom backups code here
#################################################


# Handle CLI requests
cli.handle()
