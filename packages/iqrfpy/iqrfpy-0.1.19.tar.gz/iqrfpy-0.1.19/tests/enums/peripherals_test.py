import unittest
from iqrfpy.enums.peripherals import *


class PeripheralsTestCase(unittest.TestCase):

    def test_has_value_ok(self):
        value = EmbedPeripherals.COORDINATOR
        self.assertTrue(EmbedPeripherals.has_value(value))
        value = Standards.SENSOR
        self.assertTrue(Standards.has_value(value))

    def test_has_value_unknown(self):
        value = -1
        self.assertFalse(EmbedPeripherals.has_value(value))
        self.assertFalse(Standards.has_value(value))

    def test_get_member_ok(self):
        value = EmbedPeripherals.COORDINATOR
        self.assertEqual(
            EmbedPeripherals(value),
            EmbedPeripherals.COORDINATOR
        )
        value = Standards.SENSOR
        self.assertEqual(
            Standards(value),
            Standards.SENSOR
        )

    def test_get_member_unknown(self):
        value = -1
        with self.assertRaises(ValueError):
            EmbedPeripherals(value)
        with self.assertRaises(ValueError):
            Standards(value)

    def test_get_member_different_child(self):
        value = Standards.SENSOR
        with self.assertRaises(ValueError):
            EmbedPeripherals(value)


if __name__ == '__main__':
    unittest.main()
