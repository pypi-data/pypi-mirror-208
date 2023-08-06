import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.remove_bond import RemoveBondResponse

data_ok: dict = {
    'msgid': 'removeBondTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 55,
    'dev_nr': 10,
    'dpa': b'\x00\x00\x00\x85\x00\x00\x00\x37\x0a'

}

data_ok_1: dict = {
    'msgid': 'removeBondTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'dev_nr': 1,
    'dpa': b'\x00\x00\x00\x85\x02\x04\x00\x23\x01'
}

data_error: dict = {
    'msgid': 'removeBondTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 7,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x87\x04\x04\x07\x23'
}


class RemoveBondResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        json = {
            'mType': 'iqrfEmbedCoordinator_RemoveBond',
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
                'devNr': response_data['dev_nr']
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, RemoveBondResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, RemoveBondResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, RemoveBondResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, RemoveBondResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, RemoveBondResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, RemoveBondResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.REMOVE_BOND)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.REMOVE_BOND)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            RemoveBondResponse.from_dpa(b'\x00\x00\x00\x85\x00\x00\x00\x22')

    @parameterized.expand([
        ['from_dpa', data_ok['dev_nr'], RemoveBondResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['dev_nr'], RemoveBondResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['dev_nr'], RemoveBondResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['dev_nr'], RemoveBondResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_dev_nr(self, _, dev_nr, response):
        self.assertEqual(response.get_dev_nr(), dev_nr)
