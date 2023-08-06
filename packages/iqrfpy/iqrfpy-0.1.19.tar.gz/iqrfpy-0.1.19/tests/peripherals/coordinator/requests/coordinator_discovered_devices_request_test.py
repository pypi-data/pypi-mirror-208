import unittest
from iqrfpy.peripherals.coordinator.requests.discovered_devices import DiscoveredDevicesRequest


class DiscoveredDevicesTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.request = DiscoveredDevicesRequest(msgid='discoveredDevicesTest')
        self.dpa = b'\x00\x00\x00\x01\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_DiscoveredDevices',
            'data': {
                'msgId': 'discoveredDevicesTest',
                'req': {
                    'nAdr': 0,
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
