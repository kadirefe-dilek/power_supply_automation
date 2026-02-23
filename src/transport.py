# transport.py

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import serial

from .config import SerialConfig


class SerialTransportError(Exception):
    pass


class SerialTransport:
    """
    Thin serial transport wrapper.

    Key behaviors:
    - All writes append cfg.newline
    - send_and_receive clears input buffer to avoid stale responses
    - short settle delay before reading (instrument-friendly)
    """

    def __init__(self, cfg: SerialConfig):
        self.cfg = cfg
        self._ser: Optional[serial.Serial] = None

    def open(self) -> None:
        try:
            self._ser = serial.Serial(
                port=self.cfg.port,
                baudrate=self.cfg.baudrate,
                bytesize=self.cfg.bytesize,
                parity=self.cfg.parity,
                stopbits=self.cfg.stopbits,
                timeout=self.cfg.timeout_s,
                write_timeout=self.cfg.write_timeout_s,
                dsrdtr=False  # DSR/DTR akış kontrol kapalı (manuel süreceğiz)
            )
        except Exception as e:
            raise SerialTransportError(f"Failed to open serial port {self.cfg.port}: {e}") from e

        if not self._ser or not self._ser.is_open:
            raise SerialTransportError(f"Serial port {self.cfg.port} did not open")

        # Clean start
        try:
            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()
        except Exception:
            pass

    def close(self) -> None:
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None

    def _require_open(self) -> serial.Serial:
        if not self._ser or not self._ser.is_open:
            raise SerialTransportError("Serial port is not open")
        return self._ser

    def write_line(self, line: str) -> None:
        ser = self._require_open()
        payload = (line + self.cfg.newline).encode("utf-8", errors="replace")
        try:
            ser.write(payload)
            ser.flush()
        except Exception as e:
            raise SerialTransportError(f"Serial write failed: {e}") from e

    def read_line(self) -> str:
        ser = self._require_open()
        try:
            raw = ser.readline()  # reads until LF or timeout
            if not raw:
                return ""
            return raw.decode("utf-8", errors="replace").strip()
        except Exception as e:
            raise SerialTransportError(f"Serial read failed: {e}") from e

    def send_and_receive(self, line: str, settle_s: float = 0.10) -> str:
        ser = self._require_open()

        # Clear stale buffered responses before issuing a new query
        try:
            ser.reset_input_buffer()
        except Exception:
            pass

        '''self.write_line(line)

        # Give instrument time to generate response
        if settle_s > 0:
            time.sleep(settle_s)

        ## set dtr true, read line, set dtr false, return line
        ser.setDTR(True)
        resp = self.read_line()
        ser.setDTR(False)
        return resp'''
        
        try:
            ser.setDTR(True)
        except Exception:
            pass

        try:
            self.write_line(line)

            # Cihaza cevap üretmesi için küçük bir pencere
            if settle_s > 0:
                time.sleep(settle_s)

            # Tek-shot read yerine deadline ile retry (intermittent boş RX'i bitirir)
            timeout_s = float(getattr(ser, "timeout", 1.0) or 1.0)
            deadline = time.monotonic() + max(timeout_s, 1.0)

            resp = ""
            while time.monotonic() < deadline:
                resp = self.read_line()
                if resp:
                    return resp
                time.sleep(0.02)  # 20 ms backoff

            return resp  # "" dönebilir; üst katman bunu handle etmeli
        finally:
            # Cevabı okuduktan (veya timeout olduktan) sonra DTR'yi bırak
            try:
                ser.setDTR(False)
            except Exception:
                pass
