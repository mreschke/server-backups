#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups import utils as u
from mreschke.serverbackups.backups import Backups

# Backup servers defined in dictionary
backups = Backups({
    'localhost': {
        'enabled': True,
        'destination': {
            'location': 'ssh',
            'path': '/store/backups',
            'ssh': {
                'address': 'linstore.mreschke.net',
                'user': 'toor',
                'key': '/home/mreschke/.ssh/id_rsa'
            }
        },
    }
})

# Default overrides
backups.defaults['cleanSnapshotsAfterDays'] = 30
backups.defaults['backup']['files']['common'] = [
    '/etc/'
]
u.dump(backups.defaults)

backups.run()
