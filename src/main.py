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

    # Shared setpoints
    p.add_argument("--volt", type=float, default=5.0, help="Output voltage setpoint (Volts)")
    p.add_argument("--curr", type=float, default=0.2, help="Output current limit setpoint (Amps)")

    # A-specific knobs (E3645A)
    p.add_argument("--range", dest="range_mode", choices=["low", "high"], default="low",
                   help="(A/E3645A) Select output range: low or high")
    p.add_argument("--ovp", type=float, default=6.0, help="(A/E3645A) OVP threshold (Volts)")
    p.add_argument("--skip-ovp", action="store_true", help="(A/E3645A) Skip OVP configuration")

    # B-specific knobs (E3631A)
    p.add_argument("--rail", choices=["P6V", "P25V", "N25V"], default="P6V",
                   help="(B/E3631A) Select output rail before VOLT/CURR: P6V, P25V, N25V")
    p.add_argument("--use-apply", action="store_true",
                   help="(B/E3631A) Use APPLY instead of separate VOLT/CURR commands (requires mapping)")

    # Common toggles
    p.add_argument("--skip-reset", action="store_true", help="Skip *RST baseline reset")
    p.add_argument("--lock-remote", action="store_true", help="Lock front panel keys in remote (SYST:RWLOCK)")

    return p.parse_args()


def run_profile_a(pipeline: SupplyPipeline, args: argparse.Namespace) -> None:
    # ---- GOLDEN PATH (A / E3645A) ----
    pipeline.execute(SupplyCommand.SYSTEM_REMOTE, expect_response=False)

    if args.lock_remote:
        pipeline.execute(SupplyCommand.SYSTEM_RWLOCK, expect_response=False)

    pipeline.execute(SupplyCommand.IDN, expect_response=True)

    if not args.skip_reset:
        pipeline.execute(SupplyCommand.RESET, expect_response=False)

    pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=False)

    if args.range_mode == "low":
        pipeline.execute(SupplyCommand.SET_RANGE_LOW, expect_response=False)
    else:
        pipeline.execute(SupplyCommand.SET_RANGE_HIGH, expect_response=False)

    if not args.skip_ovp:
        pipeline.execute(SupplyCommand.OVP_SET, value=args.ovp, expect_response=False)
        pipeline.execute(SupplyCommand.OVP_ENABLE, expect_response=False)
        pipeline.execute(SupplyCommand.OVP_CLEAR, expect_response=False)

    pipeline.execute(SupplyCommand.SET_VOLTAGE, value=args.volt, expect_response=False)
    pipeline.execute(SupplyCommand.SET_CURRENT, value=args.curr, expect_response=False)

    pipeline.execute(SupplyCommand.OPEN_OUTPUT, expect_response=False)

    pipeline.execute(SupplyCommand.MEASURE_VOLTAGE, expect_response=True)
    pipeline.execute(SupplyCommand.MEASURE_CURRENT, expect_response=True)

    pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=False)
    pipeline.execute(SupplyCommand.SYSTEM_LOCAL, expect_response=False)


def run_profile_b(pipeline: SupplyPipeline, args: argparse.Namespace) -> None:
    # ---- GOLDEN PATH (B / E3631A) ----
    pipeline.execute(SupplyCommand.SYSTEM_REMOTE, expect_response=True)

    if args.lock_remote:
        # B profile may or may not support RWLOCK; config decides.
        pipeline.execute(SupplyCommand.SYSTEM_RWLOCK, expect_response=True)

    pipeline.execute(SupplyCommand.IDN, expect_response=True)

    if not args.skip_reset:
        pipeline.execute(SupplyCommand.RESET, expect_response=True)

    pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=True)

    # Rail selection is mandatory for E3631A-like supplies
    if args.rail == "P6V":
        pipeline.execute(SupplyCommand.SELECT_P6V, expect_response=True)
    elif args.rail == "P25V":
        pipeline.execute(SupplyCommand.SELECT_P25V, expect_response=True)
    else:
        pipeline.execute(SupplyCommand.SELECT_N25V, expect_response=True)

    # Setpoints
    if args.use_apply:
        # APPLY template depends on mapping; keep as optional
        # If your mapping is "APPL {voltage},{current}" you should implement that via config placeholders
        # For now, use separate commands unless you update driver to support named placeholders.
        pipeline.execute(SupplyCommand.APPLY, value=None, expect_response=True)
    else:
        pipeline.execute(SupplyCommand.SET_VOLTAGE, value=args.volt, expect_response=True)
        pipeline.execute(SupplyCommand.SET_CURRENT, value=args.curr, expect_response=True)

    pipeline.execute(SupplyCommand.OPEN_OUTPUT, expect_response=True)

    pipeline.execute(SupplyCommand.MEASURE_VOLTAGE, expect_response=True)

    pipeline.execute(SupplyCommand.MEASURE_CURRENT, expect_response=True)

    pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=True)
    pipeline.execute(SupplyCommand.SYSTEM_LOCAL, expect_response=True)


def main() -> int:
    args = parse_args()

    default_name, profiles = load_supply_profiles(args.config)
    supply_name = args.supply or default_name

    if supply_name not in profiles:
        available = ", ".join(sorted(profiles.keys()))
        raise SystemExit(f"Unknown supply profile '{supply_name}'. Available: {available}")

    profile = profiles[supply_name]

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
        if supply_name == "A":
            run_profile_a(pipeline, args)
        elif supply_name == "B":
            run_profile_b(pipeline, args)
        else:
            # Default behavior: minimal common sequence
            pipeline.execute(SupplyCommand.SYSTEM_REMOTE, expect_response=False)
            pipeline.execute(SupplyCommand.IDN, expect_response=True)
            pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=False)
            pipeline.execute(SupplyCommand.SET_VOLTAGE, value=args.volt, expect_response=False)
            pipeline.execute(SupplyCommand.SET_CURRENT, value=args.curr, expect_response=False)
            pipeline.execute(SupplyCommand.OPEN_OUTPUT, expect_response=False)
            pipeline.execute(SupplyCommand.MEASURE_VOLTAGE, expect_response=True)
            pipeline.execute(SupplyCommand.MEASURE_CURRENT, expect_response=True)
            pipeline.execute(SupplyCommand.CLOSE_OUTPUT, expect_response=False)
            pipeline.execute(SupplyCommand.SYSTEM_LOCAL, expect_response=False)

    finally:
        transport.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
