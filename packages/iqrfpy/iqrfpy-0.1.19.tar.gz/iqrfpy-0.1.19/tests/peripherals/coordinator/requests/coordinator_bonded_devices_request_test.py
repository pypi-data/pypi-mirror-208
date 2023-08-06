import unittest
from iqrfpy.peripherals.coordinator.requests.bonded_devices import BondedDevicesRequest


class BondedDevicesRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = BondedDevicesRequest(msgid='bondedDevicesTest')
        self.dpa = b'\x00\x00\x00\x02\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_BondedDevices',
            'data': {
                'msgId': 'bondedDevicesTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {}
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

