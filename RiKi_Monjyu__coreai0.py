#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'coreai:0'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)


import os
import time
import datetime

import json
import requests

from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

import random
import threading

import socket
qHOSTNAME = socket.gethostname().lower()

# パスの設定
qPath_temp    = 'temp/'
qPath_log     = 'temp/_log/'
qPath_input   = 'temp/input/'
qPath_output  = 'temp/output/'
qPath_tts     = 'temp/s6_5tts_txt/'
qPath_sandbox = 'temp/sandbox/'

# 共通ルーチン
import RiKi_Monjyu__subbot

# 定数の定義
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30
DELETE_SESSIONS_SEC   = 1200
LIST_RESULT_LIMITSEC = 1800
LIST_RESULT_AUTOCHECK = 120

# リクエストデータモデル(Mini)
class RequestMiniModel(BaseModel):
    user_id: str
    from_port: str
    to_port: str
    req_mode: str
    system_text: str
    request_text: str
    input_text: str
    file_names: list[str]
    result_savepath: str
    result_schema: str

# リクエストデータモデル(Full)
class RequestFullModel(BaseModel):
    user_id: str
    from_port: str
    to_port: str
    req_mode: str
    req_engine: str
    req_functions: str
    req_reset: str
    max_retry: str
    max_ai_count: str
    before_proc: str
    before_engine: str
    after_proc: str
    after_engine: str
    check_proc: str
    check_engine: str
    system_text: str
    request_text: str
    input_text: str
    file_names: list[str]
    result_savepath: str
    result_schema: str


class main_class:
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        # コアAIクラスの初期化とスレッドの開始
        coreai0 = coreai0_class(runMode=runMode, qLog_fn=qLog_fn,
                                main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                core_port=core_port, sub_base=sub_base, num_subais=num_subais, )
        coreai0_thread = threading.Thread(target=coreai0.run, daemon=True, )
        coreai0_thread.start()
        while True:
            time.sleep(5)


