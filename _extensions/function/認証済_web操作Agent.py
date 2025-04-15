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

import os
import time
import codecs
import subprocess

import queue
import threading

# インターフェース
ext_python_init   = '認証済_web操作Agent_pyinit.py'
ext_python_script = '認証済_web操作Agent_python.py'
qText_ready       = 'Web-Operator function ready!'
qText_start       = 'Web-Operator function start!'
qText_complete    = 'Web-Operator function complete!'
qIO_func2py       = 'temp/web操作Agent_func2py.txt'
qIO_py2func       = 'temp/web操作Agent_py2func.txt'
qIO_agent2live    = 'temp/monjyu_io_agent2live.txt'

qTimeout_reset    = 30
qTimeout_init     = 300
qTimeout_start    = 30
qTimeout_proc     = 120

AGENT_MODELS = {}
AGENT_MODELS['freeai'] = {  'gemini-2.0-flash-exp': 'gemini-2.0-flash-exp',
                            'gemini-2.0-flash-001': 'gemini-2.0-flash-001',
                            'gemini-2.0-pro-exp-02-05': 'gemini-2.0-pro-exp-02-05',
                            'gemini-2.0-flash-thinking-exp-01-21': 'gemini-2.0-flash-thinking-exp-01-21', }
AGENT_MODELS['openai'] = {  'gpt-4o-mini-2024-07-18': 'gpt-4o-mini-2024-07-18',
                            'gpt-4o-2024-11-20': 'gpt-4o-2024-11-20', 
                            'o3-mini-2025-01-31': 'o3-mini-2025-01-31', }
AGENT_MODELS['claude'] = {  'claude-3-5-sonnet-20241022': 'claude-3-5-sonnet-20241022', }
AGENT_ENGINE = 'freeai'
AGENT_MODEL  = 'gemini-2.0-flash-exp'



def io_text_read(filename=''):
    text = ''
    file1 = filename
    file2 = filename[:-4] + '.@@@'
    try:
        while (os.path.isfile(file2)):
            os.remove(file2)
            time.sleep(0.10)
        if (os.path.isfile(file1)):
            os.rename(file1, file2)
            time.sleep(0.10)
        if (os.path.isfile(file2)):
            r = codecs.open(file2, 'r', 'utf-8-sig')
            for t in r:
                t = t.replace('\r', '')
                text += t
            r.close
            r = None
            time.sleep(0.25)
        while (os.path.isfile(file2)):
            os.remove(file2)
            time.sleep(0.10)
    except:
        pass
    return text

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

