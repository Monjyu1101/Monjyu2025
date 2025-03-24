#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/konsan1101
# Thank you for keeping the rules.
# ------------------------------------------------

# RiKi_Monjyu.py

import sys
import os
import time
import datetime
import codecs
import glob
import shutil
import random
import threading
import multiprocessing

import asyncio

# ダミーインポート(pyinstaller用)
#import pip
import keyboard
import screeninfo
from playsound3 import playsound
import pyautogui
import pyperclip
import hashlib
import PIL  # Pillow
from PIL import Image, ImageGrab, ImageTk, ImageEnhance
import numpy
import cv2
import pandas
import openpyxl
import pyodbc
import sqlalchemy
import matplotlib
import seaborn
import pytesseract
import websocket

# google
from google import genai
from google.genai import types

# win32/OCR
import pytesseract
if (os.name == 'nt'):
    import win32clipboard
    import comtypes.client
    import comtypes.stream
    import winocr

# seleniumモジュールのインポート
from selenium import webdriver
from selenium.webdriver import Edge
from selenium.webdriver import Chrome
from selenium.webdriver import Firefox
from selenium.webdriver import Safari
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import webdriver_manager.chrome
import webdriver_manager.firefox
if (os.name == 'nt'):
    import webdriver_manager.microsoft

# PDF解析用モジュールのインポート
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

# 音声関連モジュールのインポート
import gtts
try:
    import googletrans
except:
    pass
import pyaudio
import speech_recognition as sr



# パス設定
qPath_base = os.path.dirname(sys.argv[0]) + '/'
if (qPath_base == '/'):
    qPath_base = os.getcwd() + '/'
else:
    os.chdir(qPath_base)

# インターフェース
qPath_temp    = 'temp/'
qPath_log     = 'temp/_log/'
qPath_work    = 'temp/_work/'
qPath_input   = 'temp/input/'
qPath_output  = 'temp/output/'
qPath_sandbox = 'temp/sandbox/'

# コアAIのポート番号設定
CORE_PORT = 8000
SUB_BASE  = 8100

# 共通ルーチンのインポート
import _v6__qFunc
qFunc = _v6__qFunc.qFunc_class()
import _v6__qLog
qLog = _v6__qLog.qLog_class()

# 処理ルーチンのインポート
import RiKi_Monjyu__conf
import RiKi_Monjyu__data
import RiKi_Monjyu__addin
import RiKi_Monjyu__coreai
import RiKi_Monjyu__subai
import RiKi_Monjyu__webui
import speech_bot_function

# シグナル処理
import signal
def signal_handler(signal_number, stack_frame):
    print(os.path.basename(__file__), 'accept signal =', signal_number)

#signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGINT,  signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)



# 実行モードの設定
runMode = 'debug'
numSubAIs = '48'
if getattr(sys, 'frozen', False):
    numSubAIs = '128'



class _main_class:
    def __init__(self):
        self.main_all_ready = False

    def init(self, runMode='debug', qLog_fn=''):
        self.runMode = runMode
        # ログ設定
        self.proc_name = 'main'
        self.proc_id = '{0:10s}'.format(self.proc_name).replace(' ', '_')
        if not os.path.isdir(qPath_log):
            os.makedirs(qPath_log)
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        qLog.init(mode='logger', filename=qLog_fn)
        qLog.log('info', self.proc_id, 'init')
        return True