class coreai0_class:
    """
    コアAIクラス
    サブAIとの通信や結果管理、FastAPIサーバーの管理を行う。
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        self.runMode = runMode
        self_port = core_port

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug(f"init:{self_port}")

        # 設定
        self.main       = main
        self.conf       = conf
        self.data       = data
        self.addin      = addin
        self.botFunc    = botFunc
        self.mcpHost    = mcpHost
        self.core_port  = core_port
        self.sub_base   = sub_base
        self.num_subais = int(num_subais)
        self.self_port  = self_port
        self.local_endpoint2 = f'http://localhost:{ int(self.core_port) + 2 }'
        self.webui_endpoint8 = f'http://{ qHOSTNAME }:{ int(self.core_port) + 8 }'

        # 自己bot設定
        self.subbot = RiKi_Monjyu__subbot.ChatClass(runMode=runMode, qLog_fn=qLog_fn, 
                                                    main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                    coreai=None,
                                                    core_port=core_port, self_port=self_port)
        self.history    = []

        # スレッドロック
        self.thread_lock = threading.Lock()

        # 最終回答の保存
        self.last_models_list = None
        self.last_input_files = None
        self.last_image_file = None
        self.last_image_time = 0

        # サブAIの順番をランダムにシャッフル
        if (self.data is not None):
            self.random_order = random.sample(self.data.subai_ports, len(self.data.subai_ports))
        self.current_order_index = 0

        # FastAPI設定
        self.app = FastAPI()
        self.app.get("/")(self.root)
        self.app.get("/get_ready_count")(self.get_ready_count)
        self.app.get('/get_models')(self.get_models)
        self.app.get("/get_subai_info_all")(self.get_subai_info_all)
        self.app.get("/get_subai_statuses_all")(self.get_subai_statuses_all)
        self.app.get("/get_sessions_all")(self.get_sessions_all)
        self.app.get("/get_sessions_port")(self.get_sessions_port)
        self.app.get("/get_input_list")(self.get_input_list)
        self.app.post("/post_req")(self.post_req)
        self.app.post("/post_request")(self.post_request)

    async def root(self, request: Request):
        # Web UI にリダイレクト
        return RedirectResponse(url=self.webui_endpoint8 + '/')

    async def get_ready_count(self):
        """
        レディ状態とビジー状態のサブAI数を返す。
        """
        if (self.data is None):
            ready_count = 0
            busy_count = 0
            res = {'ready_count': ready_count, 'busy_count': busy_count}
            return JSONResponse(content=res)

        with self.thread_lock:
            ready_count = sum(1 for info in self.data.subai_info.values() if info['status'] == 'READY')
            busy_count = sum(1 for info in self.data.subai_info.values() if info['status'] in ['BUSY', 'SERIAL', 'PARALLEL', 'CHAT'])
        res = {'ready_count': ready_count, 'busy_count': busy_count}
        return JSONResponse(content=res)

    async def get_models(self, req_mode: str) -> Dict[str, str]:
        """ 有効AI名取得(応答) """
        if (self.last_models_list is not None):
            return self.last_models_list

        models = {}
        openrt_first_auth = False

        # ChatGPT
        if self.subbot.llm.chatgpt_enable is None:
            self.subbot.llm.chatgpt_auth()
            if self.subbot.llm.chatgpt_enable:
                logger.info(f"ChatGPT    : Ready, (Models count={ len(self.subbot.llm.chatgptAPI.models) })")
        if self.subbot.llm.chatgpt_enable:
            if (req_mode == 'chat'):
                models['[chatgpt]'] = '[ChatGPT]'
                if self.subbot.llm.chatgptAPI.a_nick_name:
                    models[self.subbot.llm.chatgptAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.chatgptAPI.a_nick_name
                if self.subbot.llm.chatgptAPI.b_nick_name:
                    models[self.subbot.llm.chatgptAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.chatgptAPI.b_nick_name
                if self.subbot.llm.chatgptAPI.v_nick_name:
                    models[self.subbot.llm.chatgptAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.chatgptAPI.v_nick_name
                if self.subbot.llm.chatgptAPI.x_nick_name:
                    models[self.subbot.llm.chatgptAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.chatgptAPI.x_nick_name

        # Respo
        if self.subbot.llm.respo_enable is None:
            self.subbot.llm.respo_auth()
            if self.subbot.llm.respo_enable:
                logger.info(f"Respo      : Ready, (Models count={ len(self.subbot.llm.respoAPI.models) })")
        if self.subbot.llm.respo_enable:
            if (req_mode == 'chat'):
                models['[respo]'] = '[Respo]'
                if self.subbot.llm.respoAPI.a_nick_name:
                    models[self.subbot.llm.respoAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.respoAPI.a_nick_name
                if self.subbot.llm.respoAPI.b_nick_name:
                    models[self.subbot.llm.respoAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.respoAPI.b_nick_name
                if self.subbot.llm.respoAPI.v_nick_name:
                    models[self.subbot.llm.respoAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.respoAPI.v_nick_name
                if self.subbot.llm.respoAPI.x_nick_name:
                    models[self.subbot.llm.respoAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.respoAPI.x_nick_name

        # Gemini
        if self.subbot.llm.gemini_enable is None:
            self.subbot.llm.gemini_auth()
            if self.subbot.llm.gemini_enable:
                logger.info(f"Gemini     : Ready, (Models count={ len(self.subbot.llm.geminiAPI.models) })")
        if self.subbot.llm.gemini_enable:
            if (req_mode == 'chat'):
                models['[gemini]'] = '[Gemini]'
                if self.subbot.llm.geminiAPI.a_enable and self.subbot.llm.geminiAPI.a_nick_name:
                    models[self.subbot.llm.geminiAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.geminiAPI.a_nick_name
                if self.subbot.llm.geminiAPI.b_enable and self.subbot.llm.geminiAPI.b_nick_name:
                    models[self.subbot.llm.geminiAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.geminiAPI.b_nick_name
                if self.subbot.llm.geminiAPI.v_enable and self.subbot.llm.geminiAPI.v_nick_name:
                    models[self.subbot.llm.geminiAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.geminiAPI.v_nick_name
                if self.subbot.llm.geminiAPI.x_enable and self.subbot.llm.geminiAPI.x_nick_name:
                    models[self.subbot.llm.geminiAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.geminiAPI.x_nick_name

        # FreeAI
        if self.subbot.llm.freeai_enable is None:
            self.subbot.llm.freeai_auth()
            if self.subbot.llm.freeai_enable:
                logger.info(f"FreeAI     : Ready, (Models count={ len(self.subbot.llm.freeaiAPI.models) })")
        if self.subbot.llm.freeai_enable:
            if True:
                models['[freeai]'] = '[FreeAI]'
                if self.subbot.llm.freeaiAPI.a_enable and self.subbot.llm.freeaiAPI.a_nick_name:
                    models[self.subbot.llm.freeaiAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.freeaiAPI.a_nick_name
                if self.subbot.llm.freeaiAPI.b_enable and self.subbot.llm.freeaiAPI.b_nick_name:
                    models[self.subbot.llm.freeaiAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.freeaiAPI.b_nick_name
                if self.subbot.llm.freeaiAPI.v_enable and self.subbot.llm.freeaiAPI.v_nick_name:
                    models[self.subbot.llm.freeaiAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.freeaiAPI.v_nick_name
                if self.subbot.llm.freeaiAPI.x_enable and self.subbot.llm.freeaiAPI.x_nick_name:
                    models[self.subbot.llm.freeaiAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.freeaiAPI.x_nick_name

        # Claude
        if self.subbot.llm.claude_enable is None:
            self.subbot.llm.claude_auth()
            if self.subbot.llm.claude_enable:
                logger.info(f"Claude     : Ready, (Models count={ len(self.subbot.llm.claudeAPI.models) })")
        if self.subbot.llm.claude_enable:
            if (req_mode == 'chat'):
                models['[claude]'] = '[Claude]'
                if self.subbot.llm.claudeAPI.a_enable and self.subbot.llm.claudeAPI.a_nick_name:
                    models[self.subbot.llm.claudeAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.claudeAPI.a_nick_name
                if self.subbot.llm.claudeAPI.b_enable and self.subbot.llm.claudeAPI.b_nick_name:
                    models[self.subbot.llm.claudeAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.claudeAPI.b_nick_name
                if self.subbot.llm.claudeAPI.v_enable and self.subbot.llm.claudeAPI.v_nick_name:
                    models[self.subbot.llm.claudeAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.claudeAPI.v_nick_name
                if self.subbot.llm.claudeAPI.x_enable and self.subbot.llm.claudeAPI.x_nick_name:
                    models[self.subbot.llm.claudeAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.claudeAPI.x_nick_name

        # OpenRouter
        if self.subbot.llm.openrt_enable is None:
            self.subbot.llm.openrt_auth()
            if self.subbot.llm.openrt_enable:
                logger.info(f"OpenRouter : Ready, (Models count={ len(self.subbot.llm.openrtAPI.models) })")
                openrt_first_auth = True
        if self.subbot.llm.openrt_enable:
            if True:
                models['[openrt]'] = '[OpenRouter]'
                if self.subbot.llm.openrtAPI.a_enable and self.subbot.llm.openrtAPI.a_nick_name:
                    models[self.subbot.llm.openrtAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.openrtAPI.a_nick_name
                if self.subbot.llm.openrtAPI.b_enable and self.subbot.llm.openrtAPI.b_nick_name:
                    models[self.subbot.llm.openrtAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.openrtAPI.b_nick_name
                if self.subbot.llm.openrtAPI.v_enable and self.subbot.llm.openrtAPI.v_nick_name:
                    models[self.subbot.llm.openrtAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.openrtAPI.v_nick_name
                if self.subbot.llm.openrtAPI.x_enable and self.subbot.llm.openrtAPI.x_nick_name:
                    models[self.subbot.llm.openrtAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.openrtAPI.x_nick_name

        # Perplexity
        if self.subbot.llm.perplexity_enable is None:
            self.subbot.llm.perplexity_auth()
            if self.subbot.llm.perplexity_enable:
                logger.info(f"Perplexity : Ready, (Models count={ len(self.subbot.llm.perplexityAPI.models) })")
        if self.subbot.llm.perplexity_enable:
            if (req_mode == 'chat'):
                models['[perplexity]'] = '[Perplexity]'
                if self.subbot.llm.perplexityAPI.a_enable and self.subbot.llm.perplexityAPI.a_nick_name:
                    models[self.subbot.llm.perplexityAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.perplexityAPI.a_nick_name
                if self.subbot.llm.perplexityAPI.b_enable and self.subbot.llm.perplexityAPI.b_nick_name:
                    models[self.subbot.llm.perplexityAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.perplexityAPI.b_nick_name
                if self.subbot.llm.perplexityAPI.v_enable and self.subbot.llm.perplexityAPI.v_nick_name:
                    models[self.subbot.llm.perplexityAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.perplexityAPI.v_nick_name
                if self.subbot.llm.perplexityAPI.x_enable and self.subbot.llm.perplexityAPI.x_nick_name:
                    models[self.subbot.llm.perplexityAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.perplexityAPI.x_nick_name

        # Grok
        if self.subbot.llm.grok_enable is None:
            self.subbot.llm.grok_auth()
            if self.subbot.llm.grok_enable:
                logger.info(f"Grok       : Ready, (Models count={ len(self.subbot.llm.grokAPI.models) })")
        if self.subbot.llm.grok_enable:
            if (req_mode == 'chat'):
                models['[grok]'] = '[Grok]'
                if self.subbot.llm.grokAPI.a_enable and self.subbot.llm.grokAPI.a_nick_name:
                    models[self.subbot.llm.grokAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.grokAPI.a_nick_name
                if self.subbot.llm.grokAPI.b_enable and self.subbot.llm.grokAPI.b_nick_name:
                    models[self.subbot.llm.grokAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.grokAPI.b_nick_name
                if self.subbot.llm.grokAPI.v_enable and self.subbot.llm.grokAPI.v_nick_name:
                    models[self.subbot.llm.grokAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.grokAPI.v_nick_name
                if self.subbot.llm.grokAPI.x_enable and self.subbot.llm.grokAPI.x_nick_name:
                    models[self.subbot.llm.grokAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.grokAPI.x_nick_name

        # Groq
        if self.subbot.llm.groq_enable is None:
            self.subbot.llm.groq_auth()
            if self.subbot.llm.groq_enable:
                logger.info(f"Groq       : Ready, (Models count={ len(self.subbot.llm.groqAPI.models) })")
        if self.subbot.llm.groq_enable:
            if (req_mode == 'chat'):
                models['[groq]'] = '[Groq]'
                if self.subbot.llm.groqAPI.a_enable and self.subbot.llm.groqAPI.a_nick_name:
                    models[self.subbot.llm.groqAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.groqAPI.a_nick_name
                if self.subbot.llm.groqAPI.b_enable and self.subbot.llm.groqAPI.b_nick_name:
                    models[self.subbot.llm.groqAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.groqAPI.b_nick_name
                if self.subbot.llm.groqAPI.v_enable and self.subbot.llm.groqAPI.v_nick_name:
                    models[self.subbot.llm.groqAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.groqAPI.v_nick_name
                if self.subbot.llm.groqAPI.x_enable and self.subbot.llm.groqAPI.x_nick_name:
                    models[self.subbot.llm.groqAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.groqAPI.x_nick_name

        # Ollama
        if self.subbot.llm.ollama_enable is None:
            self.subbot.llm.ollama_auth()
            if self.subbot.llm.ollama_enable:
                logger.info(f"Ollama     : Ready, (Models count={ len(self.subbot.llm.ollamaAPI.models) })")
        if self.subbot.llm.ollama_enable:
            if True:
                models['[ollama]'] = '[Ollama]'
                if self.subbot.llm.ollamaAPI.a_enable and self.subbot.llm.ollamaAPI.a_nick_name:
                    models[self.subbot.llm.ollamaAPI.a_nick_name.lower()] = ' ' + self.subbot.llm.ollamaAPI.a_nick_name
                if self.subbot.llm.ollamaAPI.b_enable and self.subbot.llm.ollamaAPI.b_nick_name:
                    models[self.subbot.llm.ollamaAPI.b_nick_name.lower()] = ' ' + self.subbot.llm.ollamaAPI.b_nick_name
                if self.subbot.llm.ollamaAPI.v_enable and self.subbot.llm.ollamaAPI.v_nick_name:
                    models[self.subbot.llm.ollamaAPI.v_nick_name.lower()] = ' ' + self.subbot.llm.ollamaAPI.v_nick_name
                if self.subbot.llm.ollamaAPI.x_enable and self.subbot.llm.ollamaAPI.x_nick_name:
                    models[self.subbot.llm.ollamaAPI.x_nick_name.lower()] = ' ' + self.subbot.llm.ollamaAPI.x_nick_name

        # openrtの情報でmodel情報を更新
        if (openrt_first_auth == True):
            sorted_model = {k: self.subbot.llm.openrtAPI.models[k] for k in sorted(self.subbot.llm.openrtAPI.models)}
            for key in sorted_model.keys():
                id = sorted_model[key]['id']
                token = sorted_model[key]['token']
                modality = sorted_model[key]['modality']
                date_ymd = sorted_model[key]['date']
                if (id.find('/') > 0):
                    model = id[id.find('/')+1:]

                    # chatgpt
                    modelx = model
                    if (modelx == 'o1'):
                        modelx =  'o1-2024-12-17'
                    if (modelx == 'o3-mini'):
                        modelx =  'o3-mini-2025-01-31'
                    if (model in self.subbot.llm.chatgptAPI.models):
                        self.subbot.llm.chatgptAPI.models[model]['token'] = str(token)
                        self.subbot.llm.chatgptAPI.models[model]['modality'] = str(modality)
                        #self.subbot.llm.chatgptAPI.models[model]['date'] = str(date_ymd)
                    if (modelx in self.subbot.llm.chatgptAPI.models):
                        self.subbot.llm.chatgptAPI.models[modelx]['token'] = str(token)
                        self.subbot.llm.chatgptAPI.models[modelx]['modality'] = str(modality)
                        #self.subbot.llm.chatgptAPI.models[modelx]['date'] = str(date_ymd)

                    # respo
                    if (model in self.subbot.llm.respoAPI.models):
                        self.subbot.llm.respoAPI.models[model]['token'] = str(token)
                        self.subbot.llm.respoAPI.models[model]['modality'] = str(modality)
                        #self.subbot.llm.respoAPI.models[model]['date'] = str(date_ymd)
                    if (modelx in self.subbot.llm.respoAPI.models):
                        self.subbot.llm.respoAPI.models[modelx]['token'] = str(token)
                        self.subbot.llm.respoAPI.models[modelx]['modality'] = str(modality)
                        #self.subbot.llm.respoAPI.models[modelx]['date'] = str(date_ymd)

                    # gemini
                    modelx = model
                    if (modelx == 'gemini-2.0-flash-thinking-exp:free'):
                        modelx =  'gemini-2.0-flash-thinking-exp-01-21'
                    modelx = modelx.replace(':free', '')
                    model  = model.replace(':free', '')
                    if (model in self.subbot.llm.geminiAPI.models):
                        #self.subbot.llm.geminiAPI.models[model]['token'] = str(token)
                        self.subbot.llm.geminiAPI.models[model]['modality'] = str(modality)
                        self.subbot.llm.geminiAPI.models[model]['date'] = str(date_ymd)
                    if (modelx in self.subbot.llm.geminiAPI.models):
                        #self.subbot.llm.geminiAPI.models[modelx]['token'] = str(token)
                        self.subbot.llm.geminiAPI.models[modelx]['modality'] = str(modality)
                        self.subbot.llm.geminiAPI.models[modelx]['date'] = str(date_ymd)

                    # freeai
                    if (model in self.subbot.llm.freeaiAPI.models):
                        #self.subbot.llm.freeaiAPI.models[model]['token'] = str(token)
                        self.subbot.llm.freeaiAPI.models[model]['modality'] = str(modality)
                        self.subbot.llm.freeaiAPI.models[model]['date'] = str(date_ymd)
                    if (modelx in self.subbot.llm.freeaiAPI.models):
                        #self.subbot.llm.freeaiAPI.models[modelx]['token'] = str(token)
                        self.subbot.llm.freeaiAPI.models[modelx]['modality'] = str(modality)
                        self.subbot.llm.freeaiAPI.models[modelx]['date'] = str(date_ymd)

                    # claude
                    modelx = model
                    if (modelx == 'claude-3-opus'):
                        modelx =  'claude-3-opus-20240229'
                    if (modelx == 'claude-3.5-sonnet'):
                        modelx =  'claude-3-5-sonnet-20241022'
                    if (modelx == 'claude-3.7-sonnet'):
                        modelx =  'claude-3-7-sonnet-20250219'
                    modelx = modelx.replace('claude-3.5', 'claude-3-5')
                    modelx = modelx.replace('claude-3.7', 'claude-3-7')
                    if (model in self.subbot.llm.claudeAPI.models):
                        self.subbot.llm.claudeAPI.models[model]['token'] = str(token)
                        self.subbot.llm.claudeAPI.models[model]['modality'] = str(modality)
                        #self.subbot.llm.claudeAPI.models[model]['date'] = str(date_ymd)
                    if (modelx in self.subbot.llm.claudeAPI.models):
                        self.subbot.llm.claudeAPI.models[modelx]['token'] = str(token)
                        self.subbot.llm.claudeAPI.models[modelx]['modality'] = str(modality)
                        #self.subbot.llm.claudeAPI.models[modelx]['date'] = str(date_ymd)

                    # perplexity
                    if (model in self.subbot.llm.perplexityAPI.models):
                        self.subbot.llm.perplexityAPI.models[model]['token'] = str(token)
                        self.subbot.llm.perplexityAPI.models[model]['modality'] = str(modality)
                        self.subbot.llm.perplexityAPI.models[model]['date'] = str(date_ymd)

                    # grok
                    if (model in self.subbot.llm.grokAPI.models):
                        self.subbot.llm.grokAPI.models[model]['token'] = str(token)
                        self.subbot.llm.grokAPI.models[model]['modality'] = str(modality)
                        #self.subbot.llm.grokAPI.models[model]['date'] = str(date_ymd)

                    # groq
                    if (model in self.subbot.llm.groqAPI.models):
                        #self.subbot.llm.groqAPI.models[model]['token'] = str(token)
                        self.subbot.llm.groqAPI.models[model]['modality'] = str(modality)
                        #self.subbot.llm.groqAPI.models[model]['date'] = str(date_ymd)

        self.last_models_list = models
        return self.last_models_list

    async def get_subai_info_all(self):
        """
        すべてのサブAIの情報を返す。
        """
        if (self.data is None):
            return JSONResponse(content={})
        
        return JSONResponse(content=self.data.subai_info)

    async def get_subai_statuses_all(self):
        """
        すべてのサブAIのステータスとニックネームを返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        subai_status = {port: {'status': info['status'], 'nick_name': info['nick_name'], 'upd_time': info['upd_time']} for port, info in self.data.subai_info.items()}
        return JSONResponse(content=subai_status)

    async def get_sessions_all(self, user_id: str):
        """
        すべての結果を返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        with self.thread_lock:
            current_time = datetime.datetime.now()
            sessions_to_delete = [
                key for key, value in self.data.subai_sessions_all.items()
                if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_SESSIONS_SEC
            ]
            for key in sessions_to_delete:
                del self.data.subai_sessions_all[key]
        return JSONResponse(content=self.data.subai_sessions_all)

    async def get_sessions_port(self, user_id: str, from_port: str):
        """
        ポート指定で、結果を返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        result = {}
        with self.thread_lock:
            for key, value in self.data.subai_sessions_all.items():
                if (value['user_id'] == user_id) and (value['from_port'] == from_port):
                    result[key] = value
            if (len(result) == 0):
                current_time = datetime.datetime.now()
                sessions_to_delete = [
                    key for key, value in self.data.subai_sessions_all.items()
                    if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_SESSIONS_SEC
                ]
                for key in sessions_to_delete:
                    del self.data.subai_sessions_all[key]
        return JSONResponse(content=result)

    async def get_input_list(self):
        # 入力ディレクトリ内のファイル一覧を取得
        now = datetime.datetime.now()
        file_table = [
            (f, os.path.getmtime(os.path.join(qPath_input, f)))
            for f in os.listdir(qPath_input)
            if os.path.isfile(os.path.join(qPath_input, f))
        ]
        file_table.sort(key=lambda x: x[1], reverse=True)
        input_files = []
        image_file = ''
        
        checked = True # 最初の１件チェック
        for f, mod_time in file_table:
            if (now - datetime.datetime.fromtimestamp(mod_time)) < datetime.timedelta(seconds=LIST_RESULT_LIMITSEC):
                file_path = os.path.join(qPath_input, f)
                if (now - datetime.datetime.fromtimestamp(mod_time)) < datetime.timedelta(seconds=LIST_RESULT_AUTOCHECK):
                    if (image_file == ''):
                        image_file = file_path
                else:
                    checked = False
                input_files.append(
                    #f"{f} {datetime.datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S')} {checked}"
                    {"file_name": f, "upd_time": datetime.datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S'), "checked": checked}
                )
                checked = False # 最初の１件チェック
            else:
                break
        
        if self.last_input_files != input_files:
            self.last_input_files = input_files
            self.last_image_file = image_file
            self.last_image_time = time.time()
        return JSONResponse(content={"files": input_files})

    async def post_req(self, postData: RequestMiniModel):
        """
        サブAIにリクエストを送信する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = str(postData.user_id) if postData.user_id else "debug"
        from_port = str(postData.from_port) if postData.from_port else self.core_port
        to_port = str(postData.to_port) if postData.to_port else self._get_available_port()
        #if to_port is None:
        #    raise HTTPException(status_code=503, detail='Service Unavailable')
        req_mode = str(postData.req_mode) if postData.req_mode else "chat"
        req_engine = self.data.mode_setting[req_mode]['req_engine']
        req_functions = self.data.mode_setting[req_mode]['req_functions']
        req_reset = self.data.mode_setting[req_mode]['req_reset']
        max_retry = self.data.mode_setting[req_mode]['max_retry']
        max_ai_count = self.data.mode_setting[req_mode]['max_ai_count']
        before_proc = self.data.mode_setting[req_mode]['before_proc']
        before_engine = self.data.mode_setting[req_mode]['before_engine']
        after_proc = self.data.mode_setting[req_mode]['after_proc']
        after_engine = self.data.mode_setting[req_mode]['after_engine']
        check_proc = self.data.mode_setting[req_mode]['check_proc']
        check_engine = self.data.mode_setting[req_mode]['check_engine']
        system_text = postData.system_text
        request_text = postData.request_text
        input_text = postData.input_text
        file_names = postData.file_names
        result_savepath = postData.result_savepath
        result_schema = postData.result_schema

        # resetの自動設定
        if (req_reset == '') and (postData.to_port == ''):
            req_reset = 'yes,'

        # シンプル実行
        if  (req_mode in ['clip', 'voice']) or (from_port == to_port) or (to_port is None):
            if  ((max_retry == '') or (max_retry == '0')) \
            and (before_proc.find('profile,' ) < 0) \
            and (before_proc.find('prompt,'  ) < 0) \
            and (after_proc.find('all,'     ) < 0) \
            and (after_proc.find('summary,' ) < 0) \
            and (after_proc.find('code,'    ) < 0):

                # ローカル実行
                if (to_port is None) or (to_port == ''):
                    to_port = from_port
                local_bot_thread = threading.Thread(target=self._local_bot, 
                                                    args=(user_id, from_port, to_port, 
                                                    req_mode, req_engine,
                                                    req_functions,
                                                    system_text, request_text, input_text,
                                                    file_names, result_savepath, result_schema, ), 
                                                    daemon=True, )
                local_bot_thread.start()

                return JSONResponse(content={'message': f'Processing started on port {to_port} with request text: {request_text}', 'port': to_port})

        return self._request(   user_id=user_id, from_port=from_port, to_port=to_port, 
                                req_mode=req_mode, req_engine=req_engine,
                                req_functions=req_functions, req_reset= req_reset,
                                max_retry=max_retry, max_ai_count=max_ai_count, 
                                before_proc=before_proc, before_engine=before_engine, 
                                after_proc=after_proc, after_engine=after_engine,
                                check_proc=check_proc, check_engine=check_engine,
                                system_text=system_text, request_text=request_text, input_text=input_text,
                                file_names=file_names, result_savepath=result_savepath, result_schema=result_schema, )

    # ローカル実行
    def _local_bot(self,    user_id: str, from_port: str, to_port: str, 
                            req_mode: str, req_engine: str,
                            req_functions: str,
                            system_text: str, request_text: str, input_text: str,
                            file_names: list[str], result_savepath: str, result_schema: str, ):

        # パラメータ設定
        if True:
            if (req_functions == ''):
                req_functions = 'yes,'

        # 開始
        with self.thread_lock:
            key_val = f"{user_id}:{from_port}:{to_port}"
            now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            self.data.subai_sessions_all[key_val] = {
                "key_val": key_val,
                "user_id": user_id, "from_port": from_port, "to_post": to_port,
                "req_mode": req_mode,
                "inp_time": now_time, "sys_text": system_text, "req_text": request_text, "inp_text": input_text, 
                "file_names": file_names, 
                "out_time": None, "out_text": None, "out_data": None,
                "status": None,
                "upd_time": now_time, "dsp_time": None, }

        # function_modules 設定
        function_modules = {}
        if (req_functions == 'yes,'):
            if (self.botFunc is not None):
                function_modules = self.botFunc.function_modules

        # mcp tools 設定
        if (self.mcpHost is not None):
            mcp_modules = self.mcpHost.get_mcp_modules()
            for key, mcp_module in mcp_modules.items():
                function_modules[key] = mcp_module

        # ファイル設定
        filePath = []
        for fname in file_names:
            fpath = qPath_input + os.path.basename(fname)
            if (os.path.isfile(fpath)):
                filePath.append(fpath)

        # chatBot処理
        res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
            self.subbot.llm.chatBot(    req_mode=req_mode, engine=req_engine,
                                        chat_class='auto', model_select='auto', session_id=self.self_port, 
                                        history=self.history, function_modules=function_modules,
                                        sysText=system_text, reqText=request_text, inpText=input_text,
                                        filePath=filePath, inpLang='ja', outLang='ja', )

        output_text = ''
        output_text += f"[{ res_engine }] ({ self.self_port }:{ res_api }) \n"
        output_text += res_text
        output_data = ''
        if (req_mode == 'clip'):
            output_data += f"[{ res_engine }] ({ self.self_port }:{ res_api }) \n"
        output_data += res_data
        output_path = res_path
        output_files = res_files

        # 終了
        status = 'READY'

        # 完了通知
        try:
            response = requests.post(
                self.local_endpoint2 + '/post_complete', 
                json={'user_id': user_id, 'from_port': from_port, 'to_port': to_port,
                      'req_mode': req_mode,
                      'system_text': system_text, 'request_text': request_text, 'input_text': input_text,
                      'result_savepath': result_savepath, 'result_schema': result_schema,
                      'output_text': output_text, 'output_data': output_data,
                      'output_path': output_path, 'output_files': output_files,
                      'status': status},
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Error response (/post_complete) : {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error communicating (/post_complete) : {e}")
            return False

    async def post_request(self, postData: RequestFullModel):
        """
        サブAIにリクエストを送信する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = str(postData.user_id) if postData.user_id else "debug"
        from_port = str(postData.from_port) if postData.from_port else self.core_port
        to_port = str(postData.to_port) if postData.to_port else self._get_available_port()
        if to_port is None:
            raise HTTPException(status_code=503, detail='Service Unavailable')
        req_mode = str(postData.req_mode) if postData.req_mode else "chat"
        req_engine = str(postData.req_engine) if postData.req_engine else ""
        req_functions = str(postData.req_functions) if postData.req_functions else ""
        req_reset = str(postData.req_reset) if postData.req_reset else ""
        max_retry = str(postData.max_retry) if postData.max_retry else ""
        max_ai_count = str(postData.max_ai_count) if postData.max_ai_count else ""
        before_proc = str(postData.before_proc) if postData.before_proc else ""
        before_engine = str(postData.before_engine) if postData.before_engine else ""
        after_proc = str(postData.after_proc) if postData.after_proc else ""
        after_engine = str(postData.after_engine) if postData.after_engine else ""
        check_proc = str(postData.check_proc) if postData.check_proc else ""
        check_engine = str(postData.check_engine) if postData.check_engine else ""
        system_text = postData.system_text
        request_text = postData.request_text
        input_text = postData.input_text
        file_names = postData.file_names
        result_savepath = postData.result_savepath
        result_schema = postData.result_schema

        # resetの自動設定
        if (req_reset == '') and (postData.to_port == ''):
            req_reset = 'yes,'

        return self._request(   user_id=user_id, from_port=from_port, to_port=to_port, 
                                req_mode=req_mode, req_engine=req_engine,
                                req_functions=req_functions, req_reset= req_reset,
                                max_retry=max_retry, max_ai_count=max_ai_count, 
                                before_proc=before_proc, before_engine=before_engine, 
                                after_proc=after_proc, after_engine=after_engine,
                                check_proc=check_proc, check_engine=check_engine,
                                system_text=system_text, request_text=request_text, input_text=input_text,
                                file_names=file_names, result_savepath=result_savepath, result_schema=result_schema, )

    def _request(self,  user_id: str, from_port: str, to_port: str, 
                        req_mode: str, req_engine: str,
                        req_functions: str, req_reset: str,
                        max_retry: str, max_ai_count: str, 
                        before_proc: str, before_engine: str, 
                        after_proc: str, after_engine: str,
                        check_proc: str, check_engine: str,
                        system_text: str, request_text: str, input_text: str,
                        file_names: list[str], result_savepath: str, result_schema: str, ):
        begin_bye_flag = False
        if (request_text[:6] == 'begin,') \
        or (request_text[:4] == 'bye,'):
            begin_bye_flag = True
        """
        サブAIにリクエストを送信する内部処理。
        """
        if (to_port in self.data.subai_info.keys()):
            with self.thread_lock:
                if self.data.subai_info[to_port]['status'] not in ['READY', 'SESSION']:
                    raise HTTPException(status_code=503, detail=f'subai on port {to_port} is not available')
        try:
            if (self.data.subai_reset[to_port]['reset'] == 'yes,'):
                self.data.subai_reset[to_port]['reset'] = ''
                req_reset = 'yes,'
            if (req_mode == 'websearch'):
                request_text, input_text = self._web_search(request_text=request_text, input_text=input_text, )
            endpoint = f"http://localhost:{ to_port }"
            response = requests.post(
                endpoint + '/post_request',
                json={'user_id': user_id, 'from_port': from_port, 'to_port': to_port, 
                      'req_mode': req_mode, 'req_engine': req_engine,
                      'req_functions': req_functions, 'req_reset': req_reset,
                      'max_retry': max_retry, 'max_ai_count': max_ai_count, 
                      'before_proc': before_proc, 'before_engine': before_engine, 
                      'after_proc': after_proc, 'after_engine': after_engine,
                      'check_proc': check_proc, 'check_engine': check_engine,
                      'system_text': system_text, 'request_text': request_text, 'input_text': input_text,
                      'file_names': file_names, 'result_savepath': result_savepath, 'result_schema': result_schema, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                if (to_port in self.data.subai_info.keys()):
                    with self.thread_lock:
                        if (to_port in self.data.subai_reset.keys()):
                            self.data.subai_reset[to_port]['reset'] = ''
                        if (req_mode not in ['serial', 'parallel', 'session']):
                            self.data.subai_info[to_port]['status'] = 'CHAT'
                        else:
                            self.data.subai_info[to_port]['status'] = req_mode.upper()
                        self.data.subai_info[to_port]['upd_time'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                with self.thread_lock:
                    key_val = f"{user_id}:{from_port}:{to_port}"
                    now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    if (begin_bye_flag != True):
                        if (from_port == self.core_port):
                            self.data.subai_input_log_key += 1
                            self.data.subai_input_log_all[self.data.subai_input_log_key] = {
                                    "user_id": user_id, "from_port": from_port, "to_post": to_port,
                                    "req_mode": req_mode,
                                    "inp_time": now_time, "sys_text": system_text, "req_text": request_text, "inp_text": input_text,
                                    "upd_time": now_time, "dsp_time": None, }
                            self.data.subai_output_log_key += 1
                            self.data.subai_output_log_all[self.data.subai_output_log_key] = {
                                    "key_val": key_val,
                                    "user_id": user_id, "from_port": from_port, "to_post": to_port,
                                    "req_mode": req_mode,
                                    "out_time": now_time, "out_text": '... Now Processing ...', "out_data": '... Now Processing ...',
                                    "status": None,
                                    "upd_time": now_time, "dsp_time": None, }
                        self.data.subai_sessions_all[key_val] = {
                            "key_val": key_val,
                            "user_id": user_id, "from_port": from_port, "to_post": to_port,
                            "req_mode": req_mode,
                            "inp_time": now_time, "sys_text": system_text, "req_text": request_text, "inp_text": input_text, 
                            "file_names": file_names, 
                            "out_time": None, "out_text": None, "out_data": None,
                            "status": None,
                            "upd_time": now_time, "dsp_time": None, }
                return JSONResponse(content={'message': f'Processing started on port {to_port} with request text: {request_text}', 'port': to_port})
            else:
                logger.error(f"Error response ({ to_port }/post_request) : {response.status_code} - {response.text}")
                with self.thread_lock:
                    self.data.subai_info[to_port]['status'] = 'NONE'
                raise HTTPException(status_code=response.status_code, detail=response.text)
        except Exception as e:
            logger.error(f"Error communicating ({ to_port }/post_request) : {e}")
            if (to_port in self.data.subai_info.keys()):
                with self.thread_lock:
                    self.data.subai_info[to_port]['status'] = 'NONE'
            raise HTTPException(status_code=503, detail=f'Error communicating with subai on port {to_port}')

    def _get_available_port(self):
        """
        空いているサブAIのポートを返す。
        """
        if (self.data is not None):
        
            with self.thread_lock:
                for _ in range(self.num_subais):
                    port = self.random_order[self.current_order_index]
                    self.current_order_index = (self.current_order_index + 1) % self.num_subais
                    if (port in self.data.subai_info.keys()):
                        if self.data.subai_info[port]['status'] == 'READY':
                            return port

        return None
    
    def _web_search(self, request_text: str, input_text: str, ):
        addin_module = self.addin.addin_modules.get('addin_web_search', None)
        if (addin_module is not None):
            if (addin_module['onoff'] == 'on'):
                try:
                    dic = {}
                    dic['runMode']  = self.runMode
                    dic['search_text'] = request_text
                    json_dump = json.dumps(dic, ensure_ascii=False, )
                    func_proc = addin_module['func_proc']
                    res_json  = func_proc(json_dump)
                    args_dic = json.loads(res_json)
                    text = args_dic.get('result_text')
                    if (text is not None) and (text != '') and (text != '!'):
                        input_text = input_text.rstrip() + '\n' + text
                except Exception as e:
                    print(e)
        return request_text, input_text



    def run(self):
        """
        サーバー設定と起動
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # フロントエンドのオリジンを指定
            allow_credentials=True,
            allow_methods=["*"],  # すべてのHTTPメソッドを許可
            allow_headers=["*"],  # すべてのヘッダーを許可
        )
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=int(self.self_port),
            log_level="error",
            access_log=False
        )

        

if __name__ == '__main__':
    core_port = '8000'
    sub_base  = '8100'
    numSubAIs = '48'

    coreai0 = main_class(   runMode='debug', qLog_fn='', 
                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)

    #while True:
    #    time.sleep(5)


