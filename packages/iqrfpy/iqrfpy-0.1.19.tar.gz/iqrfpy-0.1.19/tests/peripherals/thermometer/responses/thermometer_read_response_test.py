import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import ThermometerResponseCommands
from iqrfpy.enums.message_types import ThermometerMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import DpaResponsePacketLengthError
from iqrfpy.peripherals.thermometer.responses.read import ReadResponse
from tests.helpers.json import generate_json_response

data_ok: dict = {
    'msgid': 'readTest',
    'nadr': 3,
    'hwpid': 5122,
    'rcode': 0,
    'dpa_value': 106,
    'temperature': 24.0625,
    'result': {
        'temperature': 24.0625,
    },
    'dpa': b'\x03\x00\x0a\x80\x02\x14\x00\x6a\x18\x81\x01'
}

data_ok_1: dict = {
    'msgid': 'readTest',
    'nadr': 3,
    'hwpid': 5122,
    'rcode': 0,
    'dpa_value': 106,
    'temperature': -20.5,
    'result': {
        'temperature': -20.5,
    },
    'dpa': b'\x03\x00\x0a\x80\x02\x14\x00\x6a\xeb\xb8\x0e'
}

data_error: dict = {
    'msgid': 'readTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x0a\x80\x04\x04\x01\x23'
}


class ReadResponseTestCase(unittest.TestCase):

    @parameterized.expand([
        ['from_dpa', data_ok, ReadResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, ReadResponse.from_dpa(data_ok_1['dpa']), False],
        [
            'from_json',
            data_ok,
            ReadResponse.from_json(
                generate_json_response(
                    ThermometerMessages.READ,
                    data_ok
                )
            ),
            True
        ],
        [
            'from_json',
            data_ok_1,
            ReadResponse.from_json(
                generate_json_response(
                    ThermometerMessages.READ,
                    data_ok_1
                )
            ),
            True
        ],
        ['from_dpa_error', data_error, ReadResponse.from_dpa(data_error['dpa']), False],
        [
            'from_json_error',
            data_error,
            ReadResponse.from_json(
                generate_json_response(
                    ThermometerMessages.READ,
                    data_error
                )
            ),
            True
        ]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.THERMOMETER)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), ThermometerResponseCommands.READ)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), ThermometerMessages.READ)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(DpaResponsePacketLengthError):
            ReadResponse.from_dpa(b'\x03\x00\x0a\x80\x02\x14\x00\x6a\x18')

    @parameterized.expand([
        ['from_dpa', data_ok['temperature'], ReadResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['temperature'], ReadResponse.from_dpa(data_ok_1['dpa'])],
        [
            'from_json',
            data_ok['temperature'],
            ReadResponse.from_json(
                generate_json_response(
                    ThermometerMessages.READ,
                    data_ok
                )
            )
        ],
        [
            'from_json',
            data_ok_1['temperature'],
            ReadResponse.from_json(
                generate_json_response(
                    ThermometerMessages.READ,
                    data_ok_1
                )
            )
        ],
    ])
    def test_get_temperature(self, _, temperature: float, response: ReadResponse):
        self.assertEqual(response.get_temperature(), temperature)
