import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.bond_node import BondNodeRequest


class BondNodeRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x00\x00\x00\x04\xff\xff\x01\x00'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_BondNode',
            'data': {
                'msgId': 'bondNodeTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'reqAddr': 1,
                        'bondingMask': 0
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['req_addr', 1, 1, b'\x00\x00\x00\x04\xff\xff\x01\x01'],
        ['req_addr', 239, 1, b'\x00\x00\x00\x04\xff\xff\xef\x01'],
        ['bonding_test_retries', 1, 10, b'\x00\x00\x00\x04\xff\xff\x01\x0a'],
        ['bonding_test_retries', 1, 5, b'\x00\x00\x00\x04\xff\xff\x01\x05']
    ])
    def test_to_dpa(self, _, req_addr, bonding_test_retries, expected):
        request = BondNodeRequest(req_addr=req_addr, bonding_test_retries=bonding_test_retries)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        ['req_addr', 1, 1],
        ['req_addr', 239, 1],
        ['bonding_test_retries', 1, 10],
        ['bonding_test_retries', 1, 5],
        ['iquip', 240, 0]
    ])
    def test_to_json(self, _, req_addr: int, bonding_test_retries: int):
        request = BondNodeRequest(req_addr=req_addr, bonding_test_retries=bonding_test_retries, msgid='bondNodeTest')
        self.json['data']['req']['param']['reqAddr'] = req_addr
        self.json['data']['req']['param']['bondingMask'] = bonding_test_retries
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [239, b'\x00\x00\x00\x04\xff\xff\xef\x00'],
        [10, b'\x00\x00\x00\x04\xff\xff\x0a\x00']
    ])
    def test_set_req_addr(self, req_addr, dpa):
        request = BondNodeRequest(req_addr=1, bonding_test_retries=0, msgid='bondNodeTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_req_addr(req_addr)
        self.json['data']['req']['param']['reqAddr'] = req_addr
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [1, b'\x00\x00\x00\x04\xff\xff\x01\x01'],
        [5, b'\x00\x00\x00\x04\xff\xff\x01\x05']
    ])
    def test_set_bonding_test_retries(self, bonding_test_retries, dpa):
        request = BondNodeRequest(req_addr=1, bonding_test_retries=0, msgid='bondNodeTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_bonding_test_retries(bonding_test_retries)
        self.json['data']['req']['param']['bondingMask'] = bonding_test_retries
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [-1, 1],
        [256, 1],
        [1000, 0],
        [1, -1],
        [1, 420]
    ])
    def test_construct_invalid(self, req_addr, bonding_test_retries):
        with self.assertRaises(ValueError):
            BondNodeRequest(req_addr=req_addr, bonding_test_retries=bonding_test_retries)