if __name__ == '__main__':
    main_name = 'Monjyu'
    main_id = '{0:10s}'.format(main_name).replace(' ', '_')

    # 制限日設定
    limit_date = '{:1d}{:1d}'.format(int(float(3.0)), int(float(1.0)))
    limit_date = '{:1d}{:1d}'.format(int(float(1.0)), int(float(2.0))) + '/' + limit_date
    limit_date = '/' + limit_date
    limit_date = '{:3d}{:1d}'.format(int(float(202.0)), int(float(6.0))) + limit_date
    #limit_date = '2026/12/31'
    dt = datetime.datetime.now()
    dateinfo_today = dt.strftime('%Y/%m/%d')
    dt = datetime.datetime.strptime(limit_date, '%Y/%m/%d') + datetime.timedelta(days=-60)
    dateinfo_start = dt.strftime('%Y/%m/%d')
    main_start = time.time()

    # ディレクトリ作成
    qFunc.makeDirs(qPath_temp, remove=False)
    qFunc.makeDirs(qPath_log, remove=False)
    qFunc.makeDirs(qPath_work, remove=False)
    qFunc.makeDirs(qPath_input, remove=False)
    qFunc.makeDirs(qPath_output, remove=False)
    qFunc.makeDirs(qPath_sandbox, remove=False)

    # ログの初期化
    nowTime = datetime.datetime.now()
    basename = os.path.basename(__file__)
    basename = basename.replace('.py', '')
    qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + basename + '.log'
    qLog.init(mode='logger', filename=qLog_fn)
    qLog.log('info', main_id, 'init')
    qLog.log('info', main_id, basename + ' runMode, ... ')

    # パラメータの取得
    if True:
        if len(sys.argv) >= 2:
            runMode = str(sys.argv[1]).lower()
        if len(sys.argv) >= 3:
            numSubAIs = str(sys.argv[2])
        qLog.log('info', main_id, 'runMode   = ' + str(runMode))
        qLog.log('info', main_id, 'numSubAIs = ' + str(numSubAIs))

    # 初期設定
    if True:
         # ライセンス制限
        if (dateinfo_today >= dateinfo_start):
            qLog.log('warning', main_id, '利用ライセンスは、 ' + limit_date + ' まで有効です。')
        if (dateinfo_today > limit_date):
            time.sleep(60)
            sys.exit(0)

        # ポート設定
        core_port = str(CORE_PORT)
        sub_base  = str(SUB_BASE)

        # main 初期化
        main = _main_class()
        main.init(runMode=runMode, qLog_fn=qLog_fn)
        
        # conf 初期化
        conf = RiKi_Monjyu__conf._conf_class()
        conf.init(runMode=runMode, qLog_fn=qLog_fn)

        # 環境変数設定
        if  (conf.openai_organization[:1] != '<'):
            os.environ['OPENAI_ORGANIZATION'] = conf.openai_organization
        if  (conf.openai_key_id[:1] != '<'):
            os.environ['OPENAI_API_KEY'] = conf.openai_key_id
        if  (conf.freeai_key_id[:1] != '<'):
            os.environ['FREEAI_API_KEY'] = conf.freeai_key_id
            os.environ['GOOGLE_API_KEY'] = conf.freeai_key_id
            os.environ['REACT_APP_GEMINI_API_KEY'] = conf.freeai_key_id
        if  (conf.freeai_key_id[:1] == '<') \
        and (conf.gemini_key_id[:1] != '<'):
            os.environ['GOOGLE_API_KEY'] = conf.gemini_key_id
            os.environ['REACT_APP_GEMINI_API_KEY'] = conf.gemini_key_id
        if  (conf.claude_key_id[:1] != '<'):
            os.environ['ANTHROPIC_API_KEY'] = conf.claude_key_id

        # data 初期化
        data = RiKi_Monjyu__data._data_class(   runMode=runMode, qLog_fn=qLog_fn,
                                                main=main, conf=conf,
                                                core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)

        # addin 初期化
        addin = RiKi_Monjyu__addin._addin_class()
        addin.init(runMode=runMode, qLog_fn=qLog_fn,
                   addins_path='_extensions/monjyu/', secure_level='low')
        res, msg = addin.addins_load()
        if res != True or msg != '':
            print(msg)
            print()
        res, msg = addin.addins_reset()
        if res != True or msg != '':
            print(msg)
            print()

        # botFunction 初期化
        botFunc = speech_bot_function.botFunction()
        res, msg = botFunc.functions_load(
            functions_path='_extensions/function/', secure_level='low')
        if res != True or msg != '':
            print(msg)
            print()
        res, msg = botFunc.functions_reset()
        if res != True or msg != '':
            print(msg)
            print()

        # autoSandbox
        addin_module = addin.addin_modules.get('addin_autoSandbox', None)
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'addin_autoSandbox')
            except Exception as e:
                print(e)

        # ClipnMonjyu
        addin_module = addin.addin_modules.get('monjyu_UI_ClipnMonjyu', None)
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'monjyu_UI_ClipnMonjyu')
            except Exception as e:
                print(e)

        # task_worker
        addin_module = addin.addin_modules.get('monjyu_task_worker', None)
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(botFunc=botFunc, data=data, )
                    print('reset', 'monjyu_task_worker')
            except Exception as e:
                print(e)

        # key2Live_freeai
        liveai_enable = False
        addin_module = addin.addin_modules.get('monjyu_UI_key2Live_freeai', None)
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'monjyu_UI_key2Live_freeai')
                    liveai_enable = True

                    data.live_models['freeai']  = addin_module['class'].sub_proc.liveAPI.live_models
                    data.live_voices['freeai']  = addin_module['class'].sub_proc.liveAPI.live_voices
                    data.live_setting['freeai'] = { "live_model": addin_module['class'].sub_proc.liveAPI.live_model,
                                                    "live_voice": addin_module['class'].sub_proc.liveAPI.live_voice,
                                                    "shot_interval_sec": str(addin_module['class'].sub_proc.liveAPI.shot_interval_sec),
                                                    "clip_interval_sec": str(addin_module['class'].sub_proc.liveAPI.clip_interval_sec), }
            except Exception as e:
                print(e)

        # key2Live_openai
        #liveai_enable = False
        addin_module = addin.addin_modules.get('monjyu_UI_key2Live_openai', None)
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'monjyu_UI_key2Live_openai')
                    liveai_enable = True

                    data.live_models['openai']  = addin_module['class'].sub_proc.liveAPI.live_models
                    data.live_voices['openai']  = addin_module['class'].sub_proc.liveAPI.live_voices
                    data.live_setting['openai'] = { "live_model": addin_module['class'].sub_proc.liveAPI.live_model,
                                                    "live_voice": addin_module['class'].sub_proc.liveAPI.live_voice,
                                                    "shot_interval_sec": str(addin_module['class'].sub_proc.liveAPI.shot_interval_sec),
                                                    "clip_interval_sec": str(addin_module['class'].sub_proc.liveAPI.clip_interval_sec), }
            except Exception as e:
                print(e)

        # web操作Agent
        webOperator_enable = False
        for module_dic in botFunc.function_modules.values():
            if (module_dic['func_name'] == 'web_operation_agent'):
                try:
                    if (module_dic['onoff'] == 'on'):
                        func_reset = module_dic['func_reset']
                        res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                        print('reset', 'web_operation_agent')
                        webOperator_enable = True

                        data.webOperator_models['freeai'] = module_dic['class'].agent_models['freeai']
                        data.webOperator_models['openai'] = module_dic['class'].agent_models['openai']
                        data.webOperator_models['claude'] = module_dic['class'].agent_models['claude']
                        data.webOperator_setting = {    'engine':   module_dic['class'].agent_engine,
                                                        'model':    module_dic['class'].agent_model,
                                                        'max_step': module_dic['class'].agent_max_step,
                                                        'browser':  module_dic['class'].agent_browser, }
                except Exception as e:
                    print(e)
                break

        # research操作Agent
        researchAgent_enable = False
        for module_dic in botFunc.function_modules.values():
            if (module_dic['func_name'] == 'research_operation_agent'):
                try:
                    if (module_dic['onoff'] == 'on'):
                        func_reset = module_dic['func_reset']
                        res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                        print('reset', 'research_operation_agent')
                        researchAgent_enable = True

                        data.researchAgent_models['freeai'] = module_dic['class'].agent_models['freeai']
                        data.researchAgent_models['openai'] = module_dic['class'].agent_models['openai']
                        data.researchAgent_models['claude'] = module_dic['class'].agent_models['claude']
                        data.researchAgent_setting = {  'engine':   module_dic['class'].agent_engine,
                                                        'model':    module_dic['class'].agent_model,
                                                        'max_step': module_dic['class'].agent_max_step,
                                                        'browser':  module_dic['class'].agent_browser, }
                except Exception as e:
                    print(e)
                break

    # コアAI起動
    if True:
        coreai = RiKi_Monjyu__coreai.CoreAiClass(   runMode=runMode, qLog_fn=qLog_fn,
                                                    main=main, conf=conf, data=data, addin=addin, botFunc=botFunc,
                                                    core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)
        coreai_thread = threading.Thread(target=coreai.run)
        coreai_thread.daemon = True
        coreai_thread.start()

    # サブAI起動
    if True:
        # サブプロフィール設定(ランダム)
        subai_profiles = random.sample(range(int(numSubAIs)), int(numSubAIs))

        subai_class = {}
        subai_thread = {}
        for n in range(int(numSubAIs)):
            self_port = str(SUB_BASE + n + 1)
            subai_class[n] = RiKi_Monjyu__subai.SubAiClass( runMode=runMode, qLog_fn=qLog_fn,
                                                            main=main, conf=conf, data=data, addin=addin, botFunc=botFunc,
                                                            coreai=coreai, 
                                                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs,
                                                            self_port=self_port, profile_number=subai_profiles[n])
            subai_thread[n] = threading.Thread(target=subai_class[n].run)
            subai_thread[n].daemon = True
            subai_thread[n].start()

    # ウェブUI起動
    if True:
        self_port = str(CORE_PORT + 8)
        webui_class = RiKi_Monjyu__webui.WebUiClass(runMode=runMode, qLog_fn=qLog_fn,
                                                    main=main, conf=conf, data=data, addin=addin, botFunc=botFunc,
                                                    coreai=coreai, 
                                                    core_port=core_port, sub_base=sub_base, num_subais=numSubAIs,
                                                    self_port=self_port)
        webui_thread = threading.Thread(target=webui_class.run)
        webui_thread.daemon = True
        webui_thread.start()

    # 起動メッセージ
    print()
    qLog.log('info', main_id, "================================================================================================")
    qLog.log('info', main_id, " Thank you for using our systems.")
    qLog.log('info', main_id, " To use [ Assistant AI 文殊/Monjyu(もんじゅ) ], Access 'http://localhost:8008/' in your browser.")
    if (liveai_enable == True):
        qLog.log('info', main_id, " To use [ Live AI 力/RiKi(りき) ], Press ctrl-l or ctrl-r three times.")
    if (webOperator_enable == True):
        qLog.log('info', main_id, " To use [ Agentic AI Web-Operator(ウェブオペレーター) ], Specify use at the prompt.")
    if (researchAgent_enable == True):
        qLog.log('info', main_id, " To use [ Agentic AI Research-Agent(リサーチエージェント) ], Specify use at the prompt.")
    qLog.log('info', main_id, "================================================================================================")
    print()
    main.main_all_ready = True

    # モデル情報設定
    _ = asyncio.run( coreai.get_models(req_mode='chat') )    

    # 無限ループでプロセスを監視
    while True:
        time.sleep(5)


