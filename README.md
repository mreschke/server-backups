# Server Backups

Config driven server backups that feel like a simple backup.py script

* PyPi: https://pypi.org/project/mreschke-serverbackups
* Github: https://github.com/mreschke/server-backups


# Installation

```bash
pip install mreschke-serverbackups
```


# Usage

All backups are initiated from a simple `backups.py` file.  Create this file with:

```bash
cd /usr/local/bin
serverbackups init-cli-script
```

This `backups.py` can hold your server backup definitions as a dictionary, fully self contained.
Or you can choose to use `yaml` files in `/etc/serverbackups` to separate each server in its own `/etc/serverbackups/config.d` file.
To initialize a stock `/etc/serverbackups` directory run

```bash
serverbackups init-directory

# Defaults to /etc/serverbackups.  Optionally, set a different directory
serverbackups init-directory --path /etc/someother/dir
```

Read below for how to modify the configs.  Once you have a good configuration setup you can run the
backups like so

```bash
# Run all servers AND custom python code
./backups.py run --all

# Run all servers with NO custom python code
./backups.py run --servers

# Run a single server (no custom python code)
./backups.py run --server=myserver

# Run all servers defined in the same cluster (no custom python code)
./backups.py run --cluster=webfarm

# Run only custom code in backups.py, NOT the server definition arrays
./backups.py run --custom
```



# Basic Idea

The basic idea is to replace your quick and simple backup `bash` script with a more
comprehensive but still simple and readable `backups.py` file.  This file can backup common items
such as files and databases using `rsync` hard-link style snapshots in a simple
config driven manner.  Instead of hacking bash scripts to rsync properly you can use
a simple config instead.  At the end of `backups.py` after all backups have executed
from this simple dictionary/yaml definition you can still code your own functionality
right in python as you normally would in a bash script.  This gives you the power
of a script with the added benefit if easy config driven common backup routines.

Whether you are using inline `backups.py` dictionaries to define your server or
using `/etc/serverbackups/config.d/*` files the concept of how the system works
is the same.

You define an array of server to backup.  Each server has many options including
source, destination, files to backup and exclude, databases to backup and pre/post
scripts to run.


## Backup Strategy

I use `rsync` and `ssh` for all backups local or remote.  To cut down on storage costs I am utilizing
rsync hard-link style snapshots.  This means your snapshot folder looks full and complete each day (not
a diff or incremental look) but in actuality most of those files are hard linked to previous snapshots.
This means the storage used on the backup server is only the size of all unique files combined + the ones
previously deleted.  Total storage is NOT every days worth of files, that would be HUGE.
I adapted the code from http://anouar.adlani.com/2011/12/how-to-backup-with-rsync-tar-gpg-on-osx.html
to accomplish this.  The trick is in the `rsync --hard-links --link-dest` parameters.  This storage saving
trick allows you to have a generous purge strategy, keeping years worth of weekly, monthly and yearly backups
without sacrificing storage.


## Defaults

Most of the settings for a single server are redundant and can therefore be
deduplicated in to what I call a `defaults` config.  The `defaults` config
is `merged` with **each** server definition in your array.  This keeps your server definition
small and clean.  `Defaults` and each of your server configs are deep merged which
allows you to override small pieces of the `defaults` for each server as needed.

Defaults are completely **optional** and are there to help cut down on redundant configuration.  If
you are simply backing up a single server, just define the entire complete server options and forget
a 'defaults' definition.

**NOTICE - Sensible Defaults Applied**

If you do not define your own 'defaults', a sensible 'defaults' are still applied to keep even a single
server definition less verbose.  Run `serverbackups show-builtin-defaults` to see the `defaults` that are
still being applied here.  For example you don't need to define the prune rates, ssh port or ssh key
if the `defaults` are acceptable.

Because of the `defaults` system, your actual server definitions can be much smaller.  For example, here
is a minimal server definition that inherits from `defaults`

