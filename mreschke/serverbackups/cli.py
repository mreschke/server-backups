import os
import io
import sys
import yaml
import click
from mreschke.serverbackups.backupserver import BackupServer, dd, dump

# Exit if not running as root
# if os.geteuid() != 0: exit('This script must be run as root')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
def handle():
    """
    \b
    mreschke.serverbackups
    Copyright (c) 2018 Matthew Reschke
    License http://mreschke.com/license/mit
    """
    pass


@handle.command()
# @click.option('-a', '--all', default='backups.py', show_default=True)
@click.option('--all', is_flag=True, help="Run all backups (both config.yml and custom code)")
@click.option('--custom', is_flag=True, help="Run only custom backup code")
@click.option('--servers', is_flag=True, help="Run entire config.yml only, no custom code")
@click.option('--server', help="Run just one server from config.yml")
@click.option('--cluster', help="Run all servers in a cluster from config.yml")
def run(all, custom, servers, server, cluster):
    """Run backups"""


def load(backups):
    # Only run with proper cli flags
    if not any(x in ['--all', '--servers', '--server', '--cluster'] for x in sys.argv): return

    log("Running server backups")

    if backups.servers:
        # Passing in a dictionary of servers
        log("Backups defined as inline dictionary", 1)
    else:
        # Using config directory
        log(f"Using config dir {backups.config_path}", 1)

    # Run a single server
    if '--server' in sys.argv:
        server = sys.argv[sys.argv.index("--server") + 1]
        log(f"Running single server '{server}'", 1)

    # Run all servers in a single cluster
    elif '--cluster' in sys.argv:
        cluster = sys.argv[sys.argv.index("--cluster") + 1]
        log(f"Running servers in cluster '{cluster}'", 1)

    else:
        log(f"Running all servers defined in config", 1)
        backups.run()


def backupserversOLD(config_path='/etc/mreschke/serverbackups', servers=None, defaults=None):
    """Run the main BackupServer class from the server config.yml and config.d files"""

    # Only run with proper cli flags
    if not any(x in ['--all', '--servers', '--server', '--cluster'] for x in sys.argv): return

    log("Running server backups")

    if servers:
        # Passing in a dictionary of servers
        log("Backups defined as inline dictionary", 1)
        if not defaults:
            log("No defaults dictionary passed inline, using builtin defaults", 1)
            defaults_file = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults.yml'
            with io.open(defaults_file, 'r') as stream:
                defaults = yaml.load(stream, Loader=yaml.SafeLoader)
        else:
            log("Defaults defined as inline dictionary string", 1)
            defaults = yaml.load(defaults)
    else:
        # Using config directory
        log(f"Using config dir {config_path}", 1)
        configd_path = config_path + '/config.d'
        defaults_file = config_path + '/defaults.yml'

        # Read defaults.yml file
        with io.open(defaults_file, 'r') as stream:
            defaults = yaml.load(stream)

        # Read each server config in config.d folder
        servers = {}
        for file in os.listdir(configd_path):
            with io.open(f"{configd_path}/{file}", 'r') as stream:
                servers = {**servers, **yaml.load(stream)}

    # Run a single server
    if '--server' in sys.argv:
        server = sys.argv[sys.argv.index("--server") + 1]
        log(f"=== Running single server '{server}' defined in {configd_path}/*", 1)

    # Run all servers in a single cluster
    elif '--cluster' in sys.argv:
        cluster = sys.argv[sys.argv.index("--cluster") + 1]
        log(f"=== Running servers in cluster '{cluster}' defined in {configd_path}/*", 1)

    else:
        log(f"Running all servers defined in config", 1)
        for server, options in servers.items():
            BackupServer(server, options, defaults).run()


def allowcustom():
    """Helper for backups.py to determine if custom backup code should be run"""
    return any(x in ['--custom', '--all'] for x in sys.argv)


def log(log, indent=0):
    """Log string to console with indentation and colors"""
    if indent == 0:
        click.secho("\n### " + log + " ###", fg='green')
    elif indent == 1:
        click.secho("\n=== " + log + " ===", fg='bright_white')
    elif indent == 2:
        click.secho("\n----- " + log + " -----", fg='bright_blue')
    elif indent == 3:
        click.secho("\n------- " + log + " -----", fg='bright_cyan')
    elif indent >= 4:
        click.secho("\n--------- " + log + " -------", fg='bright_magenta')


# Explicit exports
__all__ = ['handle', 'allowcustom', 'load', 'log', 'dump', 'dd']
