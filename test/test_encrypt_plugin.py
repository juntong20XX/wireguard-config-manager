"""
test load_plugin functions for encrypt
"""
from wg_config_manager import load_plugin as lp

import os
from unittest import main, TestCase


class TestLoadEncryptPlugin(TestCase):
    def setUp(self):
        self.config_exist = lp.PathMap.CONFIG_FILE.is_file()
        self.loader = lp.load_plugin("{APP_DIR}", "gpg")
        self.encrypt_functions = self.loader.get_encrypt_types()
    def test_get_encrypt_functions(self):
        """
        try to get and exec encrypt function(s) in plugin `gpg`
        """
        self.assertListEqual(list(self.encrypt_functions), ["GnuPG"])
    def test_gpg_encrypt_gnupg(self):
        """
        test GnuPG encrypt and decrypt functions in plugin gpg
        """
        text_byte = b"some disvaluable text"
        b = self.loader.exec_encrypt("GnuPG", text_byte)
        bb = self.loader.exec_decrypt("GnuPG", b)
        self.assertEqual(text_byte, bb)
    def tearDown(self) -> None:
        if not self.config_exist:
            os.remove(lp.PathMap.CONFIG_FILE)


if __name__ == "__main__":
    main()
