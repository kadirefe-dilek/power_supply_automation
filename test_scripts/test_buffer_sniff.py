import serial, time

ser = serial.Serial("COM7", 9600, timeout=0.2, rtscts=False, xonxoff=False, dsrdtr=False)
ser.dtr = True
ser.rts = True
time.sleep(0.2)

ser.reset_input_buffer()
ser.write(b"*IDN?\r\n"); ser.flush()

buf = b""
t0 = time.time()
while time.time() - t0 < 3.0:
    chunk = ser.read(256)
    if chunk:
        buf += chunk
        print("GOT:", chunk)
print("TOTAL:", buf)

ser.close()
