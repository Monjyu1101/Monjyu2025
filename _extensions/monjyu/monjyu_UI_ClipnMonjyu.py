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
import shutil

import json
import threading

import requests

import pyperclip
import numpy as np
from PIL import Image, ImageGrab
import hashlib

import pandas as pd

import array

if (os.name == 'nt'):
    import platform
    import ctypes
    from ctypes import wintypes
    import comtypes.client
    UIAutomation = comtypes.client.GetModule("UIAutomationCore.dll")
    IUIAutomation = comtypes.client.CreateObject("{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomation.IUIAutomation)

from playsound3 import playsound



# インターフェース
qPath_input    = 'temp/input/'
READY_BASE_SEC = 60
READY_WAIT_SEC = 300

# 定数の定義
CORE_PORT = '8000'
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30

# 指令文字列
HEADER_LIST = ["openai", "riki", "assistant", "vision", "claude", "gemini", "perplexity", "pplx", "openrt", "ollama", "local", "freeai", "free", ]
INNER_LIST  = ["???", "？？？", "!!!", "！！！", ]



class _clip_woker:

    def __init__(self, runMode='assistant', ):
        self.runMode = runMode
        self.user_id = 'admin'

        # ディレクトリ作成
        if (not os.path.isdir(qPath_input)):
            os.makedirs(qPath_input)

        # 変数設定
        self.last_string = "Monjyu READY!"
        self.last_image_hash = None
        self.last_image_list = []
        pyperclip.copy(self.last_string)

        # Monjyu
        self.monjyu = _monjyu_class(runMode=runMode, )

        # clip2memo
        self.clip2memo = _clip_to_memo(runMode=runMode, )

        # スレッドロック
        self.thread_lock = threading.Lock()

        # Worker デーモン起動
        self.worker_proc = threading.Thread(target=self.proc_worker, args=(), daemon=True, )
        self.worker_proc.start()

    # Worker デーモン
    def proc_worker(self):
        startTime = time.time()
        time.sleep(READY_BASE_SEC)
        while True:
            hit = False
            if ((self.monjyu.main is None) and ((time.time() - startTime) > READY_WAIT_SEC)) \
            or ((self.monjyu.main is not None) and (self.monjyu.main.main_all_ready == True)):
                batch_string = None
                batch_image  = None
                batch_list   = None
                with self.thread_lock:
                    
                    # クリップボードの内容を取得
                    clip_string = ''
                    clip_image = None
                    
                    # クリップボードから文字列を取得
                    try:
                        clip_string = pyperclip.paste()
                    except Exception as e:
                        print('Clip&Monjyu :', f"Error in getting string from clipboard: {e}")
                        
                    # クリップボードから画像を取得
                    try:
                        clip_image = ImageGrab.grabclipboard()
                        # # 画像が取得できたか確認
                        # if not isinstance(clip_image, Image.Image):
                        #     clip_image = None
                        #else:
                        #    clip_image = np.array(clip_image)
                    except Exception as e:
                        print('Clip&Monjyu :', f"Error in getting image from clipboard: {e}")
                        
                    # 文字列の変更を確認
                    if (clip_string != ''):
                        if isinstance(clip_string, str) and clip_string != self.last_string:
                            self.last_string = clip_string
                            batch_string = clip_string

                    # 画像の変更を確認
                    if clip_image is not None:
                        # 画像が変更された場合、処理
                        if isinstance(clip_image, Image.Image):
                            image_hash = hashlib.sha256(clip_image.tobytes()).hexdigest()
                            if self.last_image_hash is None or image_hash != self.last_image_hash:  # 変更確認
                                self.last_image_hash = image_hash
                                batch_image = clip_image
                        # リストが変更された場合、処理
                        if isinstance(clip_image, list):
                            if clip_image != self.last_image_list:  # 変更確認
                                self.last_image_list = clip_image
                                batch_list = clip_image

                hit = False
                if (batch_string is not None):
                    hit = True
                    self.string_proc(batch_string)
                if (batch_image is not None):
                    hit = True
                    self.image_proc(batch_image)
                if (batch_list is not None):
                    hit = True
                    self.list_proc(batch_list)

            if hit == True:
                time.sleep(0.25)
            else:
                time.sleep(0.50)

    def to_clip(self, clip_string: str):
        # クリップボードへ
        with self.thread_lock:
            send_text = '\n' + clip_string.rstrip() + '\n'
            self.last_string = send_text
            pyperclip.copy(send_text)
        return True

    def string_proc(self, clip_string):
        clip_string = clip_string.replace('\r', '')
        # 文字列処理スレッド
        #print('Clip&Monjyu :', "Hallo String, " + clip_string)

        input_text = ''

        # ヘッダー文字列？
        clip_model = ''
        if (clip_string.find(',') >= 1):
            clip_model = clip_string[:clip_string.find(',')].lower()
            clip_model = clip_model.strip()
            if (clip_model != ''):
                if (clip_model in HEADER_LIST) \
                or (clip_model in self.monjyu.chat_models.keys()):
                    input_text = clip_string[clip_string.find(',')+1:]
                    input_text = clip_model + ',\n' + input_text.strip()

        # インナー文字列？
        for inner in INNER_LIST:
            if (clip_string.lower().find(inner) >= 0):
                input_text = clip_string.replace(str(inner), '')
                break

        # 特別文字列？
        if (clip_string.strip()[-3:] == '===') or (clip_string.strip()[-3:] == '＝＝＝'):
            input_text  = '以下の式を計算して！' + '\n'
            input_text += "''' \n"
            input_text += clip_string.strip()[:-3] + '\n'
            input_text += "'''"
        elif (clip_string.strip()[-3:].lower() == ',ja') or (clip_string.strip()[-3:].lower() == '，ｊａ'):
            input_text  = '以下の文章を和訳して！' + '\n'
            input_text += "''' \n"
            input_text += clip_string.strip()[:-3] + '\n'
            input_text += "'''"
        elif (clip_string.strip()[-3:].lower() == ',en') or (clip_string.strip()[-3:].lower() == '，ｅｎ'):
            input_text  = '以下の文章を英訳して！' + '\n'
            input_text += "''' \n"
            input_text += clip_string.strip()[:-3] + '\n'
            input_text += "'''"

        # AI処理
        if (input_text != ''):
            print('Clip&Monjyu :', 'detect clipboard request.')

            # accept
            self.play(outFile='_sounds/_sound_accept.mp3')

            # 確認表示
            txt  = '[REQUEST]\n'
            txt += input_text
            self.clip2memo.to_memo(txt=txt, )

            # AI要求送信
            sysText = 'あなたは美しい日本語を話す賢いアシスタントです。'
            reqText = ''
            inpText = input_text
            res_port = self.monjyu.request(req_mode='clip', user_id=self.user_id, sysText=sysText, reqText=reqText, inpText=inpText, )

            # ng
            if (res_port is None):
                self.play(outFile='_sounds/_sound_ng.mp3')
            
            return True

        # パス？
        if (clip_string[:1] in ['"', "'"]):
            try:
                clip_list = []
                file_names = clip_string.splitlines()
                for file_name in file_names:
                    file_name = file_name[1:len(file_name)-1]
                    if (os.path.isfile(file_name)):
                        clip_list.append(file_name)
                if (len(clip_list) > 0):
                    return self.list_proc(clip_list)
            except:
                pass

        # url？
        if (clip_string[:7] == 'http://') or (clip_string[:8] == 'https://'):
            return self.monjyu.post_clip_names(user_id=self.user_id, clip_names=[clip_string], )

        # データ？ → excel
        try:
            pandas_df = pd.read_clipboard()
            y,x = pandas_df.shape
            # 表データならexcel出力
            if (y>2 and x>2):
                #print('Clip&Monjyu :', pandas_df)
                
                # 保管
                nowTime  = datetime.datetime.now()
                #filename = qPath_input + nowTime.strftime('%Y%m%d.%H%M%S') + '.fromclip.json'
                #pandas_df.to_json(filename, force_ascii=False)
                filename = qPath_input + nowTime.strftime('%Y%m%d.%H%M%S') + '.fromclip.xlsx'
                pandas_df.to_excel(filename, sheet_name='Sheet1', index=False, )
                print('Clip&Monjyu :', 'detect clipboard data.')
                clip_names = [filename]
                return self.monjyu.post_clip_names(user_id=self.user_id, clip_names=clip_names, )

        except:
            pass

        #return False
        return self.monjyu.post_clip_text(user_id=self.user_id, clip_text=clip_string, )

    def image_proc(self, clip_image):
        # 画像処理スレッド
        #print('Clip&Monjyu :', "Hallo Image,")

        # イメージ保管
        try:
            nowTime  = datetime.datetime.now()
            filename = qPath_input + nowTime.strftime('%Y%m%d.%H%M%S') + '.fromclip.png'
            clip_image.convert('RGB').save(filename)
            print('Clip&Monjyu :', 'detect clipboard image.')
            clip_names = [filename]
            return self.monjyu.post_clip_names(user_id=self.user_id, clip_names=clip_names, )
        except:
            pass

        return False

    def list_proc(self, clip_list):
        # リスト処理スレッド
        #print('Clip&Monjyu :', "Hallo list,")

        # ファイル名？
        try:
            check = clip_list[0]
            if (os.path.isfile(check)):
                clip_files = True
                print('Clip&Monjyu :', 'detect clipboard files.')

                if (len(clip_list) > 20):
                    print('Clip&Monjyu :', 'max files over error. (max=20)')
                    return False

                clip_names = []
                for list_name in clip_list:
                    if (os.path.getsize(list_name) > 20000000):
                        print('Clip&Monjyu :', f'max bytes over error. { list_name }, (max=20000000)')
                    else:
                        basename = os.path.basename(list_name)
                        filename = qPath_input + basename
                        print('Clip&Monjyu :', filename)
                        shutil.copyfile(list_name, filename)
                        clip_names.append(filename)
                return self.monjyu.post_clip_names(user_id=self.user_id, clip_names=clip_names, )
        except:
            pass

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

        # main,data,addin,botFunc,
        self.main    = None
        self.data    = None
        self.addin   = None
        self.botFunc = None

        # ポート設定等
        self.chat_models = {}

        # ポート設定等
        self.local_endpoint0 = f'http://localhost:{ int(CORE_PORT) + 0 }'
        self.local_endpoint5 = f'http://localhost:{ int(CORE_PORT) + 5 }'

        # subai デーモン起動
        get_models_thread = threading.Thread(target=self.get_models, args=(), daemon=True, )
        get_models_thread.start()

    # get_model デーモン
    def get_models(self):
        startTime = time.time()
        time.sleep(READY_BASE_SEC)
        while True:
            if ((self.main is None) and ((time.time() - startTime) > READY_WAIT_SEC)) \
            or ((self.main is not None) and (self.main.main_all_ready == True)):

                # ファイル添付
                self.chat_models = {}
                try:
                    params = {"req_mode": "chat"}
                    response = requests.get(
                        self.local_endpoint0 + '/get_models',
                        params=params,
                        timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
                    )
                    if response.status_code == 200:
                        results = response.json()
                        for key, value in results.items():
                            key = key.replace('[', '')
                            key = key.replace(']', '')
                            self.chat_models[key.lower()] = value.lower()
                        print('Clip&Monjyu :', 'Clip&Monjyu is READY.')
                        break
                    else:
                        print('Clip&Monjyu :', f"Error response ({ CORE_PORT }/get_models) : {response.status_code} - {response.text}")
                except Exception as e:
                    print('Clip&Monjyu :', f"Error communicating ({ CORE_PORT }/get_models) : {e}")

            time.sleep(10.00)

    def request(self, req_mode='chat', user_id='admin', sysText='', reqText='', inpText='', ):
        res_port = None

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
                    if (f['checked'] == True):
                        file_names.append(f['file_name'])
            else:
                print('Clip&Monjyu :', f"Error response (webui/get_input_list) : {response.status_code}")
        except Exception as e:
            print('Clip&Monjyu :', f"Error communicating (webui/get_input_list) : {e}")

        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint0 + '/post_req',
                json={'user_id': user_id, 'from_port': CORE_PORT, 'to_port': CORE_PORT,
                    'req_mode': req_mode,
                    'system_text': sysText, 'request_text': reqText, 'input_text': inpText,
                    'file_names': file_names, 'result_savepath': '', 'result_schema': '', },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                res_port = str(response.json()['port'])
            else:
                print('Clip&Monjyu :', f"Error response ({ CORE_PORT }/post_req) : {response.status_code}")
        except Exception as e:
            print('Clip&Monjyu :', f"Error communicating ({ CORE_PORT }/post_req) : {e}")
        return res_port

    def post_clip_names(self, user_id='admin', clip_names=[], ):
        try:
            response = requests.post(
                self.local_endpoint5 + '/post_clip_names',
                json={'user_id': user_id, 'clip_names': clip_names, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                return True
            else:
                print('Clip&Monjyu :', f"Error response ({ CORE_PORT }/post_clip_names) : {response.status_code}")
        except Exception as e:
            print('Clip&Monjyu :', f"Error communicating ({ CORE_PORT }/post_clip_names) : {e}")
        return False

    def post_clip_text(self, user_id='admin', clip_text='', ):
        try:
            response = requests.post(
                self.local_endpoint5 + '/post_clip_text',
                json={'user_id': user_id, 'clip_text': clip_text, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                return True
            else:
                print('Clip&Monjyu :', f"Error response ({ CORE_PORT }/post_clip_text) : {response.status_code}")
        except Exception as e:
            print('Clip&Monjyu :', f"Error communicating ({ CORE_PORT }/post_clip_text) : {e}")
        return False



class _clip_to_memo:

    def __init__(self, runMode='assistant', ):
        self.runMode = runMode

    def to_memo(self, txt='', ):
        if (txt is None) or (txt == ''):
            return True
        send_text = txt.rstrip() + '\n\n'
        self.notePad(txt=send_text, cr=False, lf=False, )
        return True

    def enum_child_windows_proc(self, handle, list):
        list.append(handle)
        return 1

    def notePad10(self, txt='', cr=True, lf=False):
        winTitle = '無題 - メモ帳'
        parent_handle = ctypes.windll.user32.FindWindowW(0, winTitle)
        if parent_handle == 0:
            winTitle = '*無題 - メモ帳'
            parent_handle = ctypes.windll.user32.FindWindowW(0, winTitle)
            if parent_handle == 0:
                return False

        out_txt = txt
        if cr or lf:
            out_txt = out_txt.replace('\r', '').replace('\n', '')
        if cr:
            out_txt += '\r'
        if lf:
            out_txt += '\n'

        try:
            child_handles = array.array('i')
            ENUM_CHILD_WINDOWS = ctypes.WINFUNCTYPE(
                ctypes.c_int,
                ctypes.c_int,
                ctypes.py_object
            )
            ctypes.windll.user32.EnumChildWindows(
                parent_handle,
                ENUM_CHILD_WINDOWS(self.enum_child_windows_proc),
                ctypes.py_object(child_handles)
            )
            WM_CHAR = 0x0102
            for i in range(len(out_txt)):
                ctypes.windll.user32.SendMessageW(child_handles[0], WM_CHAR, ord(out_txt[i]), 0)
            return True
        except Exception as e:
            print('Clip&Monjyu :', e)
            return False

    def find_edit_control(self, element, depth=0, max_depth=10):
        if depth > max_depth:
            return None

        try:
            control_type = element.CurrentControlType
            class_name = element.CurrentClassName

            if control_type == UIAutomation.UIA_EditControlTypeId or class_name == "RichEditD2DPT":
                return element

            children = element.FindAll(UIAutomation.TreeScope_Children, IUIAutomation.CreateTrueCondition())
            for i in range(children.Length):
                child = children.GetElement(i)
                result = self.find_edit_control(child, depth + 1, max_depth)
                if result:
                    return result
        except Exception as e:
            print('Clip&Monjyu :', f"Error at depth {depth}: {e}")

        return None
        
    def notePad11(self, txt='', cr=True, lf=False):
        winTitle = 'タイトルなし - メモ帳'
        notepad_window = ctypes.windll.user32.FindWindowW(None, winTitle)
        if notepad_window == 0:
            winTitle = '*タイトルなし - メモ帳'
            notepad_window = ctypes.windll.user32.FindWindowW(None, winTitle)
            if notepad_window == 0:
                return False

        out_txt = txt
        if cr or lf:
            out_txt = out_txt.replace('\r', '').replace('\n', '')
        if cr:
            out_txt += '\r'
        if lf:
            out_txt += '\n'

        element = IUIAutomation.ElementFromHandle(notepad_window)
        edit_element = self.find_edit_control(element)

        if edit_element:
            try:
                EM_REPLACESEL = 0x00C2

                # 選択範囲を置換
                for char in out_txt:
                    ctypes.windll.user32.SendMessageW(edit_element.CurrentNativeWindowHandle, EM_REPLACESEL, True, char)

                return True
            except Exception as e:
                print('Clip&Monjyu :', e)
        return False

    def notePad(self, txt='', cr=True, lf=False):
        if (os.name != 'nt'):
            return False
        else:
            version = platform.release()
            if version == '10':
                return self.notePad10(txt, cr, lf)
            elif version == '11':
                return self.notePad11(txt, cr, lf)
            else:
                #print('Clip&Monjyu :', f"Unsupported Windows version: {version}")
                return False



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "monjyu_UI_ClipnMonjyu"
        self.func_ver  = "v0.20240813"
        self.func_auth = "y+MlAmcqvzqaXoBZtIz/V9H611RcQmQJ/HqghKjoH/1eSmmAQ9zTVio4xBlwCyn1"
        self.function  = {
            "name": self.func_name,
            "description": "拡張ＵＩ_Monjyu(もんじゅ)のクリップボードインターフェース機能。",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "userId": {
                        "type": "string",
                        "description": "ユーザーID 例) admin"
                    },
                    "sendText": {
                        "type": "string",
                        "description": "出力文字列 例) おはよう"
                    },
                },
                "required": ["runMode", "userId", "sendText"]
            }
        }

        # 初期設定
        self.runMode    = 'assistant'

        # クリップボード監視
        self.clip_worker = _clip_woker(runMode=self.runMode, )

        # 結果をクリップボードへ
        self.clip2memo  = _clip_to_memo(runMode=self.runMode, )

    def func_reset(self, main=None, data=None, addin=None, botFunc=None, ):
        if (main is not None):
            self.clip_worker.monjyu.main = main
        if (data is not None):
            self.clip_worker.monjyu.data = data
        if (addin is not None):
            self.clip_worker.monjyu.addin = addin
        if (botFunc is not None):
            self.clip_worker.monjyu.botFunc = botFunc
        return True

    def func_proc(self, json_kwargs=None, ):
        #print('Clip&Monjyu :', json_kwargs)

        # 引数
        runMode  = None
        userId   = None
        sendText = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode  = args_dic.get('runMode')
            userId   = args_dic.get('userId')
            sendText = args_dic.get('sendText')

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # 処理
        self.clip_worker.to_clip(sendText)
        self.clip2memo.to_memo(sendText)

        # 戻り
        dic = {}
        dic['result'] = "ok"
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('Clip&Monjyu :', '  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    json_dic = {}
    json_dic['runMode']  = "assistant"
    json_dic['userId']   = "admin"
    json_dic['sendText'] = "おはよう\nございます"
    json_kwargs = json.dumps(json_dic, ensure_ascii=False, )
    print(ext.func_proc(json_kwargs))

    time.sleep(120)


