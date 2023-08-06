from typing import Dict, Any
from pathlib import Path

import os
import json
import sys
import logging


def getEnvVar(key: str, default: str) -> str:
    if os.environ.get(key) is None:
        os.environ[key] = default

    return os.environ[key]


DEFAULT_CONFIG = {
    "username": None,
    "password": None,
    "token": None,
    "refreshToken": None,
    "serverUrl": getEnvVar("CTX_API_URL", "https://devext.biomechservices.com:29007/"),
    "storagePath": getEnvVar("CTX_STORAGE_PATH", "~/.coretex"),

    # Configuration related to Coretex.ai Node
    "nodeName": getEnvVar("CTX_NODE_NAME", ""),
    "organizationID": getEnvVar("CTX_ORGANIZATION_ID", ""),
    "image": None
}


def _verifyConfiguration(config: Dict[str, Any]) -> bool:
    # Checks if all keys from default config exist in loaded one
    requiredKeys = list(DEFAULT_CONFIG.keys())
    return all(key in config.keys() for key in requiredKeys)


def _loadConfiguration(configPath: Path) -> Dict[str, Any]:
    with configPath.open("r") as configFile:
        config: Dict[str, Any] = json.load(configFile)

    if not _verifyConfiguration(config):
        raise RuntimeError(">> [Coretex] Invalid configuration")

    return config


def _syncConfigWithEnv() -> None:
    configPath = Path("~/.config/coretex/config.json").expanduser()

    # If configuration does not exist create default one
    if not configPath.exists():
        logging.getLogger("coretexpylib").info(">> [Coretex] Configuration not found, creating default one")
        configPath.parent.mkdir(parents = True, exist_ok = True)

        with configPath.open("w") as configFile:
            json.dump(DEFAULT_CONFIG, configFile, indent = 4)

    # Load configuration and override environmet variable values
    try:
        config = _loadConfiguration(configPath)
    except BaseException as ex:
        logging.getLogger("coretexpylib").critical(">> [Coretex] Configuration is invalid")
        logging.getLogger("coretexpylib").critical(">> [Coretex] To configure user use \"coretex config --user\" command")
        logging.getLogger("coretexpylib").critical(">> [Coretex] To configure node use \"coretex config --node\" command")

        sys.exit(1)

    os.environ["CTX_API_URL"] = config["serverUrl"]
    os.environ["CTX_STORAGE_PATH"] = config["storagePath"]
    os.environ["CTX_NODE_NAME"] = config["nodeName"]
    os.environ["CTX_ORGANIZATION_ID"] = config["organizationID"]
