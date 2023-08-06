import unittest
from iqrfpy.peripherals.ledr.requests.flashing import FlashingRequest


class SetOnRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = FlashingRequest(nadr=1, msgid='flashingTest')
        self.dpa = b'\x01\x00\x06\x04\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedLedr_Flashing',
            'data': {
                'msgId': 'flashingTest',
                'req': {
                    'nAdr': 1,
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
