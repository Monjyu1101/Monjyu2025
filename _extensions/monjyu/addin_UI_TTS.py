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

import keyboard



import importlib

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

use_openai_list   = ['kondou-latitude', 'kondou-main11', 'kondou-sub64', 'repair-surface7', ]



# インターフェース

qPath_tts    = 'temp/s6_5tts_txt/'

# 規定値
OPERATION_WAIT_SEC = 60



class _tts_woker:

    def __init__(self, runMode='assistant', ):
        self.runMode = runMode

        # ディレクトリ作成
        if (not os.path.isdir(qPath_tts)):
            os.makedirs(qPath_tts)

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
                hit = self.tts_proc()
            except:
                pass
            if hit == True:
                time.sleep(0.25)
            else:
                time.sleep(0.50)

        return True

    def tts_proc(self, remove=True, ):
        res        = False
        about_flag = False
        
        path = qPath_tts
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

                        # 文書成形
                        text = self.text_replace(text=text, )

                        if (text != '') and (text != '!'):
                            res = True

                            language = 'auto'
                            if (text[:3] == 'ja,') or (text[:3] == 'en,'):
                                language = text[:2]
                                text = text[3:]
 
                            speaker  = 'auto'
                            if   (text[:5] == 'free,'):
                                speaker = text[:4]
                                text = text[5:]
                            elif (text[:7] == 'google,'):
                                speaker = text[:6]
                                text = text[7:]
                            elif (text[:6] == 'openai,'):
                                speaker = text[:5]
                                text = text[6:]

                            elif (text[:6] == '四国めたん,'):
                                speaker = text[:5]
                                text = text[6:]
                            elif (text[:5] == '九州そら,'):
                                speaker = text[:4]
                                text = text[5:]
                            elif (text[:6] == 'ずんだもん,'):
                                speaker = text[:5]
                                text = text[6:]
                            elif (text[:5] == '青山龍星,'):
                                speaker = text[:4]
                                text = text[5:]
                            elif (text[:5] == '玄野武宏,'):
                                speaker = text[:4]
                                text = text[5:]

                            text = text.strip()
                            if (text[:1] == '"') and (text[-1:] == '"'):
                                text = text[1:len(text)-1]

                            for t in text.splitlines():

                                if  (time.time() > (self.last_key_time + OPERATION_WAIT_SEC)) \
                                and (about_flag == False):

                                    # 音声合成
                                    try:
                                        if (tts is not None):
                                            dic = {}
                                            dic['runMode']     = self.runMode
                                            dic['speech_text'] = str(t)
                                            dic['speaker']     = speaker
                                            dic['language']    = language
                                            if (speaker == '') or (speaker == 'auto'):
                                                if (qHOSTNAME in use_openai_list):
                                                    dic['speaker'] = 'openai'
                                            dic['immediate']   = 'no'
                                            json_dump = json.dumps(dic, ensure_ascii=False, )
                                            res_json = tts.func_proc(json_dump)
                                            #args_dic = json.loads(res_json)
                                            #text = args_dic.get('speech_text')
                                        else:
                                            print('★音声合成は利用できません！')
                                            print(str(t))
                                    except Exception as e:
                                        print(e)

                                else:
                                    about_flag = True
                                    break

                except Exception as e:
                    print(e)

        return res

    def text_replace(self, text=''):
        if "```" not in text:
            return self.text_replace_sub(text)
        else:
            # ```が2か所以上含まれている場合の処理
            first_triple_quote_index = text.find("```")
            last_triple_quote_index = text.rfind("```")
            if first_triple_quote_index == last_triple_quote_index:
                return self.text_replace_sub(text)
            # textの先頭から最初の```までをtext_replace_subで成形
            text_before_first_triple_quote = text[:first_triple_quote_index]
            formatted_before = self.text_replace_sub(text_before_first_triple_quote)
            formatted_before = formatted_before.strip() + '\n'
            # 最初の```から最後の```の直前までを文字列として抽出
            code_block = text[first_triple_quote_index : last_triple_quote_index]
            code_block = code_block.strip() + '\n'
            # 最後の```以降の部分をtext_replace_subで成形
            text_after_last_triple_quote = text[last_triple_quote_index:]
            formatted_after = self.text_replace_sub(text_after_last_triple_quote)
            formatted_after = formatted_after.strip() + '\n'
            # 結果を結合して戻り値とする
            return (formatted_before + code_block + formatted_after).strip()

    def text_replace_sub(self, text='', ):
        if (text.strip() == ''):
            return ''

        text = text.replace('\r', '')

        text = text.replace('。', '。\n')
        text = text.replace('?', '?\n')
        text = text.replace('？', '?\n')
        text = text.replace('!', '!\n')
        text = text.replace('！', '!\n')
        text = text.replace('。\n」','。」')
        text = text.replace('。\n"' ,'。"')
        text = text.replace("。\n'" ,"。'")
        text = text.replace('?\n」','?」')
        text = text.replace('?\n"' ,'?"')
        text = text.replace("?\n'" ,"?'")
        text = text.replace('!\n」','!」')
        text = text.replace('!\n"' ,'!"')
        text = text.replace("!\n'" ,"!'")
        text = text.replace("!\n=" ,"!=")
        text = text.replace("!\n--" ,"!--")

        text = text.replace('\n \n ' ,'\n')
        text = text.replace('\n \n' ,'\n')

        hit = True
        while (hit == True):
            if (text.find('\n\n')>0):
                hit = True
                text = text.replace('\n\n', '\n')
            else:
                hit = False

        return text.strip()

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



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "extension_UI_TTS"
        self.func_ver  = "v0.20240518"
        self.func_auth = "w7TfpPMfw02yCbP5cLjmc1e69oPZWBKsB+VWh0pFu6Y="
        self.function  = {
            "name": self.func_name,
            "description": "拡張ＵＩ_音声合成する。",
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
        self.sub_worker = _tts_woker(runMode=self.runMode, )
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


