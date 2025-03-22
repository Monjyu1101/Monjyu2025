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

from playsound3 import playsound

import keyboard



# インターフェース

qPath_play = 'temp/s6_7play/'

# 規定値
OPERATION_WAIT_SEC = 60



class _play_woker:

    def __init__(self, runMode='assistant', ):
        self.runMode      = runMode

        # ディレクトリ作成
        if (not os.path.isdir(qPath_play)):
            os.makedirs(qPath_play)

        # キーボード監視 開始
        self.last_key_time = 0
        self.kb_handler_id = None
        self.start_kb_listener()

        # Worker デーモン起動
        self.worker_proc = threading.Thread(target=self.proc_worker, args=(), daemon=True, )
        self.worker_proc.start()

    # キーボード監視 開始
    def start_kb_listener(self, runMode='assistant',):
        # イベントハンドラの登録
        self.last_key_time = 0
        self.kb_handler_id = keyboard.hook(self._keyboard_event_handler)
    # イベントハンドラ
    def _keyboard_event_handler(self, event):
        self.last_key_time = time.time()
    # キーボード監視 終了
    def stop_kb_listener(self):
        try:
            if (self.kb_handler_id is not None):
                keyboard.unhook(self.kb_handler_id)
                self.kb_handler_id = None
        except Exception as e:
            print(e)

    # Worker デーモン
    def proc_worker(self):
        while True:
            hit = False
            try:
                hit = self.play_check()
            except:
                pass
            if hit == True:
                time.sleep(0.25)
            else:
                time.sleep(0.50)

        return True

    def play_check(self, remove=True, ):
        res        = False
        about_flag = False
        
        path = qPath_play
        path_files = glob.glob(path + '*.*')
        path_files.sort()
        if (len(path_files) > 0):

            for f in path_files:

                try:

                    proc_file = f.replace('\\', '/')

                    if (proc_file[-4:].lower() == '.wav' and proc_file[-8:].lower() != '.wrk.wav') \
                    or (proc_file[-4:].lower() == '.mp3' and proc_file[-8:].lower() != '.wrk.mp3'):
                        f1 = proc_file
                        f2 = proc_file[:-4] + '.wrk' + proc_file[-4:]
                        try:
                            os.rename(f1, f2)
                            proc_file = f2
                        except Exception as e:
                            pass

                    if (proc_file[-8:].lower() == '.wrk.wav') \
                    or (proc_file[-8:].lower() == '.wrk.mp3'):

                        if  (time.time() > (self.last_key_time + OPERATION_WAIT_SEC)) \
                        and (about_flag == False):

                            # play
                            self.play(outFile=proc_file)

                        else:
                            about_flag = True

                        # remove
                        self.remove(filename=proc_file)

                except Exception as e:
                    print(e)

        return res

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



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "extension_UI_play"
        self.func_ver  = "v0.20240910"
        self.func_auth = "nYUEbRRi4AA5hiHmqWNvMH87/Xlxo3vqNgKwsACQPhI="
        self.function  = {
            "name": self.func_name,
            "description": "拡張ＵＩ_サウンド再生する。",
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
        self.sub_worker = _play_woker(runMode=self.runMode, )
        self.func_reset()

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

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
        #print('  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ "runMode" : "assistant" }'))

    time.sleep(60)


