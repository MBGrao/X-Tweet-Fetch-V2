import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import logging
from src import utils

class TestUtils(unittest.TestCase):
    def test_setup_logger(self):
        logger = utils.setup_logger("test_logger", logging.DEBUG)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.DEBUG)
    
    def test_safe_run_success(self):
        def add(a, b):
            return a + b
        result = utils.safe_run(add, 2, 3)
        self.assertEqual(result, 5)
    
    def test_safe_run_exception(self):
        def raise_error():
            raise ValueError("Test error")
        with self.assertRaises(ValueError):
            utils.safe_run(raise_error)

if __name__ == '__main__':
    unittest.main()
