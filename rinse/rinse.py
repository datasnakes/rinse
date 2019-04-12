import click
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


@rinse.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
), help="Start a basic installation (e.g. - ./configure; make; make check; make install).")
@click.argument('version', default="latest")
@click.option("--clear", "-c", default=list(["all"]), multiple=True,
              help="Remove any files associated with previous attempts to install R.", show_default=True)
@click.option("--without-make", default=False, is_flag=True, show_default=True,
              help="Do not run 'make' on configured source files.")
@click.option("--without-check", "check", default=True, is_flag=True,
              show_default=True,
              help="Run 'make check' on configured source files.")
@click.option("--without-install", "installer", default=True, is_flag=True,
              show_default=True,
              help="Run 'make install' on configured source files.")
@click.option("--install-info", default=False, is_flag=True, show_default=True,
              help="Run 'make install-info' on configured source files.")
@click.option("--install-pdf", default=False, is_flag=True, show_default=True,
              help="Run 'make install-pdf' on configured source files.")
@click.option("--install-tests", default=False, is_flag=True,
              show_default=True,
              help="Run 'make install-tests' on configured source files.")
@click.option("--test-check", default=False, is_flag=True, show_default=True,
              help="Run 'make check' on test files.")
@click.option("--test-check-devel", default=False, is_flag=True,
              show_default=True,
              help="Run 'make check-devel' on test files.")
@click.option("--test-check-all", default=False, is_flag=True,
              show_default=True,
              help="Run 'make check-all' on test files.")
@click.option('--verbose', '-v', is_flag=True,
              help="Show verbose cli output.")
@click.pass_context
def install(ctx, version, clear, without_make, check, installer, install_info,
            install_pdf, install_tests, test_check, test_check_devel,
            test_check_all, verbose):
    # Configure
    ctx.invoke(configure, version=version, clear=clear, verbose=verbose)
    # Install
    ctx.invoke(make, version=version, clear=clear, without_make=without_make,
               check=check, installer=installer, install_info=install_info,
               install_pdf=install_pdf, install_tests=install_tests)
    # Test Installation
    ctx.invoke(test, version=version, clear=clear, check=test_check,
               check_devel=test_check_devel, check_all=test_check_all)


@rinse.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
    help_option_names=['--chelp'],
), help="Start a custom configuration for installing R (e.g. - ./configure --help.")
@click.argument('version', default="latest")
@click.option("--clear", "-c", default=list(["all"]), multiple=True,
              help="Remove any files associated with previous attempts to install R.", show_default=True)
@click.option("--overwrite-source", default=False,
              help="Download and overwrite the source tarball.", show_default=True)
@click.option('--verbose', '-v', is_flag=True,
              help="Show verbose cli output.")
@click.pass_context
def configure(ctx, version, clear, overwrite_source, verbose):
    installR = ctx.obj['installR']
    configure_opts = " ".join(ctx.args)
    installR = installR(version=version, path=ctx.obj['path'], name=ctx.obj['name'],
                        method="source", repos=ctx.obj['repos'],
                        config_clear=clear, config_keep=version,
                        glbl=None, init=False, verbose=verbose)
    src_file_path = installR.source_download(overwrite=overwrite_source)
    installR.source_setup(src_file_path=src_file_path)
    installR.source_configure(configure_opts=configure_opts)


@rinse.command(help="Start running custom make commands for the installation.")
@click.argument('version')
@click.option("--clear", "-c", default=list(["all"]), multiple=True,
              help="Remove any files associated with previous attempts to install R.", show_default=True)
@click.option("--without-make", default=False, is_flag=True, show_default=True,
              help="Do not run 'make' on configured source files.")
@click.option("--check", default=False, is_flag=True, show_default=True,
              help="Run 'make check' on configured source files.")
@click.option("--install", "installer", default=False, is_flag=True, show_default=True,
              help="Run 'make install' on configured source files.")
@click.option("--install-info", default=False, is_flag=True, show_default=True,
              help="Run 'make install-info' on configured source files.")
@click.option("--install-pdf", default=False, is_flag=True, show_default=True,
              help="Run 'make install-pdf' on configured source files.")
@click.option("--install-tests", default=False, is_flag=True, show_default=True,
              help="Run 'make install-tests' on configured source files.")
@click.option('--verbose', '-v', is_flag=True,
              help="Show verbose cli output.")
@click.pass_context
def make(ctx, without_make, version, clear, check, installer, install_info, install_pdf, install_tests, verbose):
    installR = ctx.obj['installR']
    installR = installR(version=version, path=ctx.obj['path'],
                        name=ctx.obj['name'], method="source", repos=ctx.obj['repos'],
                        config_clear=clear, config_keep=version, glbl=None,
                        init=False, verbose=verbose)
    installR.source_make(without_make=without_make, check=check, install=installer, install_info=install_info,
                         install_pdf=install_pdf, install_tests=install_tests)


@rinse.command(help="Start running various make installation tests.")
@click.argument('version')
@click.option("--clear", "-c", default=list(["all"]), multiple=True,
              help="Remove any files associated with previous attempts to install R.", show_default=True)
@click.option("--check", default=False, is_flag=True, show_default=True,
              help="Run 'make check' on test files.")
@click.option("--check-devel", default=False, is_flag=True, show_default=True,
              help="Run 'make check-devel' on test files.")
@click.option("--check-all", default=False, is_flag=True, show_default=True,
              help="Run 'make check-all' on test files.")
@click.option('--verbose', '-v', is_flag=True,
              help="Show verbose cli output.")
@click.pass_context
def test(ctx, version, clear, check, check_devel, check_all, verbose):
    installR = ctx.obj['installR']
    installR = installR(version=version, path=ctx.obj['path'], name=ctx.obj['name'],
                        method="source", repos=ctx.obj['repos'], config_clear=clear,
                        config_keep=version, glbl=None, init=False, verbose=verbose)
    installR.source_test(check=check, check_devel=check_devel, check_all=check_all)


@rinse.command(name="global", help="Switch the global R version.")
@click.argument('version')
@click.pass_context
def _global(ctx, version):
    installR = ctx.obj['installR']
    installR(version=version, path=ctx.obj['path'], name=ctx.obj['name'],
             method="source", repos=ctx.obj['repos'], config_clear=False,
             config_keep=version, glbl=version, init=False, verbose=False)
