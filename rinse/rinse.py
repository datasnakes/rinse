import click
from os import listdir, chdir, mkdir, symlink, remove, environ
from rinse.core import BaseInstallR
from rinse.utils import get_system_installer


@click.group()
# @click.option("--global", "-g", "glbl", default=None,
#               help="Select the version of R available to your global environment.")
@click.option("--source", "method", flag_value="source", default=True, show_default=True)
@click.option("--spack", "method", flag_value="spack", show_default=True)
@click.option("--local", "method", flag_value="local", show_default=True)
@click.option("--path", "-p", default="~/.beRi",
              help="An absolute installation path for rinse.", show_default=True)
@click.option("--name", "-n", default=".rinse",
              help="A directory name for rinse.", show_default=True)
@click.option("--repos", "-r", default="http://cran.rstudio.com",
              help="The repository to use for downloading source files.")
@click.pass_context
def rinse(ctx, repos, method, path, name):
    ctx.ensure_object(dict)
    ctx.obj['path'] = path
    ctx.obj['name'] = name
    ctx.obj['method'] = method
    ctx.obj['repos'] = repos
    if path != "~/.beRi":
        raise NotImplementedError("Rinse only supports installing into the home directory at this time.")

    # Get the system dependent installation class
    installR = get_system_installer()
    ctx.obj['installR'] = installR


@rinse.command(help="Initialize rinse using the /<path>/<name>.")
@click.pass_context
def init(ctx):
    # Initialize rinse
    BaseInstallR(path=ctx.obj['path'], name=ctx.obj['name'], init=True)


@rinse.command(name="global")
@click.pass_context
def _global(ctx):
    pass


@rinse.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
    help_option_names=['--chelp'],
))
@click.argument('version', default="latest")
@click.option("--clear", "-c", default=list(["all"]), multiple=True,
              help="Remove any files associated with previous attempts to install R.", show_default=True)
@click.argument('configure_opts', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def install(ctx, version, clear):
    ctx.obj['version'] = version
    ctx.obj['clear'] = clear
    ctx.invoke(configure, configure_opts=version)
    ctx.invoke(make)


@rinse.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
    help_option_names=['--chelp'],
))
@click.argument('version', default="latest")
@click.option("--clear", "-c", default=list(["all"]), multiple=True,
              help="Remove any files associated with previous attempts to install R.", show_default=True)
@click.argument('configure_opts', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def configure(ctx, version, clear, configure_opts):
    installR = ctx.obj['installR']
    installR = installR(version=version, path=ctx.obj['path'], name=ctx.obj['name'], method="source",
                        repos=ctx.obj['repos'], config_clear=clear, glbl=None, init=False)
    src_file_path = installR.source_download()
    rinse_bin = installR.source_setup(src_file_path=src_file_path)
    chdir(str(rinse_bin))
    installR.source_configure(rinse_bin=rinse_bin, configure_opts=configure_opts)


@rinse.command()
@click.pass_context
def make(ctx):
    pass
