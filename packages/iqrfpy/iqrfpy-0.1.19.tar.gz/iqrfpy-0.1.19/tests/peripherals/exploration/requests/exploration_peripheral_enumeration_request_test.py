import unittest
from iqrfpy.peripherals.exploration.requests.peripheral_enumeration import PeripheralEnumerationRequest


class PeripheralEnumerationRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = PeripheralEnumerationRequest(nadr=1, msgid='peripheralEnumerationTest')
        self.dpa = b'\x01\x00\xff\x3f\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedExplore_Enumerate',
            'data': {
                'msgId': 'peripheralEnumerationTest',
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
