import sys

import click

from . import log
from .utils import dd, dump

# Exit if not running as root - NO, can be use backups too
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


def start(backups):
    # Only run with proper cli flags
    if 'run' not in sys.argv and '--help' not in sys.argv:
        log.error('Missing run option, see --help')
        exit(1)

    if not any(x in ['--all', '--servers', '--server', '--cluster'] for x in sys.argv):
        if 'run' in sys.argv and '--custom' not in sys.argv and '--help' not in sys.argv and '-h' not in sys.argv:
            log.error('Missing run option, see --help')
            exit(1)
        return

    log.blank()
    log.separator()
    log.header3("Running server backups")
    log.separator()

    if backups.servers:
        # Passing in a dictionary of servers
        log.bullet("Backups defined as inline dictionary")
    else:
        # Using config directory
        log.bullet("Using config dir {}".format(backups.config_path))

    # Run a single server
    if '--server' in sys.argv:
        server = sys.argv[sys.argv.index("--server") + 1]
        log.bullet("Running single server '{}'".format(server))
        backups.run(server=server)

    # Run all servers in a single cluster
    elif '--cluster' in sys.argv:
        cluster = sys.argv[sys.argv.index("--cluster") + 1]
        log.bullet("Running servers in cluster '{}'".format(cluster))
        backups.run(cluster=cluster)

    else:
        log.bullet("Running all servers defined in config")
        backups.run()


# def backupserversOLD(config_path='/etc/mreschke/serverbackups', servers=None, defaults=None):
#     """Run the main BackupServer class from the server config.yml and config.d files
#     """
#     # Only run with proper cli flags
#     if not any(x in ['--all', '--servers', '--server', '--cluster'] for x in sys.argv): return

#     log.blank()
#     log.separator()
#     log.header3("Running server backups")
#     log.separator()

#     if servers:
#         # Passing in a dictionary of servers
#         log.bullet("Backups defined as inline dictionary")
#         if not defaults:
#             log.bullet("No DEFAULTS dictionary passed inline, using builtin DEFAULTS")
#             defaults_file = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults.yml'
#             with io.open(defaults_file, 'r') as stream:
#                 defaults = yaml.load(stream, Loader=yaml.SafeLoader)
#         else:
#             log.bullet("DEFAULTS defined as inline dictionary string")
#             defaults = yaml.load(defaults)
#     else:
#         # Using config directory
#         log.bullet("Using config dir {}".format(config_path))
#         configd_path = config_path + '/config.d'
#         defaults_file = config_path + '/defaults.yml'

#         # Read defaults.yml file
#         with io.open(defaults_file, 'r') as stream:
#             defaults = yaml.load(stream)

#         # Read each server config in config.d folder
#         servers = {}
#         for file in os.listdir(configd_path):
#             with io.open(configd_path + "/" + file, 'r') as stream:
#                 servers = {**servers, **yaml.load(stream)}

#     # Run a single server
#     if '--server' in sys.argv:
#         server = sys.argv[sys.argv.index("--server") + 1]
#         log.bullet("Running single server '{}'".format(server))
#         BackupServer(log, server, servers[server], defaults).run()

#     # Run all servers in a single cluster
#     elif '--cluster' in sys.argv:
#         cluster = sys.argv[sys.argv.index("--cluster") + 1]
#         log.bullet("Running servers in cluster '" + cluster + "'")
#         for server, options in servers.items():
#             if options['cluster'] == cluster:
#                 BackupServer(log, server, options, defaults).run()

#     else:
#         log.bullet("Running all servers defined in config")
#         for server, options in servers.items():
#             BackupServer(log, server, options, defaults).run()

def allowcustom():
    """Helper for backups.py to determine if custom backup code should be run
    """
    return any(x in ['--custom', '--all'] for x in sys.argv)


# Explicit exports
__all__ = ['handle', 'allowcustom', 'start', 'log', 'dump', 'dd']
