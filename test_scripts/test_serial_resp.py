import serial, time

PORT = "COM7"
BAUD = 9600  # dokümana göre gerekirse değiştir: 19200/38400 vs.
TIMEOUT = 1.0

def tx(ser, s: str):
    raw = s.encode("ascii", errors="replace")
    print(f"[TX] {raw!r}")
    ser.write(raw)
    ser.flush()

def rx_line(ser):
    data = ser.readline()  # \n görünce döner, timeout ile çıkar
    print(f"[RX] {data!r}")
    return data

with serial.Serial(
    PORT,
    BAUD,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    timeout=TIMEOUT,
    xonxoff=False,
    rtscts=False,
    dsrdtr=False,
) as ser:
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # 1) Clear status
    tx(ser, "*CLS\r\n")
    time.sleep(0.1)

    # 2) IDN
    tx(ser, "*IDN?\r\n")
    rx_line(ser)

    # 3) Read error queue a few times
    for _ in range(3):
        tx(ser, "SYST:ERR?\r\n")
        rx_line(ser)
        time.sleep(0.1)
