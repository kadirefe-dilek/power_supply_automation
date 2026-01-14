from __future__ import annotations

import sys

from .config import SerialConfig
from .transport import SerialTransport
from .pipeline import SupplyPipeline
from .enums import SupplyCommand

def main() -> int:
    # Örnek: python -m src.main COM3
    port = sys.argv[1] if len(sys.argv) > 1 else "COM3"

    cfg = SerialConfig(
        port=port,
        baudrate=9600,
        timeout_s=1.0,
        newline="\n",   # cihaz "\r\n" istiyorsa değiştir
    )

    transport = SerialTransport(cfg)
    pipeline = SupplyPipeline(transport)

    transport.open()
    try:
        # 0) Arayüz testi (echo)
        pipeline.echo_to_console_and_line("HELLO_SUPPLY")

        # 1) Kimlik
        pipeline.execute(SupplyCommand.IDN, expect_response=True)

        # 2) Set V/I
        pipeline.execute(SupplyCommand.SET_VOLTAGE, value=5.0, expect_response=False)
        pipeline.execute(SupplyCommand.SET_CURRENT, value=1.0, expect_response=False)

        # 3) Output ON
        pipeline.execute(SupplyCommand.OPEN_OUTPUT, expect_response=False)

        # 4) Ölçüm
        pipeline.execute(SupplyCommand.MEASURE_VOLTAGE, expect_response=True)
        pipeline.execute(SupplyCommand.MEASURE_CURRENT, expect_response=True)

        # 5) Output OFF
        pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=False)

    finally:
        transport.close()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
