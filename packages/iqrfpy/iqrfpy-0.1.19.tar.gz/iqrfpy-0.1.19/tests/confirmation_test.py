import unittest
from iqrfpy.enums.commands import NodeRequestCommands
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.confirmation import Confirmation


class ConfirmationTestCase(unittest.TestCase):

    def test_from_dpa_ok(self):
        message = Confirmation.from_dpa(b'\x01\x00\x01\x00\xff\xff\xff\x36\x01\x04\x01')
        self.assertEqual(message.get_nadr(), 1)
        self.assertEqual(message.get_pnum(), EmbedPeripherals.NODE)
        self.assertEqual(message.get_pcmd(), NodeRequestCommands.READ)
        self.assertEqual(message.get_hwpid(), 65535)
        self.assertEqual(message.get_dpa_value(), 54)
        self.assertEqual(message.get_request_hops(), 1)
        self.assertEqual(message.get_response_hops(), 1)
        self.assertEqual(message.get_timeslot(), 4)

    def test_from_dpa_invalid_len(self):
        with self.assertRaises(ValueError):
            Confirmation.from_dpa(b'\x01\x00\x01\x00\xff\xff')

    def test_from_dpa_not_confirmation(self):
        with self.assertRaises(ValueError):
            Confirmation.from_dpa(b'\x01\x00\x01\x00\xff\xff\x00\x36\x01\x04\x01')

    def test_from_json_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            Confirmation.from_json({})
