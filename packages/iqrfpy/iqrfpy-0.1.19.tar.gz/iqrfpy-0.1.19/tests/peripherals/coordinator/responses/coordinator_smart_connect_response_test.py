import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.smart_connect import SmartConnectResponse

data_ok: dict = {
    'msgid': 'smartConnectTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 71,
    'bond_addr': 1,
    'dev_nr': 2,
    'dpa': b'\x00\x00\x00\x92\x00\x00\x00\x47\x01\x02'
}

data_ok_1: dict = {
    'msgid': 'smartConnectTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'bond_addr': 10,
    'dev_nr': 100,
    'dpa': b'\x00\x00\x00\x92\x02\x04\x00\x23\x0a\x64'
}

data_error: dict = {
    'msgid': 'smartConnectTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 7,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x92\x04\x04\x07\x23'
}


class SmartConnectResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        json = {
            'mType': 'iqrfEmbedCoordinator_SmartConnect',
            'data': {
                'msgId': response_data['msgid'],
                'rsp': {
                    'nAdr': response_data['nadr'],
                    'hwpId': response_data['hwpid'],
                    'rCode': response_data['rcode'],
                    'dpaVal': response_data['dpa_value']
                },
                'insId': 'iqrfgd2-1',
                'status': response_data['rcode']
            }
        }
        if response_data['rcode'] == 0:
            json['data']['rsp']['result'] = {
                'bondAddr': response_data['bond_addr'],
                'devNr': response_data['dev_nr']
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, SmartConnectResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, SmartConnectResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, SmartConnectResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, SmartConnectResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, SmartConnectResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, SmartConnectResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.SMART_CONNECT)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.SMART_CONNECT)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            SmartConnectResponse.from_dpa(b'\x00\x00\x00\x84\x00\x00\x00\x22')

    @parameterized.expand([
        ['from_dpa', data_ok['bond_addr'], SmartConnectResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['bond_addr'], SmartConnectResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['bond_addr'], SmartConnectResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['bond_addr'], SmartConnectResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_bond_addr(self, _, bond_addr, response):
        self.assertEqual(response.get_bond_addr(), bond_addr)

    @parameterized.expand([
        ['from_dpa', data_ok['dev_nr'], SmartConnectResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['dev_nr'], SmartConnectResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['dev_nr'], SmartConnectResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['dev_nr'], SmartConnectResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_dev_nr(self, _, dev_nr, response):
        self.assertEqual(response.get_dev_nr(), dev_nr)
