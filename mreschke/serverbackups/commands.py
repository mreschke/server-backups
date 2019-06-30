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


@cli.command()
@click.option('-f', '--filename', default='backups.py', show_default=True)
def init(filename):
    """Initialize a new backups.py in the current folder"""

    #if os.geteuid() != 0: exit('Init must be run as root')

    template = os.path.dirname(os.path.realpath(__file__)) + '/templates/' + 'template.py'
    #template_config = os.path.dirname(os.path.realpath(__file__)) + '/' + 'template.yml'
    path = os.getcwd()
    file = path + '/' + filename
    #config_path = '/etc/mreschke/serverbackups'
    #config = config_path + '/config.yml'

    # Create /etc/mreschke/serverbackups/config.yml if not exists
    #if not os.path.exists(config_path):
    #    os.makedirs(config_path)
    #if not os.path.exists(config):
    #    copyfile(template_config, config)

    if os.path.isfile(file): exit(f"File {filename} already exists")
    if click.confirm(f"You are about to create a new {file}, continue?"):
        click.secho(f"Creating new backup file {file}", fg='green')
        copyfile(template, file)
        click.secho("Done")
    else:
        exit("Cancelled, bye.")


# Initiate cli
if __name__ == '__main__':
    cli()
