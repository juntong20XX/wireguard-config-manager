"""
test wireguard_core.py
"""
from wg_config_manager import wireguard_core as wc

import unittest


class TestWG(unittest.TestCase):
    def test_gen_key(self):
        """
        test gen_private_key and gen_public_key
        """
        pri = wc.gen_private_key("wg.exe")
        print("private key:", pri)
        self.assertIsInstance(pri, str)
        p_1 = wc.gen_public_key(pri, "wg.exe")
        self.assertEqual(p_1, wc.gen_public_key(pri, "wg.exe"))
        print("public key:", p_1)


if __name__ == "__main__":
    unittest.main()
