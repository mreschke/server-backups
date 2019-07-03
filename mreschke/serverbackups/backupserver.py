import os
#import sh
import click
import subprocess
from glob import glob
from datetime import datetime, timedelta
from .utils import dump, dd


class BackupServer:
    """Backup a single server defined as a dictionary of options"""

    __author__ = "Matthew Reschke <mail@mreschke.com>"
    __license__ = "MIT"

    def __init__(self, server, options, defaults=None):
        """Initialize backup class"""

        # Merge and replace defaults and options
        options = self._merge_defaults(options, defaults)

        # Set instance variables
        self.options = options
        self.server = server
        self.snapshot = datetime.today().strftime(options['snapshotDateFormat'])
        self.today = datetime.today().strftime("%Y%m%d")

    def run(self):
        """Run backups"""

        # Do not run if backup is disabled
        if 'enabled' in self.options.keys() and self.options['enabled'] is False:
            self._log(f"Server '{self.server}' configuration DISABLED, skipping server")
            return

        # Begin backup routine
        self._log(f"Running '{self.server}' server backup now")

        # Show YAML config in output
        self._log(f"YAML config for '{self.server}'", 1)
        dump(self.options)

        # Prepare backup directories
        self._prepare()

        # Backup server items
        self._backup_files()
        #self.backup_script_output() #CODED and DONE!
        #self.backup_mysql()

        # Cleanup old snapshots
        self._cleanup()

    def _backup_files(self):
        """
        Backup local or remote files using rsync hardlink snapshots
        See http://anouar.adlani.com/2011/12/how-to-backup-with-rsync-tar-gpg-on-osx.html
        """

        # Merge all files into a single array
        files = self.options['backup']['files']['common'] + self.options['backup']['files']['extra']
        if (not files): return

        # Create exclude file for rsync
        excludeFile = '/tmp/backups.exclude'
        if os.path.exists(excludeFile): os.remove(excludeFile)
        with open(excludeFile, 'w') as f: f.write('\n'.join(self.options['backup']['files']['exclude']))

        # Get a string of source files
        src = []
        src_location = self.options['source']['location']
        src_ssh = []
        for file in files:
            if src_location == 'local':
                src.append(file)
            elif src_location == 'ssh':
                src_ssh = self.options['destination']['ssh']
                src.append(src_ssh['user'] + '@' + src_ssh['address'] + ':' + file)
        src = ' '.join(src)  # Array to string rsync

        # Get destination string
        dest = self.options['destination']['path']
        dest_original = dest
        dest_location = self.options['destination']['location']
        dest_ssh = []
        if dest_location == 'local':
            pass
        elif dest_location == 'ssh':
            dest_ssh = self.options['destination']['ssh']
            dest = dest_ssh['user'] + '@' + dest_ssh['address'] + ':' + dest

        # Define backup directories
        base = dest + '/' + self.server
        current = dest_original + '/' + self.server + '/current' # Should always be local versoin, not user@server
        snapshot = base + '/snapshots/' + self.snapshot
        #dd(base, current, snapshot)

        # Backup new snapshot
        self._log("Backing up files {} to {}".format(src, snapshot), 1)
        params = "--archive --verbose --relative --hard-links --delete --progress --partial --compress"

        sshString = ''
        if src_location == 'ssh':
            sshString = "-e \"ssh -p {} -i {} -o LogLevel=quiet\"".format(src_ssh['port'], src_ssh['key'])
        elif dest_location == 'ssh':
            sshString = "-e \"ssh -p {} -i {} -o LogLevel=quiet\"".format(dest_ssh['port'], dest_ssh['key'])

        # Execute rsync
        try:
            cmd = "rsync {} {} --exclude-from={} --link-dest={} {} {}".format(sshString, params, excludeFile, current, src, snapshot)
            #os.system(cmd)
            #subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout
            #print(results.stdout.decode('utf-8'))

            #f"-e 'ssh -p {self.sshPort} -i {self.sshKey} -o LogLevel=quiet'",

            # Works, but no stream
            #rsync = sh.rsync.bake(e=f"ssh -p {self.sshPort} -i {self.sshKey} -o LogLevel=quiet")
            #print(rsync(
                #'--archive', '--verbose', '--relative', '--hard-links', '--delete', '--progress', '--partial', '--compress',
                #f"--exclude-from={excludeFile}",
                #f"--link-dest={current}",
                #src,
                #snapshot
            #))

            #exit(cmd)

            from sarge import run
            run(cmd)

            exit(cmd)

        except KeyboardInterrupt:
            exit()

    def _backup_script_output(self):
        """Backup the output of a script"""

        src = self.backupRoot + '/' + self.server + '/snapshots/' + self.snapshot
        for (name, script) in self.scripts.items():
            # Do not run disabled scripts
            if 'enabled' in script.keys() and script['enabled'] is False: continue

            cmd = script['script']
            output = script['output']
            path = src + '/' + os.path.dirname(output)
            filename = os.path.basename(output)
            os.makedirs(path, exist_ok=True)

            self._log(f"Running {name} script with output sent to {path}/{filename}", 1)
            self.execute(cmd, path + '/' + filename)

    def _backup_mysql(self):
        """Backup mysql databases and tables"""

        # Ignore disabled mysql entries
        if 'enabled' in self.mysql.keys() and self.mysql['enabled'] is False: return

        dest = self.backupRoot + '/' + self.server + '/snapshots/' + self.snapshot + '/mysqldump'
        #host = self.mysql['host']
        user = self.mysql['user']
        password = self.mysql['pass']
        dbs = self.mysql['dbs']
        excludeDbs = self.mysql['excludeDbs']

        # Convert dbs string or array into proper dictionary
        if isinstance(dbs, str):
            if (dbs == '*'):
                # Convert * into dictionary of all tables on system
                cmd = "mysql -u{} -p'{}' -Bse 'show databases'".format(user, password)
                databases = self.execute(cmd, [])
                databases = set(databases) - set(excludeDbs)  # Also dedups, now a set not a list
                dbs = []
                for database in databases:
                    dbs.append({'name': database, 'tables': '*'})
            else:
                dbs = [{'name': dbs, 'tables': '*'}]
        elif isinstance(dbs, list) and isinstance(dbs[0], dict):
            # Do nothing, dbs is in exact dictionary format we need
            pass
        elif isinstance(dbs, list):
            tmpDbs = []
            for db in dbs:
                tmpDbs.append({'name': db, 'tables': '*'})
            dbs = tmpDbs

        # Backup databases and tables
        os.makedirs(dest, exist_ok=True)
        for db in dbs:
            name = db['name']
            tables = db['tables']
            if tables == '*':
                self._log("Backing up MySQL database " + name + " ALL tables", 1)
                tables = ''
            else:
                self._log("Backing up MySQL database " + name + " ONLY " + str(len(tables)) + " tables", 1)
                tables = ' '.join(tables)

            # Backup database and all or some tables
            # --quick takes Retrieve rows for a table from the server a row at a time instead of reading entire table in memory, good for large tables
            # --single-transaction Issue a BEGIN SQL statement before dumping data from server.  Uses a consistent read and guarantees that data seen by muysqldump does nto change
            # --flush-logs Flush MySQL server log files before starting dump
            # --master-data Write the binary log file name and position to the output, good if this is part of a cluster
            # Output is piped ON MySQL server to gzip before being sent over SSH!  Do not use the --compress option, that is only between client and server (which is localhost anyhow usually)
            self.execute(f"mysqldump -u{user} -p'{password}' --quick --single-transaction --flush-logs {name} {tables} | gzip", dest + '/' + name + ".sql.gz")

    def _prepare(self):
        """Prepare backup system"""

        # Create local destination folders
        dest = self.options['destination']
        if dest['location'] == 'local':
            base = dest['path'] + '/' + self.server
            snapshot = base + '/snapshots/' + self.snapshot
            if not os.path.exists(base):
                self._log(f"Creating local destination folder {base}", 1)
                os.makedirs(snapshot, exist_ok=True)

    def _cleanup(self):
        """Cleanup old snapshots"""

        # Define backup directories
        dest = self.options['destination']
        base = dest['path'] + '/' + self.server
        current = base + '/current'
        snapshots = base + '/snapshots'

        # Symlink latest snapshot to current link
        os.system("ln -snf $(ls -1d {}/* | tail -n1) {}".format(snapshots, current))

        # Clean old snapshots
        cleanSnapshotsAfterDays = self.options['cleanSnapshotsAfterDays']
        if cleanSnapshotsAfterDays > 0:
            dateToDelete = (datetime.today() - timedelta(cleanSnapshotsAfterDays)).strftime("%Y%m%d")
            oldSnapshots = glob(snapshots + '/' + dateToDelete + "*")

            self._log("Deleting snapshots that were made {} days ago".format(cleanSnapshotsAfterDays), 1)
            if oldSnapshots:
                for oldSnapshot in oldSnapshots:
                    self._log("Deleting old snapshot {}".format(oldSnapshot), 2)
                # Delete old snapshots
                cmd = "rm -rf {}/{}*".format(snapshots, dateToDelete)
                os.system(cmd)

    def _execute(self, cmd, outputFile=None):
        """Execute command either local or over SSH"""

        if self.serverLocation == 'remote':
            cmd = "ssh -p {} -i {} -o LogLevel=quiet {}@{} \"{}\"".format(self.sshPort, self.sshKey, self.sshUser, self.serverIP, cmd)

        if isinstance(outputFile, str):
            # Save output to file denoted by outputFile
            os.system(cmd + ' > ' + outputFile)
        else:
            results = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            if isinstance(outputFile, list):
                # Return as list
                return results.stdout.decode('utf-8').split()
            else:
                # Return as string
                return results.stdout.decode('utf-8')

    def _merge_defaults(self, options, defaults):
        """Properly merge or replace options with defaults"""

        # Ensure options has all keys
        options.setdefault('source', {})
        options['source'].setdefault('ssh', {})
        options['destination'].setdefault('ssh', {})
        options.setdefault('backup', {})
        options['backup'].setdefault('files', {})
        options['backup'].setdefault('mysql', {})
        options['backup'].setdefault('scripts', {})
        options['backup']['files'].setdefault('common', [])
        options['backup']['files'].setdefault('extra', [])
        options['backup']['files'].setdefault('exclude', [])
        options['backup']['mysql'].setdefault('excludeDbs', [])

        # Merge arrays
        options['backup']['files']['common'] = defaults['backup']['files']['common'] + options['backup']['files']['common']
        options['backup']['files']['extra'] = defaults['backup']['files']['extra'] + options['backup']['files']['extra']
        options['backup']['files']['exclude'] = defaults['backup']['files']['exclude'] + options['backup']['files']['exclude']
        options['backup']['mysql']['excludeDbs'] = defaults['backup']['mysql']['excludeDbs'] + options['backup']['mysql']['excludeDbs']

        # Replace dictionaries
        options['source']['ssh'] = {**defaults['source']['ssh'], **options['source']['ssh']}
        options['source'] = {**defaults['source'], **options['source']}
        options['destination']['ssh'] = {**defaults['destination']['ssh'], **options['destination']['ssh']}
        options['destination'] = {**defaults['destination'], **options['destination']}

        options['backup']['mysql'] = {**defaults['backup']['mysql'], **options['backup']['mysql']}
        options['backup']['scripts'] = {**defaults['backup']['scripts'], **options['backup']['scripts']}

        # Delete invalid configs (for display, becuase it's dumped in the output)
        if options['source']['location'] == 'local': del options['source']['ssh']
        if options['destination']['location'] == 'local': del options['destination']['ssh']
        if options['backup']['mysql']['enabled'] is False: del options['backup']['mysql']

        # Finally replace remaining flat values
        options = {**defaults, **options}
        return options

    def _log(self, log, indent=0):
        """Log string to console with indentation and colors"""
        if indent == 0:
            click.secho("\n----- " + log + " -----", fg='bright_blue')
        elif indent == 1:
            click.secho("\n------- " + log + " -----", fg='bright_cyan')
        elif indent >= 2:
            click.secho("\n--------- " + log + " -------", fg='bright_magenta')

# End Class
