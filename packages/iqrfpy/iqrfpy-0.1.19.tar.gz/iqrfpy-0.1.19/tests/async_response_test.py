import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import ExplorationRequestCommands
from iqrfpy.enums.message_types import GenericMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.async_response import AsyncResponse

data_ok: dict = {
    'msgid': 'async',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 128,
    'dpa_value': 0,
    'dpa': b'\x00\x00\xff\x3f\x00\x00\x80\x00\x17\x04\x00\xfd\x26\x00\x00\x00\x00\x00\x00\x05',
    'json': {
        'mType': 'iqrfRaw',
        'data': {
            'msgId': 'async',
            'rsp': {
                'rData': '00.00.ff.3f.00.00.80.00.17.04.00.fd.26.00.00.00.00.00.00.05'
            },
            'status': 0,
            'insId': 'iqrfgd2-default'
        }
    }
}


class AsyncResponseTestCase(unittest.TestCase):

    @parameterized.expand([
        ['from_dpa', data_ok, AsyncResponse.from_dpa(data_ok['dpa']), False],
        ['from_json', data_ok, AsyncResponse.from_json(data_ok['json']), True],
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.EXPLORATION)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), ExplorationRequestCommands.PERIPHERALS_ENUMERATION_INFORMATION)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        with self.subTest():
            self.assertEqual(response.get_pdata(), response_data['dpa'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), GenericMessages.RAW)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            AsyncResponse.from_dpa(b'\x00\x00\x00\x80\x00\x00\x00')