def kill_pid(pid, ):
    if (os.name == 'nt'):
        try:
            kill = subprocess.Popen(['taskkill', '/pid', str(pid), '/f', ], \
                    shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
            kill.wait()
            kill.terminate()
            kill = None
            return True
        except Exception as e:
            pass
    else:
        try:
            kill = subprocess.Popen(['pkill', '-9', '-P', str(pid), ], \
                    shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
            kill.wait()
            kill.terminate()
            kill = None
            return True
        except Exception as e:
            pass
    return False

def kill_name(name, ):
    if (os.name == 'nt'):
        try:
            kill = subprocess.Popen(['taskkill', '/im', name + '.exe', '/f', ], \
                    shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
            kill.wait()
            kill.terminate()
            kill = None
            return True
        except Exception as e:
            pass
    else:
        try:
            kill = subprocess.Popen(['pkill', '-9', '-f', name, ], \
                    shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
            kill.wait()
            kill.terminate()
            kill = None
            return True
        except Exception as e:
            pass
    return False



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "web_operation_agent"
        self.func_ver  = "v0.20250101"
        self.func_auth = "1jXikXB9c2wa1/yxpsUghGPqyTvs61SjiN1lEiczdJo="
        self.function  = {
            "name": self.func_name,
            "description": \
"""
この機能は、ユーザーからブラウザ操作の指示があった場合に実行する。
この機能から、自律的にブラウザ操作が可能なAIエージェント Web-Operator(ウェブオペレーター) が実行される。
この機能で、AIエージェント Web-Operator(ウェブオペレーター) によりウェブ操作を実行し、その結果を取得することができる。
社内システム(Web)の操作は、Monjyu(もんじゅ:execute_monjyu_request) 経由で'operation_internal_web_systems'から、この機能を使います。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) agent"
                    },
                    "request_text": {
                        "type": "string",
                        "description": "依頼文字列 例) Google検索のページ(https://google.co.jp/)を表示して停止。"
                    },
                },
                "required": ["request_text"]
            }
        }

        self.start_time = None
        self.ext_python = None
        self.ext_pid    = None
        res = self.func_reset()
        self.start_time = time.time()
        self.last_time  = 0

        # 設定
        self.agent_models   = AGENT_MODELS
        self.agent_engine   = AGENT_ENGINE
        self.agent_model    = AGENT_MODEL
        self.agent_max_step = '10'
        #self.agent_browser  = 'chromium' # chromium, chrome,
        self.agent_browser  = 'chrome' # chromium, chrome,

        # main,data,addin,botFunc,
        self.main    = None
        self.data    = None
        self.addin   = None
        self.botFunc = None

    def __del__(self, ):
        # Python 停止
        if (self.ext_python != None):
            try:
                self.ext_python.terminate()
                self.ext_python = None
                kill_pid(self.ext_pid)
                kill_name('python')
                self.ext_pid    = None
            except:
                pass
        # Python kill!

    def func_reset(self, main=None, data=None, addin=None, botFunc=None, ):
        if (main is not None):
            self.main = main
        if (data is not None):
            self.data = data
        if (addin is not None):
            self.addin = addin
        if (botFunc is not None):
            self.botFunc = botFunc
        # 初回直後のリセットは無効
        if (self.start_time != None):
            if ((time.time() - self.start_time) < qTimeout_reset):
                return True

        # Python 停止
        self.__del__()

        # 結果クリア
        dummy = io_text_read(qIO_py2func)
        dummy = io_text_read(qIO_agent2live)

        # Python 初期化
        print(ext_python_init + ' loading')
        try:
            dir_path = os.path.dirname(__file__) + '/'
            self.ext_python = subprocess.Popen(['python', dir_path + ext_python_init,
            ], shell=True, )
            self.ext_pid    = self.ext_python.pid
        except Exception as e:
            print(e)
            raise RuntimeError('★Pythonの実行環境をインストールしてください！')

        # 初期化完了を待機
        wait_sec = qTimeout_init * 5
        ready = False
        checkTime = time.time()
        while ((time.time() - checkTime) < wait_sec):

            # 状況受信
            res      = io_text_read(qIO_py2func)
            res_text = res.strip()
            if (res_text != ''): 
                if (res_text != qText_ready):
                    print(res_text)
                else:
                    ready = True
                    break

            time.sleep(0.50)

        if (ready == False):
            # Python 停止
            self.__del__()
            # タイムアウトエラー
            raise RuntimeError(f"★{ ext_python_script }の起動タイムアウト({ wait_sec }s)が発生しました！")
        else:
            print(ext_python_init + ' ok')

        # 結果クリア
        dummy = io_text_read(qIO_py2func)
        dummy = io_text_read(qIO_agent2live)

        # Python 起動
        print(ext_python_script + ' loading')
        try:
            dir_path = os.path.dirname(__file__) + '/'
            self.ext_python = subprocess.Popen(['python', dir_path + ext_python_script,
            ], shell=True, )
            self.ext_pid    = self.ext_python.pid
        except Exception as e:
            print(e)
            raise RuntimeError('★Pythonの実行環境をインストールしてください！')

        # 準備完了を待機
        wait_sec = qTimeout_init
        ready = False
        checkTime = time.time()
        while ((time.time() - checkTime) < wait_sec):

            # 状況受信
            res      = io_text_read(qIO_py2func)
            res_text = res.strip()
            if (res_text != ''): 
                if (res_text != qText_ready):
                    print(res_text)
                else:
                    ready = True
                    break

            time.sleep(0.50)

        if (ready == False):
            # Python 停止
            self.__del__()
            # タイムアウトエラー
            raise RuntimeError(f"★{ ext_python_script }の起動タイムアウト({ wait_sec }s)が発生しました！")
        else:
            print(ext_python_script + ' ready')

        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 実行状況クリア
        dummy = io_text_read(qIO_py2func)
        dummy = io_text_read(qIO_agent2live)

        # 実行指示送信
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)

            try:
                if self.data is not None:
                    self.agent_engine = self.data.webOperator_setting['engine']
                    if (self.agent_engine == ''):
                        self.agent_engine = 'freeai'
                    self.agent_model = self.data.webOperator_setting['model']
                    if (self.agent_model == ''):
                        self.agent_model = list( self.agent_models[self.agent_engine].keys() )[0]
                    self.agent_max_step = self.data.webOperator_setting['max_step']
                    if (self.agent_max_step == ''):
                        self.agent_max_step = '10'
                    self.agent_browser = self.data.webOperator_setting['browser']
                    if (self.agent_browser == ''):
                        self.agent_browser = 'chromium'
                    #print(self.agent_engine, self.agent_model, self.agent_max_step)
            except Exception as e:
                print(e)

            # 連続実行はキャンセル！
            if  ((time.time() - self.last_time) < 30):
                self.last_time = time.time()
                dic = {}
                dic['result']     = 'ng'
                dic['error_text'] = '先ほどの依頼を実行中です。連続した要求には対応していません。'
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print('  --> ', json_dump)
                return json_dump

            dic = {}
            dic['runMode']      = args_dic.get('runMode', 'agent')
            dic['request_text'] = args_dic.get('request_text', '')
            dic['engine']       = self.agent_engine
            dic['model']        = self.agent_model
            dic['max_step']     = self.agent_max_step
            dic['browser']      = self.agent_browser
            json_dump = json.dumps(dic, ensure_ascii=False, )
            res = io_text_write(qIO_func2py, json_dump)
            self.last_time = time.time()

        # 実行開始を待機
        start = False
        checkTime = time.time()
        while ((time.time() - checkTime) < qTimeout_start):

            # 実行状況受信
            res      = io_text_read(qIO_py2func)
            res_text = res.strip()
            if (res_text != ''): 
                if (res_text != qText_start):
                    #print(res_text)
                    pass
                else:
                    start = True
                    break

            time.sleep(0.50)

        # タイムアウトエラー
        if (start == False):

            # エラー結果
            dic = {}
            dic['result']     = 'ng'
            dic['error_text'] = f"実行開始タイムアウト({ qTimeout_start }s)エラーが発生しました" 
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump

        # 実行完了を待機
        complete = False
        res_text = ''
        checkTime = time.time()
        while ((time.time() - checkTime) < qTimeout_proc):

            # 実行状況受信
            res      = io_text_read(qIO_py2func)
            res_text = res.strip()
            if (res_text != ''): 
                if (res_text.find(qText_complete) < 0):
                    #print(res_text)
                    pass
                else:
                    complete = True
                    res_text = res_text.replace(qText_complete, '')
                    res_text = res_text.strip()
                    break

        # 実行結果
        if (complete == True):
            json_dump = res_text
            #print('  --> ', json_dump)
            return json_dump
        else:
            dic = {}
            dic['result']     = 'ng'
            dic['error_text'] = f"実行タイムアウト({ qTimeout_proc }s)エラーが発生しました" 
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump



if __name__ == '__main__':

    ext = _class()

    json_kwargs= '{ "request_text" : "兵庫県三木市の天気を調べてください。" }'
    print(ext.func_proc(json_kwargs))

    time.sleep(90)

    json_kwargs= '{ "request_text": "表示中のページを要約してください。" }'    
    print(ext.func_proc(json_kwargs))

    time.sleep(180)


