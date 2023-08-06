import time
from datetime import datetime
from iqrfpy.exceptions import DpaRequestTimeoutError, JsonRequestTimeoutError
from iqrfpy.messages import *
from iqrfpy.iresponse import IResponse
from iqrfpy.transports.mqtt_transport import MqttTransportParams, MqttTransport


def print_formatted(text, data):
    print(f'{text:30s} {data}')


def send_receive(request: IRequest, timeout: int) -> None:
    print('===========')
    print_formatted('Request sent at:', datetime.now())
    try:
        response = transport.send_and_receive(request=request, timeout=timeout)
        response_handler(response)
    except (DpaRequestTimeoutError, JsonRequestTimeoutError) as e:
        print_formatted('Error:', str(e))


def response_handler(response: IResponse) -> None:
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
transport = MqttTransport(params=params, auto_init=True)

time.sleep(5)

send_receive(LedrPulseReq(nadr=0, msgid='pulseTest'), timeout=2)

send_receive(OsReadReq(nadr=0, msgid='osTest1'), timeout=1)


print('===========')
print_formatted('Request sent at:', datetime.now())
transport.send(OsReadReq(nadr=0, msgid='osTest2'))
rsp = transport.receive(timeout=1)
response_handler(rsp)


try:
    print('===========')
    print_formatted('Request sent at:', datetime.now())
    rsp = transport.send_and_receive(OsReadReq(nadr=2, msgid='osTest3'), timeout=1)
    response_handler(rsp)
except (DpaRequestTimeoutError, JsonRequestTimeoutError) as error:
    print_formatted('Message not received:', str(error))
