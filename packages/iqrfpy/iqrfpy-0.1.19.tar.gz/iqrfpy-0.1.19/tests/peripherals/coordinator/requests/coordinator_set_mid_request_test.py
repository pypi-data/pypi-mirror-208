import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.set_mid import SetMidRequest


class SetMidRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x00\x00\x00\x13\xff\xff\x00\x00\x00\x00\x0a'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_SetMID',
            'data': {
                'msgId': 'setMIDTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'bondAddr': 10,
                        'mid': 0
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['bond_addr', 5, 0, b'\x00\x00\x00\x13\xff\xff\x00\x00\x00\x00\x05'],
        ['bond_addr', 239, 0, b'\x00\x00\x00\x13\xff\xff\x00\x00\x00\x00\xef'],
        ['mid', 10, 2164554855, b'\x00\x00\x00\x13\xff\xff\x67\x7c\x04\x81\x0a'],
        ['mid', 10, 2164554771, b'\x00\x00\x00\x13\xff\xff\x13\x7c\x04\x81\x0a']
    ])
    def test_to_dpa(self, _, bond_addr, mid, expected):
        request = SetMidRequest(bond_addr=bond_addr, mid=mid)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        ['bond_addr', 5, 0],
        ['bond_addr', 239, 0],
        ['mid', 10, 2164554855],
        ['mid', 10, 2164554771]
    ])
    def test_to_json(self, _, bond_addr, mid):
        request = SetMidRequest(bond_addr=bond_addr, mid=mid, msgid='setMIDTest')
        self.json['data']['req']['param']['bondAddr'] = bond_addr
        self.json['data']['req']['param']['mid'] = mid
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [5, b'\x00\x00\x00\x13\xff\xff\x00\x00\x00\x00\x05'],
        [239, b'\x00\x00\x00\x13\xff\xff\x00\x00\x00\x00\xef']
    ])
    def test_set_bond_addr(self, bond_addr, dpa):
        request = SetMidRequest(bond_addr=10, mid=0, msgid='setMIDTest')
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
        [2164554855, b'\x00\x00\x00\x13\xff\xff\x67\x7c\x04\x81\x0a'],
        [2164554771, b'\x00\x00\x00\x13\xff\xff\x13\x7c\x04\x81\x0a']
    ])
    def test_set_mid(self, mid, dpa):
        request = SetMidRequest(bond_addr=10, mid=0, msgid='setMIDTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_mid(mid)
        self.json['data']['req']['param']['mid'] = mid
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [-1, 2164554855],
        [257, 2164554855],
        [5, -1],
        [10, 4294967297]
    ])
    def test_construct_invalid(self, bond_addr, mid):
        with self.assertRaises(ValueError):
            SetMidRequest(bond_addr=bond_addr, mid=mid)
