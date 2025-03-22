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

import keyboard

from PIL import Image

import io
if (os.name == 'nt'):
    import win32clipboard



import importlib

screenShot = None
try:
    import       認証済_スクリーンショット画像取得202405
    screenShot = 認証済_スクリーンショット画像取得202405._class()
except:
    try:
        #loader = importlib.machinery.SourceFileLoader('認証済_スクリーンショット画像取得202405.py', '_extensions/clipngpt/認証済_スクリーンショット画像取得202405.py')
        loader = importlib.machinery.SourceFileLoader('認証済_スクリーンショット画像取得202405.py', '_extensions/function/認証済_スクリーンショット画像取得202405.py')
        認証済_スクリーンショット画像取得202405 = loader.load_module()
        screenShot = 認証済_スクリーンショット画像取得202405._class()
    except:
        print('★"認証済_スクリーンショット画像取得202405"は利用できません！')

cameraShot = None
try:
    import       認証済_カメラ画像取得202405
    cameraShot = 認証済_カメラ画像取得202405._class()
except:
    try:
        #loader = importlib.machinery.SourceFileLoader('認証済_カメラ画像取得202405.py', '_extensions/clipngpt/認証済_カメラ画像取得202405.py')
        loader = importlib.machinery.SourceFileLoader('認証済_カメラ画像取得202405.py', '_extensions/function/認証済_カメラ画像取得202405.py')
        認証済_カメラ画像取得202405 = loader.load_module()
        cameraShot = 認証済_カメラ画像取得202405._class()
    except:
        print('★"認証済_カメラ画像取得202405"は利用できません！')



class _key2Shot:

    def __init__(self, runMode='assistant', ):
        self.runMode = runMode

        # キーボード監視 開始
        self.last_key_time = 0
        self.kb_handler_id = None
        self.start_kb_listener()

    # キーボード監視 開始
    def start_kb_listener(self, runMode='assistant',):
        self.last_prtScrn_time  = 0
        self.last_prtScrn_count = 0
        self.last_shift_r_time  = 0
        self.last_shift_r_count = 0

        # イベントハンドラの登録
        self.last_key_time      = 0
        self.debounce_interval  = 0.05  # 50ミリ秒のデバウンス時間
        self.kb_handler_id = keyboard.hook(self._keyboard_event_handler)

    # イベントハンドラ
    def _keyboard_event_handler(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            # デバウンス期間中は処理をスキップ 
            now_time = time.time()
            if (now_time - self.last_key_time < self.debounce_interval):
                return
            self.last_key_time = now_time
            self.on_press(event)
        elif event.event_type == keyboard.KEY_UP:
            self.on_release(event)

    # キーボード監視 終了
    def stop_kb_listener(self):
        try:
            if (self.kb_handler_id is not None):
                keyboard.unhook(self.kb_handler_id)
                self.kb_handler_id = None
        except Exception as e:
            print(e)

    # キーボードイベント
    def on_press(self, event):
        if (event.name == "print screen"):
            pass
        elif (event.name == "right shift"):
            pass
        else:
            self.last_prtScrn_time  = 0
            self.last_prtScrn_count = 0
            self.last_shift_r_time  = 0
            self.last_shift_r_count = 0

    def on_release(self, event):
        # --------------------
        # prtScrn キー
        # --------------------
        if (event.name == "print screen"):
            press_time = time.time()
            if ((press_time - self.last_prtScrn_time) > 1):
                self.last_prtScrn_time  = press_time
                self.last_prtScrn_count = 1
            else:
                self.last_prtScrn_count += 1
                if   (self.last_prtScrn_count < 3):
                    self.last_prtScrn_time = press_time
                else:
                    self.last_prtScrn_time  = 0
                    self.last_prtScrn_count = 0
                    #print("Press PrtScrn x 3 !")

                    # キー操作監視 停止
                    self.stop_kb_listener()

                    # スクリーンショット
                    image_path = None
                    try:
                        if (screenShot is not None):
                            dic = {}
                            dic['runMode']       = self.runMode
                            dic['screen_number'] = 'auto'
                            json_dump = json.dumps(dic, ensure_ascii=False, )
                            res_json = screenShot.func_proc(json_dump)
                            args_dic = json.loads(res_json)
                            image_path = args_dic.get('image_path')
                        else:
                            print('★スクリーンショット画像取得は利用できません！')
                    except Exception as e:
                        print(e)

                    # クリップボードへ
                    if (image_path is not None) and (os.path.isfile(image_path)):

                        try:
                            pil_img = Image.open(image_path)
                            self.image_to_clipboard(image=pil_img, )
                        except Exception as e:
                            print(e)
                            try:
                                time.sleep(1.00)
                                self.image_to_clipboard(image=pil_img, )
                            except Exception as e:
                                print(e)

                    # キー操作監視 再開
                    self.start_kb_listener()

        # --------------------
        # right shiftキー
        # --------------------
        elif (event.name == "right shift"):
            press_time = time.time()
            if ((press_time - self.last_shift_r_time) > 1):
                self.last_shift_r_time  = press_time
                self.last_shift_r_count = 1
            else:
                self.last_shift_r_count += 1
                if   (self.last_shift_r_count < 3):
                    self.last_shift_r_time = press_time
                else:
                    self.last_shift_r_time  = 0
                    self.last_shift_r_count = 0
                    #print("Press right shift x 3 !")

                    # キー操作監視 停止
                    self.stop_kb_listener()

                    # カメラ画像取得
                    image_path = None
                    try:
                        if (cameraShot is not None):
                            dic = {}
                            dic['runMode']       = self.runMode
                            dic['device_number'] = 'auto'
                            json_dump = json.dumps(dic, ensure_ascii=False, )
                            res_json = cameraShot.func_proc(json_dump)
                            args_dic = json.loads(res_json)
                            image_path = args_dic.get('image_path')
                        else:
                            print('★カメラ画像取得は利用できません！')
                    except Exception as e:
                        print(e)

                    # クリップボードへ
                    if (image_path is not None) and (os.path.isfile(image_path)):

                        try:
                            pil_img = Image.open(image_path)
                            self.image_to_clipboard(image=pil_img, )
                        except Exception as e:
                            print(e)
                            try:
                                time.sleep(1.00)
                                self.image_to_clipboard(image=pil_img, )
                            except Exception as e:
                                print(e)

                    # キー操作監視 再開
                    self.start_kb_listener()

        else:
            self.last_prtScrn_time  = 0
            self.last_prtScrn_count = 0
            self.last_shift_r_time  = 0
            self.last_shift_r_count = 0

    def image_to_clipboard(self, image=None, ):
        if (os.name != 'nt'):
            return False
        if (image is None):
            return False

        # メモリストリームにBMP形式で保存する
        bitmap = io.BytesIO()
        image.convert('RGB').save(bitmap, 'BMP')
        data = bitmap.getvalue()[14:]
        bitmap.close()

        # クリップボードにデータをセットする
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

        return True



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "extension_UI_key2Shot"
        self.func_ver  = "v0.20240518"
        self.func_auth = "h0MmuBSfyHFVSPQ+uqVSZKlKllUwCg1tJ4NtxFQ3ovUoZvaX1asT9dxcjgKknaX6"
        self.function  = {
            "name": self.func_name,
            "description": \
"""
拡張ＵＩ
キー(PrtScrn)連打で、マウス位置の画面をスクリーンショットする。
キー(right shift)連打で、カメラ画像を取得する。
""",
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
        self.runMode = 'assistant'
        self.func_reset()

        # キーボード監視 開始
        self.sub_proc = _key2Shot(runMode=self.runMode, )

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
            runMode = self.runMode
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


