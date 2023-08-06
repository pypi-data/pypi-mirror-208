import unittest
from parameterized import parameterized
from iqrfpy.peripherals.coordinator.requests.set_dpa_params import SetDpaParamsRequest, DpaParam


class SetDpaParamsRequestTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dpa = b'\x00\x00\x00\x08\xff\xff\x00'
        self.json = {
            'mType': 'iqrfEmbedCoordinator_SetDpaParams',
            'data': {
                'msgId': 'setDpaParamsTest',
                'req': {
                    'nAdr': 0,
                    'hwpId': 65535,
                    'param': {
                        'dpaParam': 0
                    }
                },
                'returnVerbose': True
            }
        }

    @parameterized.expand([
        ['dpa_param', DpaParam.LAST_RSSI, b'\x00\x00\x00\x08\xff\xff\x00'],
        ['dpa_param', DpaParam.USER_SPECIFIED, b'\x00\x00\x00\x08\xff\xff\x03'],
    ])
    def test_to_dpa(self, _, dpa_param, expected):
        request = SetDpaParamsRequest(dpa_param=dpa_param)
        self.assertEqual(
            request.to_dpa(),
            expected
        )

    @parameterized.expand([
        ['dpa_param', DpaParam.LAST_RSSI],
        ['dpa_param', DpaParam.USER_SPECIFIED],
    ])
    def test_to_json(self, _, dpa_param):
        request = SetDpaParamsRequest(dpa_param=dpa_param, msgid='setDpaParamsTest')
        self.json['data']['req']['param']['dpaParam'] = dpa_param
        self.assertEqual(
            request.to_json(),
            self.json
        )

    @parameterized.expand([
        [DpaParam.VOLTAGE, b'\x00\x00\x00\x08\xff\xff\x01'],
        [DpaParam.USER_SPECIFIED, b'\x00\x00\x00\x08\xff\xff\x03']
    ])
    def test_set_dpa_param(self, dpa_param, dpa):
        request = SetDpaParamsRequest(dpa_param=DpaParam.LAST_RSSI, msgid='setDpaParamsTest')
        self.assertEqual(
            request.to_dpa(),
            self.dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
        request.set_dpa_param(dpa_param)
        self.json['data']['req']['param']['dpaParam'] = dpa_param
        self.assertEqual(
            request.to_dpa(),
            dpa
        )
        self.assertEqual(
            request.to_json(),
            self.json
        )
