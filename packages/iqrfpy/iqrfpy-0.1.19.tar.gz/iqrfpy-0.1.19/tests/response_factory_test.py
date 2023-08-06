import unittest
from parameterized import parameterized
from iqrfpy.enums.message_types import *
from iqrfpy.exceptions import JsonMsgidMissingError, JsonMTypeMissingError, UnsupportedMessageTypeError
from iqrfpy.response_factory import *
from iqrfpy.async_response import AsyncResponse
from iqrfpy.confirmation import Confirmation
from iqrfpy.peripherals.coordinator.responses import *


class ResponseFactoryTestCase(unittest.TestCase):

    @parameterized.expand([
        [CoordinatorMessages.ADDR_INFO, CoordinatorAddrInfoFactory],
        [CoordinatorMessages.BACKUP, CoordinatorBackupFactory],
        [CoordinatorMessages.BOND_NODE, CoordinatorBondNodeFactory],
        [CoordinatorMessages.RESTORE, CoordinatorRestoreFactory],
        [CoordinatorMessages.SET_MID, CoordinatorSetMIDFactory],
    ])
    def test_get_factory_from_mtype_ok(self, mtype, expected):
        self.assertIsInstance(_get_factory_from_mtype(mtype), expected)

    @parameterized.expand([
        [OSMessages.FACTORY_SETTINGS],
        [NodeMessages.REMOVE_BOND],
    ])
    def test_get_factory_from_mtype_unsupported(self, mtype):
        with self.assertRaises(ValueError):
            _get_factory_from_mtype(mtype)

    @parameterized.expand([
        ['Async', b'\x00\x00\xff\x3f\x00\x00\x80\x00\x17\x04\x00\xfd\x26\x00\x00\x00\x00\x00\x00\x05', AsyncResponse],
        ['Confirmation', b'\x01\x00\x01\x00\xff\xff\xff\x36\x01\x04\x01', Confirmation],
        ['AddrInfo', b'\x00\x00\x00\x80\x00\x00\x00\x40\x0a\x2a', AddrInfoResponse],
        ['ClearAllBonds', b'\x00\x00\x00\x83\x00\x00\x00\x40', ClearAllBondsResponse],
        ['SmartConnect', b'\x00\x00\x00\x92\x00\x00\x00\x47\x01\x02', SmartConnectResponse]
    ])
    def test_response_from_dpa_ok(self, _, dpa, expected):
        self.assertIsInstance(ResponseFactory.get_response_from_dpa(dpa=dpa), expected)

    @parameterized.expand([
        ['RamRead', b'\x01\x00\x05\x80\x02\x00\x00\x4b\x00\x01\x02\x03\x04\x00\x00\x00\x00\x00'],
        ['Nonsense', b'\x0b\x0a']
    ])
    def test_response_from_dpa_invalid(self, _, dpa):
        with self.assertRaises(ValueError):
            ResponseFactory.get_response_from_dpa(dpa=dpa)

    @parameterized.expand([
        ['Async', {
            'mType': 'iqrfRaw',
            'data': {
                'msgId': 'async',
                'rsp': {
                    'rData': '00.00.ff.3f.00.00.80.00.17.04.00.fd.26.00.00.00.00.00.00.05'
                },
                'status': 0,
                'insId': 'iqrfgd2-default'
            }
        }, AsyncResponse],
        ['BondNode', {
            "mType": "iqrfEmbedCoordinator_BondNode",
            "data": {
                "msgId": "testEmbedCoordinator",
                "rsp": {
                    "nAdr": 0,
                    "hwpId": 0,
                    "rCode": 0,
                    "dpaVal": 53,
                    "result": {
                        "bondAddr": 1,
                        "devNr": 2
                    }
                },
                "insId": "iqrfgd2-1",
                "status": 0
            }
        }, BondNodeResponse],
        ['RemoveBond', {
            "mType": "iqrfEmbedCoordinator_RemoveBond",
            "data": {
                "msgId": "testEmbedCoordinator",
                "rsp": {
                    "nAdr": 0,
                    "hwpId": 0,
                    "rCode": 0,
                    "dpaVal": 53,
                    "result": {
                        "devNr": 1
                    }
                },
                "insId": "iqrfgd2-1",
                "status": 0
            }
        }, RemoveBondResponse],
        ['SetHops', {
            "mType": "iqrfEmbedCoordinator_SetHops",
            "data": {
                "msgId": "testEmbedCoordinator",
                "rsp": {
                    "nAdr": 0,
                    "hwpId": 0,
                    "rCode": 0,
                    "dpaVal": 0,
                    "result": {
                        "requestHops": 255,
                        "responseHops": 255
                    }
                },
                "insId": "iqrfgd2-1",
                "status": 0
            }
        }, SetHopsResponse]
    ])
    def test_response_from_json_ok(self, _, json, expected):
        self.assertIsInstance(ResponseFactory.get_response_from_json(json=json), expected)

    @parameterized.expand([
        [{'data': {'req': {}}}, JsonMsgidMissingError],
        [{'data': {'msgId': 'test'}}, JsonMTypeMissingError],
        [{'mType': 'unsupported', 'data': {'msgId': 'test'}}, UnsupportedMessageTypeError],
    ])
    def test_response_from_json_invalid(self, json, exception):
        with self.assertRaises(exception):
            ResponseFactory.get_response_from_json(json=json)

