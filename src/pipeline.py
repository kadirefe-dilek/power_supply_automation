# pipeline.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import SupplyCommand, ProtocolFlavor
from .transport import SerialTransport

@dataclass
class SupplyPipeline:
    transport: SerialTransport
    protocol: ProtocolFlavor = ProtocolFlavor.SCPI

    # --- 0) Arayüz Testi: mesajı hem ekrana hem seri hatta bas ---
    def echo_to_console_and_line(self, msg: str) -> None:
        """
        Test hook:
        - Konsola basar
        - Seri hatta aynı mesajı gönderir (cihaz echo etmese bile hat doğrulaması için faydalı)
        """
        print(f"[ECHO][TX] {msg}")
        self.transport.write_line(msg)

    # --- 1) Komut Oluşturma ---
    def build_command(
        self,
        cmd: SupplyCommand,
        value: Optional[float] = None,
        channel: Optional[int] = None
    ) -> str:
        """
        SCPI bazlı minimal bir mapping.
        Cihazına göre kolayca genişletirsin.
        """
        ch = f"{channel}" if channel is not None else None

        if self.protocol == ProtocolFlavor.SCPI:
            if cmd == SupplyCommand.IDN:
                return "*IDN?"
            if cmd == SupplyCommand.OPEN_OUTPUT:
                # Bazı cihazlarda OUTP ON, bazı cihazlarda OUTPut:STATe ON
                return "OUTP ON" if ch is None else f"OUTP{ch} ON"
            if cmd == SupplyCommand.CLOSE_OUTPUT:
                return "OUTP OFF" if ch is None else f"OUTP{ch} OFF"
            if cmd == SupplyCommand.MEASURE_VOLTAGE:
                return "MEAS:VOLT?" if ch is None else f"MEAS:VOLT? (@{ch})"
            if cmd == SupplyCommand.MEASURE_CURRENT:
                return "MEAS:CURR?" if ch is None else f"MEAS:CURR? (@{ch})"
            if cmd == SupplyCommand.SET_VOLTAGE:
                if value is None:
                    raise ValueError("SET_VOLTAGE requires 'value'.")
                return f"VOLT {value:.3f}" if ch is None else f"VOLT{ch} {value:.3f}"
            if cmd == SupplyCommand.SET_CURRENT:
                if value is None:
                    raise ValueError("SET_CURRENT requires 'value'.")
                return f"CURR {value:.3f}" if ch is None else f"CURR{ch} {value:.3f}"
            if cmd == SupplyCommand.ECHO_TEST:
                return value if isinstance(value, str) else "ECHO"
        # gelecekte vendor-specific eklenebilir
        raise NotImplementedError(f"Unsupported command/protocol: {cmd} / {self.protocol}")

    # --- 2) Hatta gönder & cevabı print et ---
    def execute(
        self,
        cmd: SupplyCommand,
        value: Optional[float] = None,
        channel: Optional[int] = None,
        expect_response: bool = True
    ) -> str:
        line = self.build_command(cmd, value=value, channel=channel)
        print(f"[TX] {line}")

        if expect_response:
            resp = self.transport.send_and_receive(line)
            print(f"[RX] {resp}")
            return resp

        self.transport.write_line(line)
        return ""
