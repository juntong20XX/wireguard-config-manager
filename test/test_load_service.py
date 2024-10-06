"""
Test plugin loader for background servers.
"""

from unittest import main, TestCase


class TestLoadService(TestCase):
    def setUp(self):
        from wg_config_manager.storage import PathMap
        PathMap.CONFIG_DIR = PathMap.APP_DIR / ".." / "data"
        PathMap.CONFIG_FILE = PathMap.CONFIG_DIR / "config.ini"
        from wg_config_manager.load_plugin import load_plugin
        self.loader = load_plugin("{APP_DIR}/v2ray", "v2ray")

    def test_service(self):
        from wg_config_manager.storage import PathMap
        server = self.loader.run_service("v2ray", "test v2ray",
                                         v2ray_path="C:/Program Files/v2ray/v2ray.exe",
                                         config_path=PathMap.CONFIG_DIR / "v2ray config example.json")
        self.assertTrue(server.returned.process.poll() is None)

    def tearDown(self):
        self.loader.stop_service("test v2ray")


if __name__ == '__main__':
    main()
