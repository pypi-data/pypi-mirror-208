import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.backup import BackupRequest


class BackupRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x00\x00\x00\x0b\xff\xff\x00'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_Backup',
            'data': {
                'msgId': 'backupTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'index': 0
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['index', 10, b'\x00\x00\x00\x0b\xff\xff\x0a'],
        ['index', 170, b'\x00\x00\x00\x0b\xff\xff\xaa'],
    ])
    def test_to_dpa(self, _, index, expected):
        request = BackupRequest(index=index)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        ['index', 10],
        ['index', 170]
    ])
    def test_to_json(self, _, index):
        request = BackupRequest(index=index, msgid='backupTest')
        self.json['data']['req']['param']['index'] = index
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [10, b'\x00\x00\x00\x0b\xff\xff\x0a'],
        [170, b'\x00\x00\x00\x0b\xff\xff\xaa']
    ])
    def test_set_index(self, index, dpa):
        request = BackupRequest(index=0, msgid='backupTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_index(index)
        self.json['data']['req']['param']['index'] = index
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [-1],
        [256],
        [1000]
    ])
    def test_construct_invalid(self, index):
        with self.assertRaises(ValueError):
            BackupRequest(index=index)
