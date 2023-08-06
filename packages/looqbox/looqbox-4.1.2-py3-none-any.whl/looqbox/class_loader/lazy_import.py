import importlib


class LazyImport:
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = None

    def __getattr__(self, attr):
        if self.module is None:
            self.module = importlib.import_module(self.module_name)
        return getattr(self.module, attr)
