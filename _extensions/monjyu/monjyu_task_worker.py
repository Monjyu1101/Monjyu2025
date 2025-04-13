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
import threading

from playsound3 import playsound
import subprocess
import requests

import importlib



# インターフェース
qIO_liveAiRun  = 'temp/monjyu_live_ai_run.txt'
qIO_agent2live = 'temp/monjyu_io_agent2live.txt'
#qPath_task     = '_config/_task/'
qPath_task_ai  = '_config/_task_ai/'

YOUBIs  = ["1_mon", "2_tue", "3_wed", "4_thu", "5_fri", "6_sat", "7_sun"]
FOLDERs = YOUBIs
FOLDERs.append("0_all")
FOLDERs.append("0_week")



# TTSの定義
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

def io_text_write(filename='', text='', encoding='utf-8', mode='w', ):
    try:
        w = codecs.open(filename, mode, encoding)
        w.write(text)
        w.close()
        w = None
        return True
    except Exception as e:
        print(e)
    w = None
    return False



class _worker_class:

    def __init__(self, runMode='assistant', ):
        self.runMode = runMode

        # woker設定
        self.worker = None
        self._running = False
        self.task_files = {}
        self.file_seq = 0

        # main,data,addin,botFunc,
        self.main    = None
        self.data    = None
        self.addin   = None
        self.botFunc = None

    def start_worker(self):
        """ワーカースレッドを開始"""
        if (not self._running):
            self._running = True
            self.worker = threading.Thread(target=self.task_worker, daemon=True, )
            self.worker.start()
        return True

    def stop_worker(self):
        """ワーカースレッドを停止"""
        if (self._running):
            self._running = False
            if self.worker:
                self.worker.join()
                self.worker = None
        return True

    def task_worker(self):
        """時刻監視を行うワーカー関数"""
        self.last_hh   = None
        self.last_hhmm = None
        
        while (self._running == True):
            now_time = datetime.datetime.now()
            current_yymmdd = now_time.strftime('%Y%m%d')
            current_hh     = now_time.strftime('%H')
            current_hh_mm  = now_time.strftime('%H:%M')
            current_hhmm   = now_time.strftime('%H%M')
            
            # 時刻が変化した場合に表示
            if (current_hh != self.last_hh):
                if (self.last_hhmm is not None):
                    print(f" TASK Worker  : { current_hh_mm } ")
                    for key in self.task_files.keys():
                        key4 = key[:4]
                        if  (key4 >= str(current_hh + '00')) \
                        and (key4 <= str(current_hh + '59')):
                            print(f" - '{ key }' ")
                self.last_hh = current_hh
                self.task_files = {}
                #res = self.load_task_files(path_base=qPath_task)
                res = self.load_task_files(path_base=qPath_task_ai)
            if (current_hhmm != self.last_hhmm):
                self.last_hhmm = current_hhmm
                self.task = threading.Thread(target=self.task_execute, args=(current_hhmm,), daemon=True, )
                self.task.start()

            # 5秒間隔で監視
            time.sleep(5)
        return True

    def is_running(self):
        return self._running

    def load_task_files(self, path_base='_config/_task_ai/', ):
        now_time = datetime.datetime.now()
        current_yymmdd  = now_time.strftime('%Y%m%d')
        current_hh      = now_time.strftime('%H')
        current_youbi_n = now_time.weekday() #月曜=0～日曜=6
        current_youbi   = YOUBIs[current_youbi_n]

        # 0_allフォルダ検索
        self.load_task_add(path_base + "0_all/")

        # 0_weekフォルダ検索
        if (current_youbi_n >= 0) and (current_youbi_n <= 4):
            self.load_task_add(path_base + "0_week/")

        # 曜日フォルダ検索
        self.load_task_add(path_base + current_youbi + '/')

        # 日付フォルダ検索
        path_dirs = glob.glob(path_base + current_yymmdd + '*')
        if (len(path_dirs) > 0):
            path_dirs.sort()
            for p in path_dirs:
                if (os.path.isdir(p)):
                    path = p.replace('\\','/') + '/'
                    self.load_task_add(path)

        return True

    def load_task_add(self, path=None,):
        if (os.path.isdir(path)):
            path_files = glob.glob(path + '*')
            if (len(path_files) > 0):
                for f in path_files:
                    if (os.path.isfile(f)):
                        f_name = f.replace('\\','/')
                        f_base = os.path.basename(f_name)
                        if (f_base[:4].isdigit()):
                            self.task_files[f_base] = f_name
                            #print(f" - '{ f_base }' ")
        return True

    def task_execute(self, hhmm='0000',):
        for f_base, f_name in self.task_files.items():
            if (f_base[:4] == hhmm):
                name, ext = os.path.splitext(f_base)
                print(f" TASK Worker  : { hhmm } - '{ f_base }' ", ext)

                try:
                    now_time  = datetime.datetime.now()
                    now_stamp = now_time.strftime('%Y%m%d.%H%M%S')

                    # file_seq カウントアップ
                    self.file_seq += 1
                    if (self.file_seq > 9999):
                        self.file_seq = 1

                    # .txt, .ai,
                    if (ext.lower() in ['.txt', '.ai']):
                        if (name[-5:].lower() != '_sjis'):
                            txts, text = self.txtsRead(f_name, encoding='utf-8', exclusive=False, )
                        else:
                            txts, text = self.txtsRead(f_name, encoding='shift_jis', exclusive=False, )
                        input_text = ''
                        if (txts != False):
                            input_text = text
                            #print(input_text)

                    # .txt,
                    if   (ext.lower() == '.txt'):
                        #self.play_tts(input_text=input_text, )
                        tts_proc = threading.Thread(target=self.play_tts, args=(input_text,), daemon=True, )
                        tts_proc.start()

                    # .mp3, .wav,
                    elif (ext.lower() in ['.mp3', '.wav']):
                        #self.play(outFile=f_name, )
                        mp3_proc = threading.Thread(target=self.play, args=(f_name,), daemon=True, )
                        mp3_proc.start()

                    # .mp4,
                    elif (ext.lower() == '.mp4'):
                        #self.play_video(play_file=f_name)
                        mp4_proc = threading.Thread(target=self.play_video, args=(f_name,), daemon=True, )
                        mp4_proc.start()

                    # .bat,
                    elif (ext.lower() == '.bat'):
                        #self.play_bat(bat_file=f_name)
                        bat_proc = threading.Thread(target=self.play_bat, args=(f_name,), daemon=True, )
                        bat_proc.start()

                    # .ai,
                    elif (ext.lower() == '.ai'):
                        #self.play_monjyu(input_text=input_text, )
                        ai_proc = threading.Thread(target=self.play_monjyu, args=(input_text,), daemon=True, )
                        ai_proc.start()

                except Exception as e:
                    print(e)

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

    def play_tts(self, input_text='おはようございます', ):
        if (input_text == ''):
            return False
        # 音声合成
        try:
            if (tts is not None):
                dic = {}
                dic['runMode']     = self.runMode
                dic['speech_text'] = str(input_text)
                dic['speaker']     = 'auto'
                dic['language']    = 'auto'
                dic['immediate']   = 'yes'
                json_dump = json.dumps(dic, ensure_ascii=False, )
                res_json = tts.func_proc(json_dump)
                #args_dic = json.loads(res_json)
                #text = args_dic.get('speech_text')
                return True
            else:
                print('★音声合成は利用できません！')
                print(str(input_text))
        except Exception as e:
            print(e)
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

    def play_video(self, play_file='temp/_work/sound.mp4', ):
        file = play_file
        if (os.name == 'nt'):
            file = play_file.replace('/','\\')
        if (not os.path.exists(file)):
            return False
        try:
            ffplay = subprocess.Popen(['ffplay', '-i', file, \
                '-autoexit', \
                #'-noborder', \
                '-alwaysontop', \
                '-loglevel', 'warning', \
                ], \
                shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
            #time.sleep(1.00)
            #qGUI.setForegroundWindow(winTitle=file, )
            return True
        except Exception as e:
            print(e)
        return False

    def play_bat(self, bat_file='temp/_work/test.bat', ):
        file = bat_file
        if (os.name == 'nt'):
            file = bat_file.replace('/','\\')
        if (not os.path.exists(file)):
            return False
        try:
            cmd = subprocess.Popen('"' + file + '"')
            #shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
            #time.sleep(1.00)
            #qGUI.setForegroundWindow(winTitle=file, )
            return True
        except Exception as e:
            print(e)
        return False

    def play_monjyu(self, input_text='おはようございます', ):
        if (input_text == ''):
            return False

        # Live 連携
        if (os.path.isfile(qIO_liveAiRun)):
            reqText = 'gpt,\n'
            reqText += input_text

        # Monjyu 連携 (tts指示)
        else:
            reqText = 'gpt,\n'
            reqText += "以下の要求の結果を、要約して、日本語で音声合成してください。\n"
            reqText += input_text

        # AI要求送信
        try:
            if self.botFunc is not None:
                module_dic = self.botFunc.function_modules.get('execute_monjyu_request', None)
                if (module_dic is not None):

                    # Monjyu function 実行
                    dic = {}
                    dic['runMode'] = 'chat' #ここは'chat'で内部的に問い合わせる
                    dic['userId'] = 'live'
                    dic['reqText'] = reqText
                    f_kwargs = json.dumps(dic, ensure_ascii=False, )
                    try:
                        ext_func_proc = module_dic['func_proc']
                        res_json = ext_func_proc( f_kwargs )
                        res_dic = json.loads(res_json)
                        res_text = res_dic.get('result_text','')
                        res_text = res_text.replace('`', '"')
                        print(res_text)
                    except Exception as e:
                        print(e)
                        return False

                    # Live 連携
                    if (os.path.isfile(qIO_liveAiRun)):
                        text = f"[TASK Worker] \n"
                        text += input_text.rstrip() + '\n'
                        text += "について、以下が結果報告です。要約して日本語で報告してください。\n"
                        text += res_text.rstrip() + '\n\n'
                        res = io_text_write(qIO_agent2live, text)

                    # Monjyu 連携 (tts指示)
                    #else:
                    #    # 音声合成
                    #    self.play_tts(input_text=res_text, )
    
                    return True

        except Exception as e:
            print(e)
        return False



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "extension_task_worker"
        self.func_ver  = "v0.20250216"
        self.func_auth = "v99C7yxRC2WOljQEzLZ3uiOkas9VLpmtQ+pqE+nlolg05s3Fuzwekbu1rvZyM/2J"
        self.function  = {
            "name": self.func_name,
            "description": \
"""
拡張機能
設定された定時タスクを実行する。
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

        # ワーカー
        self.sub_worker = _worker_class(runMode=self.runMode, )

        # リセット
        self.func_reset()

    def func_reset(self, main=None, data=None, addin=None, botFunc=None, ):
        if (main is not None):
            self.sub_worker.main = main
        if (data is not None):
            self.sub_worker.data = data
        if (addin is not None):
            self.sub_worker.addin = addin
        if (botFunc is not None):
            self.sub_worker.botFunc = botFunc
        self.sub_worker.stop_worker()
        self.sub_worker.start_worker()
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
    time.sleep(1)

    print(ext.func_proc('{ "runMode" : "assistant" }'))

    time.sleep(600)


