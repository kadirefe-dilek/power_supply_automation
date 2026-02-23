# /unit_test/test_transport.py

import unittest
from unittest.mock import patch, MagicMock

from src.config import SerialConfig
from src.transport import SerialTransport, SerialTransportError


class TestSerialTransport(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = SerialConfig(port="COM_TEST", baudrate=9600, newline="\n")

    @patch("src.transport.serial.Serial")
    def test_open_success(self, serial_ctor):
        fake_ser = MagicMock()
        fake_ser.is_open = True
        serial_ctor.return_value = fake_ser

        tr = SerialTransport(self.cfg)
        tr.open()

        serial_ctor.assert_called_once()
        self.assertTrue(tr._ser.is_open)

    @patch("src.transport.serial.Serial")
    def test_open_failure_raises(self, serial_ctor):
        serial_ctor.side_effect = Exception("boom")

        tr = SerialTransport(self.cfg)
        with self.assertRaises(SerialTransportError):
            tr.open()

    def test_write_line_requires_open(self):
        tr = SerialTransport(self.cfg)
        with self.assertRaises(SerialTransportError):
            tr.write_line("TEST")

    def test_read_line_requires_open(self):
        tr = SerialTransport(self.cfg)
        with self.assertRaises(SerialTransportError):
            tr.read_line()

    def test_send_and_receive_calls_write_then_read(self):
        tr = SerialTransport(self.cfg)
        tr._ser = MagicMock()
        tr._ser.is_open = True

        tr._ser.readline.return_value = b"OK\n"

        resp = tr.send_and_receive("PING", settle_s=0)

        tr._ser.reset_input_buffer.assert_called_once()
        tr._ser.write.assert_called_once()
        tr._ser.flush.assert_called_once()
        self.assertEqual(resp, "OK")


if __name__ == "__main__":
    unittest.main()
