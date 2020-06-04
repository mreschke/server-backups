import os
import click
from shutil import copyfile

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    \b
    mreschke.serverbackups
    Copyright (c) 2018 Matthew Reschke
    License http://mreschke.com/license/mit
    """
    pass


@cli.command('init-cli-script')
@click.option('-f', '--filename', default='backups.py', show_default=True)
def init_cli_script(filename):
    """Initialize a new backups.py in the current folder
    """
    template = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'backups_cli.py'
    path = os.getcwd()
    file = path + '/' + filename

    if os.path.isfile(file): exit("File " + filename + " already exists")
    if click.confirm("You are about to create a new " + file + ", continue?"):
        click.secho("Creating new backup file " + file, fg='green')
        copyfile(template, file)
        click.secho("Done")
    else:
        exit("Cancelled, bye.")


@cli.command('init-directory')
@click.option('-p', '--path', default='/etc/serverbackups', show_default=True)
def init_directory(path):
    """Initialize a backup and config.d directory
    """
    defaults = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults.yml'
    server = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'server_configd.yml'

    if os.path.exists(path):
        exit("Path already exists")

    if click.confirm("You are about to create a new " + path + ", continue?"):
        click.secho("Creating new backup directory " + path, fg='green')
        os.makedirs(path)
        os.mkdir(path + '/config.d')
        copyfile(defaults, path + '/defaults.yml')
        copyfile(server, path + '/config.d/myserver.example.com.yml')
        click.secho("Done")
    else:
        exit("Cancelled, bye.")


@cli.command('example-api-module')
def example_api_module():
    """Example of using the Backup class in your own code
    """
    template = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'backups_api.py'
    with open(template, 'r') as f:
        print(f.read())


@cli.command('example-defaults')
def example_defaults():
    """Example of a default.yml config
    """
    template = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults.yml'
    with open(template, 'r') as f:
        print(f.read())


@cli.command('show-builtin-defaults')
def show_defaults():
    """Builtin sensible defaults applied when you dont
    """
    template = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'defaults_blank.yml'
    with open(template, 'r') as f:
        print(f.read())


# Initiate cli
if __name__ == '__main__':
    cli()
