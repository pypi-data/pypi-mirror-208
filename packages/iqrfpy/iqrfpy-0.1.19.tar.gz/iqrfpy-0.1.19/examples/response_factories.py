from iqrfpy.peripherals.coordinator.responses import *
from iqrfpy.response_factory import ResponseFactory


def handle_addr_info_response(response: AddrInfoResponse) -> None:
    print(f'peripheral: {response.get_pnum()}')
    print(f'peripheral command: {response.get_pcmd()}')
    status = response.get_rcode()
    if status == 0:
        print(f'Addr info response dev_nr: {response.get_dev_nr()}')
        print(f'Addr info response did: {response.get_did()}')


def main():
    responses = [
        b'\x00\x00\x00\x80\x00\x00\x00\x40\x0a\x2a',
        b'\x00\x00\x00\x83\x00\x00\x00\x40',
        {
            "mType": "iqrfEmbedCoordinator_AddrInfo",
            "data": {
                "msgId": "testEmbedCoordinator",
                "rsp": {
                    "nAdr": 0,
                    "hwpId": 0,
                    "rCode": 0,
                    "dpaVal": 64,
                    "result": {
                        "devNr": 0,
                        "did": 42
                    }
                },
                "insId": "iqrfgd2-1",
                "status": 0
            }
        },
        {
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
        }
    ]
    for response in responses:
        rsp = None
        if isinstance(response, bytes):
            rsp = ResponseFactory.get_response_from_dpa(dpa=response)
        elif isinstance(response, dict):
            rsp = ResponseFactory.get_response_from_json(json=response)
        if isinstance(rsp, AddrInfoResponse):
            handle_addr_info_response(response=rsp)
        else:
            print(f'Unexpected response: {type(rsp)}')


if __name__ == '__main__':
    main()
