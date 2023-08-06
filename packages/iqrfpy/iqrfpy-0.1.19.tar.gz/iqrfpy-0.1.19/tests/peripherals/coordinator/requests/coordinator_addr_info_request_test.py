import unittest
from iqrfpy.peripherals.coordinator.requests.addr_info import AddrInfoRequest


class AddrInfoRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = AddrInfoRequest(msgid='addrInfoTest')
        self.dpa = b'\x00\x00\x00\x00\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_AddrInfo',
            'data': {
                'msgId': 'addrInfoTest',
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
