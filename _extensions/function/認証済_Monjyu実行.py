#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'func_monjyu'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)

import time

import json
import requests



# 定数の定義
CORE_PORT = '8000'
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30



class _monjyu_class:
    def __init__(self, runMode='chat' ):
        self.runMode   = runMode

        # ポート設定等
        self.local_endpoint0 = f'http://localhost:{ int(CORE_PORT) + 0 }'

    def get_ready(self):
        # ファイル添付
        try:
            response = requests.get(
                self.local_endpoint0 + '/get_ready_count',
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                results = response.json()
                isReady = results.get('ready_count',0)
                isBusy = results.get('busy_count',0)
                if isReady > 0:
                    return True
                else:
                    return False
            else:
                logger.error(f"Monjyu_Request : Error response (/get_input_list) : {response.status_code}")
        except Exception as e:
            logger.error(f"Monjyu_Request : Error communicating (/get_input_list) : {e}")
        return False

    def request(self, req_mode='chat', user_id='admin', sysText='', reqText='', inpText='', ):
        res_port = ''

        # ファイル添付
        file_names = []
        try:
            response = requests.get(
                self.local_endpoint0 + '/get_input_list',
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                results = response.json()
                for f in results['files']:
                    #fx = f.split(' ')
                    #if (fx[3] == 'checked'):
                    #    file_names.append(fx[0])
                    file_name = f.get('file_name','')
                    checked   = f.get('checked','')
                    if checked == 'yes':
                        file_names.append(file_name)
            else:
                logger.error(f"Monjyu_Request : Error response (/get_input_list) : {response.status_code}")
        except Exception as e:
            logger.error(f"Monjyu_Request : Error communicating (/get_input_list) : {e}")

        # AI要求送信
        try:
            res_port = ''
            if (req_mode in ['clip', 'voice']):
                res_port = CORE_PORT
            response = requests.post(
                self.local_endpoint0 + '/post_req',
                json={'user_id': user_id, 'from_port': CORE_PORT, 'to_port': res_port,
                    'req_mode': req_mode,
                    'system_text': sysText, 'request_text': reqText, 'input_text': inpText,
                    'file_names': file_names, 'result_savepath': '', 'result_schema': '', },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                if (res_port == ''):
                    res_port = str(response.json()['port'])
            else:
                logger.error(f"Monjyu_Request : Error response (/post_req) : {response.status_code}")
        except Exception as e:
            logger.error(f"Monjyu_Request : Error communicating (/post_req) : {e}")

        # AI結果受信
        res_text = ''
        if res_port != '':
            try:

                # AIメンバー応答待機
                timeout = time.time() + 120
                while time.time() < timeout:

                    response = requests.get(
                        self.local_endpoint0 + '/get_sessions_port?user_id=' + user_id + '&from_port=' + CORE_PORT,
                        timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
                    )
                    if response.status_code == 200:
                        results = response.json()
                        key_val = f"{ user_id }:{ CORE_PORT }:{ res_port }"
                        if key_val in results:
                            if results[key_val]["out_time"] is not None:
                                res_text = str(results[key_val]["out_data"])
                                break
                        else:
                            time.sleep(1.00)
                    else:
                        logger.error(f"Monjyu_Request : Error response (/get_sessions_port) : {response.status_code} - {response.text}")

            except Exception as e:
                logger.error(f"'Monjyu_Request : Error communicating (/get_sessions_port) : {e}")

        return res_text



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "execute_monjyu_request"
        self.func_ver  = "v0.20241029"
        self.func_auth = "n9UbwFiHQDP7UfVFM01VFS6M/2A7j1VoYhPAse082fa4FwZbpYP3S+LcetDyaAi2"
        self.function  = {
            "name": self.func_name,
            "description": \
"""
この機能は、LiveAPI(RealTimeAPI)セッションから呼び出して利用する。
この機能から、画像生成などの機能が実行可能な外部AI 文殊/Monjyu(もんじゅ) が実行される。
社内システム(WEB) 出退勤,日報,掲示板 へのログイン,出勤,退勤の操作は、'operation_internal_web_systems'機能の利用を明示して呼び出す必要がある。
この機能の呼出し時のrunModeには、以下の値を設定してください。
runMode='clip'  : クリップボード操作からの呼出し要求。
runMode='voice' : LiveAPI(RealtimeAPI)や音声入力からの呼出し要求。
runMode='chat'  : それ以外の通常の呼出し要求。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード chat,clip,voice 例) chat"
                    },
                    "userId": {
                        "type": "string",
                        "description": "ユーザーID 例) admin"
                    },
                    "reqText": {
                        "type": "string",
                        "description": "要求文字列 例) 添付画像を解説して？"
                    },
                },
                "required": ["runMode", "userId", "reqText"]
            }
        }

        # 初期設定
        self.runMode = 'chat'
        self.monjyu  = _monjyu_class()
        
    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print('Monjyu_Request :', json_kwargs)

        # 引数
        runMode = None
        userId  = None
        reqText = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode  = args_dic.get('runMode')
            userId   = args_dic.get('userId')
            reqText  = args_dic.get('reqText')

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # 処理
        req_mode = self.runMode
        if (req_mode not in ['clip', 'voice']):
            req_mode = 'chat'
        sysText  = 'あなたは美しい日本語を話す賢いアシスタントです。'
        reqText  = reqText
        inpText  = ''
        resText  = self.monjyu.request(req_mode=req_mode, user_id=userId, sysText=sysText, reqText=reqText, inpText=inpText,)

        # 戻り
        dic = {}
        if (resText != ''):
            dic['result'] = "ok"
            dic['result_text'] = resText
        else:
            dic['result'] = "ng"
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('Monjyu_Request :', '  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    json_dic = {}
    json_dic['runMode'] = "chat"
    json_dic['userId']  = "admin"
    json_dic['reqText'] = "おはようございます"
    json_kwargs = json.dumps(json_dic, ensure_ascii=False, )
    print(ext.func_proc(json_kwargs))

    time.sleep(60)


