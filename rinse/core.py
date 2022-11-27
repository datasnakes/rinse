import ctypes
import difflib
import logging
import re
import subprocess as sp
import sys
import tarfile
import urllib.request
from os import chdir, environ, listdir, mkdir, remove, symlink
from pathlib import Path
from shutil import rmtree

import requests
from cookiecutter.main import cookiecutter
from pkg_resources import resource_filename

from rinse import cookies
from rinse.utils import system_cmd


class BaseInstallR(object):

    def __init__(self, path, name, version=None, repos=None,
                 method=None, init=None, verbose=False, os=None):
        """Initialization function.

        :param path: Absolute install path
        :param name: Directory name; default = .rinse
        :param version: r version
        :param repos: the repo used for downloading source file
        :param method:
        :param init:
        :param verbose:
        :param os: windows, mac, or linux
        """
        # Rinse path setup
        self.name = name
        self.path = Path(path).expanduser().absolute()
        self.verbose = verbose

        self.rinse_path = self.path / self.name
        self.tmp_path = self.rinse_path / "tmp"
        self.src_path = self.rinse_path / "src"
        self.lib_path = self.rinse_path / "lib"
        self.bin_path = self.rinse_path / "bin"
        self.os = os

        # Set up logger
        # Change level of logger based on verbose paramater.
        if self.verbose:
            logging.basicConfig(
                format='[%(levelname)s | %(name)s - line %(lineno)d]: %(message)s')
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
                self.logger.error(
                    "The rinse path you have set already exists: %s" %
                    self.rinse_path)
            elif not self.rinse_path.exists():
                self.initial_setup()
                self.logger.info("Initializing rinse.")
        elif not self.rinse_path.exists():
            self.logger.error(
                "You have not initialized rinse yet.  Please run 'rinse init' to continue.")

        # Create class variables from parameters
        self.method = method  # source for now spack for later

        # Checking validity of specified version
        if version is None or version == "--help" or version == "latest":
            self.version = "latest"
        else:
            avail_versions = self.get_versions()
            if version in avail_versions:
                self.version = version
            # user version specification error handling
            else:
                close_match = difflib.get_close_matches(version, avail_versions, n=1)
                if len(close_match) > 0:
                    self.logger.error(
                        "Cannot find specified version '%s', did you mean '%s'?" %
                        (version, close_match[0]))
                    response = input('[Y/n]?: ')
                    if response.lower() == "y" or response.lower() == "yes":
                        self.version = close_match[0]
                    else:
                        sys.exit(0)
                else:
                    self.logger.error(
                        "Cannot find specified version '%s'. The list of available versions are:" %
                        version)
                    self.logger.info(avail_versions)
                    sys.exit(0)
        self.repos = repos

    def initial_setup(self):
        """Setup for rinse init."""
        # Prepare and run cookiecutter
        init_cookie = self.cookie_jar / Path("init")
        e_c = {
            "rinse_init_dir": self.name
        }
        cookiecutter(
            str(init_cookie),
            no_input=True,
            extra_context=e_c,
            output_dir=str(
                self.path))
        # Setup environment variables
        if self.os == "linux":
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
                        stdout = system_cmd(
                            cmd=cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        # For Windows Installation
        elif self.os == "windows":
            self.logger.info(
                "Please add %s to your Windows PATH" %
                self.rinse_path.expanduser().absolute())
            # adding beRi to environment var
            # if str(self.bin_path) not in environ["PATH"]:
            #     print(str(self.rinse_path.expanduser().absolute()))
            #     environ["PATH"] =environ["PATH"] + ';'+ str(self.rinse_path.expanduser().absolute())
            #     cmd = ["set PATH=%s" % str(environ['PATH'])]
            #     system_cmd(cmd=cmd, stdout = sp.PIPE, stderr=sp.STDOUT, shell=True)
            # subprocess.call('setx /M PATH=%PATH%;' + str(self.rinse_path.expanduser().absolute()), shell=True)
            # subprocess.call('sqsub -np ' + str(self.rinse_path.expanduser().absolute()), shell=True)
            # print(environ["PATH"])
        elif self.os == "mac":
            # TODO:
            self.logger.info("MacOS is not currently supported.")
        else:
            raise EnvironmentError("Unsupported version of OS: %s" % self.os)

    def hide_file(self, path):
        """[summary]

        :param path: [description]
        :type path: [type]
        :raises a: [description]
        :raises ctypes.WinError: [description]
        :return: [description]
        :rtype: [type]
        """
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ret = ctypes.windll.kernel32.SetFileAttributesW(path,
                                                        FILE_ATTRIBUTE_HIDDEN)
        if ret:
            self.logger.info('set to Hidden')
        else:  # return code of zero indicates failure -- raise a Windows error
            raise ctypes.WinError()

    def get_versions(self):
        url = 'https://cloud.r-project.org/bin/windows/base/old/'

        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        respData = resp.read()

        versions = re.findall(r'>R ([0-9].*?)</a>', str(respData))
        return versions


class LinuxInstallR(BaseInstallR):

    def __init__(self, version, method, name, path, repos, glbl,
                 config_clear, config_keep, init, verbose):
        super().__init__(
            path=path, version=version, repos=repos,
            method=method, name=name, init=init,
            verbose=verbose)
        self.config_clear = config_clear
        self.config_keep = config_keep
        if glbl:
            self.global_interpreter(version=glbl)

    def source_download(self, overwrite):
        """[summary]

        :param overwrite: [description]
        :type overwrite: [type]
        :return: [description]
        :rtype: [type]
        """
        # Download the source tarball
        if self.version == "latest":
            url = "%s/src/base/R-latest.tar.gz" % self.repos
        else:
            major_version = self.version[0:1]
            url = "%s/src/base/R-%s/R-%s.tar.gz" % (self.repos,
                                                    major_version, self.version)
        src_file_url = requests.get(url=url)
        src_file_path = self.src_path / "cran" / Path(url).name
        if (not src_file_path.exists()) or overwrite:
            open(str(src_file_path), 'wb').write(src_file_url.content)
        return src_file_path

    def source_setup(self, src_file_path):
        """[summary]

        :param src_file_path: [description]
        :type src_file_path: [type]
        :return: [description]
        :rtype: [type]
        """
        # Check the temp directory if necessary
        self.clear_tmp_dir()
        # Extract the contents of the source tarball
        with tarfile.open(str(src_file_path)) as r_tar_file:
            self.logger.debug("Extracting source tarball.")
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(r_tar_file, path=str(self.tmp_path))

        # Configure rinse-bin for the configuration process
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        if rinse_bin.exists():
            rmtree(rinse_bin)
            self.logger.debug("Removing existing rinse folder.")
        mkdir(str(rinse_bin))
        return rinse_bin

    def source_configure(self, configure_opts=None):
        """[summary]

        :param configure_opts: [description], defaults to None
        :type configure_opts: [type], optional
        """
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
            stdout = system_cmd(
                cmd=config_proc,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        elif isinstance(configure_opts, str) and len(configure_opts) > 0:
            config_proc = ['../configure --prefix=%s' % str(r_home), configure_opts]
            stdout = system_cmd(
                cmd=config_proc,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        else:
            config_proc = ['../configure --prefix=%s' % str(r_home)]
            stdout = system_cmd(
                cmd=config_proc,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)

    def source_make(self, without_make, check, install,
                    install_info, install_pdf, install_tests):
        """[summary]

        :param without_make: [description]
        :type without_make: [type]
        :param check: [description]
        :type check: [type]
        :param install: [description]
        :type install: [type]
        :param install_info: [description]
        :type install_info: [type]
        :param install_pdf: [description]
        :type install_pdf: [type]
        :param install_tests: [description]
        :type install_tests: [type]
        """
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        chdir(str(rinse_bin))
        if not without_make:
            make_proc = ['make']
            stdout = system_cmd(
                cmd=make_proc,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        if check:
            make_check = ['make check']
            stdout = system_cmd(
                cmd=make_check,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        if install:
            make_install = ['make install']
            stdout = system_cmd(
                cmd=make_install,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        if install_info:
            make_info = ['make install-info']
            stdout = system_cmd(
                cmd=make_info,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        if install_pdf:
            make_pdf = ['make install-pdf']
            stdout = system_cmd(
                cmd=make_pdf,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        if install_tests:
            make_tests = ['make install-tests']
            stdout = system_cmd(
                cmd=make_tests,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)

    def source_test(self, check, check_devel, check_all):
        """[summary]

        :param check: [description]
        :type check: [type]
        :param check_devel: [description]
        :type check_devel: [type]
        :param check_all: [description]
        :type check_all: [type]
        """
        rinse_bin_tests = self.tmp_path / \
            listdir(self.tmp_path)[0] / "rinse-bin" / "tests"
        chdir(str(rinse_bin_tests))
        if check:
            test_check = ["../bin/R CMD make check"]
            stdout = system_cmd(
                cmd=test_check,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        if check_devel:
            test_check_devel = ["../bin/R CMD make check-devel"]
            stdout = system_cmd(
                cmd=test_check_devel,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)
        if check_all:
            test_check_all = ["../bin/R CMD make check-all"]
            stdout = system_cmd(
                cmd=test_check_all,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                shell=True)

    def global_interpreter(self, version):
        """Set the R paths.

        :param version: The R version.
        :type version: int
        """
        version_name = "R-%s" % version
        if Path(self.bin_path / "R").is_symlink():
            remove(str(self.bin_path / "R"))
        if Path(self.bin_path / "Rscript").is_symlink():
            remove(str(self.bin_path / "Rscript"))
        if Path(self.lib_path / "cran" / version_name / "bin" / "R").exists() or \
                Path(self.lib_path / "cran" / version_name / "bin" / "Rscript").exists():
            Path(
                self.bin_path /
                "R").symlink_to(
                self.lib_path /
                "cran" /
                version_name /
                "bin" /
                "R")
            Path(
                self.bin_path /
                "Rscript").symlink_to(
                self.lib_path /
                "cran" /
                version_name /
                "bin" /
                "Rscript")
        else:
            self.logger.error("The version of R you are looking for does not exist yet.")

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
        raise NotImplementedError("Local installation is not yet supported.")

    def use_spack(self):
        raise NotImplementedError("Installation with spack is not yet supported.")


class MacInstallR(BaseInstallR):

    def __init__(self):
        raise NotImplementedError(
            "Installation of R with rinse on MacOS is not supported.")


class WindowsInstallR(BaseInstallR):

    def __init__(self, version, method, name, path, repos, glbl,
                 config_clear, config_keep, init, verbose):
        super().__init__(
            path=path, version=version, repos=repos,
            method=method, name=name,
            init=init, verbose=verbose)
        self.config_clear = config_clear
        self.config_keep = config_keep
        self.src_file_path = self.src_path
        if glbl:
            # XXX This has not been implemented for Windows yet!
            raise NotImplementedError("Global Interpreter function not written yet.")
            # self.global_interpreter(version=glbl)

    def _url_download(self, url, filepath, filename):
        """Download and save the R exe file.

        :param url: The url of the R exe.
        :type url: str
        :param filepath: The path to save the R exe to.
        :type filepath: str
        :param filename: The name of R exe file.
        :type filename: str
        """
        with open(filepath, "wb") as f:
            try:
                self.logger.info("Downloading %s" % filename)
                response = requests.get(url, stream=True)
                total_length = response.headers.get('content-length')

                if not total_length:  # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(100 * dl / total_length)
                        half_done = int(done / 2)
                        sys.stdout.write("\r[%s%s] %d%% complete" %
                                         ('=' * half_done, ' ' * (50 - half_done), done))
                        sys.stdout.flush()
            # If there is a keyboard interruption, roll back the download.
            except KeyboardInterrupt:
                f.close()
                remove(filepath)
                self.logger.exception("\n Ctrl-c pressed. Aborting!")
                sys.exit(0)

        sys.stdout.write('\n')
        self.logger.info("\n%s Downloaded Successfully" % filename)

    def _url_setup(self):
        """Format the URL based on the R version."""
        if self.version == "latest":
            ver = self.get_versions()[0]
            self.version = ver
            url = "https://cloud.r-project.org/bin/windows/base/old/%s/R-%s-win.exe" % (
                ver, ver)
            filename = "R-%s-win.exe" % ver
        else:
            ver = self.version
            url = "https://cloud.r-project.org/bin/windows/base/old/%s/R-%s-win.exe" % (
                ver, ver)
            filename = "R-%s-win.exe" % ver
        return url, filename

    def _install_exe(self, exe_file_path):
        """Install the R exe file.

        :param exe_file_path: [description]
        :type exe_file_path: [type]
        """
        # Check the temp directory if necessary
        self.clear_tmp_dir()
        # Run the R exe silently
        cmd = '%s /VERYSILENT /DIR=%s' % (exe_file_path, self.tmp_path)
        self.logger.info("Installing R in %s" % exe_file_path)
        system_cmd(cmd=cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)

    def source_download(self, overwrite, with_rtools):
        """Download the R exe.

        :param overwrite: [description]
        :type overwrite: [type]
        :param with_rtools: [description]
        :type with_rtools: boolean
        :return: File path of exe download.
        :rtype: str
        """
        # Download the source exe
        url, file_name = self._url_setup()
        self.src_file_path = self.src_path / "cran" / Path(file_name)
        src_file_path = self.src_file_path

        if (not self.src_file_path.exists()) or overwrite:
            self._url_download(url=url, filepath=self.src_file_path,
                               filename=file_name)

        if with_rtools:
            self.setup_rtools()
        return src_file_path

    def source_setup(self):
        """Install the R exe and setup rinse folder."""
        # Install the R exe
        self._install_exe(exe_file_path=self.src_file_path)
        # Create rinse-bin for the configuration process
        try:
            rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
            if rinse_bin.exists():
                rmtree(rinse_bin)
                self.logger.debug("Removing existing rinse folder.")
            mkdir(str(rinse_bin))
            self.logger.info("R successfully installed in %s" % self.tmp_path)
            return rinse_bin
        except IndexError:
            self.logger.error("Installation unsuccessful. Aborting.")
            sys.exit(0)

    def clear_tmp_dir(self):
        """Create the temporary directory for installation."""
        if self.config_clear[0] == "all":
            rmtree(str(self.tmp_path))
            self.tmp_path.mkdir(parents=True)
        elif len(self.config_clear) >= 1:
            for vrs in self.config_clear:
                if vrs not in self.config_keep:
                    rmtree(str(self.tmp_path / Path("R-%s" % vrs)))

    def create_rhome(self):
        """Create the R_HOME path."""
        rinse_bin = self.tmp_path / listdir(self.tmp_path)[0] / "rinse-bin"
        chdir(str(rinse_bin))
        r_home_name = Path(rinse_bin).parent.name
        r_home = self.lib_path / "cran" / r_home_name
        if not r_home.exists():
            self.logger.debug("Creating R home directory in %s" % r_home)
            r_home.mkdir()

    def get_versions(self):
        """Get versions of R."""
        url = 'https://cloud.r-project.org/bin/windows/base/old/'

        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        respData = resp.read()

        versions = re.findall(r'>R ([0-9].*?)</a>', str(respData))
        return versions

    def _download_rtools(self):
        """Download Rtools."""
        rtools_exe = "Rtools{}.exe"
        base_url = "https://cran.r-project.org/bin/windows/Rtools/"
        if self.version >= "3.3":
            file_name = rtools_exe.format('35')
        elif self.version == "3.2":
            file_name = rtools_exe.format('33')
        elif self.version == "3.1":
            file_name = rtools_exe.format('32')
        elif self.version == "3.0":
            file_name = rtools_exe.format('31')
        else:
            self.logger.error('%s.x R versions are not supported.' % self.version)

        # Download the Rtools exe
        self.rtools_file = file_name
        rtools_path = self.src_path / "rtools"
        if not rtools_path.exists():
            self.logger.debug("Creating Rtools directory in %s" % rtools_path)
            rtools_path.mkdir()
        rtools_url = base_url + file_name
        rtools_file_path = self.src_path / "rtools" / Path(file_name)
        self._url_download(url=rtools_url, filepath=rtools_file_path,
                           filename=file_name)
        return rtools_file_path

    def setup_rtools(self):
        """Download and install Rtools."""
        rtools_file_path = self._download_rtools()
        # Install the Rtools exe
        self._install_exe(exe_file_path=rtools_file_path)
