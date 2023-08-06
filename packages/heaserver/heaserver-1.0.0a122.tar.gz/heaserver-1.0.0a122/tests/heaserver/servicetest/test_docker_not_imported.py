import unittest
import sys
from heaserver.service.testcase import testenv

class MyTestCase(unittest.TestCase):
    def test_docker_imported(self):
        self.assertFalse('docker' in sys.modules)
