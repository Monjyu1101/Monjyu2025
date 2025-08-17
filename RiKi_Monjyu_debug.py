# RiKi_Monjyu_debug.py

import sys
import os
import time
import datetime
import codecs
import glob
import shutil

import requests

CORE_PORT1 = 8001

# 定数の定義
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30


def post_request(req_mode='chat'):
    try:
        response = requests.post(
            f'http://localhost:{CORE_PORT1}/post_req',
            json={'user_id': 'debug', 'from_port': str(CORE_PORT1), 'to_port': '',
                    'req_mode': req_mode,
                    'system_text': '', 'request_text': 'debug,', 'input_text': '',
                    'file_names': [], 'result_savepath': '', 'result_schema': '' },
            timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
        )
        if response.status_code == 200:
            print(str(response.json()['port']))
            #print(f"Debug request successful: {result}")
        else:
            print(f"Debug request failed: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Error sending debug request: {e}")
    except Exception as e:
        print(f"Unexpected error in debug request: {e}")


if __name__ == '__main__':

    #time.sleep(60 + NUM_SUBAIS)
    while True:
        post_request(req_mode='parallel')
        time.sleep(3)
        post_request(req_mode='chat')
        time.sleep(3)
        post_request(req_mode='chat')
        time.sleep(3)
        post_request(req_mode='chat')
        time.sleep(3)
        post_request(req_mode='chat')
        time.sleep(3)


