from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..enums import SupplyCommand


class PowerSupplyDriver(ABC):
    """
    Contract:
    - Converts high-level commands (SupplyCommand) into device-specific serial strings
    - Optionally declares whether a response is expected for a given command
    """

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def build_command(
        self,
        cmd: SupplyCommand,
        value: Optional[float] = None,
        channel: Optional[int] = None
    ) -> str:
        raise NotImplementedError

    def expects_response(self, cmd: SupplyCommand) -> bool:
        """
        Default heuristic:
        - Queries usually return response
        - Non-queries often do not
        This can be overridden or configured.
        """
        return cmd in {
            SupplyCommand.IDN,
            SupplyCommand.MEASURE_VOLTAGE,
            SupplyCommand.MEASURE_CURRENT,
        }
