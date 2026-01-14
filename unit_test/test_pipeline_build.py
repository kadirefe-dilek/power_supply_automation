# /unit_test/test_pipeline_build.py

import unittest

from src.pipeline import SupplyPipeline
from src.enums import SupplyCommand, ProtocolFlavor


class DummyTransport:
    # build_command testinde transport kullanılmıyor ama pipeline init istiyor
    def write_line(self, line: str) -> None:
        pass


class TestPipelineBuildCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = SupplyPipeline(transport=DummyTransport(), protocol=ProtocolFlavor.SCPI)

    def test_idn(self):
        self.assertEqual(self.pipeline.build_command(SupplyCommand.IDN), "*IDN?")

    def test_output_on_off_no_channel(self):
        self.assertEqual(self.pipeline.build_command(SupplyCommand.OPEN_OUTPUT), "OUTP ON")
        self.assertEqual(self.pipeline.build_command(SupplyCommand.CLOSE_OUTPUT), "OUTP OFF")

    def test_measure_voltage_current_no_channel(self):
        self.assertEqual(self.pipeline.build_command(SupplyCommand.MEASURE_VOLTAGE), "MEAS:VOLT?")
        self.assertEqual(self.pipeline.build_command(SupplyCommand.MEASURE_CURRENT), "MEAS:CURR?")

    def test_set_voltage_requires_value(self):
        with self.assertRaises(ValueError):
            self.pipeline.build_command(SupplyCommand.SET_VOLTAGE)

    def test_set_current_requires_value(self):
        with self.assertRaises(ValueError):
            self.pipeline.build_command(SupplyCommand.SET_CURRENT)

    def test_set_voltage_format(self):
        cmd = self.pipeline.build_command(SupplyCommand.SET_VOLTAGE, value=5.0)
        self.assertEqual(cmd, "VOLT 5.000")

    def test_set_current_format(self):
        cmd = self.pipeline.build_command(SupplyCommand.SET_CURRENT, value=1.23456)
        self.assertEqual(cmd, "CURR 1.235")  # 3 decimal rounding

    def test_with_channel_variants(self):
        self.assertEqual(
            self.pipeline.build_command(SupplyCommand.MEASURE_VOLTAGE, channel=1),
            "MEAS:VOLT? (@1)"
        )
        self.assertEqual(
            self.pipeline.build_command(SupplyCommand.MEASURE_CURRENT, channel=2),
            "MEAS:CURR? (@2)"
        )
        self.assertEqual(
            self.pipeline.build_command(SupplyCommand.OPEN_OUTPUT, channel=1),
            "OUTP1 ON"
        )
        self.assertEqual(
            self.pipeline.build_command(SupplyCommand.CLOSE_OUTPUT, channel=1),
            "OUTP1 OFF"
        )
        self.assertEqual(
            self.pipeline.build_command(SupplyCommand.SET_VOLTAGE, value=12.0, channel=2),
            "VOLT2 12.000"
        )
        self.assertEqual(
            self.pipeline.build_command(SupplyCommand.SET_CURRENT, value=0.5, channel=2),
            "CURR2 0.500"
        )


if __name__ == "__main__":
    unittest.main()
