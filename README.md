# server-backups



# CLI API FIRST - What I Want

from mreschke.serverbackups.backupserver import BackupServer

## From Dictionary
from mreschke.serverbackups import factory
defaults = factory.defaults
servers = {
    'localhost': {
        'enabled': True,
        'destination': {
            'path': '~/Backups'
        },
    }
}
backups = factory.from_dict(servers, defaults)
backups.run()


## From Folder
from mreschke.serverbackups import factory
backups = factory.from_path('/etc/mreschke/serverbackups')
backups.run()


## From CLI Script as Dictionary
from mreschke.serverbackups import cli, factory
defaults = factory.defaults
servers = {
    'localhost': {
        'enabled': True,
        'destination': {
            'path': '~/Backups'
        },
    }
}
backups = factory.from_dict(servers, defaults)
backups.run

cli.handle()








Server Backup Python Scripts and Libraries



NOTE: for mac, this requires the new rsync (brew rsync), not mac default as it cannot accept multuple remote sources


Prototype

this .backups.py WILL have a usage() and CLI flags, but they will not be coded here, they will import
./backups.py just shows usage()
-h and --help

Shows usage
    ./backups.py

Run all backups (server YML & custom)
    ./backups.py --all



--all runs all backups
--custom runs custom backups
--server prostore runs one server
--cluster knodes runs all servers in a cluster

--server prostore --skip-mysql --skip-files etc...
--server prostore --only-mysql ...


server-backups init which perhaps builds this backups.py file with some basics
    so just
    pip install server-backups
    server-backups init backups.py
    everything else is done from this ./backups.py file, not server-backups script


All code will still be behind the scnese, not in backups.py, but in this "server_backups or serverbackups PIP package"!!!

Use click! for CLI


Folders

/etc/mreschke/serverbackups
    default.yml
    config.d/
        prostore.yml
        node1.yml
        server2.yml
        cluster1.yml

Each json folder can be one OR MORE servers.  So could put all in a cluster in one file, doesn't matter
Maybe merge fields in there? {{somevariable}} ??


Example default.yml perhaps?

---
defaults:
  enabled: true
  snapshotDateFormat: YmdHi
  cleanSnapshotMethod: delete   # delete or archive
  cleanSnapshotsAfterDays: 3    # 0 to disable snapshot cleaning
  deleteArchivesAfterDays: 0    # 0 to disable archive cleaning
  server:
    location: remote
    sshPort: 22
    sshUser: root
    sshKey: ~/.ssh/dynatron-ansible.key
  backupRoot: /store/backup
  backupItems:
    files:
      common:
        - /etc/
        - /usr/local/bin/
        - /root/
        - /home/
        - /var/log/
        - /var/spool/cron/
      #extra:,
      exclude:
        - lost+found
        - .Trash-1000
    scripts:
      dpkg: {script: 'dpkg -l | gzip', output: 'dpkg.gz', enabled: true}
    mysql:
      enabled: false
      host: 127.0.0.1
      user: root
      dbs: '*'
      excludeDbs:
        - information_schema
        - performance_schema



Example server.yml file perhaps??

---
locations:
    - name: dynalb
        enabled: true
        server:
        hostname: dynalb.dynatron.io
        backupItems:
        files:
            exclude:
            - /var/log/haproxy_info.log # Rotated to prostore daily

    - name: otherserver
        because can have more than one.  Could really have ALL servers in one file, up to you







Building PyPi
-------------
You can build without a folder, just a .py, and setup.py, see https://github.com/neilalbrock/flask-elasticutils/ for example

onegov.search namespace example https://github.com/OneGov/onegov.search
See also https://packaging.python.org/guides/packaging-namespace-packages/


package names options?

PIP=mreschke.server-backups
    mreschke
        server_backups (yes underscore, has to be)
        Example: https://github.com/OneGov/onegov.search

PIP=mreschke-server-backups
    server_backups (yes underscore, has to be), no mreschke I think is ok as long as setup.py is correct
    See https://github.com/calebsmith/django-template-debug/blob/master/setup.py for perfect example, setup.py uses find_packages(), but maybe hard code


