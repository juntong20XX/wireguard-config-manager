"""
Test functions and methods in load_plugin about Semantic Versioning 2.0.0.
"""
from wg_config_manager.load_plugin import check_version_req_format, semver_lg, check_version_is_req
from wg_config_manager.load_plugin import _RE_GET_VERSION as re_semver
from wg_config_manager.errors import ConfigParseFailException

import unittest


def semver_format(version: str):
    return re_semver.match(version).groups()

class TestSemver(unittest.TestCase):
    """
    test semver
    """
    def test_check_version_req_format(self):
        """
        test load_plugin.check_version_req_format
        """ 
        with self.assertRaises(ConfigParseFailException):
            check_version_req_format("v0.1.0")
            check_version_req_format("0.1.a")
        self.assertEqual(
            check_version_req_format(">=0.1.0"),
            [(">=", "0", "1", "0", None, None)]
        )
        self.assertEqual(
            check_version_req_format(">=0.1.0, <=1.0.0-beta+exp.sha.5114f85"),
            [(">=", "0", "1", "0", None, None),
             ("<=", "1", "0", "0", "beta", "exp.sha.5114f85")]
        )
    def test_semver_lg(self):
        """
        test load_plugin.semver_lg
        """
        # examples from https://semver.org
        self.assertFalse(semver_lg(semver_format("1.0.0-alpha"),
                                   semver_format("1.0.0-alpha.1")))
        self.assertFalse(semver_lg(semver_format("1.0.0-beta.11"),
                                   semver_format("1.0.0")))
        self.assertFalse(semver_lg(semver_format("1.0.0-beta.2"),
                                   semver_format("1.0.0-beta.11")))
        self.assertFalse(semver_lg(semver_format("1.0.0-alpha.1"),
                                   semver_format("1.0.0-alpha.beta")))
    
    def test_check_version_is_req(self):
        """
        test `load_plugin.check_version_is_req`
        """
        self.assertFalse(check_version_is_req(("<=", "1", "0", "0", "beta", "hello"),  # 1.0.0-beta+hello < 1.0.0
                                              "1.0.0"))
        self.assertTrue(check_version_is_req(("==", "1", "0", "0", None, "hello"),  # 1.0.0+hello == 1.0.0
                                              "1.0.0"))
        self.assertTrue(check_version_is_req(("<=", "1", "0", "0", "beta", "exp.sha.5114f85"),  # 1.0.0-beta+exp.sha.5114f85 >= 0.0.1 
                                              "0.0.1"))

if __name__ == "__main__":
    unittest.main()
