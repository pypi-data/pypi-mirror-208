from abc import ABC, abstractmethod
from typing import Union
from iqrfpy.enums.commands import *
from iqrfpy.enums.message_types import *
from iqrfpy.enums.peripherals import *
from iqrfpy.async_response import AsyncResponse
from iqrfpy.confirmation import Confirmation
from iqrfpy.iresponse import IResponse
import iqrfpy.peripherals.exploration.responses as exploration_responses
import iqrfpy.peripherals.coordinator.responses as c_responses
import iqrfpy.peripherals.os.responses as os_responses
import iqrfpy.peripherals.eeprom.responses as eeprom_responses
import iqrfpy.peripherals.ledg.responses as ledg_responses
import iqrfpy.peripherals.ledr.responses as ledr_responses
import iqrfpy.peripherals.thermometer.responses as thermometer_responses
import iqrfpy.peripherals.uart.responses as uart_responses
from iqrfpy.utils.common import Common
from iqrfpy.utils.dpa import *
from iqrfpy.exceptions import UnsupportedMessageTypeError, UnsupportedPeripheralError, UnsupportedPeripheralCommandError

__all__ = [
    '_get_factory_from_dpa',
    '_get_factory_from_mtype',
    'ResponseFactory',
    'AsyncResponseFactory',
    'ConfirmationFactory',
    'PeripheralEnumerationFactory',
    'PeripheralInformationFactory',
    'MorePeripheralsInformationFactory',
    'CoordinatorAddrInfoFactory',
    'CoordinatorAuthorizeBondFactory',
    'CoordinatorBackupFactory',
    'CoordinatorBondedDevicesFactory',
    'CoordinatorBondNodeFactory',
    'CoordinatorClearAllBondsFactory',
    'CoordinatorDiscoveredDevicesFactory',
    'CoordinatorDiscoveryFactory',
    'CoordinatorRemoveBondFactory',
    'CoordinatorRestoreFactory',
    'CoordinatorSetDpaParamsFactory',
    'CoordinatorSetHopsFactory',
    'CoordinatorSetMIDFactory',
    'CoordinatorSmartConnectFactory',
    'OSReadFactory',
    'EepromReadFactory',
    'EepromWriteFactory',
    'LedgSetOnFactory',
    'LedgSetOffFactory',
    'LedgPulseFactory',
    'LedgFlashingFactory',
    'LedrSetOnFactory',
    'LedrSetOffFactory',
    'LedrPulseFactory',
    'LedrFlashingFactory',
    'ThermometerReadFactory',
    'UartOpenFactory',
    'UartCloseFactory',
    'UartWriteReadFactory',
    'UartClearWriteReadFactory',
]


class ResponseFactory:

    @staticmethod
    def get_response_from_dpa(dpa: bytes) -> IResponse:
        IResponse.validate_dpa_response(dpa)
        pnum = dpa[ResponsePacketMembers.PNUM]
        pcmd = dpa[ResponsePacketMembers.PCMD]
        rcode = dpa[ResponsePacketMembers.RCODE]
        if rcode == CONFIRMATION_RCODE and len(dpa) == CONFIRMATION_PACKET_LEN:
            factory = ConfirmationFactory()
        elif pcmd <= REQUEST_PCMD_MAX and rcode >= ASYNC_RESPONSE_CODE:
            factory = AsyncResponseFactory()
        elif EmbedPeripherals.has_value(pnum) and pnum != EmbedPeripherals.EXPLORATION and \
                pcmd == ExplorationResponseCommands.PERIPHERALS_ENUMERATION_INFORMATION:
            factory = PeripheralInformationFactory()
        elif pnum == BYTE_MAX and EmbedPeripherals.has_value(pcmd):
            factory = MorePeripheralsInformationFactory()
            pass
        else:
            peripheral = Common.pnum_from_dpa(pnum)
            command = Common.response_pcmd_from_dpa(peripheral, pcmd)
            factory = _get_factory_from_dpa(peripheral, command)
        return factory.create_from_dpa(dpa)

    @staticmethod
    def get_response_from_json(json: dict) -> IResponse:
        msgid = Common.msgid_from_json(json)
        mtype = Common.mtype_str_from_json(json)
        if msgid == IResponse.ASYNC_MSGID and \
                GenericMessages.has_value(mtype) and GenericMessages(mtype) == GenericMessages.RAW:
            factory = AsyncResponseFactory()
        else:
            message = Common.string_to_mtype(mtype)
            factory = _get_factory_from_mtype(message)
        return factory.create_from_json(json)


