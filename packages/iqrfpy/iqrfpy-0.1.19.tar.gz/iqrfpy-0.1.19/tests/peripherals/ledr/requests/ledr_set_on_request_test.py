import unittest
from iqrfpy.peripherals.ledr.requests.set_on import SetOnRequest


class SetOnRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = SetOnRequest(nadr=3, msgid='setOnTest')
        self.dpa = b'\x03\x00\x06\x01\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedLedr_SetOn',
            'data': {
                'msgId': 'setOnTest',
                'req': {
                    'nAdr': 3,
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
