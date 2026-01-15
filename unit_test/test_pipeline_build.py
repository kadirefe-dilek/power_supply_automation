# /unit_test/test_pipeline_build.py

import unittest

from src.enums import SupplyCommand
from src.drivers.map_driver import MapBasedDriver, DriverConfigError


class TestMapBasedDriverBuildCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = MapBasedDriver(
            driver_name="A",
            command_map={
                SupplyCommand.IDN: "*IDN?",
                SupplyCommand.RESET: "*RST",
                SupplyCommand.SYSTEM_REMOTE: "SYSTem:REMote",
                SupplyCommand.SYSTEM_LOCAL: "SYSTem:LOCal",
                SupplyCommand.SYSTEM_RWLOCK: "SYSTem:RWLock",
                SupplyCommand.SET_RANGE_LOW: "VOLT:RANG P35V",
                SupplyCommand.SET_RANGE_HIGH: "VOLT:RANG P60V",
                SupplyCommand.OVP_SET: "VOLT:PROT {value}",
                SupplyCommand.OVP_ENABLE: "VOLT:PROT:STAT ON",
                SupplyCommand.OVP_DISABLE: "VOLT:PROT:STAT OFF",
                SupplyCommand.OVP_CLEAR: "VOLT:PROT:CLE",
                SupplyCommand.OPEN_OUTPUT: "OUTP ON",
                SupplyCommand.CLOSE_OUTPUT: "OUTP OFF",
                SupplyCommand.SET_VOLTAGE: "VOLT {value}",
                SupplyCommand.SET_CURRENT: "CURR {value}",
                SupplyCommand.MEASURE_VOLTAGE: "MEAS:VOLT?",
                SupplyCommand.MEASURE_CURRENT: "MEAS:CURR?",
            },
            expect_response_set={
                SupplyCommand.IDN,
                SupplyCommand.MEASURE_VOLTAGE,
                SupplyCommand.MEASURE_CURRENT,
            },
            value_decimals=3,
        )

    def test_idn(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.IDN), "*IDN?")

    def test_reset(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.RESET), "*RST")

    def test_remote_local_lock(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.SYSTEM_REMOTE), "SYSTem:REMote")
        self.assertEqual(self.driver.build_command(SupplyCommand.SYSTEM_LOCAL), "SYSTem:LOCal")
        self.assertEqual(self.driver.build_command(SupplyCommand.SYSTEM_RWLOCK), "SYSTem:RWLock")

    def test_range_select(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.SET_RANGE_LOW), "VOLT:RANG P35V")
        self.assertEqual(self.driver.build_command(SupplyCommand.SET_RANGE_HIGH), "VOLT:RANG P60V")

    def test_ovp_set_requires_value(self):
        with self.assertRaises(DriverConfigError):
            self.driver.build_command(SupplyCommand.OVP_SET)

    def test_ovp_set_formats_value(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.OVP_SET, value=6.0), "VOLT:PROT 6.000")

    def test_ovp_enable_disable_clear(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.OVP_ENABLE), "VOLT:PROT:STAT ON")
        self.assertEqual(self.driver.build_command(SupplyCommand.OVP_DISABLE), "VOLT:PROT:STAT OFF")
        self.assertEqual(self.driver.build_command(SupplyCommand.OVP_CLEAR), "VOLT:PROT:CLE")

    def test_set_voltage_current_format(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.SET_VOLTAGE, value=5.0), "VOLT 5.000")
        self.assertEqual(self.driver.build_command(SupplyCommand.SET_CURRENT, value=0.2), "CURR 0.200")

    def test_measure(self):
        self.assertEqual(self.driver.build_command(SupplyCommand.MEASURE_VOLTAGE), "MEAS:VOLT?")
        self.assertEqual(self.driver.build_command(SupplyCommand.MEASURE_CURRENT), "MEAS:CURR?")

    def test_expects_response(self):
        self.assertTrue(self.driver.expects_response(SupplyCommand.IDN))
        self.assertTrue(self.driver.expects_response(SupplyCommand.MEASURE_VOLTAGE))
        self.assertTrue(self.driver.expects_response(SupplyCommand.MEASURE_CURRENT))
        self.assertFalse(self.driver.expects_response(SupplyCommand.OPEN_OUTPUT))
        self.assertFalse(self.driver.expects_response(SupplyCommand.RESET))


if __name__ == "__main__":
    unittest.main()