class BaseFactory(ABC):

    @abstractmethod
    def create_from_dpa(self, dpa: bytes) -> IResponse:
        """Returns a response object created from DPA message."""

    @abstractmethod
    def create_from_json(self, json: dict) -> IResponse:
        """Returns a response object created from JSON API message."""

# Generic factories


class ConfirmationFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> Confirmation:
        return Confirmation.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> Confirmation:
        return Confirmation.from_json(json=json)


class AsyncResponseFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> IResponse:
        return AsyncResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> IResponse:
        return AsyncResponse.from_json(json=json)


# Exploration factories
class PeripheralEnumerationFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> exploration_responses.PeripheralEnumerationResponse:
        return exploration_responses.PeripheralEnumerationResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.AddrInfoResponse:
        return exploration_responses.PeripheralEnumerationResponse.from_json(json=json)


class PeripheralInformationFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> exploration_responses.PeripheralInformationResponse:
        return exploration_responses.PeripheralInformationResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> exploration_responses.PeripheralInformationResponse:
        return exploration_responses.PeripheralInformationResponse.from_json(json=json)


class MorePeripheralsInformationFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> exploration_responses.PeripheralInformationResponse:
        return exploration_responses.PeripheralInformationResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> exploration_responses.PeripheralInformationResponse:
        return exploration_responses.PeripheralInformationResponse.from_json(json=json)


# Coordinator factories
class CoordinatorAddrInfoFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> c_responses.AddrInfoResponse:
        return c_responses.AddrInfoResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.AddrInfoResponse:
        return c_responses.AddrInfoResponse.from_json(json=json)


class CoordinatorAuthorizeBondFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> c_responses.AuthorizeBondResponse:
        return c_responses.AuthorizeBondResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.AuthorizeBondResponse:
        return c_responses.AuthorizeBondResponse.from_json(json=json)


class CoordinatorBackupFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> c_responses.BackupResponse:
        return c_responses.BackupResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.BackupResponse:
        return c_responses.BackupResponse.from_json(json=json)


class CoordinatorBondedDevicesFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.BondedDevicesResponse:
        return c_responses.BondedDevicesResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.BondedDevicesResponse:
        return c_responses.BondedDevicesResponse.from_json(json=json)


class CoordinatorBondNodeFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.BondNodeResponse:
        return c_responses.BondNodeResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.BondNodeResponse:
        return c_responses.BondNodeResponse.from_json(json=json)


class CoordinatorClearAllBondsFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.ClearAllBondsResponse:
        return c_responses.ClearAllBondsResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.ClearAllBondsResponse:
        return c_responses.ClearAllBondsResponse.from_json(json=json)


class CoordinatorDiscoveredDevicesFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.DiscoveredDevicesResponse:
        return c_responses.DiscoveredDevicesResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.DiscoveredDevicesResponse:
        return c_responses.DiscoveredDevicesResponse.from_json(json=json)


class CoordinatorDiscoveryFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.DiscoveryResponse:
        return c_responses.DiscoveryResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.DiscoveryResponse:
        return c_responses.DiscoveryResponse.from_json(json=json)


class CoordinatorRemoveBondFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.RemoveBondResponse:
        return c_responses.RemoveBondResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.RemoveBondResponse:
        return c_responses.RemoveBondResponse.from_json(json=json)


class CoordinatorRestoreFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.RestoreResponse:
        return c_responses.RestoreResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.RestoreResponse:
        return c_responses.RestoreResponse.from_json(json=json)


class CoordinatorSetDpaParamsFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.SetDpaParamsResponse:
        return c_responses.SetDpaParamsResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.SetDpaParamsResponse:
        return c_responses.SetDpaParamsResponse.from_json(json=json)


class CoordinatorSetHopsFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.SetHopsResponse:
        return c_responses.SetHopsResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.SetHopsResponse:
        return c_responses.SetHopsResponse.from_json(json=json)


class CoordinatorSetMIDFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.SetMidResponse:
        return c_responses.SetMidResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.SetMidResponse:
        return c_responses.SetMidResponse.from_json(json=json)


class CoordinatorSmartConnectFactory(BaseFactory):
    def create_from_dpa(self, dpa: bytes) -> c_responses.SmartConnectResponse:
        return c_responses.SmartConnectResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> c_responses.SmartConnectResponse:
        return c_responses.SmartConnectResponse.from_json(json=json)


# OS factories


class OSReadFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> os_responses.ReadResponse:
        return os_responses.ReadResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> os_responses.ReadResponse:
        return os_responses.ReadResponse.from_json(json=json)

# EEPROM factories


class EepromReadFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> eeprom_responses.ReadResponse:
        return eeprom_responses.ReadResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> eeprom_responses.ReadResponse:
        return eeprom_responses.ReadResponse.from_json(json=json)


class EepromWriteFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> eeprom_responses.WriteResponse:
        return eeprom_responses.WriteResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> eeprom_responses.WriteResponse:
        return eeprom_responses.WriteResponse.from_json(json=json)


# LEDG factories


class LedgSetOnFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledg_responses.SetOnResponse:
        return ledg_responses.SetOnResponse.from_dpa(dpa)

    def create_from_json(self, json: dict) -> ledg_responses.SetOnResponse:
        return ledg_responses.SetOnResponse.from_json(json)


class LedgSetOffFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledg_responses.SetOffResponse:
        return ledg_responses.SetOffResponse.from_dpa(dpa)

    def create_from_json(self, json: dict) -> ledg_responses.SetOffResponse:
        return ledg_responses.SetOffResponse.from_json(json)


class LedgPulseFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledg_responses.PulseResponse:
        return ledg_responses.PulseResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> ledg_responses.PulseResponse:
        return ledg_responses.PulseResponse.from_json(json=json)


class LedgFlashingFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledg_responses.FlashingResponse:
        return ledg_responses.FlashingResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> ledg_responses.FlashingResponse:
        return ledg_responses.FlashingResponse.from_json(json=json)


# LEDR factories


class LedrSetOnFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledr_responses.SetOnResponse:
        return ledr_responses.SetOnResponse.from_dpa(dpa)

    def create_from_json(self, json: dict) -> ledr_responses.SetOnResponse:
        return ledr_responses.SetOnResponse.from_json(json)


class LedrSetOffFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledr_responses.SetOffResponse:
        return ledr_responses.SetOffResponse.from_dpa(dpa)

    def create_from_json(self, json: dict) -> ledr_responses.SetOffResponse:
        return ledr_responses.SetOffResponse.from_json(json)


class LedrPulseFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledr_responses.PulseResponse:
        return ledr_responses.PulseResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> ledr_responses.PulseResponse:
        return ledr_responses.PulseResponse.from_json(json=json)


class LedrFlashingFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> ledr_responses.FlashingResponse:
        return ledr_responses.FlashingResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> ledr_responses.FlashingResponse:
        return ledr_responses.FlashingResponse.from_json(json=json)


# Thermometer factories
class ThermometerReadFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> thermometer_responses.ReadResponse:
        return thermometer_responses.ReadResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> thermometer_responses.ReadResponse:
        return thermometer_responses.ReadResponse.from_json(json=json)


