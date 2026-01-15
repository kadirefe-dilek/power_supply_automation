from __future__ import annotations

from typing import Dict, Set

from ..enums import SupplyCommand
from ..supply_config import SupplyProfile
from .base import PowerSupplyDriver
from .map_driver import MapBasedDriver, DriverConfigError


class DriverFactoryError(ValueError):
    pass


def _to_command_enum(name: str) -> SupplyCommand:
    try:
        return SupplyCommand[name]
    except KeyError as e:
        raise DriverFactoryError(f"Unknown command enum name in config: '{name}'") from e


def create_driver(profile: SupplyProfile) -> PowerSupplyDriver:
    driver_type = profile.driver.lower().strip()

    if driver_type == "map":
        command_map: Dict[SupplyCommand, str] = {}
        for k, v in profile.command_map_raw.items():
            cmd = _to_command_enum(k)
            command_map[cmd] = v

        expect_set: Set[SupplyCommand] = set()
        for x in profile.expect_response_raw:
            expect_set.add(_to_command_enum(x))

        return MapBasedDriver(
            driver_name=profile.name,
            command_map=command_map,
            expect_response_set=expect_set,
            value_decimals=3
        )

    raise DriverFactoryError(f"Unsupported driver type: '{profile.driver}'")
