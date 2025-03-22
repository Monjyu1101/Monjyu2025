#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

import json

import sys
import os
import time
import datetime
import codecs
import glob

from playsound3 import playsound
import openai
import speech_recognition as sr

import numpy as np
import cv2

if (os.name == 'nt'):
    import ctypes
    from ctypes import wintypes
    #import win32con

import threading

import socket
qHOSTNAME = socket.gethostname().lower()

use_openai_list   = ['kondou-latitude', 'kondou-main11', 'kondou-sub64', 'repair-surface7', ]



# インターフェース

qPath_work    = 'temp/_work/'

whisper_model = 'whisper-1'



class sub_class:

    def __init__(self, runMode='assistant', ):
        self.runMode      = runMode

    def init(self, ):
        return True

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

    def findWindow(self, winTitle='Display', ):
        if (os.name != 'nt'):
            return False
        parent_handle = ctypes.windll.user32.FindWindowW(0, winTitle)
        if (parent_handle == 0):
            return False
        else:
            return parent_handle

    def setForegroundWindow(self, winTitle='Display', ):
        if (os.name != 'nt'):
            return False
        parent_handle = self.findWindow(winTitle)
        if (parent_handle == False):
            return False
        else:
            ctypes.windll.user32.SetForegroundWindow(parent_handle)
            return True



class stt_class:

    def __init__(self, runMode='assistant', ):
        self.runMode  = runMode
        self.sub_proc = sub_class(runMode=runMode, )

        # ディレクトリ作成
        if (not os.path.isdir(qPath_work)):
            os.makedirs(qPath_work)

        # openai チェック
        self.openai_enable = False
        try:
            # APIキーを取得
            self.openai_organization = os.environ.get('OPENAI_ORGANIZATION', '< ? >')
            self.openai_key_id = os.environ.get('OPENAI_API_KEY', '< ? >')
            if (self.openai_organization == '') \
            or (self.openai_organization[:1] == '<') \
            or (self.openai_key_id == '') \
            or (self.openai_key_id[:1] == '<'):
                raise ValueError("Please set your openai organization and key !")

            # APIキーを設定
            openai.organization = self.openai_organization
            openai.api_key      = self.openai_key_id
            self.client = openai.OpenAI(
                organization=self.openai_organization,
                api_key=self.openai_key_id,
            )

            self.openai_enable = True
        except:
            pass

    def init(self, ):
        self.device_id  = 0
        self.recognizer = sr.Recognizer()
        self.adjust()

        return True

    def adjust(self, ):
        try:
            with sr.Microphone(device_index=self.device_id) as source:
                self.recognizer.energy_threshold = 1000     # 300-4000 検出音量
                self.recognizer.adjust_for_ambient_noise(source, duration=1, )  # ノイズ補正 1秒
                self.recognizer.pause_threshold = 2         # 開始後の無音停止秒数
        except Exception as e:
            print(e)
            return False
        return True

    def recognize(self, api='auto', language='auto', workFile='temp/_work/tts.mp3', ):
        text = ''

        # ガイド音声(開始)
        self.sub_proc.play(outFile='_sounds/_sound_ready.mp3')

        # ガイド表示
        winTitle = 'speechGuide'
        try:
            cv_img = cv2.imread('_icons/_rec.png')
            cv2.imshow(winTitle, cv_img)
            cv2.waitKey(1)
            self.sub_proc.setForegroundWindow(winTitle=winTitle, )
        except:
            pass

        # 音声入力
        print('音声入力：待機中です。どうぞ！')
        audio = None
        try:
            with sr.Microphone(device_index=self.device_id) as source:
                self.recognizer.operation_timeout = 30
                audio = self.recognizer.listen(source, timeout=15)
        except Exception as e:
            print(e)
            audio = None

        # ガイド消去
        try:
            cv2.destroyWindow(winTitle)
            cv2.waitKey(1)
        except:
            pass

        if (audio is None):
            print('音声入力：解析不能 !')
        else:
            try:

                # 保存
                with open(workFile, "wb") as f:
                    f.write(audio.get_wav_data())

                # openai
                if (text == ''):
                    if  (api == 'openai') \
                    and (self.openai_enable == True):
                        print('音声入力：解析中(openai)...')
                        try:
                            audio_file= open(workFile, 'rb')
                            transcription = self.client.audio.transcriptions.create(
                                model=whisper_model, file=audio_file, )
                            text = transcription.text
                        except Exception as e:
                            print(e)
                            text = ''

                # google
                if (text == ''):
                        print('音声入力：解析中(google)...')
                        try:
                            if (language == 'auto'):
                                self.recognizer.operation_timeout = 30
                                text = self.recognizer.recognize_google(audio, )
                            else:
                                self.recognizer.operation_timeout = 30
                                text = self.recognizer.recognize_google(audio, language=language, )
                        except Exception as e:
                            print(e)
                            text = ''

            except Exception as e:
                print(e)
                text = ''

        # ガイド音声(結果)
        if (text is None) or (text == ''):
            print('認識結果： !')
            # ng
            self.sub_proc.play(outFile='_sounds/_sound_ng.mp3')
        else:
            print('認識結果："' + text + '"')
            # ok
            self.sub_proc.play(outFile='_sounds/_sound_ok.mp3')

        # 環境音　調整
        thread = threading.Thread(target=self.adjust)
        thread.start()
        return text



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "execute_speech_to_text"
        self.func_ver  = "v0.20240518"
        self.func_auth = "w8LJgHCbPVLVZ6bmWzci0cUsMMyBIg3kdRLCNkMBq0VrTYdBaWf/xDhX7itkSzuo"
        self.function  = {
            "name": self.func_name,
            "description": \
"""
機密保持の必要性から、この機能は指示があった場合のみ実行する。
この機能で、マイクから音声入力が出来る。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "api": {
                        "type": "string",
                        "description": "認識APIの指定 auto,google,openai, 例）auto"
                    },
                    "language": {
                        "type": "string",
                        "description": "言語の指定 auto,ja-JP,en-US, 例）auto"
                    },
                },
                "required": ["runMode"]
            }
        }

        # 初期設定
        self.runMode  = 'assistant'
        self.stt_proc = stt_class(runMode=self.runMode, )
        self.func_reset()

        self.file_seq = 0

    def func_reset(self, ):
        self.stt_proc.init()
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode  = None
        api      = None
        language = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode  = args_dic.get('runMode')
            api      = args_dic.get('api')
            language = args_dic.get('language')

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # 指定
        if (api is None) or (api == 'auto'):
            api = 'auto'
            if(qHOSTNAME in use_openai_list):
                api = 'openai'

        if (language is None):
            language = 'auto'

        # カウンタ
        self.file_seq += 1
        if (self.file_seq > 9999):
            self.file_seq = 1

        # ファイル名
        nowTime  = datetime.datetime.now()
        stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
        seq      = '{:04}'.format(self.file_seq)
        filename = qPath_work + stamp + '.' + seq + '.audio.wav'

        # 音声入力
        text = self.stt_proc.recognize(api=api, language=language, workFile=filename, )

        # 戻り
        dic = {}
        if (text is not None) and (text != ''):
            dic['result'] = 'ok'
            dic['recognition_text'] = str(text)
        else:
            dic['result'] = 'ng'
            dic['recognition_text'] = ''

        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ ' \
                      + '"api" : "auto",' \
                      + '"language" : "auto"' \
                      + ' }'))
