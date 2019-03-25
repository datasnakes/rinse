from os import name as osname
from sys import platform as sysplat
import click
from rinse.core import LInstallR, MacInstall, WInstallR


@click.command()
@click.option("--path", "-p", default="~/",
              help="Select a relative installation path for R.")
@click.option("--install", default=None,
              help="Select the version of R to install.")
@click.option("--repos", "-r", default="http://cran.rstudio.com")
@click.option("--source", "method", flag_value="source", default=True)
@click.option("--spack", "method", flag_value="spack")
@click.option("--local", "method", flag_value="local")
@click.option("--init", "-i", default=False,
              help="Initialize rinse.")
@click.option("--name", "-n", default=".rinse",
              help="Select a name for the installation directory for R.")
@click.option("--config_file", default=None,
              help="A text file for sending commands to the configure script that"
                   "configures R to adapt to many kinds of systems.")
@click.option("--config_help", default=False,
              help="Display the help message for configuring R.")
def rinse(path, name, install, repos, method, init, config_file, config_help):
    if path != "~/":
        raise NotImplementedError("Rinse only supports installing into the home directory at this time.")

    if osname == "posix":
        if sysplat == "darwin":
            rinstall = MacInstall()
            rinstall.raise_error()
        elif "linux" in str(sysplat):
            rinstall = LInstallR(path=path, install=install, repos=repos, method=method, name=name, init=init,
                                 config_file=config_file, config_help=config_help)
            rinstall.installer()
        else:
            raise OSError("rinse does not support the %s operating system at this time." % sysplat)
    elif osname == "nt":
        if sysplat == "win32":
            rinstall = WInstallR()
            rinstall.raise_error()
        else:
            raise OSError("rinse does not support the %s operating system at this time." % sysplat)

