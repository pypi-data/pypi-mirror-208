import random
import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.restore import RestoreRequest


class RestoreRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b''.join(
            [b'\x00\x00\x00\x0c\xff\xff\xed\x60\x14\x51\x82\xde\x7c\x72\xde\xf8\x90\xa3\xee\x82\x75\xed\x90\x54',
             b'\xa7\xb7\x81\x33\xca\x65\x70\x07\x7b\x24\x03\x43\x08\x1e\x82\x62\xce\x0b\x10\x2b\x23\x43\xa3\x58',
             b'\xd6\xa6\x8c\x91\x11\x68\xa8']
        )
        self.json = {
            'mType': 'iqrfEmbedCoordinator_Restore',
            'data': {
                'msgId': 'restoreTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'networkData': [
                            237,
                            96,
                            20,
                            81,
                            130,
                            222,
                            124,
                            114,
                            222,
                            248,
                            144,
                            163,
                            238,
                            130,
                            117,
                            237,
                            144,
                            84,
                            167,
                            183,
                            129,
                            51,
                            202,
                            101,
                            112,
                            7,
                            123,
                            36,
                            3,
                            67,
                            8,
                            30,
                            130,
                            98,
                            206,
                            11,
                            16,
                            43,
                            35,
                            67,
                            163,
                            88,
                            214,
                            166,
                            140,
                            145,
                            17,
                            104,
                            168
                        ]
                    }
                },
                'returnVerbose': True
            }
        }

    def test_to_dpa(self):
        network_data = random.sample(range(0, 255), 49)
        expected = bytes(b'\x00\x00\x00\x0c\xff\xff' + bytes(network_data))
        request = RestoreRequest(network_data=network_data)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    def test_to_json(self):
        network_data = random.sample(range(0, 255), 49)
        request = RestoreRequest(network_data=network_data, msgid='restoreTest')
        self.json['data']['req']['param']['networkData'] = network_data
        self.assertEqual(
            request.to_json(),
            self.json
        )

    def test_set_network_data(self):
        request = RestoreRequest(network_data=self.json['data']['req']['param']['networkData'], msgid='restoreTest')
        print(request.to_dpa())
        print(self.dpa)
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        network_data = random.sample(range(0, 255), 49)
        dpa = bytes(b'\x00\x00\x00\x0c\xff\xff' + bytes(network_data))
        request.set_network_data(network_data)
        self.json['data']['req']['param']['networkData'] = network_data
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [[0] * 60],
        [[-255]],
        [[256]]
    ])
    def test_construct_invalid(self, network_data):
        with self.assertRaises(ValueError):
            RestoreRequest(network_data=network_data)
