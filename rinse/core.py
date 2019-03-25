class InstallR(object):

    def __init__(self, path, version, method="source", url=None):
        self.method = method  # source for now spack for later
        self.path = path
        self.version = version
        self.url = url
        self.install()

    def install(self):
        if self.method == "source":
            self.use_source()
        elif self.method == "spack":
            self.use_spack()
        elif self.method == "local":
            self.use_local()

    def use_local(self):
        pass

    def use_source(self):
        pass

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

