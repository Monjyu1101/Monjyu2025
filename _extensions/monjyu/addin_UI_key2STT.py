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

import pyperclip
import pyautogui



import importlib

stt = None
try:
    import 認証済_音声入力202405
    stt  = 認証済_音声入力202405._class()
except:
    try:
        #loader = importlib.machinery.SourceFileLoader('認証済_音声入力202405.py', '_extensions/clipngpt/認証済_音声入力202405.py')
        loader = importlib.machinery.SourceFileLoader('認証済_音声入力202405.py', '_extensions/function/認証済_音声入力202405.py')
        認証済_音声入力202405 = loader.load_module()
        stt  = 認証済_音声入力202405._class()
    except:
        print('★"認証済_音声入力202405"は利用できません！')

tts = None
try:
    import 認証済_音声合成202405
    tts  = 認証済_音声合成202405._class()
except:
    try:
        #loader = importlib.machinery.SourceFileLoader('認証済_音声合成202405.py', '_extensions/clipngpt/認証済_音声合成202405.py')
        loader = importlib.machinery.SourceFileLoader('認証済_音声合成202405.py', '_extensions/function/認証済_音声合成202405.py')
        認証済_音声合成202405 = loader.load_module()
        tts  = 認証済_音声合成202405._class()
    except:
        print('★"認証済_音声合成202405"は利用できません！')



import socket
qHOSTNAME = socket.gethostname().lower()

use_openai_list   = ['kondou-latitude', 'kondou-main11', 'kondou-sub64', 'repair-surface7', 'surface-pro7', 'a-zip神戸会議用sf', ]
not_feedback_list = ['kondou-latitude', 'kondou-main11', 'kondou-sub64', 'repair-surface7', ]



# インターフェース

qPath_stt    = 'temp/s6_4stt_txt/'



