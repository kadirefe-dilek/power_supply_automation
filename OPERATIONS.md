# Power Supply Automation
## Hardware, Setup, and Operational Guide

---

## 1. Purpose

This document defines the hardware requirements, software setup, validation steps,
and safe operational procedures for using the Power Supply Automation framework.

It is intended for engineers and operators who need to:
- Bring up a new hardware setup
- Validate serial communication
- Operate a programmable power supply via automation in a controlled manner

The primary objective is reliable and safe power control. Unit testing, GUI tooling,
and CI/CD integration are explicitly out of scope for this document.

---

## 2. Hardware Requirements

### 2.1 Mandatory Components

| Component | Requirement |
|----------|-------------|
| Host PC | Windows 10 or Windows 11 |
| USB–RS232 Converter | True RS-232 voltage levels (±6…±12 V) |
| Power Supply | RS-232 capable, remotely programmable |
| Cabling | TX, RX, and GND connected |

WARNING:  
TTL-level UART adapters (3.3 V / 5 V) are not compatible and must not be used.

---

### 2.2 USB–RS232 Converter Verification

Recommended converter chipsets (in order of preference):
1. FTDI (FT232 series)
2. Silicon Labs (CP210x series)
3. CH340 (acceptable with caution)

The converter must appear in Windows Device Manager as:

Ports (COM & LPT)
    USB Serial Port (COMx)

If the device does not appear as listed above, automation must not be executed.

---

### 2.3 Serial Line Pin Mapping (Minimum Configuration)

| Converter | Power Supply |
|----------|--------------|
| TX | RX |
| RX | TX |
| GND | GND |

Notes:
- RTS/CTS lines must not be connected unless explicitly required by the power supply
- Hardware flow control must be disabled by default

---

### 2.4 Electrical Safety Rules

- All cabling shall be connected while the power supply is de-energized
- Initial configuration shall be performed with:
  - Output: OFF
  - Voltage: 0 V
  - Current limit: Minimum allowed value

Failure to comply may result in equipment damage or unsafe operating conditions.

---

## 3. Software Requirements

### 3.1 Operating System

- Windows 10 or Windows 11
- Administrator privileges for driver installation

---

### 3.2 Python Environment

- Python version: 3.12
- Virtual environment name: venv_powAuto

Virtual environment activation (PowerShell):

    .\venv_powAuto\Scripts\Activate.ps1

If execution policy blocks activation:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Verification:

    python --version

The reported version must be Python 3.12.x.

---

### 3.3 Required Python Packages

| Package | Purpose |
|--------|---------|
| pyserial | Serial (RS-232) communication |

Installation command:

    pip install pyserial

---

## 4. Hardware Validation Steps

### 4.1 Loopback Test (Without Power Supply)

Purpose:
Verify the USB–RS232 converter, driver, and serial interface before connecting the power supply.

Procedure:
1. Short the TX and RX pins on the converter
2. Open PuTTY or Tera Term
3. Configure the connection:
   - Connection type: Serial
   - Port: COMx
   - Baud rate: 9600
   - Data format: 8-N-1
4. Type characters in the terminal

Expected Result:
Typed characters are echoed back to the terminal.

Failure indicates:
- Faulty converter
- Incorrect COM port selection
- Driver installation issues

---

### 4.2 Power Supply Serial Configuration

Configure the power supply via its front panel or local interface:

- Remote / Serial Control: ENABLED
- Baud rate: 9600
- Parity: None
- Stop bits: 1
- Echo: OFF (if configurable)

---

### 4.3 Terminal-Level Power Supply Verification

Before running automation, verify communication manually using a terminal application.

Command:

    *IDN?

Expected response:

    VENDOR,MODEL,SERIAL,FIRMWARE

---

## 5. Automation Usage

### 5.1 Running the Automation

From the project root directory:

    python -m src.main COM4

Replace COM4 with the correct serial port identifier.

---

### 5.2 Safe Operational Sequence

The automation enforces the following sequence:

1. Establish serial connection
2. Query device identification
3. Configure voltage and current with output OFF
4. Enable output
5. Perform voltage and current measurements
6. Disable output
7. Close serial connection

This sequence prevents sudden load application, overcurrent events,
and power supply lock-ups.

---

## 6. Troubleshooting Reference

| Symptom | Likely Cause |
|--------|--------------|
| No response | TX/RX swapped |
| Garbled data | Baud rate or parity mismatch |
| Commands sent, no reply | Missing query (?) |
| Works in terminal, not in Python | Line ending mismatch |
| Power supply freezes | Echo enabled |

---

## 7. Operational Rules

- Never enable output before setting voltage and current limits
- Always verify output using measurement commands
- Do not hardcode COM port identifiers
- Do not assume protocol behavior without consulting manufacturer documentation

---

## 8. Conclusion

Following this guide ensures:
- Correct hardware integration
- Reliable serial communication
- Safe and repeatable power control
- Readiness for advanced automation scenarios such as burn-in or power cycling

This document serves as an operational baseline for laboratory
and engineering environments.
