from cookiecutter.main import cookiecutter
from pathlib import Path
from os import listdir, chdir, mkdir
from pkg_resources import resource_filename
from rinse import cookies
import requests as re
import tarfile
import subprocess as sp


class InstallR(object):

    def __init__(self, path, install, repos, method, name, init, config_file, config_help):
        self.method = method  # source for now spack for later
        self.name = name
        self.path = Path(path).expanduser().absolute()
        self.rinse_path = self.path / self.name
        self.install = install
        self.repos = repos
        self.config_file = config_file
        self.config_help = config_help

        # Initialization step
        self.cookie_jar = Path(resource_filename(cookies.__name__, ''))
        if self.rinse_path.exists() and init is True:
            raise FileExistsError("The rinse path you have set already exists: %s" % self.path)
        elif not self.rinse_path.exists() and init is True:
            init_cookie = self.cookie_jar / Path("init")
            e_c = {
                "rinse_init_dir": self.name
            }
            cookiecutter(str(init_cookie), no_input=True, extra_context=e_c, output_dir=str(self.path))


class LInstallR(InstallR):

    def __init__(self, path, install, repos, method, name, init, config_file, config_help):
        super().__init__(path=path, install=install, repos=repos, method=method, name=name, init=init,
                         config_file=config_file, config_help=config_help)

    def installer(self):
        if self.method == "source":
            self.use_source()
        elif self.method == "spack":
            self.use_spack()
        elif self.method == "local":
            self.use_local()

    def use_source(self):
        if self.install == "latest":
            url = "%s/src/base/R-latest.tar.gz" % self.repos
        else:
            major_version = self.install[0:1]
            url = "%s/src/base/R-%s/R-%s.tar.gz" % (self.repos, major_version, self.install)
        # Download, extract, and create a bin for configuring R
        rinse_bin = self.source_setup(url=url)
        if self.config_help:
            chdir(str(rinse_bin.parent))
            config_proc = sp.Popen(['./configure', '--help'], shell=True)
            config_proc.wait(timeout=10)
        else:
            chdir(str(rinse_bin))
            self.source_configure(rinse_bin=rinse_bin)
            self.source_make()

    def source_setup(self, url):
        # Download the source tarball
        r_src_url = re.get(url=url)
        r_src_path = self.path / self.name / "src" / "cran" / Path(url).name
        open(str(r_src_path), 'wb').write(r_src_url.content)

        # Get directory list before extraction
        bef_list = listdir(str(r_src_path.parent))

        # Extract the contents of the source tarball
        with tarfile.open(str(r_src_path)) as r_tar_file:
            r_tar_file.extractall(path=str(r_src_path.parent))
        # Get directory list after extraction
        aft_list = listdir(str(r_src_path.parent))
        r_extracted = list(set(aft_list).difference(bef_list))[0]
        r_ext_path = r_src_path.parent / Path(r_extracted)
        rinse_bin = r_ext_path / "rinse-bin"
        # Create rinse-bin for the configuration process
        mkdir(str(rinse_bin))
        return rinse_bin

    def source_configure(self, rinse_bin):
        # Set up R_HOME
        r_home_name = Path(rinse_bin).parent.name
        r_home = Path(rinse_bin).parent.parent.parent.parent / "lib" / "cran" / r_home_name
        r_home.mkdir()
        if self.config_file:
            with open(self.config_file, 'r') as c_file:
                config_cmds = c_file.read()
            config_proc = sp.Popen(['../configure', '--prefix=%s' % str(r_home), config_cmds], shell=True)
            config_proc.wait()
        else:
            config_proc = sp.Popen(['../configure', '--prefix=%s' % str(r_home)], shell=True)
            config_proc.wait()

    def source_make(self):
        make_proc = sp.Popen(['make'], shell=True)
        make_proc.wait()
        make_check = sp.Popen(['make', 'check'], shell=True)
        make_check.wait()
        make_install = sp.Popen(['make', 'install'], shell=True)
        make_install.wait()
        make_tests = sp.Popen(['make', 'install-tests'], shell=True)
        make_tests.wait()

    def use_local(self):
        raise NotImplementedError("Local installation is not supported at this time.")

    def use_spack(self):
        raise NotImplementedError("Installation with spack is not supported at this time.")


class MacInstall(InstallR):

    def __init__(self, path, install, repos, method, name, init, config_file, config_help):
        super().__init__(path=path, install=install, repos=repos, method=method, name=name,
                         init=init, config_file=config_file, config_help=config_help)

    def raise_error(self):
        raise NotImplementedError("Installation of R with rinse on MacOS is not supported at this time.")


class WInstallR(InstallR):

    def __init__(self, path, install, repos, method, name, init, config_file, config_help):
        super().__init__(path=path, install=install, repos=repos, method=method, name=name,
                         init=init, config_file=config_file, config_help=config_help)

    def raise_error(self):
        raise NotImplementedError("Installation of R with rinse on Windows is not supported at this time.")

