import requests
import json
from http import HTTPStatus
from pipeline.schema.inputs import generatedProjectNameInputs
from token_generator import tokenGenerator
t = tokenGenerator()
googlejwtToken = t.generateToken('STG_Conf')
x_token = ''
gaia_api_token = ''
global_headers = {
    'x-token': f'{x_token}',
    # 'GAIA-AI-TOKEN': f'{gaia_api_token}',
    'Authorization': 'Bearer ' + googlejwtToken
    # 'Authorization': f'Bearer {gaia_api_token}'
}
base_url = 'http://localhost:8080/'


def post_stream(endPoint, data, callback):
    session = requests.Session()
    headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
    url = base_url + endPoint
    with session.post(url, stream=True, json=data, verify=False, headers=headers) as r:
        print('r', r.status_code)
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=128):
            if callback and hasattr(callback, '__call__'):
                callback(chunk.decode('utf-8'))
    return 'success'

def get(endPoint, data):
    headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
    url = base_url + endPoint
    response = requests.get(url, params=data, headers=headers)
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        data = HTTPStatus.INTERNAL_SERVER_ERROR.description
    else:
        try:
            data = json.loads(response.content)
        except Exception as ex:
            data = response.content
    return data

if __name__ == '__main__':
    # test - parse
    data = {}
    d = generatedProjectNameInputs(**data)

    results = get('livenessprobe', {})
    print('results', results)


    def callback(res):
        print('res', res)


    results = post_stream('chat', data, callback=callback)
    print('results', results)
