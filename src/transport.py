# transport.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import serial  # pip install pyserial

from .config import SerialConfig

class SerialTransportError(RuntimeError):
    pass

@dataclass
class SerialTransport:
    cfg: SerialConfig
    _ser: Optional[serial.Serial] = None

    def open(self) -> None:
        if self._ser and self._ser.is_open:
            return
        try:
            self._ser = serial.Serial(
                port=self.cfg.port,
                baudrate=self.cfg.baudrate,
                bytesize=self.cfg.bytesize,
                parity=self.cfg.parity,
                stopbits=self.cfg.stopbits,
                timeout=self.cfg.timeout_s,
                write_timeout=self.cfg.write_timeout_s,
            )
        except Exception as e:
            raise SerialTransportError(f"Serial open failed: {e}") from e

    def close(self) -> None:
        if self._ser and self._ser.is_open:
            self._ser.close()

    def write_line(self, line: str) -> None:
        if not self._ser or not self._ser.is_open:
            raise SerialTransportError("Serial port is not open.")
        payload = (line + self.cfg.newline).encode("ascii", errors="ignore")
        self._ser.write(payload)

    def read_line(self) -> str:
        if not self._ser or not self._ser.is_open:
            raise SerialTransportError("Serial port is not open.")
        raw = self._ser.readline()
        return raw.decode("ascii", errors="ignore").strip()

    def send_and_receive(self, line: str) -> str:
        self.write_line(line)
        return self.read_line()
