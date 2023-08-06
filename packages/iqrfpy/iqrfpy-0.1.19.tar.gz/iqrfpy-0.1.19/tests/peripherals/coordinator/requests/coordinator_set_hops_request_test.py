import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.set_hops import SetHopsRequest


class SetHopsRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x00\x00\x00\x09\xff\xff\xff\xff'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_SetHops',
            'data': {
                'msgId': 'setHopsTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'requestHops': 255,
                        'responseHops': 255
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['requestHops', 255, 255, b'\x00\x00\x00\x09\xff\xff\xff\xff'],
        ['requestHops', 34, 255, b'\x00\x00\x00\x09\xff\xff\x22\xff'],
        ['responseHops', 255, 10, b'\x00\x00\x00\x09\xff\xff\xff\x0a'],
        ['responseHops', 255, 239, b'\x00\x00\x00\x09\xff\xff\xff\xef']
    ])
    def test_to_dpa(self, _, request_hops, response_hops, expected):
        request = SetHopsRequest(request_hops=request_hops, response_hops=response_hops)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        ['requestHops', 255, 255],
        ['requestHops', 34, 255],
        ['responseHops', 255, 10],
        ['responseHops', 255, 239]
    ])
    def test_to_json(self, _, request_hops, response_hops):
        request = SetHopsRequest(request_hops=request_hops, response_hops=response_hops, msgid='setHopsTest')
        self.json['data']['req']['param']['requestHops'] = request_hops
        self.json['data']['req']['param']['responseHops'] = response_hops
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [1, b'\x00\x00\x00\x09\xff\xff\x01\xff'],
        [239, b'\x00\x00\x00\x09\xff\xff\xef\xff']
    ])
    def test_set_request_hops(self, request_hops, dpa):
        request = SetHopsRequest(request_hops=255, response_hops=255, msgid='setHopsTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_request_hops(request_hops)
        self.json['data']['req']['param']['requestHops'] = request_hops
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [10, b'\x00\x00\x00\x09\xff\xff\xff\x0a'],
        [239, b'\x00\x00\x00\x09\xff\xff\xff\xef']
    ])
    def test_set_response_hops(self, response_hops, dpa):
        request = SetHopsRequest(request_hops=255, response_hops=255, msgid='setHopsTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_response_hops(response_hops)
        self.json['data']['req']['param']['responseHops'] = response_hops
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [-1, 255],
        [256, 5],
        [0, -1],
        [239, 1000]
    ])
    def test_construct_invalid(self, request_hops, response_hops):
        with self.assertRaises(ValueError):
            SetHopsRequest(request_hops=request_hops, response_hops=response_hops)
