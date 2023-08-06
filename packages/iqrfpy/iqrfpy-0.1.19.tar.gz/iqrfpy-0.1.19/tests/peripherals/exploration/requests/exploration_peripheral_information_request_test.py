import unittest
from iqrfpy.enums.peripherals import EmbedPeripherals
from iqrfpy.peripherals.exploration.requests.peripheral_information import PeripheralInformationRequest


class PeripheralInformationRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = PeripheralInformationRequest(nadr=3, per=EmbedPeripherals.OS, msgid='peripheralInformationTest')
        self.dpa = b'\x03\x00\x02\x3f\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedExplore_PeripheralInformation',
            'data': {
                'msgId': 'peripheralInformationTest',
                'req': {
                    'nAdr': 3,
                    'hwpId': 65535,
                    'param': {
                        'per': 2
                    }
                },
                'returnVerbose': True
            }
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
