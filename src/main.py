# pipeline.py

from __future__ import annotations

import argparse

from .enums import SupplyCommand
from .supply_config import load_supply_profiles
from .drivers.factory import create_driver
from .transport import SerialTransport
from .config import SerialConfig
from .pipeline import SupplyPipeline


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Power Supply Automation (multi-supply, config-driven)")

    p.add_argument("port", help="Serial port (e.g., COM4)")
    p.add_argument("--config", default="power_supplies.json", help="Supply config JSON path")
    p.add_argument("--supply", default=None, help="Supply profile name (e.g., A, B). If omitted, uses config default.")

    # Golden-path parameters (operator controllable)
    p.add_argument("--range", dest="range_mode", choices=["low", "high"], default="low",
                   help="Select output range: low or high")
    p.add_argument("--ovp", type=float, default=6.0,
                   help="Over-voltage protection threshold (Volts)")
    p.add_argument("--volt", type=float, default=5.0,
                   help="Output voltage setpoint (Volts)")
    p.add_argument("--curr", type=float, default=0.2,
                   help="Output current limit setpoint (Amps)")

    # Optional toggles
    p.add_argument("--skip-reset", action="store_true", help="Skip *RST baseline reset")
    p.add_argument("--skip-ovp", action="store_true", help="Skip OVP configuration")
    p.add_argument("--lock-remote", action="store_true", help="Lock front panel keys in remote (SYST:RWLock)")

    return p.parse_args()


def main() -> int:
    args = parse_args()

    default_name, profiles = load_supply_profiles(args.config)
    supply_name = args.supply or default_name

    if supply_name not in profiles:
        available = ", ".join(sorted(profiles.keys()))
        raise SystemExit(f"Unknown supply profile '{supply_name}'. Available: {available}")

    profile = profiles[supply_name]

    # Serial config from profile + runtime port override
    cfg: SerialConfig = SerialConfig(
        port=args.port,
        baudrate=profile.serial.baudrate,
        bytesize=profile.serial.bytesize,
        parity=profile.serial.parity,
        stopbits=profile.serial.stopbits,
        timeout_s=profile.serial.timeout_s,
        write_timeout_s=profile.serial.write_timeout_s,
        newline=profile.serial.newline,
    )

    transport = SerialTransport(cfg)
    driver = create_driver(profile)
    pipeline = SupplyPipeline(transport=transport, driver=driver)

    transport.open()
    try:
        # ---- GOLDEN PATH (E3645A) ----
        # 1) Remote mode (recommended before RS-232 programming)
        pipeline.execute(SupplyCommand.SYSTEM_REMOTE, expect_response=False)

        # Optional: lock panel in remote
        if args.lock_remote:
            pipeline.execute(SupplyCommand.SYSTEM_RWLOCK, expect_response=False)

        # 2) Identify
        pipeline.execute(SupplyCommand.IDN, expect_response=True)

        # 3) Reset baseline (optional)
        if not args.skip_reset:
            pipeline.execute(SupplyCommand.RESET, expect_response=False)

        # 4) Ensure output OFF before configuration
        pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=False)

        # 5) Range selection
        if args.range_mode == "low":
            pipeline.execute(SupplyCommand.SET_RANGE_LOW, expect_response=False)
        else:
            pipeline.execute(SupplyCommand.SET_RANGE_HIGH, expect_response=False)

        # 6) OVP configuration (optional)
        if not args.skip_ovp:
            pipeline.execute(SupplyCommand.OVP_SET, value=args.ovp, expect_response=False)
            pipeline.execute(SupplyCommand.OVP_ENABLE, expect_response=False)
            # Clear any previous protection latch (harmless baseline step)
            pipeline.execute(SupplyCommand.OVP_CLEAR, expect_response=False)

        # 7) Program V/I with output OFF
        pipeline.execute(SupplyCommand.SET_VOLTAGE, value=args.volt, expect_response=False)
        pipeline.execute(SupplyCommand.SET_CURRENT, value=args.curr, expect_response=False)

        # 8) Enable output
        pipeline.execute(SupplyCommand.OPEN_OUTPUT, expect_response=False)

        # 9) Validate measurements
        pipeline.execute(SupplyCommand.MEASURE_VOLTAGE, expect_response=True)
        pipeline.execute(SupplyCommand.MEASURE_CURRENT, expect_response=True)

        # 10) Shutdown: output OFF
        pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=False)

        # 11) Return to local mode
        pipeline.execute(SupplyCommand.SYSTEM_LOCAL, expect_response=False)

    finally:
        transport.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
