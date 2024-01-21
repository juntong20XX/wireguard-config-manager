"""
Storage management.
"""
import typing
import asyncio
import tempfile
import subprocess
from pathlib import Path
from configparser import ConfigParser


APP_DIR = Path(__file__).parent
DEFAULT_CONFIG_PATH = APP_DIR / "default config.ini"
CONFIG_DIR = Path.home() / ".config" / "wg_config_manager"
CONFIG_FILE = CONFIG_DIR / "config.ini"


PATH_MAP = {
    "APP_DIR": str(APP_DIR),
    # "DEFAULT_CONFIG": str(DEFAULT_CONFIG_PATH),
    "CONFIG_DIR": str(CONFIG_DIR),
    "CONFIG_FILE": str(CONFIG_FILE)
}


def gpg_list_keys(gpg_path: str, timeout: typing.Optional[int|float]=None) -> str:
    """
    list gpg keys.
    """
    p = subprocess.run([gpg_path, "--list-keys"], check=True, text=True, capture_output=True, timeout=timeout)
    return p.stdout

def gpg_encrypt_symmetric(file_path: str, output: str|None, gpg_path: str, timeout: typing.Optional[int|float]=None) -> None:
        """
        Symmetric encrypt a file by gpg.
        """
        if output is None:
            cmds = [gpg_path, "--symmetric", file_path]
        else:
            cmds = [gpg_path, "--output", output, "--symmetric", file_path]
        subprocess.run(cmds, check=True, text=True, capture_output=True, timeout=timeout)

def gpg_decrypt_symmetric(file_path:str, gpg_path: str | None = None, timeout: typing.Optional[int|float]=None) -> bytes:
    """
    Decrypt a symmetric encrypted file by gpg, return decrypted dytes.
    """
    p = subprocess.run([gpg_path, "--decrypt", file_path], check=True, capture_output=True, timeout=timeout)
    return p.stdout


class EncryptIO:
    """
    """
    PATH_GPG = "gpg"
    TIMEOUT = 30  # default timeout seconds

    def __init__(self, path_gpg = None, timeout=None):
        """
        TODO
        """
        if path_gpg is not None:
            self.PATH_GPG = path_gpg
        if timeout is not None:
            self.TIMEOUT = timeout
    
    def gpg_list_keys(self, gpg_path: str | None =None, timeout: typing.Optional[int|float]=None) -> str:
        """
        list gpg keys.
        """
        if gpg_path is None:
            gpg_path = self.PATH_GPG
        if timeout is None:
            timeout = self.TIMEOUT
        p = subprocess.run([gpg_path, "--list-keys"], check=True, text=True, capture_output=True, timeout=timeout)
        return p.stdout
    
    def gpg_encrypt_symmetric(self, file_path: str, output=None, gpg_path: str | None =None, timeout: typing.Optional[int|float]=None) -> None:
        """
        Symmetric encrypt a file by gpg.
        """
        if gpg_path is None:
            gpg_path = self.PATH_GPG
        if timeout is None:
            timeout = self.TIMEOUT
        gpg_encrypt_symmetric(file_path, gpg_path, timeout)
    
    def gpg_decrypt_symmetric(self, file_path:str, gpg_path: str | None = None, timeout: typing.Optional[int|float]=None) -> bytes:
        """
        Decrypt a symmetric encrypted file by gpg, return decrypted dytes.
        """
        if gpg_path is None:
            gpg_path = self.PATH_GPG
        if timeout is None:
            timeout = self.TIMEOUT
        p = subprocess.run([gpg_path, "--decrypt", file_path], check=True, capture_output=True, timeout=timeout)
        return p.stdout


def load_config() -> ConfigParser:
    """
    Load config.
    """
    if not CONFIG_DIR.is_dir():
        CONFIG_DIR.mkdir()

    parser = ConfigParser(allow_no_value=True)

    if not CONFIG_FILE.is_file():
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as fp:
            parser.read_file(fp)
        with open(CONFIG_FILE, "w", encoding="utf-8") as fp:
            parser.write(fp)
    else:
        with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
            parser.read(fp)

    return parser

def dump_config(parser:ConfigParser, path=str(DEFAULT_CONFIG_PATH)):
    """
    Write config to file by parser.
    """
    with open(path, "w", encoding="utf-8") as fp:
        parser.write(fp)

if __name__ == "__main__":
    load_config()
