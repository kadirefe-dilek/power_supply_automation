# pipeline.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import SupplyCommand
from .transport import SerialTransport
from .drivers.base import PowerSupplyDriver


@dataclass
class SupplyPipeline:
    transport: SerialTransport
    driver: PowerSupplyDriver

    # --- Interface Test Hook ---
    def echo_to_console_and_line(self, msg: str) -> None:
        print(f"[ECHO][TX] {msg}")
        self.transport.write_line(msg)

    # --- Execute: build -> send -> optional read ---
    def execute(
        self,
        cmd: SupplyCommand,
        value: Optional[float] = None,
        channel: Optional[int] = None,
        expect_response: Optional[bool] = None
    ) -> str:
        line = self.driver.build_command(cmd, value=value, channel=channel)

        # If user does not override, use driver policy
        if expect_response is None:
            expect_response = self.driver.expects_response(cmd)

        print(f"[TX][{self.driver.name}] {line}")

        if expect_response:
            resp = self.transport.send_and_receive(line)
            print(f"[RX][{self.driver.name}] {resp}")
            return resp

        self.transport.write_line(line)
        return ""
