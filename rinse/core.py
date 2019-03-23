class InstallR(object):

    def __init__(self, path, version, method="source", url=None):
        self.method = method  # source for now spack for later
        self.install()

    def install(self):
        if self.method == "source":
            self.use_source()
        elif self.method == "spack":
            self.use_spack()

    def use_source(self):
        pass

    def use_spack(self):
        pass


