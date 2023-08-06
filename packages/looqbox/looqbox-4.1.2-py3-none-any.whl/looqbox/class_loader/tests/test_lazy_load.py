import unittest
from looqbox.class_loader.lazy_load import class_paths
from looqbox.class_loader.class_loader import ClassLoader


class TestLazyLoading(unittest.TestCase):
    def test_class_loading(self):
        for class_name, class_path in class_paths.items():
            class_loader = ClassLoader(class_name, class_path)
            try:
                class_loader.load_class()
            except Exception as e:
                self.fail(f"Failed to load class {class_name} from {class_path}: {e}")


if __name__ == '__main__':
    unittest.main()
