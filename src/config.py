# config.py

from dataclasses import dataclass

@dataclass(frozen=True)
class SerialConfig:
    port: str
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = "N"     # 'N', 'E', 'O', 'M', 'S'
    stopbits: int = 1
    timeout_s: float = 1.0
    write_timeout_s: float = 1.0
    newline: str = "\n"   # bazı cihazlar "\r\n" ister
