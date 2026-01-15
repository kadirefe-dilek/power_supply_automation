# supply_config.py

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .config import SerialConfig


class SupplyConfigError(ValueError):
    pass


@dataclass(frozen=True)
class SupplyProfile:
    name: str
    description: str
    driver: str
    serial: SerialConfig
    command_map_raw: Dict[str, str]
    expect_response_raw: list[str]


def _require(d: Dict[str, Any], key: str, ctx: str) -> Any:
    if key not in d:
        raise SupplyConfigError(f"Missing required key '{key}' in {ctx}.")
    return d[key]


def load_supply_profiles(config_path: str) -> tuple[str, Dict[str, SupplyProfile]]:
    """
    Returns: (default_profile_name, profiles_dict)
    """
    path = Path(config_path)
    if not path.exists():
        raise SupplyConfigError(f"Config file not found: {config_path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    default_name = _require(data, "default", "root")
    supplies = _require(data, "supplies", "root")

    if not isinstance(supplies, dict) or not supplies:
        raise SupplyConfigError("Key 'supplies' must be a non-empty object.")

    profiles: Dict[str, SupplyProfile] = {}

    for name, cfg in supplies.items():
        if not isinstance(cfg, dict):
            raise SupplyConfigError(f"Supply profile '{name}' must be an object.")

        driver = _require(cfg, "driver", f"supplies.{name}")
        description = cfg.get("description", "")

        serial_cfg = _require(cfg, "serial", f"supplies.{name}")
        command_map = _require(cfg, "command_map", f"supplies.{name}")
        expect_response = cfg.get("expect_response", [])

        serial = SerialConfig(
            port="__PORT_FROM_CLI__",  # placeholder; overridden at runtime
            baudrate=int(serial_cfg.get("baudrate", 9600)),
            bytesize=int(serial_cfg.get("bytesize", 8)),
            parity=str(serial_cfg.get("parity", "N")),
            stopbits=int(serial_cfg.get("stopbits", 1)),
            timeout_s=float(serial_cfg.get("timeout_s", 1.0)),
            write_timeout_s=float(serial_cfg.get("write_timeout_s", 1.0)),
            newline=str(serial_cfg.get("newline", "\n")),
        )

        if not isinstance(command_map, dict):
            raise SupplyConfigError(f"'command_map' must be an object in profile '{name}'.")

        if not isinstance(expect_response, list):
            raise SupplyConfigError(f"'expect_response' must be a list in profile '{name}'.")

        profiles[name] = SupplyProfile(
            name=name,
            description=str(description),
            driver=str(driver),
            serial=serial,
            command_map_raw={str(k): str(v) for k, v in command_map.items()},
            expect_response_raw=[str(x) for x in expect_response],
        )

    if default_name not in profiles:
        raise SupplyConfigError(f"Default supply '{default_name}' not found in supplies.")

    return default_name, profiles
