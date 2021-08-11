"""This script tests the OCS Security Python sample script"""

import unittest
from program import main


class OCSSecuritySampleTests(unittest.TestCase):
    """Tests for the OCS Security Python sample"""

    @classmethod
    def test_main(cls):
        """Tests the OCS Security Python main sample script"""
        main(True)


if __name__ == '__main__':
    unittest.main()