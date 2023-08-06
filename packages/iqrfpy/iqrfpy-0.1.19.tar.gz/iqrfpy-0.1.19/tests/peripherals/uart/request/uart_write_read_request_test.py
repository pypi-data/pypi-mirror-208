import random
import unittest
from typing import List
from parameterized import parameterized
from iqrfpy.exceptions import RequestParameterInvalidValueError
from iqrfpy.peripherals.uart.requests.write_read import WriteReadRequest


class WriteReadRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x03\x00\x0c\x02\xff\xff\x01\x01\x02\x03\x04\x05'
        self.json = {
            'mType': 'iqrfEmbedUart_WriteRead',
            'data': {
                'msgId': 'writeReadTest',
                'req': {
                    'nAdr': 3,
                    'hwpId': 65535,
                    'param': {
                        'readTimeout': 1,
                        'writtenData': [1, 2, 3, 4, 5]
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        [random.randint(0, 255), random.sample(range(0, 255), 10)]
    ])
    def test_to_dpa(self, read_timeout: int, data: List[int]):
        expected = self.dpa[0:6] + bytes([read_timeout]) + bytes(data)
        request = WriteReadRequest(nadr=3, read_timeout=read_timeout, data=data)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        [random.randint(0, 255), random.sample(range(0, 255), 10)],
    ])
    def test_to_json(self, read_timeout: int, data: List[int]):
        request = WriteReadRequest(nadr=3, read_timeout=read_timeout, data=data, msgid='writeReadTest')
        self.json['data']['req']['param'] = {
            'readTimeout': read_timeout,
            'writtenData': data,
        }
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        ['read_timeout', 10],
        ['read_timeout', 20],
        ['read_timeout', 7],
    ])
    def test_set_read_timeout(self, _, read_timeout: int):
        request = WriteReadRequest(nadr=3, read_timeout=1, data=[1, 2, 3, 4, 5], msgid='writeReadTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        dpa = self.dpa[0:6] + bytes([read_timeout]) + self.dpa[7:]
        self.json['data']['req']['param']['readTimeout'] = read_timeout
        request.set_read_timeout(read_timeout=read_timeout)
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        ['written_data', random.sample(range(0, 255), 10)],
    ])
    def test_set_write_data(self, _, data: List[int]):
        request = WriteReadRequest(nadr=3, read_timeout=1, data=[1, 2, 3, 4, 5], msgid='writeReadTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        dpa = self.dpa[0:7] + bytes(data)
        self.json['data']['req']['param']['writtenData'] = data
        request.set_write_data(data=data)
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        ['negative_read_timeout', -1, [1]],
        ['read_timeout_word', 256, [1]],
        ['read_timeout_invalid', 1000, [1]],
        ['data_invalid', 1, [-1]],
        ['data_too_large', 1, random.sample(range(0, 255), 70)],
    ])
    def test_construct_invalid(self, _, read_timeout: int, data: List[int]):
        with self.assertRaises(RequestParameterInvalidValueError):
            WriteReadRequest(nadr=3, read_timeout=read_timeout, data=data)
