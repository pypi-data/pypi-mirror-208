import time
from datetime import datetime

from iqrfpy.exceptions import DpaRequestTimeoutError, JsonRequestTimeoutError
import iqrfpy.messages as messages
from iqrfpy.transports.mqtt_transport import MqttTransportParams, MqttTransport
import iqrfpy.utils.dpa as dpa_const


class IqmeshNtw:
    def __init__(self):
        self.bonded_nodes = None
        self.discovered_nodes = None

    def get_nodes_number(self):
        return len(self.bonded_nodes)

    def get_discovered_nodes_number(self):
        return len(self.discovered_nodes)


def abort_script(txt):
    print(f'\n{txt}')
    print('### Script aborted ###')
    exit()


def send_receive(request: messages.IRequest, timeout) -> messages.IResponse:
    try:
        print(f'Request sent:      {datetime.now()}')
        received_response = transport.send_and_receive(request, timeout)
        print(f'Response received: {datetime.now()}')
        print(f'Message type:      {received_response.get_mtype()}')
        print(f'Message ID:        {received_response.get_msgid()}')
        pdata = received_response.get_pdata()
        if pdata:
            pdata = ' '.join("{:02X}".format(x) for x in pdata)
        print(f'PDATA (HEX):       {pdata}')
        return received_response
    except (DpaRequestTimeoutError, JsonRequestTimeoutError) as e:
        print('Error: ', str(e))
    finally:
        print('------')


params = MqttTransportParams(
    host='localhost',
    port=1883,
    client_id='python-lib-test',
    request_topic='Iqrf/DpaRequest',
    response_topic='Iqrf/DpaResponse',
    qos=1,
    keepalive=25
)

print('### Start ###')
transport = MqttTransport(params=params, auto_init=True)
time.sleep(2)  # TODO melo by byt v MqttTransport
ntw = IqmeshNtw()
timeout_c = 2

print('\n=== Coordinator: Get bonded Nodes ===')
response: messages.CoordinatorBondedDevicesRsp = send_receive(messages.CoordinatorBondedDevicesReq(), timeout_c)
if response:
    ntw.bonded_nodes = response.get_bonded()
    print(f'Bonded Nodes: {ntw.get_nodes_number()} {ntw.bonded_nodes}')
else:
    abort_script('Cannot continue without information about the number of Nodes in the network')

print('\n=== Coordinator: Get discovered Nodes ===')
response: messages.CoordinatorDiscoveredDevicesRsp = send_receive(messages.CoordinatorDiscoveredDevicesReq(), timeout_c)
if response:
    ntw.discovered_nodes = response.get_discovered()
    print(f'Discovered Nodes: {ntw.get_discovered_nodes_number()} {ntw.discovered_nodes}')
else:
    abort_script('Cannot continue without information about the number of discovered Nodes in the network')

# Timeout calculation uses the worst case of the timeslot in LP mode (100 ms)
timeout_n = ((ntw.get_discovered_nodes_number() + 1) * 0.1 * 2) + timeout_c

print('\n=== Node 3: Pulse LED G ===')
to_send = 3
sent_req = 0
received_rsp = 0

# DPA timeout shorter, should end with DPA timeout error
for _ in range(to_send):
    sent_req += 1
    response: messages.LedgPulseRsp = send_receive(messages.LedgPulseReq(nadr=3, timeout=4), timeout=10)
    if response:
        received_rsp += 1

# JSON API timeout shorter, should end with JSON API timeout error
for _ in range(to_send):
    sent_req += 1
    response: messages.LedgPulseRsp = send_receive(messages.LedgPulseReq(nadr=3, timeout=4), timeout=3)
    if response:
        received_rsp += 1

print(f'Received {received_rsp} responses from {sent_req} requests')

transport.terminate()

print('\n### End ###')
