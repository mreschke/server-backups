#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups.cli import *

# Backup servers defined in /etc/mreschke/serverbackups configurations
# =============================================================================
log("Running server backups from YAML configs")

defaultsYaml = """
---
enabled: true
snapshotDateFormat: '%Y%m%d%H%M%S'
cleanSnapshotMethod: delete   # delete or archive
cleanSnapshotsAfterDays: 3    # 0 to disable snapshot cleaning
deleteArchivesAfterDays: 0    # 0 to disable archive cleaning
server:
  location: remote
  sshPort: 22
  sshUser: root
  sshKey: ~/.ssh/id_rsa
backupRoot: /Users/mreschke/Backups
backupItems:
  files:
    common:
    - /etc/
    #- /usr/local/bin/
    #- /root/
    #- /home/
    #- /var/log/
    #- /var/spool/cron/
    extra:
      -
    exclude:
      - lost+found
      - .Trash-1000
  scripts:
    dpkg: {script: 'dpkg -l | gzip', output: 'dpkg.gz', enabled: true}
    #postgres: {script: 'sudo -u postgres pg_dump jira | gzip', output: 'jira.sql.gz', enabled: true}
  mysql:
    enabled: false
    host: 127.0.0.1
    user: root
    dbs: '*'
    excludeDbs:
      - information_schema
      - performance_schema
"""

serversYaml = """
---
'lindb1':
  enabled: true
  server:
    sshPort: 13201
    hostname: lindb1.mreschke.net
  backupItems:
    mysql:
      enabled: true
      pass: 'uioprewq0987'
      dbs:
        - mrcore4
        - mrcore5
"""
try:

    backupservers()     # Use default /etc/mreschke/serverbackups config path
    #backupservers('/etc/mreschke/serverbackups2') # Use custom config path
    #backupservers(servers=serversYaml) # Inline YAML with NO defaults
    #backupservers(servers=serversYaml, defaults=defaultYaml) # Inline YAML with defaults

except KeyboardInterrupt:
    print("KeyboardInterrupt has been caught.")



# Custom backupsYour custom backups here
# =============================================================================
if not allowcustom(): done(); exit()
log("Running custom backups from backups.py")



# Run mreschke.serverbackups package
# =============================================================================
done()



