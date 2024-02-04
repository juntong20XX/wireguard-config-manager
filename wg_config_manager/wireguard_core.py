"""
WireGuard Functions
"""
import re
import typing
from configparser import ConfigParser
from subprocess import run

from .errors import ConfigParseError, WireguardConfError
from .storage import get_parser_from_config

RESERVED_KEYS = set()


def gen_private_key(wg_path: typing.Optional[str] = None) -> str:
    """
    Generate a private key.
    """
    if wg_path is None:
        wg_path = get_parser_from_config().get("WireGuard", "path")
        if not wg_path:
            raise ConfigParseError("Can not get `WireGuard.path` from config.")
    # key gen command
    r = run([wg_path, "gen""key"], capture_output=True)
    return r.stdout.decode(encoding="ascii")


def gen_public_key(private_key: str, wg_path: typing.Optional[str] = None) -> str:
    """
    Generate the public key from `private_key`.
    :return:
    """
    if wg_path is None:
        wg_path = get_parser_from_config().get("WireGuard", "path")
        if not wg_path:
            raise ConfigParseError("Can not get `WireGuard.path` from config.")
    # key gen command
    r = run([wg_path, "pubkey"], capture_output=True, input=private_key.encode("ascii"))
    if not r.stdout:
        raise WireguardConfError("Command returns an empty key, please check input private key.")
    return r.stdout.decode(encoding="ascii")


PEER_KEYWORDS_NAMES = [("PublicKey", "public key"),
                       ("AllowedIPs", "allowed ips"),
                       ("Endpoint", "endpoint"),
                       ("PersistentKeepalive", "persistent keep alive")]

RE_IPV4 = re.compile(
    "^"
    r"((?:(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))"
    r"(?:/(\d|[012]\d|3[12]))?"
    "$")

# ipv6 regular is from https://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
RE_IPV6 = re.compile(
    r"(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,6}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,5}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4}){1,4}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]{1,4}){1,3}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,5}(:[0-9a-f]{1,4}){1,2}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,6}(:[0-9a-f]{1,4}){1,1}\Z)|"
    r"(\A(([0-9a-f]{1,4}:){1,7}|:):\Z)|"
    r"(\A:(:[0-9a-f]{1,4}){1,7}\Z)|"
    r"(\A((([0-9a-f]{1,4}:){6})(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|"
    r"(\A(([0-9a-f]{1,4}:){5}[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|"
    r"(\A([0-9a-f]{1,4}:){5}:[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,3}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4}){1,2}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|"
    r"(\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]{1,4}){1,1}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|"
    r"(\A(([0-9a-f]{1,4}:){1,5}|:):(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|"
    r"(\A:(:[0-9a-f]{1,4}){1,5}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)"
)

RE_IPS = re.compile(r"^([\d.:a-fA-F/])(:? *, *)?$")


def get_peer_config(device: str, config: ConfigParser, annotation: typing.Optional[str] = None) -> str:
    """
    get a peer config from wireguard_core config
    """
    s = ["[Peer]"]
    # annotation
    if annotation:
        if not annotation.startswith("#"):
            annotation = f"# {annotation}"
        s.append(annotation)
    # PublicKey
    public_key = config.get(device, "public key")
    if public_key is None:
        # try to generate public key from private key
        private_key = config.get(device, "private key")
        if private_key is None:
            raise WireguardConfError(f"cannot get or generate the private key for `{device}`")
        # update information after generate
        public_key = gen_public_key(private_key)
        config.set(device, "public key", public_key)
        config.set(device, "public key is auto generated", "True")
    s.append(f"PublicKey = {public_key}")
    # AllowedIPs
    allowed_ips = config.get(device, "allowed ips")
    if not allowed_ips:
        # try to set it from address
        allowed_ips = config.get(device, "address")
        if not allowed_ips:
            raise WireguardConfError(f'cannot get `allowed ips` for "{device}"')
    # --- check ip
    for ip in RE_IPS.findall(allowed_ips):
        if not RE_IPV4.match(ip) or not RE_IPV6.match(ip):
            raise WireguardConfError("please check ipaddress", ip)
    s.append(f"AllowedIPs = {allowed_ips}")
    # Endpoint
    endpoint = config.get(device, "endpoint")
    if endpoint:
        s.append(f"Endpoint = {endpoint}")
    # PersistentKeepalive
    pka = config.get(device, "persistent keep alive")
    if pka:
        if not pka.isnumeric():
            raise WireguardConfError('value for "persistent keep alive" should numer-like, get', pka)
        s.append(f"PersistentKeepalive = {pka}")
    return "\n".join(s)


def get_interface_config(device: str, config: ConfigParser, annotation: typing.Optional[str] = None) -> str:
    """
    get wireguard interface config
    :param device:
    :param config:
    :param annotation:
    :return:
    """
    raise NotImplemented


def get_config_for(device: str, config: ConfigParser, peer_devices=typing.Optional[list[str]]) -> str:
    """
    get the config for `name`
    :param device:
    :param config: config for wireguard
    :param peer_devices:
    :return:
    """
    s = []
    if device not in config.sections():
        raise WireguardConfError(f"cannot get device named `{device}` from config")
    # Interface
    s.append(get_interface_config(device, config, annotation=device))
    # Peers
    if peer_devices is None:
        peer_devices = set(config.sections()) - RESERVED_KEYS
        peer_devices.remove(device)
    for device_name in peer_devices:
        s.append(get_peer_config(device_name, config, annotation=device_name))
    return "\n".join(s)


def read_config(string: str):
    """
    read config from string
    A wireguard-manager config is like:
    ```ini
    [pc-1]
    private key=
    public key =
    public key is auto generated = False
    ```
    :return:
    """
    return ConfigParser(allow_no_value=True).read_string(string)
