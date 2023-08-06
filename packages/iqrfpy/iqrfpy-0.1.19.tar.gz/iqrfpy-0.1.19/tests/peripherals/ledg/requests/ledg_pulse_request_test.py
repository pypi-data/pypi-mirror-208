import unittest
from iqrfpy.peripherals.ledg.requests.pulse import PulseRequest


class SetOnRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = PulseRequest(nadr=1, msgid='pulseTest')
        self.dpa = b'\x01\x00\x07\x03\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedLedg_Pulse',
            'data': {
                'msgId': 'pulseTest',
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
