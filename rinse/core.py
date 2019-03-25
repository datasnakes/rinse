from cookiecutter.main import cookiecutter
from pathlib import Path
from pkg_resources import resource_filename
from rinse import cookies


class InstallR(object):

    def __init__(self, path, install, repos, method, name, init, config_file, config_help):
        self.method = method  # source for now spack for later
        self.name = name
        self.path = Path(path).expanduser().absolute()
        self.cookie_jar = Path(resource_filename(cookies.__name__, ''))

        if self.path.exists() and init is True:
            FileExistsError("The rinse path you have set already exists: %s" % self.path)
        elif not self.path.exists() and init is True:
            init_cookie = self.cookie_jar / Path("init")
            e_c = {
                "rinse_init_dir": self.name
            }
            cookiecutter(init_cookie, no_input=True, extra_context=e_c, output_dir=self.path)
        self.version = version
        self.repos = repos

    def install(self):
        if self.method == "source":
            self.use_source()
        elif self.method == "spack":
            self.use_spack()
        elif self.method == "local":
            self.use_local()

    def use_source(self):
        if self.version == "latest":
            url = "%s/src/base/R-latest.tar.gz" % self.repos
        else:
            major_version = self.version[0:1]
            url = "%s/src/base/R-%s/R-%s.tar.gz" % (self.repos, major_version, self.version)

    def use_local(self):
        raise NotImplementedError("Local installation is not supported at this time.")

    def use_spack(self):
        raise NotImplementedError("Installation with spack is not supported at this time.")


class LInstallR(InstallR):

    def __init__(self, path, version, repos, method):
        super().__init__(path=path, version=version, repos=repos, method=method)


class MacInstall(InstallR):

    def __init__(self):
        super().__init__(self)

    def raise_error(self):
        raise NotImplementedError("Installation of R with rinse on MacOS is not supported at this time.")


class WInstallR(InstallR):

    def __init__(self):
        super().__init__(self)

    def raise_error(self):
        raise NotImplementedError("Installation of R with rinse on Windows is not supported at this time.")

