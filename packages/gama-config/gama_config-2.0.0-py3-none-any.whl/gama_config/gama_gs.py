# IMPORTANT
# After changing this file, run `python3 -m gama_config.generate_schemas`
# To re-generate the json schemas

from dataclasses import dataclass
from enum import Enum
from dacite import from_dict, Config
from typing import Any, Optional
from gama_config.helpers import write_config, read_config, find_gama_config


GAMA_GS_FILE_NAME = "gama_gs.yml"
GAMA_GS_SCHEMA_URL = "https://greenroom-robotics.github.io/gama/schemas/gama_gs.schema.json"


class Mode(str, Enum):
    NONE = "none"
    XBOX = "xbox"
    THRUSTMASTER = "thrustmaster"
    THRUSTMASTER_COMBO = "thrustmaster_combo"
    WARTHOG = "warthog"
    WARTHOG_COMBO = "warthog_combo"


class Network(str, Enum):
    SHARED = "shared"
    VPN = "vpn"
    HOST = "host"


class LogLevel(str, Enum):
    INFO = "info"
    DEBUG = "debug"


@dataclass
class GamaGsConfig:
    mode: Mode = Mode.NONE
    network: Network = Network.SHARED
    prod: bool = False
    log_level: LogLevel = LogLevel.INFO
    remote_cmd_override: bool = False
    ddsrouter_groundstation_ip: Optional[str] = None
    ddsrouter_groundstation_port: Optional[str] = None
    ddsrouter_vessel_ip: Optional[str] = None
    ddsrouter_vessel_port: Optional[str] = None


def parse_gs_config(config: dict[str, Any]) -> GamaGsConfig:
    return from_dict(GamaGsConfig, config, config=Config(cast=[Mode, Network, LogLevel]))


def get_gs_config_path():
    return find_gama_config() / GAMA_GS_FILE_NAME


def read_gs_config() -> GamaGsConfig:
    return read_config(get_gs_config_path(), parse_gs_config)


def write_gs_config(config: GamaGsConfig):
    return write_config(get_gs_config_path(), config, GAMA_GS_SCHEMA_URL)
