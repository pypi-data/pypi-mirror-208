import importlib


class ClassLoader:

    def __init__(self, class_name, class_path):
        self.class_name = class_name
        self.class_path = class_path

    def load_class(self):
        module = importlib.import_module(self.class_path)
        return getattr(module, self.class_name)

    def call_class(self, *args, **kwargs):
        return self.load_class()(*args, **kwargs)