# UART factories
class UartOpenFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> uart_responses.OpenResponse:
        return uart_responses.OpenResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> uart_responses.OpenResponse:
        return uart_responses.OpenResponse.from_json(json=json)


class UartCloseFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> uart_responses.CloseResponse:
        return uart_responses.CloseResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> uart_responses.CloseResponse:
        return uart_responses.CloseResponse.from_json(json=json)


class UartWriteReadFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> uart_responses.WriteReadResponse:
        return uart_responses.WriteReadResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> uart_responses.WriteReadResponse:
        return uart_responses.WriteReadResponse.from_json(json=json)


class UartClearWriteReadFactory(BaseFactory):

    def create_from_dpa(self, dpa: bytes) -> uart_responses.ClearWriteReadResponse:
        return uart_responses.ClearWriteReadResponse.from_dpa(dpa=dpa)

    def create_from_json(self, json: dict) -> uart_responses.ClearWriteReadResponse:
        return uart_responses.ClearWriteReadResponse.from_json(json=json)


def _get_factory_from_dpa(pnum: Union[EmbedPeripherals, Standards], pcmd: Command) -> BaseFactory:
    factories = {
        EmbedPeripherals.EXPLORATION: {
            ExplorationResponseCommands.PERIPHERALS_ENUMERATION_INFORMATION: PeripheralEnumerationFactory(),
        },
        EmbedPeripherals.COORDINATOR: {
            CoordinatorResponseCommands.ADDR_INFO: CoordinatorAddrInfoFactory(),
            CoordinatorResponseCommands.AUTHORIZE_BOND: CoordinatorAuthorizeBondFactory(),
            CoordinatorResponseCommands.BACKUP: CoordinatorBackupFactory(),
            CoordinatorResponseCommands.BONDED_DEVICES: CoordinatorBondedDevicesFactory(),
            CoordinatorResponseCommands.BOND_NODE: CoordinatorBondNodeFactory(),
            CoordinatorResponseCommands.CLEAR_ALL_BONDS: CoordinatorClearAllBondsFactory(),
            CoordinatorResponseCommands.DISCOVERED_DEVICES: CoordinatorDiscoveredDevicesFactory(),
            CoordinatorResponseCommands.DISCOVERY: CoordinatorDiscoveryFactory(),
            CoordinatorResponseCommands.REMOVE_BOND: CoordinatorRemoveBondFactory(),
            CoordinatorResponseCommands.RESTORE: CoordinatorRestoreFactory(),
            CoordinatorResponseCommands.SET_DPA_PARAMS: CoordinatorSetDpaParamsFactory(),
            CoordinatorResponseCommands.SET_HOPS: CoordinatorSetHopsFactory(),
            CoordinatorResponseCommands.SET_MID: CoordinatorSetMIDFactory(),
            CoordinatorResponseCommands.SMART_CONNECT: CoordinatorSmartConnectFactory(),
        },
        EmbedPeripherals.OS: {
            OSResponseCommands.READ: OSReadFactory()
        },
        EmbedPeripherals.EEPROM: {
            EEPROMResponseCommands.READ: EepromReadFactory(),
            EEPROMResponseCommands.WRITE: EepromWriteFactory(),
        },
        EmbedPeripherals.LEDG: {
            LEDResponseCommands.SET_ON: LedgSetOnFactory(),
            LEDResponseCommands.SET_OFF: LedgSetOffFactory(),
            LEDResponseCommands.PULSE: LedgPulseFactory(),
            LEDResponseCommands.FLASHING: LedgFlashingFactory(),
        },
        EmbedPeripherals.LEDR: {
            LEDResponseCommands.SET_ON: LedrSetOnFactory(),
            LEDResponseCommands.SET_OFF: LedrSetOffFactory(),
            LEDResponseCommands.PULSE: LedrPulseFactory(),
            LEDResponseCommands.FLASHING: LedrFlashingFactory(),
        },
        EmbedPeripherals.THERMOMETER: {
            ThermometerResponseCommands.READ: ThermometerReadFactory(),
        },
        EmbedPeripherals.UART: {
            UartResponseCommands.OPEN: UartOpenFactory(),
            UartResponseCommands.CLOSE: UartCloseFactory(),
            UartResponseCommands.WRITE_READ: UartWriteReadFactory(),
            UartResponseCommands.CLEAR_WRITE_READ: UartClearWriteReadFactory(),
        }
    }
    if pnum in factories:
        if pcmd in factories[pnum]:
            return factories[pnum][pcmd]
        raise UnsupportedPeripheralCommandError(f'Unknown or unsupported peripheral command: {pcmd}')
    raise UnsupportedPeripheralError(f'Unknown or unsupported peripheral: {pnum}')


