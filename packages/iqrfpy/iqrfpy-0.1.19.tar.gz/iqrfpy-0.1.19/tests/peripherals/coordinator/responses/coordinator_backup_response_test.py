import unittest
from parameterized import parameterized
from iqrfpy.enums.commands import CoordinatorResponseCommands
from iqrfpy.enums.message_types import CoordinatorMessages
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.coordinator.responses.backup import BackupResponse

data_ok: dict = {
    'msgid': 'backupTest',
    'nadr': 0,
    'hwpid': 0,
    'rcode': 0,
    'dpa_value': 90,
    'network_data': [104, 194, 100, 134, 122, 60, 24, 180, 62, 243, 129, 4, 150, 214, 237, 148, 39, 37, 89, 220, 245,
                     188, 20, 151, 251, 68, 134, 102, 163, 173, 4, 167, 252, 14, 229, 152, 137, 194, 182, 75, 35, 146,
                     93, 222, 170, 169, 163, 197, 168],
    'dpa': b'\x00\x00\x00\x8b\x00\x00\x00\x5a\x68\xc2\x64\x86\x7a\x3c\x18\xb4\x3e\xf3\x81\x04\x96\xd6\xed\x94\x27\x25'
           b'\x59\xdc\xf5\xbc\x14\x97\xfb\x44\x86\x66\xa3\xad\x04\xa7\xfc\x0e\xe5\x98\x89\xc2\xb6\x4b\x23\x92\x5d\xde'
           b'\xaa\xa9\xa3\xc5\xa8'
}

data_ok_1: dict = {
    'msgid': 'backupTest',
    'nadr': 0,
    'hwpid': 1026,
    'rcode': 0,
    'dpa_value': 35,
    'network_data': [76, 31, 9, 191, 70, 60, 78, 16, 207, 238, 130, 216, 94, 140, 209, 39, 180, 131, 226, 181, 23, 1,
                     21, 176, 209, 24, 61, 237, 237, 106, 169, 130, 135, 53, 161, 78, 237, 227, 223, 128, 48, 102, 204,
                     121, 147, 65, 191, 215, 98],
    'dpa': b'\x00\x00\x00\x8b\x02\x04\x00\x23\x4c\x1f\x09\xbf\x46\x3c\x4e\x10\xcf\xee\x82\xd8\x5e\x8c\xd1\x27\xb4\x83'
           b'\xe2\xb5\x17\x01\x15\xb0\xd1\x18\x3d\xed\xed\x6a\xa9\x82\x87\x35\xa1\x4e\xed\xe3\xdf\x80\x30\x66\xcc\x79'
           b'\x93\x41\xbf\xd7\x62'
}

data_error: dict = {
    'msgid': 'backupTest',
    'nadr': 0,
    'hwpid': 1028,
    'rcode': 1,
    'dpa_value': 35,
    'dpa': b'\x00\x00\x00\x8b\x04\x04\x01\x23'
}


class BackupResponseTestCase(unittest.TestCase):

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
                'networkData': response_data['network_data'],
            }
        return json

    @parameterized.expand([
        ['from_dpa', data_ok, BackupResponse.from_dpa(data_ok['dpa']), False],
        ['from_dpa', data_ok_1, BackupResponse.from_dpa(data_ok_1['dpa']), False],
        ['from_json', data_ok, BackupResponse.from_json(generate_json(data_ok)), True],
        ['from_json', data_ok_1, BackupResponse.from_json(generate_json(data_ok_1)), True],
        ['from_dpa_error', data_error, BackupResponse.from_dpa(data_error['dpa']), False],
        ['from_json_error', data_error, BackupResponse.from_json(generate_json(data_error)), True]
    ])
    def test_factory_methods_ok(self, _, response_data, response, json):
        with self.subTest():
            self.assertEqual(response.get_nadr(), response_data['nadr'])
        with self.subTest():
            self.assertEqual(response.get_pnum(), EmbedPeripherals.COORDINATOR)
        with self.subTest():
            self.assertEqual(response.get_pcmd(), CoordinatorResponseCommands.BACKUP)
        with self.subTest():
            self.assertEqual(response.get_hwpid(), response_data['hwpid'])
        with self.subTest():
            self.assertEqual(response.get_rcode(), response_data['rcode'])
        if json:
            with self.subTest():
                self.assertEqual(response.get_mtype(), CoordinatorMessages.BACKUP)
            with self.subTest():
                self.assertEqual(response.get_msgid(), response_data['msgid'])

    def test_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            BackupResponse.from_dpa(b'\x00\x00\x00\x89\x00\x00\x00\x40')

    @parameterized.expand([
        ['from_dpa', data_ok['network_data'], BackupResponse.from_dpa(data_ok['dpa'])],
        ['from_dpa', data_ok_1['network_data'], BackupResponse.from_dpa(data_ok_1['dpa'])],
        ['from_json', data_ok['network_data'], BackupResponse.from_json(generate_json(data_ok))],
        ['from_json', data_ok_1['network_data'], BackupResponse.from_json(generate_json(data_ok_1))]
    ])
    def test_get_network_data(self, _, network_data, response):
        self.assertEqual(response.get_network_data(), network_data)
