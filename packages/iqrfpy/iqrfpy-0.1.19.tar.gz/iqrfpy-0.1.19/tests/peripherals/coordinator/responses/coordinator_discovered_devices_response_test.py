import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.discovered_devices import DiscoveredDevicesResponse

data_ok: dict = {
    'msgid': 'discoveredDevicesTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 71,
    'discovered_devices': [1, 2, 3],
    'dpa': b'\x00\x00\x00\x81\x00\x00\x00\x47\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
           b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
}

data_ok_1: dict = {
    'msgid': 'discoveredDevicesTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'discovered_devices': [7, 9],
    'dpa': b'\x00\x00\x00\x81\x02\x04\x00\x23\x80\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
           b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
}

data_error: dict = {
    'msgid': 'discoveredDevicesTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 7,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x81\x04\x04\x07\x23'
}


class DiscoveredDevicesResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        json = {
            'mType': 'iqrfEmbedCoordinator_DiscoveredDevices',
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
                'discoveredDevices': response_data['discovered_devices']
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, DiscoveredDevicesResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, DiscoveredDevicesResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, DiscoveredDevicesResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, DiscoveredDevicesResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, DiscoveredDevicesResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, DiscoveredDevicesResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.DISCOVERED_DEVICES)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.DISCOVERED_DEVICES)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            DiscoveredDevicesResponse.from_dpa(b'\x00\x00\x00\x81\x00\x00\x00\x22\x01\x00')

    @parameterized.expand([
        ['from_dpa', data_ok['discovered_devices'], DiscoveredDevicesResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['discovered_devices'], DiscoveredDevicesResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['discovered_devices'], DiscoveredDevicesResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['discovered_devices'], DiscoveredDevicesResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_discovered(self, _, discovered, response):
        self.assertEqual(response.get_discovered(), discovered)
