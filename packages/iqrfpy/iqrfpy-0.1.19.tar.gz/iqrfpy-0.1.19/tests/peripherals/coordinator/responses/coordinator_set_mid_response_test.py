import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.set_mid import SetMidResponse

data_ok: dict = {
    'msgid': 'setMidResponse',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 64,
    'dpa': b'\x00\x00\x00\x83\x00\x00\x00\x40'
}

data_ok_1: dict = {
    'msgid': 'setMidResponse',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x83\x02\x04\x00\x23'
}

data_error: dict = {
    'msgid': 'setMidResponse',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x83\x04\x04\x01\x23'
}


class SetMIDResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        return {
            'mType': 'iqrfEmbedCoordinator_SetMID',
            'data': {
                'msgId': response_data['msgid'],
                'rsp': {
                    'nAdr': response_data['nadr'],
                    'hwpId': response_data['hwpid'],
                    'rCode': response_data['rcode'],
                    'dpaVal': response_data['dpa_value'],
                    'result': {}
                },
                'insId': 'iqrfgd2-1',
                'status': response_data['rcode']
            }
        }

    @parameterized.expand([
        ['from_dpa', data_ok, SetMidResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, SetMidResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, SetMidResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, SetMidResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, SetMidResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, SetMidResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.SET_MID)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.SET_MID)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            SetMidResponse.from_dpa(b'\x00\x00\x00\x93\x00\x00\x00\x22\x01')
