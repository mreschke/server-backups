#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups.cli import *

# Backup servers defined in /etc/mreschke/serverbackups configurations
# =============================================================================

servers = """
'localhost':
  source:
    location: local
  destination:
    location: ssh
    path: /store/sys/bak/test
    ssh:
      address: linstore.mreschke.net
      port: 10220
      user: toor
  backup:
    files:
      extra:
        - /tmp/test/
"""
backupservers(servers=servers)


# Custom backups
# =============================================================================
if not allowcustom(): done(); exit()
log("Running custom backups from backups.py")


# Run mreschke.serverbackups package
# =============================================================================
done()



