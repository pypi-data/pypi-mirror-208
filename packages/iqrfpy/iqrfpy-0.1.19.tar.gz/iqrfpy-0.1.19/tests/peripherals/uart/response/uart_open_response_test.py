import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import UartResponseCommands
from iqrfpy.enums.message_types import UartMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import DpaResponsePacketLengthError
from iqrfpy.peripherals.uart.responses.open import OpenResponse
from tests.helpers.json import generate_json_response

data_ok: dict = {
    'msgid': 'openTest',
    'nadr': 3,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 64,
    'dpa': b'\x03\x00\x0c\x80\x00\x00\x00\x40'
}

data_ok_1: dict = {
    'msgid': 'openTest',
    'nadr': 1,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'dpa': b'\x01\x00\x0c\x80\x02\x04\x00\x23'
}

data_error: dict = {
    'msgid': 'openTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x0c\x80\x02\x04\x01\x23'
}


class CloseResponseTestCase(unittest.TestCase):

    @parameterized.expand([
        ['from_dpa', data_ok, OpenResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, OpenResponse.from_dpa(data_ok_1['dpa']), False],
        [
            'from_json',
            data_ok,
            OpenResponse.from_json(
                generate_json_response(
                    UartMessages.OPEN,
                    data_ok,
                ),
            ),
            True,
        ],
        [
            'from_json',
            data_ok_1,
            OpenResponse.from_json(
                generate_json_response(
                    UartMessages.OPEN,
                    data_ok_1,
                ),
            ),
            True,
        ],
        ['from_dpa_error', data_error, OpenResponse.from_dpa(data_error['dpa']), False],
        [
            'from_json_error',
            data_error,
            OpenResponse.from_json(
                generate_json_response(
                    UartMessages.OPEN,
                    data_error,
                ),
            ),
            True,
        ],
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.UART)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), UartResponseCommands.OPEN)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), UartMessages.OPEN)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(DpaResponsePacketLengthError):
            OpenResponse.from_dpa(b'\x03\x00\x0c\x80\x00\x00\x00\x40\x01')