In yaml format
```yaml
myloadbalancer:
  source: {ssh: {host: haproxy.example.com}}
  backup:
    files:
      exclude:
        - /var/log/haproxy_info.log
```


## Servers

Each server is defined in a python dictionary or yaml file in `/etc/serverbackups/config.d`
**ending in .yml**.  Before the backups run each server is `deep merged` with your `defaults` config to
create a full and rich server definition.


## Files

The `files` section of each server definition allows you to backup files and folders obeying the `exclude`
array.  The only difference between `common` and `extra` is that `common` was meant to be used in the `defaults`
section while `extra` was there just for you to add to each of your servers.  Technically you can still add
`common` to your server as arrays are APPENDED during the `default deep merge algorithm`.  Exclude is also
appended during merge so you can add more excludes per server while maintaining those you defined in `defaults`.


## Scripts

The script section of each server definition allows you to run arbitrary bash scripts on the destination.
The `output` of the scripts is optional.  If present, the output is saved to the snapshot folder.  This is
handy to backup the output of `dpkg -l` command for example.

There are 2 script sections, `preScripts` and `postScripts`.  The pre scripts run before any other backups
for that particular server.  Post scripts run after all backups.

Example.  I want to backup my `gitlab` server.  I really don't want to export my repositories and dig into
their postgres database manually.  Gitlab provides a command `gitlab-backup create` that does it all for me
and saves the backups to `/var/opt/gitlab/backups`.  Using a pre script to run this command before your `files`
definition grabs `/var/opt/gitlab/backups` is a good example of a pre script.  Gitlab does not clean up their
own backups so using a post script to remove `/var/opt/gitlab/backups/*.gz` is a good example of a post script.
Both of which can either store the output of the command to the snapshot, or ignore output with `output=None`.




## Push Me Pull You

Serverbackups can run
* `local -> local`,
* `local -> remote` (push via SSH and rsync)
* `remote -> local` (pull via SSH and rsync)

If you just want to backup your laptop to your server, probably the `local -> remote` is simplest.  If you
use `serverbackups` in a corporate environment like I do you probably want a single backup server that
**pulls** backups from all your servers and VMS.  Pulling has the advantage of not having to put your
SSH keys on the backup server.  So all VMs cannot SSH into the backup server.  Pulling means the backup
server needs access to all VMs but not the other way around.

In my corporate environment I have a single backup server which has SSH access into the `root` account
on every server and VM.  I use the file based `/etc/serverbackups` configuration.  Each server has
a file in `/etc/serverbackups/config.d/someserver.yml`.  Using single files for each server helps
manage the backups when you have hundreds of servers.  For best results, keep these backup files in ansible for revision control and easy deployments.


# Examples


## Standalone backups.py

If you want to define your entire backup plan including the `defaults` config in a single backup.py

```bash
cd /usr/local/bin
serverbackups init-cli-script
chmod a+x backups.py
```

Edit this new file and adjust line #1 (the shebang to your python3 location

Edit the `defaults` and `servers` dictionary adding all your servers as needed.





Creates the following stubbed example

