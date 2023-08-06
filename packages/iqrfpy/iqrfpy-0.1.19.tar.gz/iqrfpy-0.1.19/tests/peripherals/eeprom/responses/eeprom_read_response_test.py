import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import EEPROMResponseCommands
from iqrfpy.enums.message_types import EEPROMMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.eeprom.responses import ReadResponse

data_ok: dict = {
    'msgid': 'readTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 90,
    'pData': [10, 20, 30, 40, 1, 12],
    'dpa': b'\x00\x00\x03\x80\x00\x00\x00\x5a\x0a\x14\x1e\x28\x01\x0c'
}

data_ok_1: dict = {
    'msgid': 'readTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'pData': [10, 20, 30, 40, 1, 12],
    'dpa': b'\x00\x00\x03\x80\x02\x04\x00\x5a\x0a\x14\x1e\x28\x01\x0c'
}

data_error: dict = {
    'msgid': 'readTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 4,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x03\x80\x04\x04\x04\x23'
}


class ReadResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        json = {
            'mType': 'iqrfEmbedCoordinator_Backup',
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
                'pData': response_data['pData'],
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, ReadResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, ReadResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, ReadResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, ReadResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, ReadResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, ReadResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.EEPROM)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), EEPROMResponseCommands.READ)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), EEPROMMessages.READ)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    @parameterized.expand([
        ['from_dpa', data_ok['pData'], ReadResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['pData'], ReadResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['pData'], ReadResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['pData'], ReadResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_network_data(self, _, data, response):
        self.assertEqual(response.get_data(), data)