def _get_factory_from_mtype(mtype: MessageType) -> BaseFactory:
    factories = {
        ExplorationMessages.ENUMERATE: PeripheralEnumerationFactory(),
        ExplorationMessages.PERIPHERAL_INFORMATION: PeripheralInformationFactory(),
        ExplorationMessages.MORE_PERIPHERALS_INFORMATION: MorePeripheralsInformationFactory(),
        CoordinatorMessages.ADDR_INFO: CoordinatorAddrInfoFactory(),
        CoordinatorMessages.AUTHORIZE_BOND: CoordinatorAuthorizeBondFactory(),
        CoordinatorMessages.BACKUP: CoordinatorBackupFactory(),
        CoordinatorMessages.BONDED_DEVICES: CoordinatorBondedDevicesFactory(),
        CoordinatorMessages.BOND_NODE: CoordinatorBondNodeFactory(),
        CoordinatorMessages.CLEAR_ALL_BONDS: CoordinatorClearAllBondsFactory(),
        CoordinatorMessages.DISCOVERED_DEVICES: CoordinatorDiscoveredDevicesFactory(),
        CoordinatorMessages.DISCOVERY: CoordinatorDiscoveryFactory(),
        CoordinatorMessages.REMOVE_BOND: CoordinatorRemoveBondFactory(),
        CoordinatorMessages.RESTORE: CoordinatorRestoreFactory(),
        CoordinatorMessages.SET_DPA_PARAMS: CoordinatorSetDpaParamsFactory(),
        CoordinatorMessages.SET_HOPS: CoordinatorSetHopsFactory(),
        CoordinatorMessages.SET_MID: CoordinatorSetMIDFactory(),
        CoordinatorMessages.SMART_CONNECT: CoordinatorSmartConnectFactory(),
        OSMessages.READ: OSReadFactory(),
        EEPROMMessages.READ: EepromReadFactory(),
        EEPROMMessages.WRITE: EepromWriteFactory(),
        LEDGMessages.SET_ON: LedgSetOnFactory(),
        LEDGMessages.SET_OFF: LedgSetOffFactory(),
        LEDGMessages.PULSE: LedgPulseFactory(),
        LEDGMessages.FLASHING: LedgFlashingFactory(),
        LEDRMessages.SET_ON: LedrSetOnFactory(),
        LEDRMessages.SET_OFF: LedrSetOffFactory(),
        LEDRMessages.PULSE: LedrPulseFactory(),
        LEDRMessages.FLASHING: LedrFlashingFactory(),
        ThermometerMessages.READ: ThermometerReadFactory(),
        UartMessages.OPEN: UartOpenFactory(),
        UartMessages.CLOSE: UartCloseFactory(),
        UartMessages.WRITE_READ: UartWriteReadFactory(),
        UartMessages.CLEAR_WRITE_READ: UartClearWriteReadFactory(),
    }

    if mtype in factories:
        return factories[mtype]
    raise UnsupportedMessageTypeError(f'Unknown or unsupported message type: {mtype}')
