import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.discovery import DiscoveryRequest


class DiscoveryRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x00\x00\x00\x07\xff\xff\x06\x00'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_Discovery',
            'data': {
                'msgId': 'discoveryTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'txPower': 6,
                        'maxAddr': 0
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['tx_power', 0, 0, b'\x00\x00\x00\x07\xff\xff\x00\x00'],
        ['tx_power', 7, 0, b'\x00\x00\x00\x07\xff\xff\x07\x00'],
        ['max_addr', 7, 5, b'\x00\x00\x00\x07\xff\xff\x07\x05'],
        ['max_addr', 7, 239, b'\x00\x00\x00\x07\xff\xff\x07\xef']
    ])
    def test_to_dpa(self, _, tx_power, max_addr, expected):
        request = DiscoveryRequest(tx_power=tx_power, max_addr=max_addr)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        ['tx_power', 0, 0],
        ['tx_power', 7, 0],
        ['max_addr', 7, 5],
        ['max_addr', 7, 239]
    ])
    def test_to_json(self, _, tx_power, max_addr):
        request = DiscoveryRequest(tx_power=tx_power, max_addr=max_addr, msgid='discoveryTest')
        self.json['data']['req']['param']['txPower'] = tx_power
        self.json['data']['req']['param']['maxAddr'] = max_addr
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [5, b'\x00\x00\x00\x07\xff\xff\x05\x00'],
        [7, b'\x00\x00\x00\x07\xff\xff\x07\x00']
    ])
    def test_set_tx_power(self, tx_power, dpa):
        request = DiscoveryRequest(tx_power=6, max_addr=0, msgid='discoveryTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_tx_power(tx_power)
        self.json['data']['req']['param']['txPower'] = tx_power
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [0, b'\x00\x00\x00\x07\xff\xff\x06\x00'],
        [239, b'\x00\x00\x00\x07\xff\xff\x06\xef']
    ])
    def test_set_max_addr(self, max_addr, dpa):
        request = DiscoveryRequest(tx_power=6, max_addr=0, msgid='discoveryTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_max_addr(max_addr)
        self.json['data']['req']['param']['maxAddr'] = max_addr
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [-1, 0],
        [256, 0],
        [7, -10],
        [7, 520]
    ])
    def test_construct_invalid(self, tx_power, max_addr):
        with self.assertRaises(ValueError):
            DiscoveryRequest(tx_power=tx_power, max_addr=max_addr)
