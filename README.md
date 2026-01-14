# Power Supply Automation

## Overview

This repository provides a Python-based automation framework for controlling
a programmable power supply via a USB-to-RS232 serial interface.

The solution is designed to be:
- Vendor-agnostic
- Safe for laboratory and engineering use
- Suitable for automated power control, measurements, and test scenarios

The focus is on **reliable operation**, **clear separation of concerns**, and
**controlled power sequencing** rather than GUI or advanced CI features.

---

## Scope

This project supports:
- Serial (RS-232) communication with programmable power supplies
- Command-based control (e.g., set voltage/current, enable/disable output)
- Voltage and current measurements
- Scripted and repeatable power automation workflows

Out of scope:
- GUI applications
- SCPI theory documentation
- Continuous Integration (CI) pipelines
- Unit test prioritization (optional, non-blocking)

---

## Repository Structure
.
├─ src/
│ ├─ config.py # Serial configuration definitions
│ ├─ enums.py # Command and protocol enumerations
│ ├─ transport.py # Serial transport abstraction
│ ├─ pipeline.py # Power supply command pipeline
│ └─ main.py # Automation entry point
│
├─ unit_test/ # Optional unit tests (not operationally critical)
│
├─ README.md # Project overview (this file)
└─ OPERATIONS.md # Hardware, setup, and usage guide


---

## Requirements

### Hardware
- Windows-based PC
- USB-to-RS232 converter (true RS-232 voltage levels)
- Programmable power supply with RS-232 support

### Software
- Windows 10 / 11
- Python 3.12
- Visual Studio Code (recommended)
- Python virtual environment (`venv_powAuto`)

---

## Installation Summary

1. Install Python 3.12
2. Create and activate the virtual environment
3. Install required packages

```powershell
pip install pyserial


Detailed setup and operational instructions are provided in OPERATIONS.md.

Usage (Quick Start)
python -m src.main COM4


Replace COM4 with the actual serial port assigned by the system.

Operational Safety Notice

This automation controls physical hardware capable of delivering electrical power.
Incorrect usage may result in equipment damage or safety hazards.

Always follow:

Output OFF before configuration

Current limiting before enabling output

Verification via measurement commands

Refer to OPERATIONS.md for mandatory operational procedures.

License and Usage

This project is intended for internal engineering, laboratory, and test automation use.
Adaptation to specific power supply models should follow the manufacturer’s documentation.