class _key2STT:

    def __init__(self, runMode='assistant', ):
        self.runMode = runMode

        # ディレクトリ作成
        if (not os.path.isdir(qPath_stt)):
            os.makedirs(qPath_stt)

        # キーボード監視 開始
        self.last_key_time = 0
        self.kb_handler_id = None
        self.start_kb_listener()

        # カウンタ
        self.file_seq = 0

    # キーボード監視 開始
    def start_kb_listener(self):
        self.last_prtScrn_time  = 0
        self.last_prtScrn_count = 0
        self.last_alt_l_time    = 0
        self.last_alt_l_count   = 0
        self.last_alt_l_clip    = ''
        self.last_shift_l_time  = 0
        self.last_shift_l_count = 0
        self.last_shift_r_time  = 0
        self.last_shift_r_count = 0
        self.last_copy_time     = 0
        self.last_copy_string   = pyperclip.paste()

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
        if (event.name == 'print screen'):
            pass
        elif (event.name in ['alt', 'left alt', 'right alt']):
            pass
        elif (event.name in ['shift', 'left shift', 'right shift']):
            pass
        else:
            self.last_prtScrn_time  = 0
            self.last_prtScrn_count = 0
            self.last_alt_l_time    = 0
            self.last_alt_l_count   = 0
            self.last_alt_l_clip    = ''
            self.last_shift_l_time  = 0
            self.last_shift_l_count = 0
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
                if (self.last_prtScrn_count < 3):
                    self.last_prtScrn_time = press_time
                else:
                    self.last_prtScrn_time  = 0
                    self.last_prtScrn_count = 0
                    #print("Press PrtScrn x 3 !")

                    # キー操作監視 停止
                    self.stop_kb_listener()

                    # カウンタ
                    self.file_seq += 1
                    if (self.file_seq > 9999):
                        self.file_seq = 1

                    # ファイル名
                    nowTime  = datetime.datetime.now()
                    stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
                    seq      = '{:04}'.format(self.file_seq)
                    filename = qPath_stt + stamp + '.' + seq + '.prtScrn_key.txt'

                    # 画像処理待機
                    time.sleep(2.00)

                    # 音声入力
                    text = ''
                    try:
                        if (stt is not None):
                            dic = {}
                            dic['runMode']  = self.runMode
                            dic['api']      = 'auto' # auto, google, openai,
                            if(qHOSTNAME in use_openai_list):
                                dic['api']  = 'openai' # auto, google, openai,
                            dic['language'] = 'auto'
                            json_dump = json.dumps(dic, ensure_ascii=False, )
                            res_json = stt.func_proc(json_dump)
                            args_dic = json.loads(res_json)
                            text = args_dic.get('recognition_text')
                        else:
                            print('★音声入力は利用できません！')
                    except Exception as e:
                        print(e)

                    # RiKi処理
                    if (text != ''):
                        text  = 'vision,' + text + '\n'
                        #if(qHOSTNAME not in not_feedback_list):
                        #    text += '結果は要約した内容で音声合成でお願いします。\n'
                    #else:
                    #    text  = 'vision,画像を分析して報告してください。あなたが支援できる内容を教えてください\n'
                    #    # text += 'ログイン操作中である場合、\n'
                    #    # text += 'ＩＤ入力欄、パスワード入力欄ならびにログインボタンの各中心座標を使って、ログイン操作のファンクションを実行してください。\n'
                    #    # text += 'それ以外の操作中と変団できる場合、今後ＡＩ支援できる可能性について報告してください。\n'
                    self.txtsWrite(filename, txts=[text], encoding='utf-8', exclusive=False, mode='w', )
                
                    #keycontrol = Controller()
                    #keycontrol.press(keyboard.Key.ctrl)
                    #keycontrol.release(keyboard.Key.ctrl)

                    # キー操作監視 再開
                    self.start_kb_listener()

        # --------------------
        # alt キー
        # --------------------
        elif (event.name in ['alt', 'left alt', 'right alt']):
            press_time = time.time()
            if ((press_time - self.last_alt_l_time) > 1):
                self.last_alt_l_time  = press_time
                self.last_alt_l_count = 1
                if ((press_time - self.last_copy_time) < 1):
                    self.last_alt_l_clip = self.last_copy_string
                    print("Press alt key with clip text ?")
            else:
                self.last_alt_l_count += 1
                if (self.last_alt_l_count < 3):
                    self.last_alt_l_time = press_time
                else:
                    self.last_alt_l_time  = 0
                    self.last_alt_l_count = 0
                    #print("Press alt_l x 3 !")
                    if (self.last_alt_l_clip != ''):
                        print("Press alt key with clip ok.")

                    # キー操作監視 停止
                    self.stop_kb_listener()

                    # カウンタ
                    self.file_seq += 1
                    if (self.file_seq > 9999):
                        self.file_seq = 1

                    # ファイル名
                    nowTime  = datetime.datetime.now()
                    stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
                    seq      = '{:04}'.format(self.file_seq)
                    filename = qPath_stt + stamp + '.' + seq + '.alt_l_key.txt'

                    # 音声入力
                    text = ''
                    try:
                        if (stt is not None):
                            dic = {}
                            dic['runMode']  = self.runMode
                            dic['api']      = 'auto' # auto, google, openai,
                            if(qHOSTNAME in use_openai_list):
                                dic['api']  = 'openai' # auto, google, openai,
                            dic['language'] = 'auto'
                            json_dump = json.dumps(dic, ensure_ascii=False, )
                            res_json = stt.func_proc(json_dump)
                            args_dic = json.loads(res_json)
                            text = args_dic.get('recognition_text')
                        else:
                            print('★音声入力は利用できません！')
                    except Exception as e:
                        print(e)

                    # RiKi処理
                    if (text != ''):
                        text  = 'assistant,' + text + '\n'
                        #if(qHOSTNAME not in not_feedback_list):
                        #    text += '結果は要約した内容で音声合成でお願いします。\n'
                        if (self.last_alt_l_clip != ''):
                            text += "''' 補足情報 \n"
                            text += self.last_alt_l_clip + '\n'
                            text += "''' \n"

                        #text  = text
                        self.txtsWrite(filename, txts=[text], encoding='utf-8', exclusive=False, mode='w', )
                
                    #keycontrol = Controller()
                    #keycontrol.press(keyboard.Key.ctrl)
                    #keycontrol.release(keyboard.Key.ctrl)

                    # キー操作監視 再開
                    self.start_kb_listener()

        # --------------------
        # shift_l キー
        # --------------------
        elif (event.name in ['shift', 'left shift']):
            press_time = time.time()
            if ((press_time - self.last_shift_l_time) > 1):
                self.last_shift_l_time  = press_time
                self.last_shift_l_count = 1
            else:
                self.last_shift_l_count += 1
                if (self.last_shift_l_count < 3):
                    self.last_shift_l_time = press_time
                else:
                    self.last_shift_l_time  = 0
                    self.last_shift_l_count = 0
                    #print("Press shift_l x 3 !")

                    # キー操作監視 停止
                    self.stop_kb_listener()

                    # 音声入力
                    text = ''
                    try:
                        if (stt is not None):
                            dic = {}
                            dic['runMode']  = self.runMode
                            dic['api']      = 'auto' # auto, google, openai,
                            if(qHOSTNAME in use_openai_list):
                                dic['api']  = 'openai' # auto, google, openai,
                            dic['language'] = 'auto'
                            json_dump = json.dumps(dic, ensure_ascii=False, )
                            res_json = stt.func_proc(json_dump)
                            args_dic = json.loads(res_json)
                            text = args_dic.get('recognition_text')
                        else:
                            print('★音声入力は利用できません！')
                    except Exception as e:
                        print(e)
                
                    # ペースト処理
                    if (text != ''):
                        try:
                            pyperclip.copy(text)
                            pyautogui.hotkey('ctrl', 'v')
                        except Exception as e:
                            print(e)

                    #keycontrol = Controller()
                    #keycontrol.press(keyboard.Key.ctrl)
                    #keycontrol.release(keyboard.Key.ctrl)

                    # キー操作監視 再開
                    self.start_kb_listener()

        # --------------------
        # shift_r キー
        # --------------------
        elif (event.name == 'right shift'):
            press_time = time.time()
            if ((press_time - self.last_shift_r_time) > 1):
                self.last_shift_r_time  = press_time
                self.last_shift_r_count = 1
            else:
                self.last_shift_r_count += 1
                if (self.last_shift_r_count < 3):
                    self.last_shift_r_time = press_time
                else:
                    self.last_shift_r_time  = 0
                    self.last_shift_r_count = 0
                    #print("Press shift_r x 3 !")

                    # キー操作監視 停止
                    self.stop_kb_listener()

                    # # 音声合成
                    # text = 'カメラ画像を取得しました。何かお困りですか？'
                    # try:
                    #     if (tts is not None):
                    #         dic = {}
                    #         dic['runMode']     = self.runMode
                    #         dic['speech_text'] = str(text)
                    #         dic['speaker']     = 'auto'
                    #         dic['language']    = 'auto'
                    #         if(qHOSTNAME in ('kondou-latitude', 'kondou-main11')):
                    #             dic['speaker'] = 'openai'
                    #         json_dump = json.dumps(dic, ensure_ascii=False, )
                    #         res_json = tts.func_proc(json_dump)
                    #         #args_dic = json.loads(res_json)
                    #         #text = args_dic.get('speech_text')
                    #     else:
                    #         print('★音声合成は利用できません！')
                    #         print(str(text))
                    # except Exception as e:
                    #     print(e)

                    # 音声入力
                    text = ''
                    try:
                        if (stt is not None):
                            dic = {}
                            dic['runMode']  = self.runMode
                            dic['api']      = 'auto' # auto, google, openai,
                            if(qHOSTNAME in use_openai_list):
                                dic['api']  = 'openai' # auto, google, openai,
                            dic['language'] = 'auto'
                            json_dump = json.dumps(dic, ensure_ascii=False, )
                            res_json = stt.func_proc(json_dump)
                            args_dic = json.loads(res_json)
                            text = args_dic.get('recognition_text')
                        else:
                            print('★音声入力は利用できません！')
                    except Exception as e:
                        print(e)
                
                    # ペースト処理
                    if (text != ''):
                        try:
                            pyperclip.copy(text)
                            pyautogui.hotkey('ctrl', 'v')
                        except Exception as e:
                            print(e)

                    #keycontrol = Controller()
                    #keycontrol.press(keyboard.Key.ctrl)
                    #keycontrol.release(keyboard.Key.ctrl)

                    # キー操作監視 再開
                    self.start_kb_listener()

        else:
            self.last_prtScrn_time  = 0
            self.last_prtScrn_count = 0
            self.last_alt_l_time    = 0
            self.last_alt_l_count   = 0
            self.last_alt_l_clip    = ''
            self.last_shift_l_time  = 0
            self.last_shift_l_count = 0
            self.last_shift_r_time  = 0
            self.last_shift_r_count = 0

            # クリップボード確認
            clip_text = None
            try:
                clip_text = pyperclip.paste()
            except:
                clip_text = None
                try:
                    time.sleep(0.20)
                    clip_text = pyperclip.paste()
                except Exception as e:
                    print(e)
                    clip_text = None
                    
            if (clip_text is not None):
                if (clip_text != self.last_copy_string):
                    if (clip_text != ''):
                        self.last_copy_time     = time.time()
                        self.last_copy_string   = clip_text
                    else:
                        self.last_copy_time     = 0
                        self.last_copy_string   = clip_text

    def txtsWrite(self, filename, txts=[''], encoding='utf-8', exclusive=False, mode='w', ):
        if (exclusive == False):
            try:
                w = codecs.open(filename, mode, encoding)
                for txt in txts:
                    if (encoding != 'shift_jis'):
                        w.write(txt + '\n')
                    else:
                        w.write(txt + '\r\n')
                w.close()
                w = None
                return True
            except Exception as e:
                w = None
                return False
        else:
            res = self.remove(filename, )
            if (res == False):
                return False
            else:
                f2 = filename[:-4] + '.txtsWrite.tmp'
                res = self.remove(f2, )
                if (res == False):
                    return False
                else:
                    try:
                        w = codecs.open(f2, mode, encoding)
                        for txt in txts:
                            if (encoding != 'shift_jis'):
                                w.write(txt + '\n')
                            else:
                                w.write(txt + '\r\n')
                        w.close()
                        w = None
                        os.rename(f2, filename)
                        return True
                    except Exception as e:
                        w = None
                        return False



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "extension_UI_key2SST"
        self.func_ver  = "v0.20240518"
        self.func_auth = "h0MmuBSfyHFVSPQ+uqVSZBIEFnpafvnyC5iUaJ1gfkR9LeNjKv1SKFDvY+K32/wI"
        self.function  = {
            "name": self.func_name,
            "description": "拡張ＵＩ_キー(PrtScrn,alt,shift)連打で、音声入力する。",
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
        self.sub_proc = _key2STT(runMode=self.runMode, )

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



