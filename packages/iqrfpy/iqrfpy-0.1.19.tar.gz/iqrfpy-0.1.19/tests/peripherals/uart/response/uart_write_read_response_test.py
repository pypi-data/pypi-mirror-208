import unittest
from typing import List
from parameterized import parameterized
from iqrfpy.enums.commands import UartResponseCommands
from iqrfpy.enums.message_types import UartMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import DpaResponsePacketLengthError
from iqrfpy.peripherals.uart.responses.write_read import WriteReadResponse
from tests.helpers.json import generate_json_response

data_ok: dict = {
    'msgid': 'writeReadTest',
    'nadr': 3,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 90,
    'readData': [1, 2, 3, 4, 5],
    'result': {
        'readData': [1, 2, 3, 4, 5],
    },
    'dpa': b'\x03\x00\x0c\x82\x00\x00\x00\x5a\x01\x02\x03\x04\x05'
}

data_ok_1: dict = {
    'msgid': 'writeReadTest',
    'nadr': 3,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'readData': [10, 5, 1, 17, 2],
    'result': {
        'readData': [10, 5, 1, 17, 2],
    },
    'dpa': b'\x03\x00\x0c\x82\x02\x04\x00\x23\x0a\x05\x01\x11\x02'
}

data_error: dict = {
    'msgid': 'writeReadTest',
    'nadr': 1,
    'hwpid': 1028,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x01\x00\x0c\x82\x04\x04\x01\x23'
}


class WriteReadResponseTestCase(unittest.TestCase):

    @parameterized.expand([
        ['from_dpa', data_ok, WriteReadResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, WriteReadResponse.from_dpa(data_ok_1['dpa']), False],
        [
            'from_json',
            data_ok,
            WriteReadResponse.from_json(
                generate_json_response(
                    UartMessages.WRITE_READ,
                    data_ok,
                ),
            ),
            True,
        ],
        [
            'from_json',
            data_ok_1,
            WriteReadResponse.from_json(
                generate_json_response(
                    UartMessages.WRITE_READ,
                    data_ok_1,
                ),
            ),
            True,
        ],
        ['from_dpa_error', data_error, WriteReadResponse.from_dpa(data_error['dpa']), False],
        [
            'from_json_error',
            data_error,
            WriteReadResponse.from_json(
                generate_json_response(
                    UartMessages.WRITE_READ,
                    data_error,
                ),
            ),
            True,
        ]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.UART)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), UartResponseCommands.WRITE_READ)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), UartMessages.WRITE_READ)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(DpaResponsePacketLengthError):
            WriteReadResponse.from_dpa(b'\x03\x00\x0c\x82\x00')

    @parameterized.expand([
        ['from_dpa', data_ok['readData'], WriteReadResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['readData'], WriteReadResponse.from_dpa(data_ok_1['dpa'])],
        [
            'from_json',
            data_ok['readData'],
            WriteReadResponse.from_json(
                generate_json_response(
                    UartMessages.WRITE_READ,
                    data_ok,
                ),
            ),
        ],
        [
            'from_json',
            data_ok_1['readData'],
            WriteReadResponse.from_json(
                generate_json_response(
                    UartMessages.WRITE_READ,
                    data_ok_1,
                ),
            ),
        ],
    ])
    def test_get_network_data(self, _, read_data: List[int], response: WriteReadResponse):
        self.assertEqual(response.get_read_data(), read_data)
