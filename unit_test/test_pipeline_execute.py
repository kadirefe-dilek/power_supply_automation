# /unit_test/test_pipeline_execute.py

import unittest
from unittest.mock import MagicMock

from src.pipeline import SupplyPipeline
from src.enums import SupplyCommand


class TestPipelineExecute(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = MagicMock()
        self.driver = MagicMock()
        self.driver.name = "A"

        # Default driver policies
        self.driver.expects_response.side_effect = lambda cmd: cmd in {
            SupplyCommand.IDN,
            SupplyCommand.MEASURE_VOLTAGE,
            SupplyCommand.MEASURE_CURRENT
        }

        self.pipeline = SupplyPipeline(transport=self.transport, driver=self.driver)

    def test_execute_expect_response_true_uses_send_and_receive(self):
        self.driver.build_command.return_value = "*IDN?"
        self.transport.send_and_receive.return_value = "OK"

        resp = self.pipeline.execute(SupplyCommand.IDN)

        self.driver.build_command.assert_called_once_with(SupplyCommand.IDN, value=None, channel=None)
        self.transport.send_and_receive.assert_called_once_with("*IDN?")
        self.transport.write_line.assert_not_called()
        self.assertEqual(resp, "OK")

    def test_execute_expect_response_false_uses_write_line(self):
        self.driver.build_command.return_value = "OUTP ON"

        resp = self.pipeline.execute(SupplyCommand.OPEN_OUTPUT, expect_response=False)

        self.driver.build_command.assert_called_once_with(SupplyCommand.OPEN_OUTPUT, value=None, channel=None)
        self.transport.write_line.assert_called_once_with("OUTP ON")
        self.transport.send_and_receive.assert_not_called()
        self.assertEqual(resp, "")

    def test_execute_default_expectation_uses_driver_policy(self):
        self.driver.build_command.return_value = "VOLT 5.000"

        # SET_VOLTAGE default policy should be False, so should use write_line
        _ = self.pipeline.execute(SupplyCommand.SET_VOLTAGE, value=5.0)

        self.driver.build_command.assert_called_once_with(SupplyCommand.SET_VOLTAGE, value=5.0, channel=None)
        self.transport.write_line.assert_called_once_with("VOLT 5.000")
        self.transport.send_and_receive.assert_not_called()

    def test_execute_passes_value_and_channel(self):
        self.driver.build_command.return_value = "VOLT 12.000"

        _ = self.pipeline.execute(SupplyCommand.SET_VOLTAGE, value=12.0, channel=1, expect_response=False)

        self.driver.build_command.assert_called_once_with(SupplyCommand.SET_VOLTAGE, value=12.0, channel=1)
        self.transport.write_line.assert_called_once_with("VOLT 12.000")


if __name__ == "__main__":
    unittest.main()