```python
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

# Set per server defaults.  Each server can override parts of this default.
defaults = {
    'enabled': True,
    'cluster': None,

    # Keep all daily up to X days back, last snapshot in a week X weeks back, last snapshot in a month X months back...
    'prune': {
        'keepDaily': 30,
        'keepWeekly': 24,
        'keepMonthly': 60,
        'keepYearly': 10,
    },

    # Rsync options
    'rsync': {
        'verbose': True,
    },

    # Source server connection details
    'source': {
        'location': 'local',  # local, ssh,
        'ssh': {
            # Only used with location=ssh
            'host': 'server.example.com',  # or IP address,
            'port': 22,
            'user': 'root',
            'key': '~/.ssh/id_rsa',
        },
    },

    # Destination server connection details
    'destination': {
        'location': 'local',  # local, ssh,
        'path': '/mnt/backups',
        'ssh': {
            # Only used with location=ssh
            'host': 'server.example.com',  # or IP address,
            'port': 22,
            'user': 'root',
            'key': '~/.ssh/id_rsa',
        },
    },

    # Backup items
    'backup': {
        # Pre scripts run on destination before this servers backups, a good place to prep files for backup
        'preScripts': {
            'gitlab': {'script': 'sudo gitlab-backup create', 'output': 'gitlab-backup.txt', 'enabled': False},
        },

        # Files to backup on the destination.  Use extra in your actual server definition for extra files.
        # Arrays are merged with defaults, so you could append to common and exclude as well
        'files': {
            'common': [
                '/etc/',
                '/usr/local/bin/',
                '/root/',
                '/home/',
                '/var/log/',
                '/var/spool/cron/',
            ],
            'extra': [],
            'exclude': [
                'lost+found',
                '.Trash-1000',
            ],
        },

        # MySQL Databases and Tables
        # Host and port are relative inside the server itself via ssh, not remote
        'mysql': {
            'enabled': False,
            'mysqlCmd': 'mysql',
            #'mysqlCmd': 'docker exec -i mysql mysql',
            'dumpCmd': 'mysqldump',
            'dumpFlags': '--quick --single-transaction --flush-logs',
            #'dumpCmd': 'docker exec -i mysql mysqldump',
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'unknown',
            # All databases minus exclusions
            'dbs': '*',
            # A list of databases (all tables)
            # 'dbs': ['db1', 'db2'],
            # A list of database with a selection of tables
            # 'dbs': [
            #     {'name': 'db1', 'tables': ['table1', 'table2']},
            #     {'name': 'db2', 'tables': '*'},
            # ],
            'excludeDbs': [
                'information_schema',
                'performance_schema',
                'lost+found',
                '#mysql50#lost+found',
            ],
        },

        # Post scripts run on destination after this servers backups, a good place to cleanup files
        'postScripts': {
            'dpkg': {'script': 'dpkg -l | gzip', 'output': 'dpkg.gz', 'enabled': False},
        },
    },
}

# Define each server to backup (each will be merged with defaults config)
servers = {
    'myserver.example.com': {
        'enabled': True,
        'cluster': 'localhost',
        # Example of local -> local backup
        'source': {
            'location': 'local',
        },
        'destination': {
            'location': 'local',
        },
        'backup': {
            'preScripts': {
                #'gitlab': {'enabled': True}
            },
            'mysql': {
                'enabled': True,
                'mysqlCmd': 'mysql',
                #'mysqlCmd': 'docker exec -i mysql mysql',
                'dumpCmd': 'mysqldump',
                'dumpFlags': '--quick --single-transaction --flush-logs',
                #'dumpCmd': 'docker exec -i mysql mysqldump',
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': 'password',
                'dbs': '*',
            },
            'postScripts': {
                # Export dpkg package list of Linux Debian
                'dpkg': {'enabled': True},
                # Example of backing up postgres database
                #'fusionauth': {'script': 'cd /tmp/ && sudo -u postgres pg_dump fusionauth | gzip', 'output': 'fusionauth.sql.gz', 'enabled': True},
                # Example of capturing script output to snapshot
                #'test2': {'script': 'ls -Hhal /etc/', 'output': 'etc.txt', 'enabled': True},
            }
        },
    },
    'myserver2.example.com': ...
}

# Initialize Backup Class
# If you are defining servers in a dictionary above
#backups = Backups(servers=servers)

# If you are defining both servers and defaults above
backups = Backups(servers=servers, defaults=defaults)

# If you are using a config.d directory (/etc/serverbackups by default)
#backups = Backups()
#backups = Backups(config_path='/etc/alternative/dir')

# Run Backups
cli.start(backups)


# Custom backups
if not cli.allowcustom(): cli.handle(); exit()
log.header("Running custom backups from " + __file__)
#################################################
# Add your custom backups code here
#################################################
print('custom stuff here, any python code you want')


# Handle CLI requests
cli.handle()
```

Running `backups.py` can be read at the top of this readme.


## Directory based /etc/serverbackups/config.d

