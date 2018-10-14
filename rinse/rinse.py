import click

from rinse.core import install_r

# TODO Convert install from -i to just install.
@click.command()
@click.option('--install', '-i', help="Install R.")
@click.option('--version', '-v', default='3.5.0',
              help="Select the version of R to install.")
@click.option('--path', '-p', default='~/bin',
              help="Select an installation path for R.")
def cli(install, version, path):
    install_r(version, path)
