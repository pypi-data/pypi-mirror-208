import unittest
from iqrfpy.enums.commands import ExplorationRequestPeripheralCommand
from iqrfpy.peripherals.exploration.requests.more_peripherals_information import MorePeripheralsInformationRequest


class MorePeripheralsInformationRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = MorePeripheralsInformationRequest(
            nadr=3,
            per=ExplorationRequestPeripheralCommand.PER_COORDINATOR,
            msgid='morePeripheralInformationTest'
        )
        self.dpa = b'\x03\x00\xff\x00\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedExplore_MorePeripheralsInformation',
            'data': {
                'msgId': 'morePeripheralInformationTest',
                'req': {
                    'nAdr': 3,
                    'hwpId': 65535,
                    'param': {
                        'per': 0
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
