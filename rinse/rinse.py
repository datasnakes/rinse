import click
from os import listdir, chdir, mkdir, symlink, remove, environ
from rinse.core import InstallR
from rinse.utils import get_system_installer

@click.group()
@click.option("--install", default=None,
              help="Select the version of R to install.", show_default=True)
@click.option("--global", "-g", "glbl", default=None,
              help="Select the version of R available to your global environment.")
@click.option("--repos", "-r", default="http://cran.rstudio.com")
@click.option("--source", "method", flag_value="source", default=True, show_default=True)
@click.option("--spack", "method", flag_value="spack", show_default=True)
@click.option("--local", "method", flag_value="local", show_default=True)
@click.option("--path", "-p", default="~/.beRi",
              help="Select a relative installation path for rinse.", show_default=True)
@click.option("--name", "-n", default=".rinse",
              help="Select a name for the installation directory for R.", show_default=True)
@click.option("--config_file", default=None,
              help="A text file for sending commands to the configure script that"
                   " configures R to adapt to many kinds of systems.", show_default=True)
@click.option("--config_help", default=False,
              help="Display the help message for configuring R.", show_default=True)
@click.option("--config_clear", "-c", default=list(["all"]), multiple=True,
              help="Remove any files associated with previous attempts to install R.", show_default=True)
@click.pass_context
def rinse(ctx, install, glbl, repos, method, path, name, config_file, config_help, config_clear):
    ctx.ensure_object(dict)
    ctx.obj['path'] = path
    ctx.obj['name'] = name
    ctx.obj['method'] = method
    if path != "~/.beRi":
        raise NotImplementedError("Rinse only supports installing into the home directory at this time.")

    # Get the system dependent installation class
    installR = get_system_installer()
    Rhandle = installR(glbl=glbl, path=path, install=install, repos=repos, method=method, name=name,
                       config_file=config_file, config_help=config_help, config_clear=config_clear, init=False)
    ctx.obj['Rinstall'] = Rhandle
    if install is not None:
        Rhandle.installer()


@rinse.command(help="Initialize rinse using the /<path>/<name>.")
@click.pass_context
def init(ctx):
    # Initialize rinse
    InstallR(path=ctx.obj['path'], name=ctx.obj['name'], init=True)


@rinse.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
    help_option_names=['--chelp'],
))
@click.argument('configure_opts', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def configure(ctx, configure_opts):
    Rinstall = ctx.obj['Rinstall']
    rinse_bin = Rinstall.source_setup()
    chdir(str(rinse_bin))
    Rinstall.source_configure(rinse_bin=rinse_bin, configure_opts=configure_opts)


@rinse.command()
@click.pass_context
def make(ctx):
    pass


@rinse.command()
@click.pass_context
def install(ctx):
    pass
