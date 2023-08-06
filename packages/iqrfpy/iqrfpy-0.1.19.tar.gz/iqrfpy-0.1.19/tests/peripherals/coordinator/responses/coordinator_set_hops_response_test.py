import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.set_hops import SetHopsResponse

data_ok: dict = {
    'msgid': 'setHopsTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 64,
    'request_hops': 255,
    'response_hops': 255,
    'dpa': b'\x00\x00\x00\x89\x00\x00\x00\x40\xff\xff'
}

data_ok_1: dict = {
    'msgid': 'setHopsTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'request_hops': 0,
    'response_hops': 239,
    'dpa': b'\x00\x00\x00\x89\x02\x04\x00\x23\x00\xef'
}

data_error: dict = {
    'msgid': 'setHopsTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x89\x04\x04\x01\x23'
}


class SetHopsResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        json = {
            'mType': 'iqrfEmbedCoordinator_SetHops',
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
                'requestHops': response_data['request_hops'],
                'responseHops': response_data['response_hops']
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, SetHopsResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, SetHopsResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, SetHopsResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, SetHopsResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, SetHopsResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, SetHopsResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.SET_HOPS)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.SET_HOPS)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            SetHopsResponse.from_dpa(b'\x00\x00\x00\x89\x00\x00\x00\x40')

    @parameterized.expand([
        ['from_dpa', data_ok['request_hops'], SetHopsResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['request_hops'], SetHopsResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['request_hops'], SetHopsResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['request_hops'], SetHopsResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_request_hops(self, _, request_hops, response):
        self.assertEqual(response.get_request_hops(), request_hops)

    @parameterized.expand([
        ['from_dpa', data_ok['response_hops'], SetHopsResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['response_hops'], SetHopsResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['response_hops'], SetHopsResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['response_hops'], SetHopsResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_response_hops(self, _, response_hops, response):
        self.assertEqual(response.get_response_hops(), response_hops)
