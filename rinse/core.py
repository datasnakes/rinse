from os.path import expanduser, abspath


class InstallR(object):

    def __init__(self, path, version, repos, method):
        self.method = method  # source for now spack for later
        self.path = abspath(expanduser(path))
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

    def __init__(self):
        super().__init__()


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

