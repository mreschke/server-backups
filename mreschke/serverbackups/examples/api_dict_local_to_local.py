#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups.backups import Backups

# Backup servers defined in dictionary
servers = {
    'localhost': {
        'enabled': True,
        'destination': {
            'path': '/home/mreschke/Backups'
        },
    }
}
backups = Backups(servers)
backups.run()
