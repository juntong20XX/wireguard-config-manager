"""
v2ray plugin
"""

from wg_config_manager.load_plugin import FunctionParameter, AcquireValue, ServiceSelfObject

import typing
import asyncio
from pathlib import Path
from subprocess import Popen
from threading import Thread
from functools import partial
from tempfile import TemporaryDirectory, NamedTemporaryFile


def hello():
    print("hello world from", __file__)


class V2rayService:
    """
    the class for background service "v2ray"
    """

    def __init__(self, v2ray_path: str, config_path: str):
        self.v2ray_path = v2ray_path
        self.config_path = config_path
        self.process = Popen([v2ray_path, "run", "-c", config_path])

        self.health_check_thread = Thread(target=self.get_health_check_thread_target(), daemon=True)
        self.health_check_thread.start()

    def down(self):
        self.process.kill()
        self.process.wait()
        self.process = None

    def health_check(self):
        if self.process.poll() is not None:
            self.process = Popen([self.v2ray_path, "run", "-c", self.config_path])

    def get_health_check_thread_target(self):
        return partial(asyncio.run, self._health_check_coroutine_loop())

    async def _health_check_coroutine_loop(self):
        while self.process is not None:
            self.health_check()
            await asyncio.sleep(60)  # Check healthy every minute.


VERSION_REQ = ""
parameters_new = [
    FunctionParameter(name="v2ray_path",
                      default="v2ray",
                      helper="path to the v2ray application"),
    FunctionParameter(name="config_path",
                      default="{CONFIG_DIR}/config.json",
                      helper="path to the v2ray configuration")
]
BACKGROUND_SERVICE_v2ray = {"new": [V2rayService, parameters_new],
                            "teardown": [V2rayService.down, [ServiceSelfObject]]}
