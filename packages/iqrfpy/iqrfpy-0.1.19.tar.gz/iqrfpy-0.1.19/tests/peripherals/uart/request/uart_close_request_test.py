import unittest
from iqrfpy.peripherals.uart.requests.close import CloseRequest


class CloseRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = CloseRequest(nadr=1, msgid='closeTest')
        self.dpa = b'\x01\x00\x0c\x01\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedUart_Close',
            'data': {
                'msgId': 'closeTest',
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
