from cookiecutter.main import cookiecutter
from pathlib import Path
from os import listdir, chdir, mkdir, symlink, remove, environ
from shutil import rmtree
from pkg_resources import resource_filename
from rinse import cookies
import requests as re
import tarfile
import subprocess as sp


class BaseInstallR(object):

    def __init__(self, path, name, version=None, repos=None, method=None, init=None):
        # Rinse path setup
        self.name = name
        self.path = Path(path).expanduser().absolute()

        self.rinse_path = self.path / self.name
        self.tmp_path = self.rinse_path / "tmp"
        self.src_path = self.rinse_path / "src"
        self.lib_path = self.rinse_path / "lib"
        self.bin_path = self.rinse_path / "bin"

        # Initialization step
        self.cookie_jar = Path(resource_filename(cookies.__name__, ''))
        if init:
            if self.rinse_path.exists():
                raise FileExistsError("The rinse path you have set already exists: %s" % self.rinse_path)
            elif not self.rinse_path.exists():
                self.initial_setup()
        elif not self.rinse_path.exists():
            raise EnvironmentError("You have not initialized rinse yet.  Please run 'rinse init' to continue.")

        # Create class variables from parameters
        self.method = method  # source for now spack for later
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
            bash_prof = str(Path("~/.bash_profile").expanduser().absolute())
            with open(bash_prof, 'r') as prof:
                _ = prof.read()
                bas_prof_export = "export PATH=\"%s:$PATH\"" % str(self.bin_path)
                if bas_prof_export not in _:
                    with open(bash_prof, "a+") as b_prof:
                        b_prof.write("export PATH=\"%s:$PATH\"" % str(self.bin_path))
                    prof_proc = sp.Popen(["source %s" % bash_prof], shell=True)
                    prof_proc.wait()


class LinuxInstallR(BaseInstallR):

    def __init__(self, version, method, name, path, repos, glbl, config_clear, config_keep, init):
        super().__init__(path=path, version=version, repos=repos, method=method, name=name, init=init)
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

    def source_download(self):
        # Download the source tarball
        if self.version == "latest":
            url = "%s/src/base/R-latest.tar.gz" % self.repos
        else:
            major_version = self.version[0:1]
            url = "%s/src/base/R-%s/R-%s.tar.gz" % (self.repos, major_version, self.version)
        src_file_url = re.get(url=url)
        src_file_path = self.src_path / "cran" / Path(url).name
        open(str(src_file_path), 'wb').write(src_file_url.content)
        return src_file_path

    def source_setup(self, src_file_path):
        # Check the temp directory if necessary
        self.clear_tmp_dir()
        # Extract the contents of the source tarball
        with tarfile.open(str(src_file_path)) as r_tar_file:
            r_tar_file.extractall(path=str(self.tmp_path))

        # Configure rinse-bin for the configuration process
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        if rinse_bin.exists():
            rmtree(rinse_bin)
        mkdir(str(rinse_bin))
        return rinse_bin

    def source_configure(self, configure_opts=None):
        # Set up R_HOME
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        chdir(str(rinse_bin))
        r_home_name = Path(rinse_bin).parent.name
        r_home = self.lib_path / "cran" / r_home_name
        if r_home.exists() is not True:
            r_home.mkdir()
        if configure_opts == "--help":
            config_proc = sp.Popen(['../configure --help'], shell=True)
            config_proc.wait()
        elif isinstance(configure_opts, str) and len(configure_opts) > 0:
            config_proc = sp.Popen(['../configure --prefix=%s' % str(r_home), configure_opts], shell=True)
            config_proc.wait()
        else:
            config_proc = sp.Popen(['../configure --prefix=%s' % str(r_home)], shell=True)
            config_proc.wait()

    def source_make(self, without_make, check, install, install_info, install_pdf, install_tests):
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        chdir(str(rinse_bin))
        if not without_make:
            make_proc = sp.Popen(['make'], shell=True)
            make_proc.wait()
        if check:
            make_check = sp.Popen(['make check'], shell=True)
            make_check.wait()
        if install:
            make_install = sp.Popen(['make install'], shell=True)
            make_install.wait()
        if install_info:
            make_info = sp.Popen(['make install-info'], shell=True)
            make_info.wait()
        if install_pdf:
            make_pdf = sp.Popen(['make install-pdf'], shell=True)
            make_pdf.wait()
        if install_tests:
            make_tests = sp.Popen(['make install-tests'], shell=True)
            make_tests.wait()

    def source_test(self, check, check_devel, check_all):
        rinse_bin_tests = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin" / "tests"
        chdir(str(rinse_bin_tests))
        if check:
            test_check = sp.Popen(["../bin/R CMD make check"], shell=True)
            test_check.wait()
        if check_devel:
            test_check_devel = sp.Popen(["../bin/R CMD make check-devel"], shell=True)
            test_check_devel.wait()
        if check_all:
            test_check_all = sp.Popen(["../bin/R CMD make check-all"], shell=True)
            test_check_all.wait()

    def global_interpreter(self, version):
        version_name = "R-%s" % version
        if Path(self.bin_path / "R").exists() and Path(self.bin_path / "Rscript").exists():
            remove(str(self.bin_path / "R"))
            remove(str(self.bin_path / "Rscript"))
        symlink(str(self.lib_path / "cran" / version_name / "bin" / "R"), str(self.bin_path / "R"))
        symlink(str(self.lib_path / "cran" / version_name / "bin" / "Rscript", str(self.bin_path / "Rscript")))

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

    def __init__(self, path, version, repos, method, name, init):
        super().__init__(path=path, version=version, repos=repos, method=method, name=name,
                         init=init)

    def raise_error(self):
        raise NotImplementedError("Installation of R with rinse on MacOS is not supported at this time.")


class WindowsInstallR(BaseInstallR):

    def __init__(self, path, version, repos, method, name, init):
        super().__init__(path=path, version=version, repos=repos, method=method, name=name,
                         init=init)

    def raise_error(self):
        raise NotImplementedError("Installation of R with rinse on Windows is not supported at this time.")

