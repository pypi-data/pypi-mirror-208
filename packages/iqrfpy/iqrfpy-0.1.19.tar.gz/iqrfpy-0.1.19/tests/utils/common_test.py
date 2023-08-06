from parameterized import parameterized
import unittest
from iqrfpy.utils.common import *
from iqrfpy.enums.commands import *
from iqrfpy.enums.message_types import *
from iqrfpy.enums.peripherals import *
from iqrfpy.exceptions import JsonMsgidMissingError, JsonDpaValueMissingError, JsonHwpidMissingError, \
    JsonMTypeMissingError, JsonNadrMissingError, JsonRCodeMissingError, JsonResultMissingError, \
    JsonStatusMissingError, UnsupportedMessageTypeError


class CommonTestCase(unittest.TestCase):

    def setUp(self):
        self.request = {
            'mType': 'iqrfEmbedLedr_Set',
            'data': {
                'msgId': 'test',
                'req': {
                    'nAdr': 1,
                    'param': {
                        'onOff': True
                    }
                },
                'returnVerbose': True
            }
        }
        self.response = {
            'mType': 'iqrfEmbedLedr_Set',
            'data': {
                'msgId': 'testEmbedLedr',
                'rsp': {
                    'nAdr': 1,
                    'hwpId': 2,
                    'rCode': 0,
                    'dpaVal': 75,
                    'result': {}
                },
                'raw': {
                    'request': '01.00.06.01.ff.ff',
                    'requestTs': '2018-07-17T16:54:38.112445',
                    'confirmation': '01.00.06.01.ff.ff.ff.3b.01.04.01',
                    'confirmationTs': '2018-07-17T16:54:38.135078',
                    'response': '01.00.06.81.02.00.00.4b',
                    'responseTs': '2018-07-17T16:54:38.277356'
                },
                'insId': 'iqrfgd2-1',
                'statusStr': 'ok',
                'status': 0
            }
        }

    # hwpid_from_dpa tests

    def test_hwpid_from_dpa_ok(self):
        expected = 1026
        self.assertEqual(
            Common.hwpid_from_dpa(0x04, 0x02),
            expected
        )

    def test_hwpid_from_dpa_param_value_too_large(self):
        with self.assertRaises(ValueError):
            Common.hwpid_from_dpa(256, 0)

    def test_hwpid_from_dpa_param_value_negative(self):
        with self.assertRaises(ValueError):
            Common.hwpid_from_dpa(-1, 0)

    # pnum_from_dpa tests

    @parameterized.expand([
        ['RAM', EmbedPeripherals.RAM, EmbedPeripherals.RAM],
        ['OS', 2, EmbedPeripherals.OS],
        ['BinaryOutput', Standards.BINARY_OUTPUT, Standards.BINARY_OUTPUT],
        ['Sensor', 0x5E, Standards.SENSOR]
    ])
    def test_pnum_from_dpa_ok(self, _, value, expected):
        self.assertEqual(
            Common.pnum_from_dpa(value),
            expected
        )

    def test_pnum_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            Common.pnum_from_dpa(256)

    def test_pnum_from_dpa_unknown(self):
        with self.assertRaises(ValueError):
            Common.pnum_from_dpa(128)

    # pcmd_from_dpa

    @parameterized.expand([
        ['Coordinator', EmbedPeripherals.COORDINATOR, 4, CoordinatorRequestCommands.BOND_NODE],
        ['Node', EmbedPeripherals.NODE, 0, NodeRequestCommands.READ],
        ['OS', EmbedPeripherals.OS, OSRequestCommands.INDICATE, OSRequestCommands.INDICATE],
        ['Eeprom', EmbedPeripherals.EEPROM, 0, EEPROMRequestCommands.READ],
        ['Eeeprom', EmbedPeripherals.EEEPROM, 3, EEEPROMRequestCommands.WRITE],
        ['RAM', EmbedPeripherals.RAM, RAMRequestCommands.WRITE, RAMRequestCommands.WRITE],
        ['LEDR', EmbedPeripherals.LEDR, LEDRequestCommands.FLASHING, LEDRequestCommands.FLASHING],
        ['LEDG', EmbedPeripherals.LEDG, 3, LEDRequestCommands.PULSE],
        ['IO', EmbedPeripherals.IO, IORequestCommands.DIRECTION, IORequestCommands.DIRECTION],
        ['Thermometer', EmbedPeripherals.THERMOMETER, ThermometerRequestCommands.READ, ThermometerRequestCommands.READ],
        ['Uart', EmbedPeripherals.UART, 0x03, UartRequestCommands.CLEAR_WRITE_READ],
        ['Frc', EmbedPeripherals.FRC, FrcRequestCommands.EXTRA_RESULT, FrcRequestCommands.EXTRA_RESULT],
        ['Exploration', EmbedPeripherals.EXPLORATION, ExplorationRequestCommands.PERIPHERALS_ENUMERATION_INFORMATION,
         ExplorationRequestCommands.PERIPHERALS_ENUMERATION_INFORMATION],
        ['DALI', Standards.DALI, DALIRequestCommands.SEND_REQUEST_COMMANDS, DALIRequestCommands.SEND_REQUEST_COMMANDS],
        ['BinaryOutput', Standards.BINARY_OUTPUT, 0, BinaryOutputRequestCommands.SET_OUTPUT],
        ['Sensor', Standards.SENSOR, 0x3E, SensorRequestCommands.ENUMERATE],
        ['Light', Standards.LIGHT, LightRequestCommands.INCREMENT_POWER, LightRequestCommands.INCREMENT_POWER]
    ])
    def test_request_pcmd_from_dpa_ok(self, _, pnum, value, expected):
        self.assertEqual(
            Common.request_pcmd_from_dpa(pnum, value),
            expected
        )

    def test_request_pcmd_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            Common.request_pcmd_from_dpa(EmbedPeripherals.OS, 1000)

    def test_request_pcmd_from_dpa_negative(self):
        with self.assertRaises(ValueError):
            Common.request_pcmd_from_dpa(Standards.SENSOR, -1)

    @parameterized.expand([
        ['RAM', EmbedPeripherals.RAM, 5],
        ['BinaryOutput', Standards.BINARY_OUTPUT, 63]
    ])
    def test_request_pcmd_from_dpa_unknown_pcmd(self, _, pnum, value):
        with self.assertRaises(ValueError):
            Common.request_pcmd_from_dpa(pnum, value)

    @parameterized.expand([
        ['Coordinator', EmbedPeripherals.COORDINATOR, 132, CoordinatorResponseCommands.BOND_NODE],
        ['Node', EmbedPeripherals.NODE, 128, NodeResponseCommands.READ],
        ['OS', EmbedPeripherals.OS, OSResponseCommands.INDICATE, OSResponseCommands.INDICATE],
        ['Eeprom', EmbedPeripherals.EEPROM, 128, EEPROMResponseCommands.READ],
        ['Eeeprom', EmbedPeripherals.EEEPROM, 131, EEEPROMResponseCommands.WRITE],
        ['RAM', EmbedPeripherals.RAM, RAMResponseCommands.WRITE, RAMResponseCommands.WRITE],
        ['LEDR', EmbedPeripherals.LEDR, LEDResponseCommands.FLASHING, LEDResponseCommands.FLASHING],
        ['LEDG', EmbedPeripherals.LEDG, 131, LEDResponseCommands.PULSE],
        ['IO', EmbedPeripherals.IO, IOResponseCommands.DIRECTION, IOResponseCommands.DIRECTION],
        ['Thermometer', EmbedPeripherals.THERMOMETER, ThermometerResponseCommands.READ,
         ThermometerResponseCommands.READ],
        ['Uart', EmbedPeripherals.UART, 0x83, UartResponseCommands.CLEAR_WRITE_READ],
        ['Frc', EmbedPeripherals.FRC, FrcResponseCommands.EXTRA_RESULT, FrcResponseCommands.EXTRA_RESULT],
        ['Exploration', EmbedPeripherals.EXPLORATION, ExplorationResponseCommands.PERIPHERALS_ENUMERATION_INFORMATION,
         ExplorationResponseCommands.PERIPHERALS_ENUMERATION_INFORMATION],
        ['DALI', Standards.DALI, DALIResponseCommands.SEND_REQUEST_COMMANDS,
         DALIResponseCommands.SEND_REQUEST_COMMANDS],
        ['BinaryOutput', Standards.BINARY_OUTPUT, 128, BinaryOutputResponseCommands.SET_OUTPUT],
        ['Sensor', Standards.SENSOR, 0xBE, SensorResponseCommands.ENUMERATE],
        ['Light', Standards.LIGHT, LightResponseCommands.INCREMENT_POWER, LightResponseCommands.INCREMENT_POWER]
    ])
    def test_response_pcmd_from_dpa_ok(self, _, pnum, value, expected):
        self.assertEqual(
            Common.response_pcmd_from_dpa(pnum, value),
            expected
        )

    def test_response_pcmd_from_dpa_invalid(self):
        with self.assertRaises(ValueError):
            Common.response_pcmd_from_dpa(EmbedPeripherals.OS, 1000)

    def test_response_pcmd_from_dpa_negative(self):
        with self.assertRaises(ValueError):
            Common.response_pcmd_from_dpa(Standards.SENSOR, -1)

    @parameterized.expand([
        ['RAM', EmbedPeripherals.RAM, 133],
        ['BinaryOutput', Standards.BINARY_OUTPUT, 240]
    ])
    def test_response_pcmd_from_dpa_unknown_pcmd(self, _, pnum, value):
        with self.assertRaises(ValueError):
            Common.response_pcmd_from_dpa(pnum, value)

    @parameterized.expand([
        ['AddrInfo', EmbedPeripherals.COORDINATOR, CoordinatorResponseCommands.ADDR_INFO, CoordinatorMessages.ADDR_INFO],
        ['Backup', EmbedPeripherals.COORDINATOR, CoordinatorResponseCommands.BACKUP, CoordinatorMessages.BACKUP],
        ['BondedDevices', EmbedPeripherals.COORDINATOR, 0x82, CoordinatorMessages.BONDED_DEVICES],
        ['BondNode', 0, 132, CoordinatorMessages.BOND_NODE],
        ['ClearAllBonds', EmbedPeripherals.COORDINATOR, 0x83, CoordinatorMessages.CLEAR_ALL_BONDS],
        ['DiscoveredDevices', EmbedPeripherals.COORDINATOR, 0x81, CoordinatorMessages.DISCOVERED_DEVICES],
        ['Discovery', EmbedPeripherals.COORDINATOR, CoordinatorResponseCommands.DISCOVERY, CoordinatorMessages.DISCOVERY],
        ['RemoveBond', 0x00, 0x85, CoordinatorMessages.REMOVE_BOND],
        ['Restore', EmbedPeripherals.COORDINATOR, CoordinatorResponseCommands.RESTORE, CoordinatorMessages.RESTORE],
        ['SetDpaParams', 0, CoordinatorResponseCommands.SET_DPA_PARAMS, CoordinatorMessages.SET_DPA_PARAMS],
        ['SetHops', EmbedPeripherals.COORDINATOR, CoordinatorResponseCommands.SET_HOPS, CoordinatorMessages.SET_HOPS],
        ['SetMID', EmbedPeripherals.COORDINATOR, 0x93, CoordinatorMessages.SET_MID],
        ['SmartConnect', EmbedPeripherals.COORDINATOR, 146, CoordinatorMessages.SMART_CONNECT]
    ])
    def test_mtype_from_dpa_ok(self, _, pnum, pcmd, expected):
        self.assertEqual(Common.mtype_from_dpa_response(pnum, pcmd), expected)

    @parameterized.expand([
        ['InvalidPer', 170, 3],
        ['InvalidPcmd', EmbedPeripherals.COORDINATOR, 55]
    ])
    def test_mtype_from_dpa_unknown(self, _, pnum, pcmd):
        with self.assertRaises(ValueError):
            Common.mtype_from_dpa_response(pnum, pcmd)

    # msgid_from_json tests

    def test_msgid_from_json_ok(self):
        expected = 'test'
        self.assertEqual(
            Common.msgid_from_json(self.request),
            expected
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_msgid_from_json_missing_key(self, value):
        with self.assertRaises(JsonMsgidMissingError):
            Common.msgid_from_json(value)

    # mtype_str_from_json tests

    def test_mtype_str_from_json_ok(self):
        self.assertEqual(
            Common.mtype_str_from_json(self.response),
            'iqrfEmbedLedr_Set'
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_mtype_str_from_json_missing_key(self, value):
        with self.assertRaises(JsonMTypeMissingError):
            Common.mtype_str_from_json(value)

    # nadr_from_json tests

    def test_nadr_from_json_ok(self):
        expected = 1
        self.assertEqual(
            Common.nadr_from_json(self.response),
            expected,
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_nadr_from_json_missing_key(self, value):
        with self.assertRaises(JsonNadrMissingError):
            Common.nadr_from_json(value)

    # hwpid_from_json tests

    def test_hwpid_from_json_ok(self):
        expected = 2
        self.assertEqual(
            Common.hwpid_from_json(self.response),
            expected
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_hwpid_from_json_missing_key(self, value):
        with self.assertRaises(JsonHwpidMissingError):
            Common.hwpid_from_json(value)

    # rcode_from_json tests

    def test_rcode_from_json_ok(self):
        expected = 0
        self.assertEqual(
            Common.rcode_from_json(self.response),
            expected
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_rcode_from_json_missing_key(self, value):
        with self.assertRaises(JsonRCodeMissingError):
            Common.rcode_from_json(value)

    # dpa_value_from_json tests

    def test_dpa_value_from_json_ok(self):
        expected = 75
        self.assertEqual(
            Common.dpa_value_from_json(self.response),
            expected
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_dpa_value_from_json_missing_key(self, value):
        with self.assertRaises(JsonDpaValueMissingError):
            Common.dpa_value_from_json(value)

    # result_from_json tests

    def test_result_from_json_ok(self):
        expected = {}
        self.assertEqual(
            Common.result_from_json(self.response),
            expected
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_result_from_json_missing_key(self, value):
        with self.assertRaises(JsonResultMissingError):
            Common.result_from_json(value)

    def test_status_from_json_ok(self):
        expected = 0
        self.assertEqual(
            Common.status_from_json(self.response),
            expected
        )

    @parameterized.expand([
        [{}],
        [{'data': {'req': {}}}]
    ])
    def test_status_from_json_missing_key(self, value):
        with self.assertRaises(JsonStatusMissingError):
            Common.status_from_json(value)

    # string_to_mtype tests

    @parameterized.expand([
        ['Raw', 'iqrfRaw', GenericMessages.RAW],
        ['AddrInfo', 'iqrfEmbedCoordinator_AddrInfo', CoordinatorMessages.ADDR_INFO],
        ['SensorRead', 'iqrfSensor_ReadSensorsWithTypes', SensorMessages.READ_SENSORS_WITH_TYPES],
        ['LightEnumerate', 'iqrfLight_Enumerate', LightMessages.ENUMERATE]
    ])
    def test_string_to_mtype_ok(self, _, string, expected):
        self.assertEqual(Common.string_to_mtype(string), expected)

    @parameterized.expand(['test', 'unknown', 'iqrfEmbedCoordinator_Nonexistent'])
    def test_string_to_mtype_unknown(self, string):
        with self.assertRaises(UnsupportedMessageTypeError):
            Common.string_to_mtype(string)

    # bitmap_to_nodes tests

    @parameterized.expand([
        ['empty', [], []],
        ['single', [0x0e], [1, 2, 3]],
        ['full', [0xFF, 0xFF, 0xFF, 0xFF], [i for i in range(0, 32)]]
    ])
    def test_bitmap_to_nodes(self, _, bitmap, expected):
        self.assertEqual(
            Common.bitmap_to_nodes(bitmap),
            expected
        )

    # nodes_to_bitmap tests

    @parameterized.expand([
        ['empty', [], []],
        ['single', [1, 2, 3], [0x0e]],
        ['full', [i for i in range(0, 32)], [0xFF, 0xFF, 0xFF, 0xFF]]
    ])
    def test_nodes_to_bitmap(self, _, nodes, expected):
        self.assertEqual(
            Common.nodes_to_bitmap(nodes),
            expected
        )

    # is_hex_string tests

    @parameterized.expand([
        ['empty', '', False],
        ['hexadecimal', '96bcac11a', True],
        ['non-hexadecimal', 'abcdefx', False]
    ])
    def test_is_hex_string(self, _, value, expected):
        self.assertEqual(
            Common.is_hex_string(value),
            expected
        )

    # hex_string_to_list tests

    @parameterized.expand([
        ['short', '0efa', [14, 250]],
        ['ibk', '9a691f1a2101216503e5c588ffe7f6c2', [154, 105, 31, 26, 33, 1, 33, 101,
                                                     3, 229, 197, 136, 255, 231, 246, 194]]
    ])
    def test_hex_string_to_list_ok(self, _, string, expected):
        self.assertEqual(
            Common.hex_string_to_list(string),
            expected
        )

    @parameterized.expand([
        ['empty', ''],
        ['odd_length_string', 'aab'],
        ['non-hexadecimal', 'aaax']
    ])
    def test_hex_string_to_list_invalid(self, _, value):
        with self.assertRaises(ValueError):
            Common.hex_string_to_list(value)

    # values_in_byte_range tests

    @parameterized.expand([
        ['empty', [], True],
        ['bytes', [255, 10, 12, 7], True],
        ['too_high', [1000, 5], False],
        ['negative', [-1, 10, 12, 7], False]
    ])
    def test_values_in_byte_range(self, _, value, expected):
        self.assertEqual(
            Common.values_in_byte_range(value),
            expected
        )
