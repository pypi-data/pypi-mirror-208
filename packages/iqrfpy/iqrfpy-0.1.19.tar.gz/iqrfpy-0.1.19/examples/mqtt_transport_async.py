from datetime import datetime
import time

from iqrfpy.peripherals.ledr.requests.pulse import PulseRequest
from iqrfpy.iresponse import IResponse
from iqrfpy.transports.mqtt_transport import MqttTransportParams, MqttTransport


def print_formatted(text, data):
    print(f'{text:30s} {data}')


def handler(response: IResponse) -> None:
    print_formatted('Received message at:', datetime.now())
    print_formatted('Message type:', response.get_mtype())
    print_formatted('Message ID:', response.get_msgid())
    print_formatted('Response code:', response.get_rcode())


params = MqttTransportParams(
        host='localhost',
        port=1883,
        client_id='python-lib-test',
        request_topic='Iqrf/DpaRequest',
        response_topic='Iqrf/DpaResponse',
        qos=1,
        keepalive=25
    )
transport = MqttTransport(params=params, callback=handler, auto_init=True)

while True:
    time.sleep(5)
    print('===========')
    print_formatted('Request sent at:', datetime.now())
    request = PulseRequest(nadr=3)
    transport.send(request)
    print_formatted('Request message ID:', request.get_msg_id())
