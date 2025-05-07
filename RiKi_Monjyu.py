#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'main'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.getLogger('comtypes.client._code_cache').setLevel(logging.WARNING)
logging.getLogger('uvicorn').setLevel(logging.WARNING)
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
logging.getLogger('uvicorn.app').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('google_genai').setLevel(logging.WARNING)

import sys
#from rainbow_logging_handler import RainbowLoggingHandler
#logger_format   = logging.Formatter('%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s')
#rainbow_handler = RainbowLoggingHandler(sys.stderr, color_funcName=('black', 'yellow', True))
#rainbow_handler.setFormatter(logger_format)
#for h in logger.handlers:
#    logger.removeHandler(h)
#logger.addHandler(rainbow_handler)


import os
import time
import datetime
import glob
import shutil
import random
import threading

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

# 処理ルーチンのインポート
import RiKi_Monjyu__conf
import RiKi_Monjyu__data
import RiKi_Monjyu__addin
import RiKi_Monjyu__mcpHost
import RiKi_Monjyu__coreai0
import RiKi_Monjyu__coreai1
import RiKi_Monjyu__coreai2
import RiKi_Monjyu__coreai4
import RiKi_Monjyu__coreai5
import RiKi_Monjyu__subai
import RiKi_Monjyu__webui
import speech_bot__function

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



def makeDirs(ppath, remove=False, ):
    try:
        if (len(ppath) > 0):
            path=ppath.replace('\\', '/')
            if (path[-1:] != '/'):
                path += '/'
            if (not os.path.isdir(path[:-1])):
                os.makedirs(path[:-1])
            else:
                if (remove == True):
                    try:
                        shutil.rmtree(path, ignore_errors=True, )
                    except Exception as e:
                        pass
                elif (str(remove).isdigit()):
                    files = glob.glob(path + '*')
                    for f in files:
                        try:
                            nowTime   = datetime.datetime.now()
                            fileStamp = os.path.getmtime(f)
                            fileTime  = datetime.datetime.fromtimestamp(fileStamp)
                            td = nowTime - fileTime
                            if (td.days >= int(remove)):
                                os.remove(f) 
                        except Exception as e:
                            pass

    except Exception as e:
        pass
    return True


class _main_class:
    def __init__(self):
        self.main_all_ready = False

    def init(self, runMode='debug', qLog_fn=''):
        self.runMode = runMode
        logger.debug('init')
        return True

