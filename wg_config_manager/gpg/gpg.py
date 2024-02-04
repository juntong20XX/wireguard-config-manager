"""

"""
from wg_config_manager.load_plugin import FunctionParameter, AcquireValue

import typing
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile


def gpg_list_keys(gpg_path: str, timeout: typing.Optional[int | float] = None) -> str:
    """
    list gpg keys.
    """
    p = subprocess.run([gpg_path, "--list-keys"], check=True, text=True, capture_output=True, timeout=timeout)
    return p.stdout


def gpg_encrypt_symmetric(file_path: str, output: str | None, gpg_path: str,
                          timeout: typing.Optional[int | float] = None) -> None:
    """
    Symmetric encrypt a file by gpg.
    """
    if output is None:
        cmds = [gpg_path, "--symmetric", file_path]
    else:
        cmds = [gpg_path, "--output", output, "--symmetric", file_path]
    subprocess.run(cmds, check=True, text=True, capture_output=True, timeout=timeout)


def gpg_decrypt_symmetric(file_path: str, gpg_path: str | None = None,
                          timeout: typing.Optional[int | float] = None) -> bytes:
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

    def __init__(self, path_gpg=None, timeout=None):
        """
        TODO
        """
        if path_gpg is not None:
            self.PATH_GPG = path_gpg
        if timeout is not None:
            self.TIMEOUT = timeout

    def gpg_list_keys(self, gpg_path: str | None = None, timeout: typing.Optional[int | float] = None) -> str:
        """
        list gpg keys.
        """
        if gpg_path is None:
            gpg_path = self.PATH_GPG
        if timeout is None:
            timeout = self.TIMEOUT
        p = subprocess.run([gpg_path, "--list-keys"], check=True, text=True, capture_output=True, timeout=timeout)
        return p.stdout

    def gpg_encrypt_symmetric(self, file_path: str, output=None, gpg_path: str | None = None,
                              timeout: typing.Optional[int | float] = None) -> None:
        """
        Symmetric encrypt a file by gpg.
        """
        if gpg_path is None:
            gpg_path = self.PATH_GPG
        if timeout is None:
            timeout = self.TIMEOUT
        gpg_encrypt_symmetric(file_path, output, gpg_path, timeout)

    def gpg_decrypt_symmetric(self, file_path: str, gpg_path: str | None = None,
                              timeout: typing.Optional[int | float] = None) -> bytes:
        """
        Decrypt a symmetric encrypted file by gpg, return decrypted dytes.
        """
        if gpg_path is None:
            gpg_path = self.PATH_GPG
        if timeout is None:
            timeout = self.TIMEOUT
        p = subprocess.run([gpg_path, "--decrypt", file_path], check=True, capture_output=True, timeout=timeout)
        return p.stdout


def gpg_encrypt_symmetric_callback(target: bytes, gpg_path, timeout) -> bytes:
    """
    Symmetric encrypt a file by gpg, the return encrypted bytes.
    """
    with TemporaryDirectory() as d:
        dp = Path(d)
        file_path = dp / "input.txt"
        output = dp / "output.gpg"
        with open(file_path, "wb") as fp:
            fp.write(target)
        gpg_encrypt_symmetric(file_path=str(file_path), output=str(output), gpg_path=gpg_path, timeout=timeout)
        with open(output, "rb") as fp:
            return fp.read()


def gpg_decrypt_symmetric_callback(target, gpg_path, timeout) -> bytes:
    with NamedTemporaryFile() as fp:
        fp.write(target)
        fp.flush()
        return gpg_decrypt_symmetric(fp.name, gpg_path, timeout)


def read_timeout(s: str):
    r = float(s)
    if r > 0:
        return r
    return None


parameters_encrypt = [
    FunctionParameter(name="target", default=AcquireValue("TARGET DATA"), user_accessible=False),
    FunctionParameter(name="gpg_path", default="{gpg_path}"),
    FunctionParameter(name="timeout", default="-1", before_pass=read_timeout),
]
parameters_decrypt = [
    FunctionParameter(name="target", default=AcquireValue("TARGET DATA"), user_accessible=False),
    FunctionParameter(name="gpg_path", default="{gpg_path}"),
    FunctionParameter(name="timeout", default="-1", before_pass=read_timeout),
]

VERSION_REQ = ""

ENCRYPT_TYPE_GnuPG = {"encrypt": [gpg_encrypt_symmetric_callback, parameters_encrypt],
                      "decrypt": [gpg_decrypt_symmetric_callback, parameters_decrypt]}
