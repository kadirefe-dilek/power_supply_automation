# Power Supply Automation

## Overview

This repository provides a Python-based automation framework for controlling
programmable DC power supplies via a USB-to-RS232 serial interface.

The framework is designed to be:
- Vendor-agnostic and configuration-driven
- Safe for laboratory and engineering environments
- Extensible to support multiple power supply models
- Suitable for scripted power control, measurement, and validation workflows

The primary focus is **operational reliability, safety, and repeatability**.
Graphical interfaces and CI/CD tooling are intentionally out of scope.

---

## Supported Power Supplies

The automation supports multiple power supplies through external configuration.

### Default Configuration
- **Profile A (default): Keysight / Agilent E3645A**
  - RS-232 communication
  - SCPI command set
  - Dual output range support
  - Over-Voltage Protection (OVP)
  - Remote / Local / Panel Lock control

Additional supplies can be added by extending `power_supplies.json`
without modifying core automation logic.

---

## Repository Structure

```
.
├─ src/
│  ├─ config.py           Serial configuration definitions
│  ├─ enums.py            High-level supply command enumeration
│  ├─ transport.py        Serial transport abstraction (pyserial)
│  ├─ supply_config.py    Supply profile loader (JSON-based)
│  ├─ pipeline.py         Execution pipeline (driver + transport)
│  ├─ drivers/
│  │  ├─ base.py          Driver interface definition
│  │  ├─ map_driver.py    Map-based SCPI/ASCII driver
│  │  └─ factory.py       Driver factory
│  └─ main.py             Automation entry point (CLI)
│
├─ unit_test/             Unit tests (updated for multi-supply support)
│
├─ power_supplies.json    Supply configuration (default = E3645A)
├─ README.md              Project overview (this file)
└─ OPERATIONS.md          Hardware setup and operational guide
```

---

## Requirements

### Hardware
- Windows-based PC
- USB-to-RS232 converter (true RS-232 voltage levels, not TTL)
- Programmable power supply with RS-232 support  
  (E3645A is the default reference implementation)

### Software
- Windows 10 / Windows 11
- Python 3.12
- Visual Studio Code (recommended)
- Python virtual environment: `venv_powAuto`

---

## Installation Summary

1. Install Python 3.12
2. Create and activate the virtual environment
3. Install required Python packages

```powershell
pip install pyserial
```

Refer to **OPERATIONS.md** for detailed hardware setup and validation steps.

---

## Running the Automation  
### (Windows / VS Code Terminal)

All commands are executed from the repository root directory.

### Activate Virtual Environment

```powershell
.\venv_powAuto\Scripts\Activate.ps1
```

If PowerShell execution policy blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Verify:

```powershell
python --version
```

---

### Default Execution (E3645A – Profile A)

Runs the full **golden path** using the default supply profile (A = E3645A):

```powershell
python -m src.main COM4
```

Where:
- `COM4` is the serial port assigned to the USB–RS232 adapter

---

### Golden Path Sequence (E3645A)

The default execution performs the following sequence:

1. Switch power supply to **REMOTE** mode
2. Query identification (`*IDN?`)
3. Reset to a known baseline (`*RST`)
4. Ensure output is OFF
5. Select output range (default: LOW / 35 V)
6. Configure OVP and enable protection
7. Set voltage and current limits
8. Enable output
9. Measure voltage and current
10. Disable output
11. Return to **LOCAL** mode

This sequence is designed to prevent unsafe power application
and ensure deterministic behavior.

---

### Custom Execution Options

#### Select Output Range
```powershell
python -m src.main COM4 --range high
```

#### Override Voltage / Current / OVP
```powershell
python -m src.main COM4 --volt 12.0 --curr 0.5 --ovp 13.0
```

#### Skip Reset or OVP (Debug / Advanced Use)
```powershell
python -m src.main COM4 --skip-reset --skip-ovp
```

#### Lock Front Panel in Remote Mode
```powershell
python -m src.main COM4 --lock-remote
```

---

## Adding a New Power Supply

To add support for a new power supply:

1. Add a new profile entry to `power_supplies.json`
2. Define serial parameters and command mappings
3. Select the profile at runtime:

```powershell
python -m src.main COM4 --supply B
```

No changes to the pipeline or transport layers are required.

---

## Safety Notice

This automation framework controls physical hardware capable of delivering
electrical power.

Always follow these rules:
- Configure voltage and current limits with output OFF
- Enable output only after configuration
- Verify output using measurement commands
- Follow the procedures defined in **OPERATIONS.md**

Failure to follow these rules may result in equipment damage or safety hazards.

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