if __name__ == '__main__':

    # 制限日設定
    limit_date = '{:1d}{:1d}'.format(int(float(3.0)), int(float(1.0)))
    limit_date = '{:1d}{:1d}'.format(int(float(1.0)), int(float(0.0))) + '/' + limit_date
    limit_date = '/' + limit_date
    limit_date = '{:3d}{:1d}'.format(int(float(202.0)), int(float(6.0))) + limit_date
    #limit_date = '2026/10/31'
    dt = datetime.datetime.now()
    dateinfo_today = dt.strftime('%Y/%m/%d')
    dt = datetime.datetime.strptime(limit_date, '%Y/%m/%d') + datetime.timedelta(days=-180)
    dateinfo_start = dt.strftime('%Y/%m/%d')
    main_start = time.time()

    # ディレクトリ作成
    makeDirs(qPath_temp, remove=False)
    makeDirs(qPath_log, remove=False)
    makeDirs(qPath_work, remove=False)
    makeDirs(qPath_input, remove=False)
    makeDirs(qPath_output, remove=False)
    makeDirs(qPath_sandbox, remove=False)

    # ログの初期化
    nowTime = datetime.datetime.now()
    basename = os.path.basename(__file__)
    basename = basename.replace('.py', '')
    qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + basename + '.log'
    #qLog.init(mode='logger', filename=qLog_fn)
    logger.info('init')
    logger.info(f'{basename} runMode, ... ')

    # パラメータの取得
    if True:
        if len(sys.argv) >= 2:
            runMode = str(sys.argv[1]).lower()
        if len(sys.argv) >= 3:
            numSubAIs = str(sys.argv[2])
        logger.info(f'runMode   = {runMode}')
        logger.info(f'numSubAIs = {numSubAIs}')

    # 初期設定
    if True:
         # ライセンス制限
        if (dateinfo_today >= dateinfo_start):
            logger.warning(f'利用ライセンス(Python3.10support)は、 {limit_date} まで有効です。')
        if (dateinfo_today > limit_date):
            time.sleep(60)
            sys.exit(0)

        # ポート設定
        core_port = str(CORE_PORT)
        sub_base  = str(SUB_BASE)

    # main 初期化
    if True:
        main = _main_class()
        main.init(runMode=runMode, qLog_fn=qLog_fn)
        
    # conf 初期化
    if True:
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
    if True:
        data = RiKi_Monjyu__data._data_class(   runMode=runMode, qLog_fn=qLog_fn,
                                                main=main, conf=conf,
                                                core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)

    # addin 初期化
    if True:
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
    if True:
        botFunc = speech_bot__function.botFunction()
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
        addin_module = addin.addin_modules.get('automatic_sandbox')
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'automatic_sandbox')
            except Exception as e:
                print(e)

        # ClipnMonjyu
        addin_module = addin.addin_modules.get('monjyu_UI_ClipnMonjyu')
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'monjyu_UI_ClipnMonjyu')
            except Exception as e:
                print(e)

        # task_worker
        addin_module = addin.addin_modules.get('extension_task_worker')
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(botFunc=botFunc, data=data, )
                    print('reset', 'extension_task_worker')
            except Exception as e:
                print(e)

        # key2Live_freeai
        liveai_enable = False
        addin_module = addin.addin_modules.get('extension_UI_key2Live_freeai')
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'extension_UI_key2Live_freeai')
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
        addin_module = addin.addin_modules.get('extension_UI_key2Live_openai')
        if (addin_module is not None):
            try:
                if (addin_module['onoff'] == 'on'):
                    func_reset = addin_module['func_reset']
                    res  = func_reset(main=main, data=data, addin=addin, botFunc=botFunc, )
                    print('reset', 'extension_UI_key2Live_openai')
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
        module_dic = botFunc.function_modules.get('web_operation_agent', None)
        if (module_dic is not None):
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

        # research操作Agent
        researchAgent_enable = False
        module_dic = botFunc.function_modules.get('research_operation_agent', None)
        if (module_dic is not None):
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

    # mcpHost起動
    if True:
        mcpHost = RiKi_Monjyu__mcpHost._mcpHost_class(  runMode=runMode, qLog_fn=qLog_fn,
                                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc)
        mcpHost_thread = threading.Thread(target=mcpHost.run)
        mcpHost_thread.daemon = True
        mcpHost_thread.start()

    # コアAI起動
    if True:
        coreai0 = RiKi_Monjyu__coreai0.coreai0_class(   runMode=runMode, qLog_fn=qLog_fn,
                                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                        core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)
        coreai0_thread = threading.Thread(target=coreai0.run)
        coreai0_thread.daemon = True
        coreai0_thread.start()

        coreai1 = RiKi_Monjyu__coreai1.coreai1_class(   runMode=runMode, qLog_fn=qLog_fn,
                                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                        coreai=coreai0, 
                                                        core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)
        coreai1_thread = threading.Thread(target=coreai1.run)
        coreai1_thread.daemon = True
        coreai1_thread.start()

        coreai2 = RiKi_Monjyu__coreai2.coreai2_class(   runMode=runMode, qLog_fn=qLog_fn,
                                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                        coreai=coreai0, 
                                                        core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)
        coreai2_thread = threading.Thread(target=coreai2.run)
        coreai2_thread.daemon = True
        coreai2_thread.start()

        coreai4 = RiKi_Monjyu__coreai4.coreai4_class(   runMode=runMode, qLog_fn=qLog_fn,
                                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                        coreai=coreai0, 
                                                        core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)
        coreai4_thread = threading.Thread(target=coreai4.run)
        coreai4_thread.daemon = True
        coreai4_thread.start()

        coreai5 = RiKi_Monjyu__coreai5.coreai5_class(   runMode=runMode, qLog_fn=qLog_fn,
                                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                        coreai=coreai0, 
                                                        core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)
        coreai5_thread = threading.Thread(target=coreai5.run)
        coreai5_thread.daemon = True
        coreai5_thread.start()

    # サブAI起動
    if True:
        # サブプロフィール設定(ランダム)
        subai_profiles = random.sample(range(int(numSubAIs)), int(numSubAIs))

        subai_class = {}
        subai_thread = {}
        for n in range(int(numSubAIs)):
            self_port = str(SUB_BASE + n + 1)
            subai_class[n] = RiKi_Monjyu__subai.SubAiClass( runMode=runMode, qLog_fn=qLog_fn,
                                                            main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                            coreai=coreai0, 
                                                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs,
                                                            self_port=self_port, profile_number=subai_profiles[n])
            subai_thread[n] = threading.Thread(target=subai_class[n].run)
            subai_thread[n].daemon = True
            subai_thread[n].start()

    # ウェブUI起動
    if True:
        self_port = str(CORE_PORT + 8)
        webui_class = RiKi_Monjyu__webui.WebUiClass(runMode=runMode, qLog_fn=qLog_fn,
                                                    main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                    coreai=coreai0, 
                                                    core_port=core_port, sub_base=sub_base, num_subais=numSubAIs,
                                                    self_port=self_port)
        webui_thread = threading.Thread(target=webui_class.run)
        webui_thread.daemon = True
        webui_thread.start()

    # 起動メッセージ
    if True:
        # 30秒待機
        time.sleep(30)

        print()
        logger.info("=============================================================================")
        logger.info(" Thank you for using our systems.")
        logger.info(" Multiple AI Platforms with MCP, Monjyu (もんじゅ), 'http://localhost:8008/'.")
        if (liveai_enable == True):
            logger.info(" Live AI 力/RiKi(りき), Press ctrl-l or ctrl-r three times.")
        if (webOperator_enable == True):
            logger.info(" Agentic AI Web-Operator(ウェブオペレーター), Specify use at the prompt.")
        if (researchAgent_enable == True):
            logger.info(" Agentic AI Research-Agent(リサーチエージェント), Specify use at the prompt.")
        logger.info("=============================================================================")
        print()

    # モデル情報設定
    asyncio.run( coreai0.get_models(req_mode='chat') )

    # 15秒待機
    time.sleep(15)
    print()
    logger.info("Monjyu (もんじゅ) is Ready,")

    # 準備完了
    main.main_all_ready = True

    # 無限ループでプロセスを監視
    while True:
        time.sleep(5)


