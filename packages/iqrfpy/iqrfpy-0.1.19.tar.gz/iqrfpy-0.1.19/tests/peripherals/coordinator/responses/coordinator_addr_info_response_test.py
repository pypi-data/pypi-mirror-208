import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.addr_info import AddrInfoResponse

data_ok: dict = {
    'msgid': 'addrInfoTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 64,
    'dev_nr': 10,
    'did': 42,
    'dpa': b'\x00\x00\x00\x80\x00\x00\x00\x40\x0a\x2a'
}

data_ok_1: dict = {
    'msgid': 'addrInfoTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'dev_nr': 5,
    'did': 42,
    'dpa': b'\x00\x00\x00\x80\x02\x04\x00\x23\x05\x2a'
}

data_error: dict = {
    'msgid': 'addrInfoTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x80\x04\x04\x01\x23'
}


class AddrInfoResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        json = {
            'mType': 'iqrfEmbedCoordinator_AddrInfo',
            'data': {
                'msgId': response_data['msgid'],
                'rsp': {
                    'nAdr': response_data['nadr'],
                    'hwpId': response_data['hwpid'],
                    'rCode': response_data['rcode'],
                    'dpaVal': response_data['dpa_value'],
                },
                'insId': 'iqrfgd2-1',
                'status': response_data['rcode']
            }
        }
        if response_data['rcode'] == 0:
            json['data']['rsp']['result'] = {
                'devNr': response_data['dev_nr'],
                'did': response_data['did']
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, AddrInfoResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, AddrInfoResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, AddrInfoResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, AddrInfoResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, AddrInfoResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, AddrInfoResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.ADDR_INFO)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.ADDR_INFO)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            AddrInfoResponse.from_dpa(b'\x00\x00\x00\x80\x00\x00\x00\x40\x0a')

    @parameterized.expand([
        ['from_dpa', data_ok['dev_nr'], AddrInfoResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['dev_nr'], AddrInfoResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['dev_nr'], AddrInfoResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['dev_nr'], AddrInfoResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_dev_nr(self, _, dev_nr, response):
        self.assertEqual(response.get_dev_nr(), dev_nr)

    @parameterized.expand([
        ['from_dpa', data_ok['did'], AddrInfoResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['did'], AddrInfoResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['did'], AddrInfoResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['did'], AddrInfoResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_did(self, _, did, response):
        self.assertEqual(response.get_did(), did)
