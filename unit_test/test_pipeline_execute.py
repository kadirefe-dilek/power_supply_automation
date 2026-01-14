# /unit_test/test_pipeline_execute.py

import unittest
from unittest.mock import MagicMock

from src.pipeline import SupplyPipeline
from src.enums import SupplyCommand, ProtocolFlavor


class TestPipelineExecute(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = MagicMock()
        self.pipeline = SupplyPipeline(transport=self.transport, protocol=ProtocolFlavor.SCPI)

    def test_echo_to_console_and_line_writes_to_line(self):
        # echo_to_console_and_line sadece write_line çağırmalı
        self.pipeline.echo_to_console_and_line("HELLO_SUPPLY")
        self.transport.write_line.assert_called_once_with("HELLO_SUPPLY")

    def test_execute_expect_response_true_uses_send_and_receive(self):
        self.transport.send_and_receive.return_value = "OK"
        resp = self.pipeline.execute(SupplyCommand.IDN, expect_response=True)

        self.transport.send_and_receive.assert_called_once_with("*IDN?")
        self.transport.write_line.assert_not_called()
        self.assertEqual(resp, "OK")

    def test_execute_expect_response_false_uses_write_line(self):
        resp = self.pipeline.execute(SupplyCommand.OPEN_OUTPUT, expect_response=False)

        self.transport.write_line.assert_called_once_with("OUTP ON")
        self.transport.send_and_receive.assert_not_called()
        self.assertEqual(resp, "")

    def test_execute_set_voltage_no_response(self):
        _ = self.pipeline.execute(SupplyCommand.SET_VOLTAGE, value=5.0, expect_response=False)
        self.transport.write_line.assert_called_once_with("VOLT 5.000")

    def test_execute_measure_voltage_reads_response(self):
        self.transport.send_and_receive.return_value = "4.999"
        resp = self.pipeline.execute(SupplyCommand.MEASURE_VOLTAGE, expect_response=True)
        self.transport.send_and_receive.assert_called_once_with("MEAS:VOLT?")
        self.assertEqual(resp, "4.999")


if __name__ == "__main__":
    unittest.main()
