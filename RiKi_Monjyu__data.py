#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'data'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)


import sys
import os
import time
import datetime
import codecs
import glob
import shutil

import requests

import random
import threading

import socket
qHOSTNAME = socket.gethostname().lower()

# 一時ファイル保存用パス
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'

# 定数の定義
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30



class _data_class:
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        self.runMode = runMode

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug('init')

        # 各種設定の初期化
        self.main      = main
        self.conf      = conf

        # 設定
        self.core_port = core_port
        self.sub_base  = sub_base
        self.num_subais = int(num_subais)
        self.local_endpoint = f'http://localhost:{ self.core_port }'

        # サブAIの情報
        self.subai_ports = [str(port) for port in range(int(self.sub_base) + 1, int(self.sub_base) + 1 + self.num_subais)]
        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.subai_info = {port: {'status': 'NONE', 'nick_name': None, 'upd_time':now_time} for port in self.subai_ports}
        self.subai_reset = {port: {'reset': 'yes,'} for port in self.subai_ports}

        # 結果の保存
        self.subai_sessions_all     = {}
        self.subai_input_log_key    = 0
        self.subai_input_log_all    = {}
        self.subai_output_log_key   = 0
        self.subai_output_log_all   = {}
        self.subai_debug_log_key    = 0
        self.subai_debug_log_all    = {}
        self.subai_histories_key    = 0
        self.subai_histories_all    = {}

        # sandbox表示更新
        self.sandbox_update = True
        self.sandbox_file   = None

        # 設定の保存
        self.mode_setting   = {}
        self.engine_models  = {}
        self.engine_models['chatgpt']    = {}
        self.engine_models['respo']      = {}
        self.engine_models['gemini']     = {}
        self.engine_models['freeai']     = {}
        self.engine_models['claude']     = {}
        self.engine_models['openrt']     = {}
        self.engine_models['perplexity'] = {}
        self.engine_models['grok']       = {}
        self.engine_models['groq']       = {}
        self.engine_models['ollama']     = {}
        self.engine_setting = {}
        self.addins_setting = {}
        self.live_models = {}
        self.live_models['freeai'] = {}
        self.live_models['openai'] = {}
        self.live_voices = {}
        self.live_voices['freeai'] = {}
        self.live_voices['openai'] = {}
        self.live_setting = {}
        self.live_setting['freeai'] = {}
        self.live_setting['openai'] = {}
        self._reset()

        # スレッドロック
        self.thread_lock = threading.Lock()

        # サブAI監視 開始
        self.start_subais()

    def _reset(self):

        # sandbox表示更新
        self.sandbox_update = True
        self.sandbox_file   = None

        # 各動作モードの設定
        self.mode_setting['chat'] = {
            "req_engine": "",
            "req_functions": "", "req_reset": "",
            "max_retry": "0", "max_ai_count": "0",
            "before_proc": "none,", "before_engine": "",
            "after_proc": "none,", "after_engine": "",
            "check_proc": "none,", "check_engine": ""
        }

        self.mode_setting['vision'] = self.mode_setting['chat']
        self.mode_setting['websearch'] = self.mode_setting['chat']

        self.mode_setting['serial'] = {
            "req_engine": "", 
            "req_functions": "", "req_reset": "",
            "max_retry": "", "max_ai_count": "",
            "before_proc": "", "before_engine": "",
            "after_proc": "", "after_engine": "",
            "check_proc": "", "check_engine": ""
        }

        self.mode_setting['parallel'] = self.mode_setting['serial']

        self.mode_setting['session'] = self.mode_setting['chat']
        self.mode_setting['clip'] = self.mode_setting['chat']
        self.mode_setting['voice'] = self.mode_setting['chat']

        # engineの設定
        self.engine_setting['chatgpt'] = {
            "a_nick_name": "",
            "b_nick_name": "",
            "v_nick_name": "",
            "x_nick_name": "",
            "max_wait_sec": "",
            "a_model": "",
            "a_use_tools": "",
            "b_model": "",
            "b_use_tools": "",
            "v_model": "",
            "v_use_tools": "",
            "x_model": "",
            "x_use_tools": ""
        }
        self.engine_setting['respo']  = self.engine_setting['chatgpt']
        self.engine_setting['gemini'] = self.engine_setting['chatgpt']
        self.engine_setting['freeai'] = self.engine_setting['chatgpt']
        self.engine_setting['claude'] = self.engine_setting['chatgpt']
        self.engine_setting['openrt'] = self.engine_setting['chatgpt']
        self.engine_setting['perplexity'] = self.engine_setting['chatgpt']
        self.engine_setting['grok'] = self.engine_setting['chatgpt']
        self.engine_setting['groq'] = self.engine_setting['chatgpt']
        self.engine_setting['ollama'] = self.engine_setting['chatgpt']

        # addinsの設定
        self.addins_setting = {
            "result_text_save": "", 
            "speech_tts_engine": "", 
            "speech_stt_engine": "",
            "text_clip_input": "",
            "text_url_execute": "",
            "text_pdf_execute": "",
            "image_ocr_execute": "",
            "image_yolo_execute": ""
        }

        # liveの設定 freeai
        #self.live_models[ 'freeai'] = {}
        #self.live_voices[ 'freeai'] = {}
        self.live_setting['freeai'] = { "live_model": "",
                                        "live_voice": "", 
                                        "shot_interval_sec":"",
                                        "clip_interval_sec":"", }
        # liveの設定 openai
        #self.live_models[ 'openai'] = {}
        #self.live_voices[ 'openai'] = {}
        self.live_setting['openai'] = self.live_setting['freeai']

    def update_subai_status(self, port: str):
        """
        サブAIのステータスを定期的に更新する。
        """
        while True:
            sleep_sec = random.uniform(self.num_subais, self.num_subais * 2)
            time.sleep(sleep_sec)
            if  (self.main is None) \
            or ((self.main is not None) and (self.main.main_all_ready == True)):

                try:
                    endpoint = self.local_endpoint.replace( f':{ self.core_port }', f':{ port }' )
                    response = requests.get(endpoint + '/get_info', timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT))
                    if response.status_code == 200:
                        new_status = response.json()['status']
                        nick_name = response.json()['nick_name']
                        full_name = response.json()['full_name']
                        info_text = response.json()['info_text']
                        with self.thread_lock:
                            old_status = self.subai_info[port].get('status')
                            upd_time   = self.subai_info[port].get('upd_time')
                            if (new_status != old_status):
                                upd_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                            self.subai_info[port] = {
                                'status': new_status, 
                                'nick_name': nick_name, 
                                'full_name': full_name, 
                                'info_text': info_text, 
                                'upd_time': upd_time, }
                    else:
                        logger.error(f"Error response ({ port }/get_info) : {response.status_code}")
                        with self.thread_lock:
                            self.subai_info[port]['status'] = 'NONE'
                            self.subai_info[port]['upd_time'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                except Exception as e:
                    logger.error(f"Error communicating ({ port }/get_info) : {e}")
                    with self.thread_lock:
                        self.subai_info[port]['status'] = 'NONE'
                        self.subai_info[port]['upd_time'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    def start_subais(self):
        """
        サブAIのステータス更新スレッドを開始する。
        """
        for port in self.subai_ports:
            try:
                thread = threading.Thread(target=self.update_subai_status, args=(port,), daemon=True, )
                thread.start()
            except Exception as e:
                logger.error(f"Failed to start subai on port {port}: {e}")

    def reset(self, user_id: str, ):
        # 設定リセット
        self._reset()
        # サブAIリセット
        with self.thread_lock:
            self.subai_reset = {port: {'reset': 'yes,'} for port in self.subai_ports}
        # サブAI CANCEL 処理
        self.cancel(user_id=user_id, )
        return True

    def cancel(self, user_id: str, ):
        # サブAI CANCEL 処理
        for port in self.subai_ports:
            if self.subai_info[port]['status'] in ['SERIAL', 'PARALLEL', 'CHAT', 'SESSION']:
                thread = threading.Thread(target=self._send_cancel, args=(user_id, port,), daemon=True, )
                thread.start()
        return True

    def _send_cancel(self, user_id: str, to_port: str):
        """
        サブAIへのキャンセル送信処理。
        """
        try:
            endpoint = self.local_endpoint.replace( f':{ self.core_port }', f':{ to_port }' )
            response = requests.post(
                endpoint + '/post_cancel',
                json={'user_id': user_id, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                with self.thread_lock:
                    self.subai_info[to_port]['status'] = 'CANCEL'
                return True
            else:
                with self.thread_lock:
                    self.subai_info[to_port]['status'] = 'ERROR'
                return False
        except Exception as e:
            logger.error(f"Error communicating ({ to_port }/post_cancel) : {e}")
            with self.thread_lock:
                self.subai_info[to_port]['status'] = 'NONE'
        return False



if __name__ == '__main__':
    core_port = '8000'
    sub_base  = '8100'
    numSubAIs = '48'

    data = _data_class( runMode='debug', qLog_fn='', 
                        core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)


