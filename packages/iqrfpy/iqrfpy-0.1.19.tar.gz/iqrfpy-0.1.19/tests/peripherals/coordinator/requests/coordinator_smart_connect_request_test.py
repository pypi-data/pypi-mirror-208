import random
import unittest
from dataclasses import dataclass
from typing import Union
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.smart_connect import SmartConnectRequest


@dataclass
class DataRegular:
    req_addr = 10
    bonding_test_retries = 3
    ibk = [32, 28, 94, 118, 47, 117, 215, 226, 68, 195, 250, 9, 179, 222, 14, 161]
    mid = 2165321045
    virtual_device_address = 255
    expected_dpa = b''.join([
        b'\x00\x00\x00\x12\xff\xff\x0a\x03\x20\x1c\x5e\x76\x2f\x75\xd7\xe2\x44\xc3\xfa\x09\xb3\xde\x0e\xa1\x55'
        b'\x2d\x10\x81\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    ])


class DataTempAddr:
    req_addr = 254
    bonding_test_retries = 0
    ibk = [111, 249, 157, 155, 80, 108, 206, 40, 171, 71, 174, 231, 200, 33, 83, 146]
    mid = 0
    virtual_device_address = 0
    expected_dpa = b''.join([
        b'\x00\x00\x00\x12\xff\xff\xfe\x00\x6f\xf9\x9d\x9b\x50\x6c\xce\x28\xab\x47\xae\xe7\xc8\x21\x53\x92\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    ])


class SmartConnectRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b''.join([
            b'\x00\x00\x00\x12\xff\xff\x0b\x01\x9a\x69\x1f\x1a\x21\x01\x21\x65\x03\xe5\xc5\x88\xff\xe7\xf6\xc2\x55',
            b'\x2d\x10\x81\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        ])
        self.json = {
            'mType': 'iqrfEmbedCoordinator_SmartConnect',
            'data': {
                'msgId': 'smartConnectTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'reqAddr': 11,
                        'bondingTestRetries': 1,
                        'ibk': [
                            154,
                            105,
                            31,
                            26,
                            33,
                            1,
                            33,
                            101,
                            3,
                            229,
                            197,
                            136,
                            255,
                            231,
                            246,
                            194
                        ],
                        'mid': 2165321045,
                        'virtualDeviceAddress': 255,
                        'userData': [
                            0,
                            0,
                            0,
                            0
                        ]
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['regular', DataRegular],
        ['temporary_addr', DataTempAddr]
    ])
    def test_to_dpa(self, _, data: Union[DataRegular, DataTempAddr]):
        request = SmartConnectRequest(
            req_addr=data.req_addr,
            bonding_test_retries=data.bonding_test_retries,
            ibk=data.ibk,
            mid=data.mid,
            virtual_device_address=data.virtual_device_address
        )
        print(request.to_dpa())
        print(data.expected_dpa)
        self.assertEqual(
            request.to_dpa(),
            data.expected_dpa
        )

    @parameterized.expand([
        ['regular', DataRegular],
        ['temporary_addr', DataTempAddr]
    ])
    def test_to_json(self, _, data: Union[DataRegular, DataTempAddr]):
        request = SmartConnectRequest(
            req_addr=data.req_addr,
            bonding_test_retries=data.bonding_test_retries,
            ibk=data.ibk,
            mid=data.mid,
            virtual_device_address=data.virtual_device_address,
            msgid='smartConnectTest'
        )
        self.json['data']['req']['param']['reqAddr'] = data.req_addr
        self.json['data']['req']['param']['bondingTestRetries'] = data.bonding_test_retries
        self.json['data']['req']['param']['ibk'] = data.ibk
        self.json['data']['req']['param']['mid'] = data.mid
        self.json['data']['req']['param']['virtualDeviceAddress'] = data.virtual_device_address
        print(request.to_json())
        print(self.json)
        self.assertEqual(
            request.to_json(),
            self.json
        )

    def test_set_req_addr(self):
        request = SmartConnectRequest(
            req_addr=self.json['data']['req']['param']['reqAddr'],
            bonding_test_retries=self.json['data']['req']['param']['bondingTestRetries'],
            ibk=self.json['data']['req']['param']['ibk'],
            mid=self.json['data']['req']['param']['mid'],
            virtual_device_address=self.json['data']['req']['param']['virtualDeviceAddress'],
            msgid='smartConnectTest'
        )
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        request.set_req_addr(DataRegular.req_addr)
        self.json['data']['req']['param']['reqAddr'] = DataRegular.req_addr
        dpa = list(self.dpa)
        dpa[6] = DataRegular.req_addr
        dpa = bytes(dpa)
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    def test_set_bonding_test_retries(self):
        request = SmartConnectRequest(
            req_addr=self.json['data']['req']['param']['reqAddr'],
            bonding_test_retries=self.json['data']['req']['param']['bondingTestRetries'],
            ibk=self.json['data']['req']['param']['ibk'],
            mid=self.json['data']['req']['param']['mid'],
            virtual_device_address=self.json['data']['req']['param']['virtualDeviceAddress'],
            msgid='smartConnectTest'
        )
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        request.set_bonding_test_retries(DataRegular.bonding_test_retries)
        self.json['data']['req']['param']['bondingTestRetries'] = DataRegular.bonding_test_retries
        dpa = list(self.dpa)
        dpa[7] = DataRegular.bonding_test_retries
        dpa = bytes(dpa)
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    def test_set_ibk(self):
        request = SmartConnectRequest(
            req_addr=self.json['data']['req']['param']['reqAddr'],
            bonding_test_retries=self.json['data']['req']['param']['bondingTestRetries'],
            ibk=self.json['data']['req']['param']['ibk'],
            mid=self.json['data']['req']['param']['mid'],
            virtual_device_address=self.json['data']['req']['param']['virtualDeviceAddress'],
            msgid='smartConnectTest'
        )
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        request.set_ibk(DataRegular.ibk)
        self.json['data']['req']['param']['ibk'] = DataRegular.ibk
        dpa = list(self.dpa)
        dpa = dpa[:8] + DataRegular.ibk + dpa[24:]
        dpa = bytes(dpa)
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    def test_set_mid(self):
        request = SmartConnectRequest(
            req_addr=self.json['data']['req']['param']['reqAddr'],
            bonding_test_retries=self.json['data']['req']['param']['bondingTestRetries'],
            ibk=self.json['data']['req']['param']['ibk'],
            mid=self.json['data']['req']['param']['mid'],
            virtual_device_address=self.json['data']['req']['param']['virtualDeviceAddress'],
            msgid='smartConnectTest'
        )
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        request.set_mid(DataRegular.mid)
        self.json['data']['req']['param']['mid'] = DataRegular.mid
        dpa_mid = [
            DataRegular.mid & 0xFF,
            (DataRegular.mid >> 8) & 0xFF,
            (DataRegular.mid >> 16) & 0xFF,
            (DataRegular.mid >> 24) & 0xFF
        ]
        dpa = list(self.dpa)
        dpa = dpa[:24] + dpa_mid + dpa[28:]
        dpa = bytes(dpa)
        print(request.to_dpa())
        print(dpa)
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    def test_set_virtual_device_address(self):
        request = SmartConnectRequest(
            req_addr=self.json['data']['req']['param']['reqAddr'],
            bonding_test_retries=self.json['data']['req']['param']['bondingTestRetries'],
            ibk=self.json['data']['req']['param']['ibk'],
            mid=self.json['data']['req']['param']['mid'],
            virtual_device_address=self.json['data']['req']['param']['virtualDeviceAddress'],
            msgid='smartConnectTest'
        )
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        request.set_virtual_device_address(DataRegular.virtual_device_address)
        self.json['data']['req']['param']['virtualDeviceAddress'] = DataRegular.virtual_device_address
        dpa = list(self.dpa)
        dpa[29] = DataRegular.virtual_device_address
        dpa = bytes(dpa)
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        ['req_addr', -1, 0, [random.randint(0, 255)] * 16, 0, 0],
        ['req_addr', 275, 0, [random.randint(0, 255)] * 16, 0, 0],
        ['bonding_test_retries', 1, -1, [random.randint(0, 255)] * 16, 0, 0],
        ['bonding_test_retries', 1, 270, [random.randint(0, 255)] * 16, 0, 0],
        ['ibk', 1, 1, [10], 0, 0],
        ['ibk', 1, 1, [random.randint(0, 255)] * 17, 0, 0],
        ['ibk', 1, 1, [0, 0, 0, 0, 0, 0, 0, 0, 256, 0, 0, 0, 0, 0, 0, 0], 0, 0],
        ['mid', 1, 1, [random.randint(0, 255)] * 16, -1, 0],
        ['mid', 1, 1, [random.randint(0, 255)] * 16, 4294967298, 0],
        ['virtual_device_address', 1, 1, [random.randint(0, 255)] * 16, 0, -1],
        ['virtual_device_address', 1, 1, [random.randint(0, 255)] * 16, 0, 256],
    ])
    def test_construct_invalid(self, _, req_addr, bonding_test_retries, ibk, mid, virtual_device_address):
        with self.assertRaises(ValueError):
            SmartConnectRequest(
                req_addr=req_addr,
                bonding_test_retries=bonding_test_retries,
                ibk=ibk,
                mid=mid,
                virtual_device_address=virtual_device_address
            )
