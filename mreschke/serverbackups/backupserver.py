import os
#import sh
import click
import subprocess
from glob import glob
from datetime import datetime, timedelta
from .utils import dump, dd
from types import SimpleNamespace as obj


class BackupServer:
    """Backup a single server defined as a dictionary of options"""

    __author__ = "Matthew Reschke <mail@mreschke.com>"
    __license__ = "MIT"

    def __init__(self, server, options, defaults=None):
        """Initialize backup class"""

        # Merge and replace defaults and options
        options = self.merge_defaults(options, defaults)

        # Set instance variables
        self.options = options
        self.server = server
        self.snapshot = datetime.today().strftime(options['snapshotDateFormat'])
        self.snapshotPath = self.path('snapshots/' + self.snapshot)
        self.today = datetime.today().strftime("%Y%m%d")

    def run(self):
        """Run backups"""

        # Do not run if backup is disabled
        if 'enabled' in self.options.keys() and self.options['enabled'] is False:
            self.log(f"Server '{self.server}' configuration DISABLED, skipping server")
            return

        # Begin backup routine
        self.log(f"Running '{self.server}' server backup now")

        # Show YAML config in output
        self.log(f"YAML config for '{self.server}'", 1)
        dump(self.options)  # Keep this one, nice output

        # Prepare backup directories
        self.prepare()

        # Backup server items
        self.backup_files()
        #self.backup_script_output()
        #self.backup_mysql()

        # Cleanup old snapshots
        self.cleanup()

    def path(self, path=None):
        result = self.options['destination']['path'] + '/' + self.server
        if path: return result + '/' + path
        return result

    def backend(self, type=None):
        backend = self.options['destination']['location']
        if type:
            return type == backend
        return backend

    def backup_files(self):
        """
        Backup local or remote files using rsync hardlink snapshots
        See http://anouar.adlani.com/2011/12/how-to-backup-with-rsync-tar-gpg-on-osx.html
        """

        # Merge all files into a single array
        files = self.options['backup']['files']['common'] + self.options['backup']['files']['extra']
        if (not files): return

        # Create exclude file for rsync
        exclude_file = '/tmp/backups.exclude'
        if os.path.exists(exclude_file): os.remove(exclude_file)
        with open(exclude_file, 'w') as f: f.write('\n'.join(self.options['backup']['files']['exclude']))

        # Get a string of source files
        src = []
        src_location = self.options['source']['location']
        src_ssh = []
        for file in files:
            if src_location == 'local':
                src.append(file)
            elif src_location == 'ssh':
                src_ssh = self.options['destination']['ssh']
                src.append(src_ssh['user'] + '@' + src_ssh['host'] + ':' + file)
        src = ' '.join(src)  # Array to string rsync

        # Get destination string
        dest = self.path()
        dest_ssh = []
        if self.backend('local'):
            pass
        elif self.backend('ssh'):
            dest_ssh = self.options['destination']['ssh']
            dest = dest_ssh['user'] + '@' + dest_ssh['host'] + ':' + dest

        # Define backup directories
        base = dest  # Will be either local or user@server
        current = self.path('current')  # Should always be local version, not user@server
        snapshot = base + '/snapshots/' + self.snapshot  # Will be either local or user@server
        #dd(base, current, snapshot)

        # Backup new snapshot
        self.log("Backing up files {} to {}".format(src, snapshot), 1)
        params = "--archive --verbose --relative --hard-links --delete --progress --partial --compress"

        ssh_string = ''
        if src_location == 'ssh':
            ssh_string = "-e \"ssh -p {} -i {} -o LogLevel=quiet\"".format(src_ssh['port'], src_ssh['key'])
        elif self.backend('ssh'):
            ssh_string = "-e \"ssh -p {} -i {} -o LogLevel=quiet\"".format(dest_ssh['port'], dest_ssh['key'])

        # Execute rsync
        try:
            cmd = "rsync {} {} --exclude-from={} --link-dest={} {} {}".format(ssh_string, params, exclude_file, current, src, snapshot)
            #os.system(cmd)
            #subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout
            #print(results.stdout.decode('utf-8'))

            #f"-e 'ssh -p {self.sshPort} -i {self.sshKey} -o LogLevel=quiet'",

            # Works, but no stream
            #rsync = sh.rsync.bake(e=f"ssh -p {self.sshPort} -i {self.sshKey} -o LogLevel=quiet")
            #print(rsync(
                #'--archive', '--verbose', '--relative', '--hard-links', '--delete', '--progress', '--partial', '--compress',
                #f"--exclude-from={exclude_file}",
                #f"--link-dest={current}",
                #src,
                #snapshot
            #))

            #exit(cmd)

            from sarge import run
            run(cmd)

        except KeyboardInterrupt:
            exit()

    def backup_script_output(self):
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

            self.log(f"Running {name} script with output sent to {path}/{filename}", 1)
            self.execute(cmd, path + '/' + filename)

    def backup_mysql(self):
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
                self.log("Backing up MySQL database " + name + " ALL tables", 1)
                tables = ''
            else:
                self.log("Backing up MySQL database " + name + " ONLY " + str(len(tables)) + " tables", 1)
                tables = ' '.join(tables)

            # Backup database and all or some tables
            # --quick takes Retrieve rows for a table from the server a row at a time instead of reading entire table in memory, good for large tables
            # --single-transaction Issue a BEGIN SQL statement before dumping data from server.  Uses a consistent read and guarantees that data seen by muysqldump does nto change
            # --flush-logs Flush MySQL server log files before starting dump
            # --master-data Write the binary log file name and position to the output, good if this is part of a cluster
            # Output is piped ON MySQL server to gzip before being sent over SSH!  Do not use the --compress option, that is only between client and server (which is localhost anyhow usually)
            self.execute(f"mysqldump -u{user} -p'{password}' --quick --single-transaction --flush-logs {name} {tables} | gzip", dest + '/' + name + ".sql.gz")

    def prepare(self):
        """Prepare backup system"""

        # Create directory (either local or remote)
        self.log(f"Creating destination snapshot folder {self.snapshotPath}", 1)
        self.execute("mkdir -p " + self.snapshotPath)

    def cleanup(self):
        """Cleanup old snapshots"""

        # Define backup directories
        current = self.path('current')
        snapshots = self.path('snapshots')

        # Symlink latest snapshot to current link
        # Only difference is on remote, the $() is escaped
        if self.backend('local'):
            cmd = "ln -snf $(ls -1d {}/* | tail -n1) {}".format(snapshots, current)
        elif self.backend('ssh'):
            cmd = "ln -snf \\$(ls -1d {}/* | tail -n1) {}".format(snapshots, current)
        self.execute(cmd)

        # Clean old snapshots
        cleanSnapshotsAfterDays = self.options['cleanSnapshotsAfterDays']
        if cleanSnapshotsAfterDays > 0:
            dateToDelete = (datetime.today() - timedelta(cleanSnapshotsAfterDays)).strftime("%Y%m%d")
            oldSnapshots = glob(snapshots + '/' + dateToDelete + "*")

            self.log("Deleting snapshots that were made {} days ago".format(cleanSnapshotsAfterDays), 1)
            if oldSnapshots:
                for oldSnapshot in oldSnapshots:
                    self.log("Deleting old snapshot {}".format(oldSnapshot), 2)
                # Delete old snapshots
                cmd = "rm -rf {}/{}*".format(snapshots, dateToDelete)
                self.execute(cmd)
                #os.system(cmd)

    def execute(self, cmd, outputFile=None):
        """Execute command either local or over SSH"""

        #dest = self.options['destination']['location']
        dest = self.options['destination']
        if self.backend('ssh'):
            ssh = obj(**dest['ssh'])
            #cmd = "ssh -p {} -i {} -o LogLevel=quiet {}@{} \"{}\"".format(ssh.port, ssh.key, ssh.user, ssh.host, cmd)
            cmd = f"ssh -p {ssh.port} -i {ssh.key} -o LogLevel=quiet {ssh.user}@{ssh.host} \"{cmd}\""
            #dump(cmd)

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

    def merge_defaults(self, options, defaults):
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

    def log(self, log, indent=0):
        """Log string to console with indentation and colors"""
        if indent == 0:
            click.secho("\n----- " + log + " -----", fg='bright_blue')
        elif indent == 1:
            click.secho("\n------- " + log + " -----", fg='bright_cyan')
        elif indent >= 2:
            click.secho("\n--------- " + log + " -------", fg='bright_magenta')

# End Class
