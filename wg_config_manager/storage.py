"""
Storage management.
"""
from pathlib import Path
from dataclasses import dataclass
from configparser import ConfigParser


__APP_DIR = Path(__file__).parent
DEFAULT_CONFIG_PATH = __APP_DIR / "default config.ini"
__CONFIG_DIR = Path.home() / ".config" / "wg_config_manager"
__CONFIG_FILE = __CONFIG_DIR / "config.ini"


@dataclass
class PathMap:
    """
    Config paths, the mapping to format path.
    """
    APP_DIR: Path
    CONFIG_DIR: Path
    CONFIG_FILE: Path
    
    def __getitem__(self, item):
        return getattr(self, item)

PathMap = PathMap(
    APP_DIR = __APP_DIR,
    # DEFAULT_CONFIG = str(DEFAULT_CONFIG_PATH),
    CONFIG_DIR = __CONFIG_DIR,
    CONFIG_FILE = __CONFIG_FILE
)


def get_parser_from_config() -> ConfigParser:
    """
    Load config.
    """
    if not PathMap.CONFIG_DIR.is_dir():
        PathMap.CONFIG_DIR.mkdir()

    parser = ConfigParser(allow_no_value=True)

    if not PathMap.CONFIG_FILE.is_file():
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as fp:
            parser.read_file(fp)
        with open(PathMap.CONFIG_FILE, "w", encoding="utf-8") as fp:
            parser.write(fp)
    else:
        with open(PathMap.CONFIG_FILE, "r", encoding="utf-8") as fp:
            parser.read(fp)

    return parser

def dump_parser_to_config(parser:ConfigParser, path=str(DEFAULT_CONFIG_PATH)):
    """
    Write config to file by parser.
    """
    with open(path, "w", encoding="utf-8") as fp:
        parser.write(fp)

if __name__ == "__main__":
    get_parser_from_config()
