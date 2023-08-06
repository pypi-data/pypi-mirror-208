import unittest
from iqrfpy.peripherals.os.requests.read import ReadRequest


class ReadRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = ReadRequest(nadr=3, msgid='osReadTest')
        self.dpa = b'\x03\x00\x02\x00\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedOs_Read',
            'data': {
                'msgId': 'osReadTest',
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
