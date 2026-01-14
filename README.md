# Power Supply Automation

## Overview

This repository provides a Python-based automation framework for controlling a
programmable power supply via a USB-to-RS232 serial interface.

The solution is designed to be:
- Vendor-agnostic
- Safe for laboratory and engineering environments
- Suitable for scripted power control and measurement workflows

The primary focus is **operational reliability and safety**, not graphical interfaces
or extensive test frameworks.

---

## Scope

This project supports:
- RS-232 serial communication with programmable power supplies
- Command-based control (voltage, current, output enable/disable)
- Voltage and current measurements
- Repeatable automation workflows

Out of scope:
- Graphical user interfaces (GUI)
- SCPI theory or protocol standard documentation
- Continuous Integration (CI/CD) pipelines
- Mandatory unit test coverage

---

## Repository Structure

.
├─ src/
│  ├─ config.py        Serial configuration definitions
│  ├─ enums.py         Command and protocol enumerations
│  ├─ transport.py    Serial transport abstraction
│  ├─ pipeline.py     Power supply command pipeline
│  └─ main.py         Automation entry point
│
├─ unit_test/          Optional unit tests (non-blocking)
│
├─ README.md           Project overview
└─ OPERATIONS.md       Hardware setup and operational guide

---

## Requirements

### Hardware
- Windows-based PC
- USB-to-RS232 converter (true RS-232 voltage levels)
- Programmable power supply with RS-232 support

### Software
- Windows 10 or Windows 11
- Python 3.12
- Visual Studio Code (recommended)
- Python virtual environment (venv_powAuto)

---

## Installation Summary

1. Install Python 3.12
2. Create and activate the virtual environment
3. Install required Python packages

```powershell
pip install pyserial
```

Detailed setup and operational instructions are provided in **OPERATIONS.md**.

---

## Quick Start

Activate the virtual environment and run the automation:

```powershell
python -m src.main COM4
```

Replace `COM4` with the serial port assigned by the operating system.

---

## Operational Safety Notice

This automation framework controls physical hardware capable of delivering
electrical power.

Improper usage may result in:
- Equipment damage
- Unexpected power application
- Safety hazards

Always follow these principles:
- Configure voltage and current limits with output OFF
- Enable output only after configuration
- Verify output using measurement commands

Refer to **OPERATIONS.md** for mandatory operational procedures.

---

## Intended Use

This project is intended for:
- Laboratory automation
- Engineering validation and test setups
- Controlled power sequencing and measurements

Adaptation to specific power supply models must follow the manufacturer’s
official documentation.

---

## Disclaimer

This software is provided as-is for engineering and laboratory use.
The user is responsible for validating correct operation with the
target hardware configuration.
