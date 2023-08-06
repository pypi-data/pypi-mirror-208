import unittest
from iqrfpy.peripherals.coordinator.requests.clear_all_bonds import ClearAllBondsRequest


class ClearAllBondsRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = ClearAllBondsRequest(msgid='clearAllBondsTest')
        self.dpa = b'\x00\x00\x00\x03\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_ClearAllBonds',
            'data': {
                'msgId': 'clearAllBondsTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {},
                },
                'returnVerbose': True
            },
        }

    def test_to_dpa(self):
        self.assertEqual(
            self.request.to_dpa(),
            self.dpa
        )

    def test_to_json(self):
        self.assertEqual(
            self.request.to_json(),
            self.json
        )
