#!/usr/bin/env python3

# Import mReschke Server Backup Scripts
from mreschke.serverbackups.cli import *

# Backup servers defined in /etc/mreschke/serverbackups configurations
# =============================================================================
log("Running server backups from YAML configs")

server = {
    'enabled': True,
    'source': {
        'server': 'linprox.mreschke.net',
        'location': 'remote',
        'sshPort': 22,
        'sshUser': 'root',
        'sshKey': '~/.ssh/id_rsa',
    },
    'server': {
        'location': 'local'
    },
}

print(server)
exit()

defaultYaml = """
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
#backupservers(serversYaml=serversYaml)
#backupservers(defaultYaml=defaultYaml, serversYaml=serversYaml)
#backupservers(config_path='/etc/mreschke/serverbackups')
# ALSO pass in python dict instead of yaml
    #backupserfvers(servers=servers, default=default)




# Custom backupsYour custom backups here
# =============================================================================
if not allowcustom(): done(); exit()
log("Running custom backups from backups.py")



# Run mreschke.serverbackups package
# =============================================================================
done()
