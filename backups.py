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

# Run backups
backups = Backups()
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
