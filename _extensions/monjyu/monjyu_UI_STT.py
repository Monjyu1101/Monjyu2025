#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

import sys
import os
import time
import datetime
import codecs
import glob

import json

import queue
import threading

import requests

from playsound3 import playsound



# インターフェース

qPath_stt    = 'temp/s6_4stt_txt/'

# 定数の定義
CORE_PORT = '8000'
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30



class _stt_woker:

    def __init__(self, runMode='assistant' ):
        self.runMode   = runMode

        # ディレクトリ作成
        if (not os.path.isdir(qPath_stt)):
            os.makedirs(qPath_stt)

        # Monjyu
        self.monjyu = _monjyu_class(runMode=runMode, )

        # Worker デーモン起動
        self.worker_proc = threading.Thread(target=self.proc_worker, args=(), daemon=True, )
        self.worker_proc.start()

    # Worker デーモン
    def proc_worker(self):
        while True:
            hit = self.stt_proc()
            if hit == True:
                time.sleep(0.25)
            else:
                time.sleep(0.50)
        return True

    def stt_proc(self, remove=True, ):
        res        = False
        about_flag = False
        
        path = qPath_stt
        path_files = glob.glob(path + '*.txt')
        path_files.sort()
        if (len(path_files) > 0):

            for f in path_files:

                try:

                    proc_file = f.replace('\\', '/')

                    if (proc_file[-4:].lower() == '.txt' and proc_file[-8:].lower() != '.wrk.txt'):
                        f1 = proc_file
                        f2 = proc_file[:-4] + '.wrk.txt'
                        try:
                            os.rename(f1, f2)
                            proc_file = f2
                        except Exception as e:
                            pass

                    if (proc_file[-8:].lower() == '.wrk.txt'):
                        f1 = proc_file
                        f2 = proc_file[:-8] + proc_file[-4:]
                        try:
                            os.rename(f1, f2)
                            proc_file = f2
                        except Exception as e:
                            pass

                        if (proc_file[-9:].lower() != '_sjis.txt'):
                            txts, text = self.txtsRead(proc_file, encoding='utf-8', exclusive=False, )
                        else:
                            txts, text = self.txtsRead(proc_file, encoding='shift_jis', exclusive=False, )

                        if (remove == True):
                            self.remove(proc_file)

                        if (text != '') and (text != '!'):
                            res = True

                            # AI要求送信
                            user_id = 'admin'
                            sysText = 'あなたは美しい日本語を話す賢いアシスタントです。'
                            reqText = ''
                            inpText = text
                            res_port = self.monjyu.request(req_mode='voice', user_id=user_id, sysText=sysText, reqText=reqText, inpText=inpText, )

                            # フィードバック
                            if (res_port is None):
                                # ng
                                self.play(outFile='_sounds/_sound_ng.mp3')

                except Exception as e:
                    print('Monjyu_STT :', e)

        return res

    def txtsRead(self, filename, encoding='utf-8', exclusive=False, ):
        if (not os.path.exists(filename)):
            return False, ''

        encoding2 = encoding
        if (encoding2 == 'utf-8'):
            encoding2 =  'utf-8-sig'

        if (exclusive == False):
            try:
                txts = []
                txt  = ''
                r = codecs.open(filename, 'r', encoding2)
                for t in r:
                    t = t.replace('\n', '')
                    t = t.replace('\r', '')
                    txt  = (txt + ' ' + str(t)).strip()
                    txts.append(t)
                r.close
                r = None
                return txts, txt
            except Exception as e:
                r = None
                return False, ''
        else:
            f2 = filename[:-4] + '.txtsRead.tmp'
            res = self.remove(f2, )
            if (res == False):
                return False, ''
            else:
                try:
                    os.rename(filename, f2)
                    txts = []
                    txt  = ''
                    r = codecs.open(f2, 'r', encoding2)
                    for t in r:
                        t = t.replace('\n', '')
                        t = t.replace('\r', '')
                        txt = (txt + ' ' + str(t)).strip()
                        txts.append(t)
                    r.close
                    r = None
                    self.remove(f2, )
                    return txts, txt
                except Exception as e:
                    r = None
                    return False, ''

    def remove(self, filename, maxWait=1, ):
        if (not os.path.exists(filename)):
            return True

        if (maxWait == 0):
            try:
                os.remove(filename) 
                return True
            except Exception as e:
                return False
        else:
            chktime = time.time()
            while (os.path.exists(filename)) and ((time.time() - chktime) <= maxWait):
                try:
                    os.remove(filename)
                    return True
                except Exception as e:
                    pass
                time.sleep(0.10)

            if (not os.path.exists(filename)):
                return True
            else:
                return False

    def play(self, outFile='temp/_work/sound.mp3', ):
        if (outFile is None) or (outFile == ''):
            return False
        if (not os.path.isfile(outFile)):
            return False
        try:
            # 再生
            playsound(sound=outFile, block=True, )
            return True
        except Exception as e:
            print(e)
        return False



class _monjyu_class:
    def __init__(self, runMode='assistant' ):
        self.runMode   = runMode

        # ポート設定等
        self.core_port1 = str(int(CORE_PORT) + 1)
        self.local_endpoint1 = f'http://localhost:{ self.core_port1 }'

    def request(self, req_mode='chat', user_id='admin', sysText='', reqText='', inpText='', ):
        res_port = None

        # ファイル添付
        file_names = []
        try:
            response = requests.get(
                self.local_endpoint1 + '/get_input_list',
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                results = response.json()
                for f in results['files']:
                    if (f['checked'] == True):
                        file_names.append(f['file_name'])
            else:
                print('Monjyu_STT :', f"Error response ({ self.core_port1 }/get_input_list) : {response.status_code} - {response.text}")
        except Exception as e:
            print('Monjyu_STT :', f"Error communicating ({ self.core_port1 }/get_input_list) : {e}")

        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint1 + '/post_req',
                json={'user_id': user_id, 'from_port': CORE_PORT, 'to_port': CORE_PORT,
                    'req_mode': req_mode,
                    'system_text': sysText, 'request_text': reqText, 'input_text': inpText,
                    'file_names': file_names, 'result_savepath': '', 'result_schema': '', },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                res_port = str(response.json()['port'])
            else:
                print('Monjyu_STT :', f"Error response ({ self.core_port1 }/post_request) : {response.status_code} - {response.text}")
        except Exception as e:
            print('Monjyu_STT :', f"Error communicating ({ self.core_port1 }/post_request) : {e}")
        return res_port



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "monjyu_UI_STT"
        self.func_ver  = "v0.20240813"
        self.func_auth = "Y07oRYdcYW7xoJZwICB+cv/LAcADnOy1NeTP6uaIOLM="
        self.function  = {
            "name": self.func_name,
            "description": "拡張ＵＩ_音声認識結果を処理する。",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                },
                "required": ["runMode"]
            }
        }

        # 初期設定
        self.runMode    = 'assistant'
        self.sub_worker = _stt_woker(runMode=self.runMode, )
        self.func_reset()

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print('Monjyu_STT :', json_kwargs)

        # 引数
        runMode = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode = args_dic.get('runMode')

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # 処理

        # 戻り
        dic = {}
        dic['result'] = "ok"
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('Monjyu_STT :', '  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ "runMode" : "assistant" }'))

    time.sleep(60)


