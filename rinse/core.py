from cookiecutter.main import cookiecutter
from pathlib import Path
from os import listdir, chdir, mkdir, symlink, remove, environ
from shutil import rmtree
from pkg_resources import resource_filename
from rinse import cookies
import requests as re
import tarfile
from rinse.utils import system_cmd
import subprocess as sp
import logging


class BaseInstallR(object):

    def __init__(self, path, name, version=None, repos=None, method=None, init=None, verbose=False):
        # Rinse path setup
        self.name = name
        self.path = Path(path).expanduser().absolute()
        self.verbose = verbose

        self.rinse_path = self.path / self.name
        self.tmp_path = self.rinse_path / "tmp"
        self.src_path = self.rinse_path / "src"
        self.lib_path = self.rinse_path / "lib"
        self.bin_path = self.rinse_path / "bin"
        
        # Set up logger
        # Change level of logger based on verbose paramater.
        if self.verbose:
            logging.basicConfig(format='[%(levelname)s | %(name)s - line %(lineno)d]: %(message)s')
            # Filter the debug logging
            logging.getLogger("rinse").setLevel(logging.DEBUG)
        else:
            logging.basicConfig(format='%(levelname)s: %(message)s',
                                level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialization step
        self.cookie_jar = Path(resource_filename(cookies.__name__, ''))
        if init:
            if self.rinse_path.exists():
                raise FileExistsError("The rinse path you have set already exists: %s" % self.rinse_path)
            elif not self.rinse_path.exists():
                self.initial_setup()
                self.logger.info("Initializing rinse.")
        elif not self.rinse_path.exists():
            raise EnvironmentError("You have not initialized rinse yet.  Please run 'rinse init' to continue.")

        # Create class variables from parameters
        self.method = method  # source for now spack for later
        if version == "--help":
            self.version = "latest"
        else:
            self.version = version
        self.repos = repos

    def initial_setup(self):
        # Prepare and run cookiecutter
        init_cookie = self.cookie_jar / Path("init")
        e_c = {
            "rinse_init_dir": self.name
        }
        cookiecutter(str(init_cookie), no_input=True, extra_context=e_c, output_dir=str(self.path))
        # Setup environment variables
        if str(self.bin_path) not in environ["PATH"]:
            # See if .bash_profile or .profile exists
            bash_prof = Path("~/.bash_profile").expanduser().absolute()
            sh_prof = Path("~/.profile").expanduser().absolute()
            if not bash_prof.exists():
                if not sh_prof.exists():
                    bash_prof.touch(mode=0o700)
                    set_prof = bash_prof
                else:
                    set_prof = sh_prof
            else:
                set_prof = bash_prof
            self.logger.info("Setting the PATH in %s" % str(set_prof))
            # Use the set .*profile to append to PATH
            with open(str(set_prof), 'r') as prof:
                _ = prof.read()
                bas_prof_export = "export PATH=\"%s:$PATH\"" % str(self.bin_path)
                if bas_prof_export not in _:
                    with open(str(set_prof), "a+") as b_prof:
                        b_prof.write("export PATH=\"%s:$PATH\"" % str(self.bin_path))
                    cmd = ["source %s" % str(set_prof)]
                    stdout = system_cmd(cmd=cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)


class LinuxInstallR(BaseInstallR):

    def __init__(self, version, method, name, path, repos, glbl, config_clear, config_keep, init, verbose):
        super().__init__(path=path, version=version, repos=repos, method=method, name=name, init=init, verbose=verbose)
        self.config_clear = config_clear
        self.config_keep = config_keep
        if glbl is not None:
            self.global_interpreter(version=glbl)

    def installer(self):
        if self.method == "source":
            src_file_path = self.source_download()
            self.source_setup(src_file_path=src_file_path)
            self.source_configure()
            self.source_make()
        elif self.method == "spack":
            self.use_spack()
        elif self.method == "local":
            self.use_local()

    def source_download(self, overwrite):
        # Download the source tarball
        if self.version == "latest":
            url = "%s/src/base/R-latest.tar.gz" % self.repos
            self.logger.info("Downloading the latest R version.")
        else:
            major_version = self.version[0:1]
            url = "%s/src/base/R-%s/R-%s.tar.gz" % (self.repos, major_version, self.version)
            self.logger.info("Downloading R version %s" % major_version)
        src_file_url = re.get(url=url)
        src_file_path = self.src_path / "cran" / Path(url).name
        if (not src_file_path.exists()) or overwrite:
            open(str(src_file_path), 'wb').write(src_file_url.content)
        return src_file_path

    def source_setup(self, src_file_path):
        # Check the temp directory if necessary
        self.clear_tmp_dir()
        # Extract the contents of the source tarball
        with tarfile.open(str(src_file_path)) as r_tar_file:
            self.logger.debug("Extracting source tarball.")
            r_tar_file.extractall(path=str(self.tmp_path))

        # Configure rinse-bin for the configuration process
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        if rinse_bin.exists():
            rmtree(rinse_bin)
            self.logger.debug("Removing existing rinse folder.")
        mkdir(str(rinse_bin))
        return rinse_bin

    def source_configure(self, configure_opts=None):
        # Set up R_HOME
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        chdir(str(rinse_bin))
        r_home_name = Path(rinse_bin).parent.name
        r_home = self.lib_path / "cran" / r_home_name
        if not r_home.exists():
            self.logger.debug("Creating R home directory in %s" % r_home)
            r_home.mkdir()
        if configure_opts == "--help":
            config_proc = ['../configure --help']
            stdout = system_cmd(cmd=config_proc, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        elif isinstance(configure_opts, str) and len(configure_opts) > 0:
            config_proc = ['../configure --prefix=%s' % str(r_home), configure_opts]
            stdout = system_cmd(cmd=config_proc, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        else:
            config_proc = ['../configure --prefix=%s' % str(r_home)]
            stdout = system_cmd(cmd=config_proc, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)

    def source_make(self, without_make, check, install, install_info, install_pdf, install_tests):
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        chdir(str(rinse_bin))
        if not without_make:
            make_proc = ['make']
            stdout = system_cmd(cmd=make_proc, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        if check:
            make_check = ['make check']
            stdout = system_cmd(cmd=make_check, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        if install:
            make_install = ['make install']
            stdout = system_cmd(cmd=make_install, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        if install_info:
            make_info = ['make install-info']
            stdout = system_cmd(cmd=make_info, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        if install_pdf:
            make_pdf = ['make install-pdf']
            stdout = system_cmd(cmd=make_pdf, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        if install_tests:
            make_tests = ['make install-tests']
            stdout = system_cmd(cmd=make_tests, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)

    def source_test(self, check, check_devel, check_all):
        rinse_bin_tests = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin" / "tests"
        chdir(str(rinse_bin_tests))
        if check:
            test_check = ["../bin/R CMD make check"]
            stdout = system_cmd(cmd=test_check, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        if check_devel:
            test_check_devel = ["../bin/R CMD make check-devel"]
            stdout = system_cmd(cmd=test_check_devel, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        if check_all:
            test_check_all = ["../bin/R CMD make check-all"]
            stdout = system_cmd(cmd=test_check_all, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)

    def global_interpreter(self, version):
        version_name = "R-%s" % version
        if Path(self.bin_path / "R").is_symlink():
            remove(str(self.bin_path / "R"))
        if Path(self.bin_path / "Rscript").is_symlink():
            remove(str(self.bin_path / "Rscript"))
        if Path(self.lib_path / "cran" / version_name / "bin" / "R").exists() or \
                Path(self.lib_path / "cran" / version_name / "bin" / "Rscript").exists():
            Path(self.bin_path / "R").symlink_to(self.lib_path / "cran" / version_name / "bin" / "R")
            Path(self.bin_path / "Rscript").symlink_to(self.lib_path / "cran" / version_name / "bin" / "Rscript")
        else:
            self.logger.info("The version of R you are looking for does not exist yet.")
            raise FileNotFoundError

    def clear_tmp_dir(self):
        # Set up the temporary directory for installation
        if self.config_clear[0] == "all":
            rmtree(str(self.tmp_path))
            self.tmp_path.mkdir(parents=True)
        elif len(self.config_clear) >= 1:
            for vrs in self.config_clear:
                if vrs not in self.config_keep:
                    rmtree(str(self.tmp_path / Path("R-%s" % vrs)))

    def use_local(self):
        raise NotImplementedError("Local installation is not supported at this time.")

    def use_spack(self):
        raise NotImplementedError("Installation with spack is not supported at this time.")


class MacInstallR(BaseInstallR):

    def __init__(self):
        raise NotImplementedError("Installation of R with rinse on MacOS is not supported at this time.")


class WindowsInstallR(BaseInstallR):

    def __init__(self):
        raise NotImplementedError("Installation of R with rinse on Windows is not supported at this time.")

