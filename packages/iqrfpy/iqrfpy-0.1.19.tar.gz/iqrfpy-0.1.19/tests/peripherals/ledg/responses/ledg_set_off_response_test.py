import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import LEDResponseCommands
from iqrfpy.enums.message_types import LEDGMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.ledg.responses.set_off import SetOffResponse
from iqrfpy.response_factory import ResponseFactory

data_ok: dict = {
    'msgid': 'setOffTest',
    'nadr': 1,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 64,
    'dpa': b'\x01\x00\x07\x80\x00\x00\x00\x40'
}

data_ok_1: dict = {
    'msgid': 'setOffTest',
    'nadr': 2,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'dpa': b'\x02\x00\x07\x80\x02\x04\x00\x23'
}

data_error: dict = {
    'msgid': 'setOffTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x07\x80\x02\x04\x01\x23'
}


class SetOffResponseTestCase(unittest.TestCase):

    @staticmethod
    def generate_json(response_data: dict):
        return {
            'mType': 'iqrfEmbedLedg_SetOff',
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
        ['from_dpa', data_ok, SetOffResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, SetOffResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, SetOffResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, SetOffResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, SetOffResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, SetOffResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.LEDG)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), LEDResponseCommands.SET_OFF)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), LEDGMessages.SET_OFF)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            ResponseFactory.get_response_from_dpa(b'\x00\x00\x07\x80\x00\x00\x00\x22\x32')
