import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.remove_bond import RemoveBondRequest


class RemoveBondRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x00\x00\x00\x05\xff\xff\x01'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_RemoveBond',
            'data': {
                'msgId': 'removeBondTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'bondAddr': 1
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['bond_addr', 10, b'\x00\x00\x00\x05\xff\xff\x0a'],
        ['bond_addr', 170, b'\x00\x00\x00\x05\xff\xff\xaa'],
    ])
    def test_to_dpa(self, _, bond_addr, expected):
        request = RemoveBondRequest(bond_addr=bond_addr)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        ['bond_addr', 10],
        ['bond_addr', 170],
    ])
    def test_to_json(self, _, bond_addr):
        request = RemoveBondRequest(bond_addr=bond_addr, msgid='removeBondTest')
        self.json['data']['req']['param']['bondAddr'] = bond_addr
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [5, b'\x00\x00\x00\x05\xff\xff\x05'],
        [239, b'\x00\x00\x00\x05\xff\xff\xef']
    ])
    def test_set_index(self, bond_addr, dpa):
        request = RemoveBondRequest(bond_addr=1, msgid='removeBondTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_bond_addr(bond_addr)
        self.json['data']['req']['param']['bondAddr'] = bond_addr
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [-1],
        [256],
        [1000]
    ])
    def test_construct_invalid(self, bond_addr):
        with self.assertRaises(ValueError):
            RemoveBondRequest(bond_addr=bond_addr)
