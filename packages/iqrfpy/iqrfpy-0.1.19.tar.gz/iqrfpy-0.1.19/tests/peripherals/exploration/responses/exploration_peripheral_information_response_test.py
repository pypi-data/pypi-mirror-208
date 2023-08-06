import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import ExplorationResponseCommands
from iqrfpy.enums.message_types import ExplorationMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.exceptions import DpaResponsePacketLengthError
from iqrfpy.peripherals.exploration.responses.peripheral_information import PeripheralInformationResponse
from tests.helpers.json import generate_json_response

data_ok: dict = {
    'msgid': 'peripheralInformationTest',
    'pnum': EmbedPeripherals.OS,
    'nadr': 3,
    'hwpid': 5122,
    'rcode': 0,
    'dpa_value': 79,
    'result': {
        'perTe': 3,
        'perT': 3,
        'par1': 3,
        'par2': 169,
        'per': EmbedPeripherals.OS
    },
    'dpa': b'\x03\x00\x02\xbf\x02\x14\x00\x4f\x03\x03\x03\xa9'
}

data_error: dict = {
    'msgid': 'peripheralInformationTest',
    'pnum': EmbedPeripherals.EXPLORATION,
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 7,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x02\xbf\x04\x04\x07\x23'
}


class PeripheralInformationResponseTestCase(unittest.TestCase):
    @parameterized.expand([
        ['from_dpa', data_ok, PeripheralInformationResponse.from_dpa(data_ok['dpa']), False],
        [
            'from_json',
            data_ok,
            PeripheralInformationResponse.from_json(
                generate_json_response(
                    ExplorationMessages.PERIPHERAL_INFORMATION,
                    data_ok
                )
            ),
            True,
        ],
        ['from_dpa_error', data_error, PeripheralInformationResponse.from_dpa(data_error['dpa']), False],
        [
            'from_json_error',
            data_error,
            PeripheralInformationResponse.from_json(
                generate_json_response(
                    ExplorationMessages.PERIPHERAL_INFORMATION,
                    data_error
                )
            ),
            True,
        ]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), response_data['pnum'])
        with self.subTest():
            self.assertEqual(response.get_pcmd(), ExplorationResponseCommands.PERIPHERALS_ENUMERATION_INFORMATION)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), ExplorationMessages.PERIPHERAL_INFORMATION)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(DpaResponsePacketLengthError):
            PeripheralInformationResponse.from_dpa(b'\x03\x00\x02\xbf\x02\x14\x00\x4f\x03')

    @parameterized.expand([
        ['from_dpa', data_ok['result']['perTe'], PeripheralInformationResponse.from_dpa(data_ok['dpa'])],
        [
            'from_json',
            data_ok['result']['perTe'],
            PeripheralInformationResponse.from_json(
                generate_json_response(ExplorationMessages.PERIPHERAL_INFORMATION, data_ok)
            )
        ]
    ])
    def test_get_perte(self, _, perte: int, response: PeripheralInformationResponse):
        self.assertEqual(response.get_perte(), perte)

    @parameterized.expand([
        ['from_dpa', data_ok['result']['perT'], PeripheralInformationResponse.from_dpa(data_ok['dpa'])],
        [
            'from_json',
            data_ok['result']['perT'],
            PeripheralInformationResponse.from_json(
                generate_json_response(ExplorationMessages.PERIPHERAL_INFORMATION, data_ok)
            )
        ]
    ])
    def test_get_pert(self, _, pert: int, response: PeripheralInformationResponse):
        self.assertEqual(response.get_pert(), pert)

    @parameterized.expand([
        ['from_dpa', data_ok['result']['par1'], PeripheralInformationResponse.from_dpa(data_ok['dpa'])],
        [
            'from_json',
            data_ok['result']['par1'],
            PeripheralInformationResponse.from_json(
                generate_json_response(ExplorationMessages.PERIPHERAL_INFORMATION, data_ok)
            )
        ]
    ])
    def test_get_par1(self, _, par1: int, response: PeripheralInformationResponse):
        self.assertEqual(response.get_par1(), par1)

    @parameterized.expand([
        ['from_dpa', data_ok['result']['par2'], PeripheralInformationResponse.from_dpa(data_ok['dpa'])],
        [
            'from_json',
            data_ok['result']['par2'],
            PeripheralInformationResponse.from_json(
                generate_json_response(ExplorationMessages.PERIPHERAL_INFORMATION, data_ok)
            )
        ]
    ])
    def test_get_par2(self, _, par2: int, response: PeripheralInformationResponse):
        self.assertEqual(response.get_par2(), par2)
