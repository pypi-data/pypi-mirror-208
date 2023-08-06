from iqrfpy.enums.message_types import MessageType


def generate_json_response(message_type: MessageType, response_data: dict):
    json = {
        'mType': message_type.value,
        'data': {
            'msgId': response_data['msgid'],
            'rsp': {
                'nAdr': response_data['nadr'],
                'hwpId': response_data['hwpid'],
                'rCode': response_data['rcode'],
                'dpaVal': response_data['dpa_value']
            },
            'insId': 'iqrfgd2-1',
            'status': response_data['rcode']
        }
    }
    if response_data['rcode'] == 0 and 'result' in response_data:
        json['data']['rsp']['result'] = response_data['result']
    return json
