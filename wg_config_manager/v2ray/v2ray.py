"""
v2ray plugin
"""

from wg_config_manager.load_plugin import FunctionParameter, AcquireValue

import typing
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile


def hello():
    print("hello world from", __file__)


hello()
