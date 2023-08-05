import json
import requests


def get_config_data(config_host, config_port):
    url = 'http://{}:{}/api/data'.format(config_host, config_port)
    body = {
        'action': 'get_config_data',
        'args': {}
    }

    try:
        res = requests.post(url, json=body)
        res = json.loads(res.text, encoding='utf-8')
        return res['value'] if res['status'] == 'ok' else {}
    except:
        return {}
