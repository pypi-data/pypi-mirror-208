import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.discovery import DiscoveryResponse

data_ok: dict = {
    'msgid': 'discoveryTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 55,
    'disc_nr': 15,
    'dpa': b'\x00\x00\x00\x87\x00\x00\x00\x37\x0f'

}

data_ok_1: dict = {
    'msgid': 'discoveryTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'disc_nr': 3,
    'dpa': b'\x00\x00\x00\x87\x02\x04\x00\x23\x03'
}

data_error: dict = {
    'msgid': 'discoveryTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 7,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x87\x04\x04\x07\x23'
}


class DiscoveryResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        json = {
            'mType': 'iqrfEmbedCoordinator_Discovery',
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
                'discNr': response_data['disc_nr']
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, DiscoveryResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, DiscoveryResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, DiscoveryResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, DiscoveryResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, DiscoveryResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, DiscoveryResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.DISCOVERY)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.DISCOVERY)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            DiscoveryResponse.from_dpa(b'\x00\x00\x00\x87\x00\x00\x00\x22')

    @parameterized.expand([
        ['from_dpa', data_ok['disc_nr'], DiscoveryResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['disc_nr'], DiscoveryResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['disc_nr'], DiscoveryResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['disc_nr'], DiscoveryResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_disc_nr(self, _, disc_nr, response):
        self.assertEqual(response.get_disc_nr(), disc_nr)
