import click

@click.command()
@click.option('--install', '-i', help="Will print verbose messages.")
@click.option('--version', '-v', default='3.5.0',
              help="Select the version of R to install.")
def cli(install, version):
    click.echo("Hello World")
