import unittest
from parameterized import parameterized
from iqrfpy.exceptions import RequestParameterInvalidValueError
from iqrfpy.peripherals.eeprom.requests.read import ReadRequest


class ReadRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x05\x00\x03\x00\xff\xff\x0a\x05'
        self.json = {
            'mType': 'iqrfEmbedEeprom_Read',
            'data': {
                'msgId': 'readTest',
                'req': {
                    'nAdr': 5,
                    'hwpId': 65535,
                    'param': {
                        'address': 10,
                        'len': 5
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        [5, 10, 5, b'\x05\x00\x03\x00\xff\xff\x0a\x05'],
        [0, 5, 22, b'\x00\x00\x03\x00\xff\xff\x05\x16'],
    ])
    def test_to_dpa(self, nadr: int, address: int, length: int, expected):
        request = ReadRequest(nadr=nadr, address=address, length=length)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        [5, 10, 5],
        [0, 5, 22],
    ])
    def test_to_json(self, nadr: int, address: int, length: int):
        request = ReadRequest(nadr=nadr, address=address, length=length, msgid='readTest')
        self.json['data']['req']['nAdr'] = nadr
        self.json['data']['req']['param']['address'] = address
        self.json['data']['req']['param']['len'] = length
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [2, b'\x05\x00\x03\x00\xff\xff\x02\x05'],
        [17, b'\x05\x00\x03\x00\xff\xff\x11\x05'],
    ])
    def test_set_address(self, address, dpa):
        request = ReadRequest(nadr=5, address=10, length=5, msgid='readTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_address(address=address),
        self.json['data']['req']['param']['address'] = address
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [20, b'\x05\x00\x03\x00\xff\xff\x0a\x14'],
        [13, b'\x05\x00\x03\x00\xff\xff\x0a\x0d'],
    ])
    def test_set_length(self, length, dpa):
        request = ReadRequest(nadr=5, address=10, length=5, msgid='readTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_length(length=length),
        self.json['data']['req']['param']['len'] = length
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
    def test_set_address_invalid(self, address):
        request = ReadRequest(nadr=5, address=10, length=5, msgid='readTest')
        with self.assertRaises(RequestParameterInvalidValueError):
            request.set_address(address=address)

    @parameterized.expand([
        [-1],
        [256],
        [1000]
    ])
    def test_set_length_invalid(self, length):
        request = ReadRequest(nadr=5, address=10, length=5, msgid='readTest')
        with self.assertRaises(RequestParameterInvalidValueError):
            request.set_length(length=length)

    @parameterized.expand([
        [-1, 1],
        [256, 10],
        [1000, 15],
        [10, -1],
        [10, 256]
    ])
    def test_construct_invalid(self, address, length):
        with self.assertRaises(RequestParameterInvalidValueError):
            ReadRequest(nadr=0, address=address, length=length)
