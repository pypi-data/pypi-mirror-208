import unittest
from iqrfpy.peripherals.ledg.requests.set_off import SetOffRequest


class SetOnRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = SetOffRequest(nadr=5, msgid='setOffTest')
        self.dpa = b'\x05\x00\x07\x00\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedLedg_SetOff',
            'data': {
                'msgId': 'setOffTest',
                'req': {
                    'nAdr': 5,
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