If you have a lot of servers, a single backup.py with a massive server dictinary soon becomes a bit
unwieldy.  As an alternative you can define your `defaults` and `server` configs as separate files in a
directory (normally `/etc/serverbackups`)


Create the directory with a example `defaults.yml` and example `config.d/myserver.example.com` file

```bash
serverbackups init-directory

# Defaults to /etc/serverbackups.  Optionally, set a different directory
serverbackups init-directory --path /etc/someother/dir
```

You still need a `backups.py` which initiates the backups, see the top of the readme to create one.

Now your `backups.py` will look something like this

```python
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

# Initialize Backup Class
backups = Backups()

# Or if using an alternate directory
#backups = Backups(config_path='/etc/alternative/dir')

# Run Backups
cli.start(backups)


# Custom backups
if not cli.allowcustom(): cli.handle(); exit()
log.header("Running custom backups from " + __file__)
#################################################
# Add your custom backups code here
#################################################
print('custom stuff here, any python code you want')


# Handle CLI requests
cli.handle()
```

Running `backups.py` can be read at the top of this readme.



## As a python module/package

Serverbackups can also be used right inside your own python code as a module.  No need for a `backups.py`
though you can still optionally use `/etc/serverbackups` style files if needed.

Imagine as part of your own python program, you simply want to backup a file or database.  Using `serverbackups`
as a module import can help with this.


Example of a simple
```python
from datetime import date
from mreschke.serverbackups import Backups, log

# Optionally configure logger, but this app may have its own log settings
log.init({
    'console': {
        'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    },
    'file': {
        'enabled': True,
        'file': '/tmp/backups-{}.log'.format(date.today().strftime('%Y-%m-%d')),
    }
})

# In this example I am NOT defining a defaults config because I may just be
# backing up a single server.  Defaults are used to deduplicate common items
# in multiple servers.  If you only have one server, just define the entire config
# in the server itself

# NOTE sensible defaults are still applied to keep even a single server definition
# less verbose.  Run `serverbackups show-builtin-defaults` to see the defaults that are
# still being applied here

# Define each server to backup (each will be merged with defaults config)
# Source and Destination default to 'local'
servers = {
    'myserver.example.com': {
        'destination': {'path': '/mnt/Backups'},
        'backup': {
            'files': {
                'common': [
                    '/etc/',
                ],
                'exclude': [
                    'lost+found',
                    '.Trash-1000',
                ],
            },
        },
    },
}

# Initialize Backup Class
# If you are defining servers in a dictionary above, without a separate defaults
backups = Backups(servers=servers)

# If you are defining both servers and defaults above
#backups = Backups(servers=servers, defaults=defaults)

# If you are using a config.d directory (/etc/serverbackups by default)
#backups = Backups()
#backups = Backups(config_path='/etc/alternative/dir')

# Run backups
# Can just run them all
backups.run()

# Or can flip through each and add your own logic per server if needed
#for server in backups.servers:
    #backups.run(server)
```


# Pruning

Rsync hard-link style snapshots are pruned every time the backups run.

The `prune` server or defaults config determines the prune rates
```python
# Keep all daily up to X days back, last snapshot in a week X weeks back, last snapshot in a month X months back...
'prune': {
    'keepDaily': 30,
    'keepWeekly': 24,
    'keepMonthly': 60,
    'keepYearly': 10,
},
```

Lets say we are running the backups **twice** a day.  The above configuration means we keep each daily
backup for 30 days (meaning 60 backups since 2 a day).

Keep the LAST/LATEST weekly backup.  This means the last backup on Saturday of each week for 24 weeks.

Keep the LAST/LATEST monthly backup.  This means the last backup on the 31st of each month for 60 months (5 years)

Keep the LAST/LATEST yearly backup.  This all 12/31 backups of each year will be saved.

The default prune settings may seem like a wast of storage, but read my `Backup Strategy` notes above.  Using
rsync hard-link style snapshots saves space by using unix hard links to deduplicate files efficiently.
