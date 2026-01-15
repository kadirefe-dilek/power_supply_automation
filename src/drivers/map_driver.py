from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Set

from ..enums import SupplyCommand
from .base import PowerSupplyDriver


class DriverConfigError(ValueError):
    pass


@dataclass(frozen=True)
class MapBasedDriver(PowerSupplyDriver):
    """
    Device-agnostic mapping driver.

    command_map examples:
      "SET_VOLTAGE": "VOLT {value}"
      "OPEN_OUTPUT": "OUTP ON"
      "MEASURE_VOLTAGE": "MEAS:VOLT?"

    Supported placeholders:
      {value}   -> formatted numeric (default 3 decimals)
      {channel} -> integer channel if applicable
    """
    driver_name: str
    command_map: Dict[SupplyCommand, str]
    expect_response_set: Set[SupplyCommand]
    value_decimals: int = 3

    @property
    def name(self) -> str:
        return self.driver_name

    def expects_response(self, cmd: SupplyCommand) -> bool:
        return cmd in self.expect_response_set

    def build_command(
        self,
        cmd: SupplyCommand,
        value: Optional[float] = None,
        channel: Optional[int] = None
    ) -> str:
        if cmd not in self.command_map:
            raise DriverConfigError(f"Command '{cmd.name}' is not mapped for driver '{self.name}'.")

        template = self.command_map[cmd]

        # Prepare substitution dict
        subs = {}
        if "{value}" in template:
            if value is None:
                raise DriverConfigError(f"Command '{cmd.name}' requires 'value' but none provided.")
            subs["value"] = f"{value:.{self.value_decimals}f}"
        if "{channel}" in template:
            if channel is None:
                raise DriverConfigError(f"Command '{cmd.name}' requires 'channel' but none provided.")
            subs["channel"] = str(int(channel))

        try:
            return template.format(**subs)
        except KeyError as e:
            raise DriverConfigError(f"Template for '{cmd.name}' has unresolved placeholder: {e}") from e
