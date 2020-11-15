import os
import shutil
import subprocess
from datetime import date, datetime, timedelta
from types import SimpleNamespace as obj

from . import log
from .utils import dd, dump


class BackupServer:
    """Backup a single server defined as a dictionary of options"""

    __author__ = "Matthew Reschke <mail@mreschke.com>"
    __license__ = "MIT"

    def __init__(self, server, options, defaults=None):
        """Initialize backup class
        """
        # This class assumes a perfact and complete options dictionary for ONE single server
        # All defaults are already merged by the handling Backups class before being passed in
        self.options = options

        # Make option attributes for easier usage
        self.enabled = options['enabled']
        self.cluster = options['cluster']
        self.prune = obj(**options['prune'])
        self.rsync = obj(**options['rsync'])
        self.rsync.exclude_file = '/tmp/backups.exclude'
        self.src = obj(**options['source'])
        self.src.ssh = obj(**options['source']['ssh'])
        self.dest = obj(**options['destination'])
        self.dest.ssh = obj(**options['destination']['ssh'])
        self.files = obj(**options['backup']['files'])
        self.pre_scripts = []
        if 'preScripts' in options['backup']:
            for script in options['backup']['preScripts']:
                self.pre_scripts.append(obj(**{
                    'name': script,
                    **options['backup']['preScripts'][script]
                }))
        self.post_scripts = []
        if 'postScripts' in options['backup']:
            for script in options['backup']['postScripts']:
                self.post_scripts.append(obj(**{
                    'name': script,
                    **options['backup']['postScripts'][script]
                }))
        self.mysql = obj(**options['backup']['mysql'])

        # Set other attributes
        self.src.server = server
        self.dest.server = self.src.server if self.dest.location == 'local' else self.dest.ssh.host
        #self.dest.snapshot = datetime.today().strftime(options['snapshotDateFormat'])
        self.dest.snapshot = datetime.today().strftime("%Y-%m-%d_%H%M%S")
        self.dest.snapshot_path = self.path('snapshots/' + self.dest.snapshot)
        self.today = datetime.today().strftime("%Y%m%d")

    def run(self):
        """Run backups
        """
        # Do not run if backup is disabled
        if not self.enabled:
            log.notice("Server {} configuration DISABLED, skipping server".format(self.src.server))
            return

        # Begin backup routine
        log.line()
        log.header2("Backing up server {}".format(self.src.server))
        log.line()
        log.bullet2("Direction {} -> {}".format(self.src.location, self.dest.location))
        log.bullet2("SRC server={}, type={}".format(self.src.server, self.src.location))
        log.bullet2("DEST server={}, type={}".format(self.dest.server, self.dest.location))

        # Show YAML config in output
        log.bullet2("YAML config for {}".format(self.src.server))
        log.info((self.options))
        dump(self.options)  # Keep this one, nice output

        # Prepare backup directories
        self.prepare()

        # Run pre-scripts
        self.backup_scripts('pre', self.pre_scripts)

        # Backup files
        self.backup_files()

        # Backup MySQL
        self.backup_mysql()

        # Run post-scripts
        self.backup_scripts('post', self.post_scripts)

        # Cleanup old snapshots
        self.cleanup()

    def prepare(self):
        """Prepare backup system
        """
        log.header4("Preparing System")
        # Create DEST snapshot directory
        log.bullet("Creating DEST snapshot folder {}:{}".format(self.dest.server, self.dest.snapshot_path))
        self.execute_dest("mkdir -p " + self.dest.snapshot_path)

    def backup_scripts(self, type, scripts):
        """Execute script on DEST and optionally backup the output to snapshot folder
        """
        for script in scripts:
            if not script.enabled: continue
            log.header4("Running {} script '{}'".format(type.upper(), script.name))
            output = None
            if hasattr(script, 'output'):
                log.bullet("Saving script output to '{}' to DEST snapshot".format(script.output))
                output = self.dest.snapshot_path + '/' + script.output
            self.execute(cmd=script.script, outfile=output)

    def backup_files(self):
        """Backup local or remote files using rsync hardlink snapshots
        See http://anouar.adlani.com/2011/12/how-to-backup-with-rsync-tar-gpg-on-osx.html
        """
        log.header4("Backing up files")

        # Merge all files into a single array
        files = self.options['backup']['files']['common'] + self.options['backup']['files']['extra']
        if (not files): return

        # Create exclude file for rsync
        if os.path.exists(self.rsync.exclude_file): os.remove(self.rsync.exclude_file)
        with open(self.rsync.exclude_file, 'w') as f: f.write('\n'.join(self.options['backup']['files']['exclude']))

        # Get a string of source files.  This means many files can be backed up
        # with a single rsync command
        src = []
        for file in files:
            if self.src.location == 'local':
                src.append(file)
            elif self.src.location == 'ssh':
                src.append(self.src.ssh.user + "@" + self.src.ssh.host + ":" + file)
        src = ' '.join(src)  # Array to string rsync

        # Get destination string
        dest = self.path()
        if self.dest.location == 'ssh':
            dest = self.dest.ssh.user + "@" + self.dest.ssh.host + ":" + dest

        # Snapshot folder (from dest, so either local or user@server remote)
        snapshot = dest + '/snapshots/' + self.dest.snapshot  # Will be either local or user@server

        # Current folder for rsync --link-dest, even if rsyncing to remove server this is a / local style path
        # not user@server.  Rsync is smart enough to know you mean the remote servers filesystem here.
        current = self.path('current')
        #dd(src, dest, current, snapshot)

        # Backup new snapshot
        log.bullet("Backing up files {} to {}".format(src, snapshot))
        params = "--archive --relative --hard-links --delete --progress --partial --compress "
        if self.rsync.verbose:
            params += "--verbose "
        else:
            params += "--quiet "

        ssh_string = ''
        if self.src.location == 'ssh':
            ssh_string = "-e \"ssh -p {} -i {} -o LogLevel=quiet\"".format(self.src.ssh.port, self.src.ssh.key)
        elif self.dest.location == 'ssh':
            ssh_string = "-e \"ssh -p {} -i {} -o LogLevel=quiet\"".format(self.dest.ssh.port, self.dest.ssh.key)

        # Execute rsync
        try:
            cmd = "rsync {} {} --exclude-from={} --link-dest={} {} {}".format(ssh_string, params, self.rsync.exclude_file, current, src, snapshot)

            # Always executed local (where backup script is run)
            log.bullet4(cmd)
            os.system(cmd)

        except KeyboardInterrupt:
            exit()

    def backup_mysql(self):
        """Backup mysql databases and tables
        """
        log.header4("Backing up MySQL databases")

        # Ignore disabled mysql entries
        if not self.mysql.enabled: return

        # Always local, the self.execute below will add proper SSH output as needed
        dest = self.dest.snapshot_path + '/mysqldump'
        self.execute_dest("mkdir -p " + dest)

        # Mysql Connection
        mysql_cmd = self.mysql.mysqlCmd
        dump_cmd = self.mysql.dumpCmd
        host = self.mysql.host
        port = self.mysql.port
        user = self.mysql.user
        password = self.mysql.password
        dbs = self.mysql.dbs
        excludeDbs = self.mysql.excludeDbs

        # Convert dbs string or array into proper array of {name, tables[]} dictionary
        if isinstance(dbs, str):
            if (dbs == '*'):
                # Convert * into dictionary of all tables on system
                cmd = mysql_cmd + " --user={} --password='{}' --host={} --port={} -Bse 'show databases'".format(user, password, host, port)
                databases = self.execute(cmd=cmd, output_list=True, skip_logging=True)  # Skip logging as it has password
                databases = set(databases) - set(excludeDbs)  # Also dedups, now a set not a list
                dbs = []
                for database in databases:
                    dbs.append({'name': database, 'tables': '*'})
            else:
                dbs = [{'name': dbs, 'tables': '*'}]
        elif isinstance(dbs, list) and isinstance(dbs[0], dict):
            # Do nothing, dbs is in exact dictionary format we need
            # Just end the if
            pass
        elif isinstance(dbs, list):
            tmpDbs = []
            for db in dbs:
                tmpDbs.append({'name': db, 'tables': '*'})
            dbs = tmpDbs

        # Backup databases and tables
        for db in dbs:
            name = db['name']
            tables = db['tables']
            if tables == '*':
                log.bullet("Backing up MySQL database '{}', ALL tables".format(name))
                tables = ''
            else:
                log.bullet("Backing up MySQL database '{}', ONLY {} tables".format(name, str(len(tables))))
                tables = ' '.join(tables)

            # Backup database and all or some tables
            # --quick takes Retrieve rows for a table from the server a row at a time instead of reading entire table in memory, good for large tables
            # --single-transaction Issue a BEGIN SQL statement before dumping data from server.  Uses a consistent read and guarantees that data seen by muysqldump does nto change
            # --flush-logs Flush MySQL server log files before starting dump
            # --master-data Write the binary log file name and position to the output, good if this is part of a cluster

            # Dump flags are optionaly even in defaults.  I only added because MariaDB 10.1 does NOT like flush-logs
            flags = "--quick --single-transaction --flush-logs"
            if hasattr(self.mysql, 'dumpFlags'):
                flags = self.mysql.dumpFlags

            # Output is piped ON MySQL server to gzip before being sent over SSH!  Do not use the --compress option, that is only between client and server (which is localhost anyhow usually)
            cmd = dump_cmd + " --user={} --password='{}' --host={} --port={} {} {} {} | gzip".format(user, password, host, port, flags, name, tables)
            self.execute(cmd=cmd, outfile=dest + '/' + name + ".sql.gz", skip_logging=True, dryrun=False)

    def cleanup(self):
        """Cleanup old snapshots
        """
        log.header4("Cleaning up system and symlinking current snapshot")

        # Delete rsync exclude file
        if os.path.exists(self.rsync.exclude_file): os.remove(self.rsync.exclude_file)

        # Define backup directories
        current = self.path('current')
        snapshots = self.path('snapshots')

        # Symlink latest snapshot to current link
        # Only difference is on remote, the $() is escaped
        if self.dest.location == 'local':
            cmd = "ln -snf $(ls -1d {}/* | tail -n1) {}".format(snapshots, current)
        else:
            cmd = "ln -snf \\$(ls -1d {}/* | tail -n1) {}".format(snapshots, current)
        self.execute_dest(cmd)

        # Prune old snapshots according to daily, weekly, monthly and yearly prune variables
        self.prune_snapshots()

    def prune_snapshots(self):
        """Prune old snapshots according to daily, weekly, monthly and yearly prune variables
        """
        log.header4("Pruning Snapshots (keepDaily:{}, keepWeekly:{}, keepMonthly:{}, keepYearly:{})".format(self.prune.keepDaily, self.prune.keepWeekly, self.prune.keepMonthly, self.prune.keepYearly))

        # Define snapshot date parser helper
        def dates(snapshot):
            # Snapshot date and snapshot time, and weekday
            sd = date(int(snapshot[0:4]), int(snapshot[5:7]), int(snapshot[8:10]))
            st = int(snapshot[11:-1])
            wd = int(sd.strftime("%w"))  # 0=Sunday, 6=Saturday
            return (sd, st, wd)

        # Snapshot folder and start date
        snapshot_path = self.path('snapshots')
        today = date.today()

        # FAKER DATA for Testing Only
        # start = date(2009, 1, 1)
        # while start < today:
        #     start += timedelta(days=1)
        #     snapshot = snapshot_path + '/' + start.strftime("%Y-%m-%d_010101")
        #     if not os.path.exists(snapshot): os.mkdir(snapshot)
        #     snapshot = snapshot_path + '/' + start.strftime("%Y-%m-%d_020101")
        #     if not os.path.exists(snapshot): os.mkdir(snapshot)

        # Get all snapshot folders (always on destination)
        snapshots = sorted(self.execute_dest("/bin/ls " + snapshot_path))
        if len(snapshots) == 0: return

        # Find days to keep
        # Keeps multiple of the same day back to keepDaily
        keep_daily = []
        for i, snapshot in enumerate(snapshots):
            # Get snapshot date and time
            sd, st, wd = dates(snapshot)

            days_back = today - timedelta(days=self.prune.keepDaily)
            if sd >= days_back:
                keep_daily.append(snapshot)

        # Remove keep_daily from snapshots
        snapshots = [x for x in snapshots if x not in keep_daily]
        if len(snapshots) == 0: return

        # Get list of only latest snapshot of each day
        # Remove any snapshots of the SAME day that are earlier in the day, keeping the latest of each day
        add = ''
        current = dates(snapshots[0])[0]  # date
        latest_days = []
        for i, snapshot in enumerate(snapshots):
            # Get snapshot date and time
            sd, st, wd = dates(snapshot)

            if sd != current:
                latest_days.append(add)
            add = snapshot
            current = sd
        latest_days.append(snapshots[-1])
        snapshots = latest_days

        # Get list of only latest snapshots of each week
        add = ''
        current = dates(snapshots[0])[2]  # week day
        latest_weeks = []
        for i, snapshot in enumerate(snapshots):
            # Get snapshot date and time
            sd, st, wd = dates(snapshot)

            if wd < current:
                latest_weeks.append(add)
            add = snapshot
            current = wd

        # Take top latest weekly snapshots according to self.prune.keepWeekly
        keep_weekly = latest_weeks[-self.prune.keepWeekly:]

        # Remove keep_weekly from snapshots
        snapshots = [x for x in snapshots if x not in keep_weekly]
        if len(snapshots) == 0: return

        # Get list of only latest snapshots of each month
        add = ''
        current = dates(snapshots[0])[0].day
        latest_months = []
        for i, snapshot in enumerate(snapshots):
            # Get snapshot date and time
            sd, st, wd = dates(snapshot)

            if sd.day < current:
                latest_months.append(add)
            add = snapshot
            current = sd.day

        # Take top latest monthly snapshots according to self.prune.keepMonthly
        keep_monthly = latest_months[-self.prune.keepMonthly:]

        # Remove keep_monthly from snapshots
        snapshots = [x for x in snapshots if x not in keep_monthly]
        if len(snapshots) == 0: return

        # Get list of only latest snapshots of each year
        add = ''
        current = dates(snapshots[0])[0].month
        latest_years = []
        for i, snapshot in enumerate(snapshots):
            # Get snapshot date and time
            sd, st, wd = dates(snapshot)

            if sd.month < current:
                latest_years.append(add)
            add = snapshot
            current = sd.month

        # Take top latest yearly snapshots according to self.prune.keepYearly
        keep_yearly = latest_years[-self.prune.keepYearly:]

        # Remove keep_monthly from snapshots
        snapshots = [x for x in snapshots if x not in keep_yearly]
        if len(snapshots) == 0: return

        # Now we have a perfect set of snapshots to keep
        # dump('KEEP DAILY', keep_daily)
        # dump('KEEP WEEKLY', keep_weekly)
        # dump('KEEP MONTHLY', keep_monthly)
        # dump('KEEP YEARLY', keep_yearly)

        # Delete all other snapshot folders besides those in keep_*
        # Have to get a fresh list of actual files and subtract daily, weekly, monthly, yearly
        # Cannot simply use snapshots as is not, because we removed all files of the same day
        oldsnapshots = sorted(self.execute_dest("/bin/ls " + snapshot_path))
        oldsnapshots = [x for x in oldsnapshots if x not in keep_daily]
        oldsnapshots = [x for x in oldsnapshots if x not in keep_weekly]
        oldsnapshots = [x for x in oldsnapshots if x not in keep_monthly]
        oldsnapshots = [x for x in oldsnapshots if x not in keep_yearly]
        for oldsnapshot in oldsnapshots:
            fullpath = snapshot_path + '/' + oldsnapshot
            log.bullet("Deleting old snapshot {}".format(fullpath))
            self.execute_dest("/bin/rm -rf '{}'".format(fullpath))

    def execute(self, cmd, outfile=None, output_list=False, skip_logging=False, dryrun=False):
        """Execute command local or remote with optional output saved to snapshot folder
        local->local = script=local, output=local
        local->remote = script=local, output=remote
        remote->local = script=remote, output=local
        """
        # Get src and dest location types (local or ssh)
        src = self.src.location
        dest = self.dest.location
        outfile_cmd = ''

        # local->local = script=local, output=local
        if src == 'local' and dest == 'local':
            # Execute script locally, save output locally
            # cat /etc/hosts > /snapshot/dir/hosts
            if outfile: outfile_cmd = cmd + " > " + str(outfile)
        elif src == 'local' and dest == 'ssh':
            # Execute script locally, save output remotely
            # cat /etc/hosts | ssh toor@linstore 'cat > /snapshot/dir/hosts'
            if outfile: outfile_cmd = cmd + " | " + self.ssh_string('dest') + "'cat > " + str(outfile) + "'"
        elif src == 'ssh' and dest == 'local':
            # Execute script remotely, save output locally
            #ssh toor@linstore cat /etc/hosts > /snapshot/dir/hosts
            cmd = self.ssh_string('src') + " \"" + cmd + "\""
            if outfile: outfile_cmd = cmd + " >  " + str(outfile)

        if dryrun:
            cmd = 'DRYRUN: ' + cmd
            outfile_cmd = 'DRYRUN: ' + outfile_cmd

        if outfile is None and output_list is False:
            # Execute the command, no output
            if not skip_logging: log.bullet4(cmd)
            if not dryrun: os.system(cmd)
        else:
            if outfile:
                # Execute the command and > output to outfile
                if not skip_logging: log.bullet4(outfile_cmd)
                if not dryrun: os.system(outfile_cmd)
            elif output_list:
                # Execute the command and capture output to python list
                if not skip_logging: log.bullet4(cmd)
                if not dryrun: return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').split()
                return []

    def execute_dest(self, cmd, skip_logging=False, dryrun=False):
        """Execute command without output on DEST
        """
        if self.dest.location == 'ssh':
            cmd = self.ssh_string('dest') + " \"" + cmd + "\""

        # Execute the command and capture output to python list
        if not skip_logging: log.bullet4(cmd)
        if not dryrun: return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').split()

    def path(self, path=None):
        """Get the DEST server backup path (without snapshot or current, just server backup root)
        """
        result = self.dest.path + '/' + self.src.server
        if path: return result + '/' + path
        return result

    def ssh_string(self, location):
        """Get an ssh connection string for src or dest
        """
        if location == 'src':
            return ("ssh"
                + " -p " + str(self.src.ssh.port)
                + " -i " + self.src.ssh.key
                + " -o LogLevel=quiet "
                + self.src.ssh.user + "@" + self.src.ssh.host
                + " "
            )
        elif location == 'dest':
            return ("ssh"
                + " -p " + str(self.dest.ssh.port)
                + " -i " + self.dest.ssh.key
                + " -o LogLevel=quiet "
                + self.dest.ssh.user + "@" + self.dest.ssh.host
                + " "
            )
