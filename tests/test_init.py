import unittest

class TestInitImport(unittest.TestCase):
    def test_import_src(self):
        try:
            import src  # noqa: F401
        except Exception as e:
            self.fail(f"Importing src package failed: {e}")

if __name__ == '__main__':
    unittest.main()
