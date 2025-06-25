#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'coreai:4'

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
import shutil

import json

from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

import threading

import socket
qHOSTNAME = socket.gethostname().lower()

# パスの設定
qPath_log     = 'temp/_log/'
qPath_output  = 'temp/output/'
qPath_reacts  = '_datas/reacts/'
qPath_sandbox = 'temp/sandbox/'
win_code_path = 'C:/Program Files/Microsoft VS Code/Code.exe'


# モード別設定データモデル
class postModeDataModel(BaseModel):
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

# Addins設定データモデル
class postAddinsDataModel(BaseModel):
    result_text_save: str
    speech_tts_engine: str
    speech_stt_engine: str
    text_clip_input: str
    text_url_execute: str
    text_pdf_execute: str
    image_ocr_execute: str
    image_yolo_execute: str

# エンジン設定データモデル
class postEngineSettingDataModel(BaseModel):
    engine: str
    max_wait_sec: str
    a_model: str
    a_use_tools: str
    b_model: str
    b_use_tools: str
    v_model: str
    v_use_tools: str
    x_model: str
    x_use_tools: str

# Live設定データモデル
class postLiveDataModel(BaseModel):
    engine: str
    live_model: str
    live_voice: str
    shot_interval_sec: str
    clip_interval_sec: str

# Agent engine設定データモデル
class postAgentEngine(BaseModel):
    agent: str
    engine: str

# Agent setting設定データモデル
class postAgentSetting(BaseModel):
    agent: str
    engine: str
    model: str
    max_step: str
    browser: str

# set react json 文字列モデル
class setReactModel(BaseModel):
    filename: str


class main_class:
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        # コアAIクラスの初期化とスレッドの開始
        coreai4 = coreai4_class(runMode=runMode, qLog_fn=qLog_fn,
                                main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                core_port=core_port, sub_base=sub_base, num_subais=num_subais, )
        coreai4_thread = threading.Thread(target=coreai4.run, daemon=True, )
        coreai4_thread.start()
        while True:
            time.sleep(5)


class coreai4_class:
    """
    コアAIクラス(4)
    FastAPIサーバーの管理を行う。
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreai=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        self.runMode = runMode
        self_port = str(int(core_port)+4)

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
        self.coreai     = coreai
        self.core_port  = core_port
        self.sub_base   = sub_base
        self.num_subais = int(num_subais)
        self.self_port  = self_port
        self.webui_endpoint8 = f'http://{ qHOSTNAME }:{ int(self.core_port) + 8 }'

        # スレッドロック
        self.thread_lock = threading.Lock()

        # 最終回答の保存

        # FastAPI設定
        self.app = FastAPI()
        self.app.get("/")(self.root)
        self.app.get("/get_mode_setting")(self.get_mode_setting)
        self.app.post("/post_mode_setting")(self.post_mode_setting)
        self.app.get("/get_engine_models")(self.get_engine_models)
        self.app.get("/get_engine_setting")(self.get_engine_setting)
        self.app.post("/post_engine_setting")(self.post_engine_setting)
        self.app.get("/get_addins_setting")(self.get_addins_setting)
        self.app.post("/post_addins_setting")(self.post_addins_setting)
        self.app.get("/get_live_models")(self.get_live_models)
        self.app.get("/get_live_voices")(self.get_live_voices)
        self.app.get("/get_live_setting")(self.get_live_setting)
        self.app.post("/post_live_setting")(self.post_live_setting)
        self.app.get("/get_agent_engine")(self.get_agent_engine)
        self.app.get("/get_agent_setting")(self.get_agent_setting)
        self.app.post("/post_agent_engine")(self.post_agent_engine)
        self.app.post("/post_agent_setting")(self.post_agent_setting)
        self.app.post("/post_set_react")(self.post_set_react)

    async def root(self, request: Request):
        # Web UI にリダイレクト
        return RedirectResponse(url=self.webui_endpoint8 + '/')

    async def get_mode_setting(self, req_mode: str):
        # 設定情報を返す
        if (self.data is not None):
            result = self.data.mode_setting[req_mode]
        else:
            result = {}
        return JSONResponse(content=result)

    async def post_mode_setting(self, data: postModeDataModel):
        # 設定情報を更新する
        req_mode = str(data.req_mode) if data.req_mode else ""
        req_engine = str(data.req_engine) if data.req_engine else ""
        req_functions = str(data.req_functions) if data.req_functions else ""
        req_reset = str(data.req_reset) if data.req_reset else ""
        max_retry = str(data.max_retry) if data.max_retry else ""
        max_ai_count = str(data.max_ai_count) if data.max_ai_count else ""
        before_proc = str(data.before_proc) if data.before_proc else ""
        before_engine = str(data.before_engine) if data.before_engine else ""
        after_proc = str(data.after_proc) if data.after_proc else ""
        after_engine = str(data.after_engine) if data.after_engine else ""
        check_proc = str(data.check_proc) if data.check_proc else ""
        check_engine = str(data.check_engine) if data.check_engine else ""
        if (self.data is not None):
            self.data.mode_setting[req_mode] = {    "req_engine": req_engine,
                                                    "req_functions": req_functions, "req_reset": req_reset,
                                                    "max_retry": max_retry, "max_ai_count": max_ai_count,
                                                    "before_proc": before_proc, "before_engine": before_engine,
                                                    "after_proc": after_proc, "after_engine": after_engine,
                                                    "check_proc": check_proc, "check_engine": check_engine }
        return JSONResponse(content={'message': 'post_mode_setting successfully'})

    async def get_engine_models(self, engine: str) -> Dict[str, str]:
        # 設定情報を返す
        try:
            if (self.data is not None) and (self.coreai is not None):

                if (engine == 'chatgpt'):
                    if (len(self.data.engine_models['chatgpt']) != len(self.coreai.subbot.llm.chatgptAPI.models)):
                        self.data.engine_models['chatgpt'] = {}
                        for key,value in self.coreai.subbot.llm.chatgptAPI.models.items():
                            self.data.engine_models['chatgpt'][key]      = self.coreai.subbot.llm.chatgptAPI.models[key]["date"] + " : " \
                                                                         + self.coreai.subbot.llm.chatgptAPI.models[key]["id"] + ", " \
                                                                         + str(self.coreai.subbot.llm.chatgptAPI.models[key]["token"]) + ", " \
                                                                         + self.coreai.subbot.llm.chatgptAPI.models[key]["modality"] + ", "

                elif (engine == 'respo'):
                    if (len(self.data.engine_models['respo']) != len(self.coreai.subbot.llm.respoAPI.models)):
                        self.data.engine_models['respo'] = {}
                        for key,value in self.coreai.subbot.llm.respoAPI.models.items():
                            self.data.engine_models['respo'][key]      = self.coreai.subbot.llm.respoAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.respoAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.respoAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.respoAPI.models[key]["modality"] + ", "

                elif (engine == 'gemini'):
                    if (len(self.data.engine_models['gemini']) != len(self.coreai.subbot.llm.geminiAPI.models)):
                        self.data.engine_models['gemini'] = {}
                        for key,value in self.coreai.subbot.llm.geminiAPI.models.items():
                            self.data.engine_models['gemini'][key]      = self.coreai.subbot.llm.geminiAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.geminiAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.geminiAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.geminiAPI.models[key]["modality"] + ", "

                elif (engine == 'freeai'):
                    if (len(self.data.engine_models['freeai']) != len(self.coreai.subbot.llm.freeaiAPI.models)):
                        self.data.engine_models['freeai'] = {}
                        for key,value in self.coreai.subbot.llm.freeaiAPI.models.items():
                            self.data.engine_models['freeai'][key]      = self.coreai.subbot.llm.freeaiAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.freeaiAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.freeaiAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.freeaiAPI.models[key]["modality"] + ", "

                elif (engine == 'claude'):
                    if (len(self.data.engine_models['claude']) != len(self.coreai.subbot.llm.claudeAPI.models)):
                        self.data.engine_models['claude'] = {}
                        for key,value in self.coreai.subbot.llm.claudeAPI.models.items():
                            self.data.engine_models['claude'][key]      = self.coreai.subbot.llm.claudeAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.claudeAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.claudeAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.claudeAPI.models[key]["modality"] + ", "

                elif (engine == 'openrt'):
                    if (len(self.data.engine_models['openrt']) != len(self.coreai.subbot.llm.openrtAPI.models)):
                        self.data.engine_models['openrt'] = {}
                        for key,value in self.coreai.subbot.llm.openrtAPI.models.items():
                            self.data.engine_models['openrt'][key]      = self.coreai.subbot.llm.openrtAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.openrtAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.openrtAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.openrtAPI.models[key]["modality"] + ", "

                elif (engine == 'perplexity'):
                    if (len(self.data.engine_models['perplexity']) != len(self.coreai.subbot.llm.perplexityAPI.models)):
                        self.data.engine_models['perplexity'] = {}
                        for key,value in self.coreai.subbot.llm.perplexityAPI.models.items():
                            self.data.engine_models['perplexity'][key]  = self.coreai.subbot.llm.perplexityAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.perplexityAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.perplexityAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.perplexityAPI.models[key]["modality"] + ", "

                elif (engine == 'grok'):
                    if (len(self.data.engine_models['grok']) != len(self.coreai.subbot.llm.grokAPI.models)):
                        self.data.engine_models['grok'] = {}
                        for key,value in self.coreai.subbot.llm.grokAPI.models.items():
                            self.data.engine_models['grok'][key]        = self.coreai.subbot.llm.grokAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.grokAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.grokAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.grokAPI.models[key]["modality"] + ", "

                elif (engine == 'groq'):
                    if (len(self.data.engine_models['groq']) != len(self.coreai.subbot.llm.groqAPI.models)):
                        self.data.engine_models['groq'] = {}
                        for key,value in self.coreai.subbot.llm.groqAPI.models.items():
                            self.data.engine_models['groq'][key]        = self.coreai.subbot.llm.groqAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.groqAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.groqAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.groqAPI.models[key]["modality"] + ", "

                elif (engine == 'ollama'):
                    if (len(self.data.engine_models['ollama']) != len(self.coreai.subbot.llm.ollamaAPI.models)):
                        self.data.engine_models['ollama'] = {}
                        for key,value in self.coreai.subbot.llm.ollamaAPI.models.items():
                            self.data.engine_models['ollama'][key]      = self.coreai.subbot.llm.ollamaAPI.models[key]["date"] + " : " \
                                                                        + self.coreai.subbot.llm.ollamaAPI.models[key]["id"] + ", " \
                                                                        + str(self.coreai.subbot.llm.ollamaAPI.models[key]["token"]) + ", " \
                                                                        + self.coreai.subbot.llm.ollamaAPI.models[key]["modality"] + ", "

                result = self.data.engine_models[engine]
            else:
                result = {}

        except Exception as e:
            #print(e)
            #raise HTTPException(status_code=500, detail='post_engine_models error:' + e)
            return JSONResponse(content={})
        return JSONResponse(content=result)

    async def get_engine_setting(self, engine: str):
        # 設定情報を返す
        try:
            if (self.data is not None) and (self.coreai is not None):

                if (engine == 'chatgpt'):
                    self.data.engine_setting['chatgpt'] = {
                        "a_nick_name": self.coreai.subbot.llm.chatgptAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.chatgptAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.chatgptAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.chatgptAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.chatgptAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.chatgptAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.chatgptAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.chatgptAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.chatgptAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.chatgptAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.chatgptAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.chatgptAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.chatgptAPI.x_use_tools,
                    }

                elif (engine == 'respo'):
                    self.data.engine_setting['respo'] = {
                        "a_nick_name": self.coreai.subbot.llm.respoAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.respoAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.respoAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.respoAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.respoAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.respoAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.respoAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.respoAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.respoAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.respoAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.respoAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.respoAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.respoAPI.x_use_tools,
                    }

                elif (engine == 'gemini'):
                    self.data.engine_setting['gemini'] = {
                        "a_nick_name": self.coreai.subbot.llm.geminiAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.geminiAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.geminiAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.geminiAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.geminiAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.geminiAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.geminiAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.geminiAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.geminiAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.geminiAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.geminiAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.geminiAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.geminiAPI.x_use_tools,
                    }

                elif (engine == 'freeai'):
                    self.data.engine_setting['freeai'] = {
                        "a_nick_name": self.coreai.subbot.llm.freeaiAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.freeaiAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.freeaiAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.freeaiAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.freeaiAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.freeaiAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.freeaiAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.freeaiAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.freeaiAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.freeaiAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.freeaiAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.freeaiAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.freeaiAPI.x_use_tools,
                    }

                elif (engine == 'claude'):
                    self.data.engine_setting['claude'] = {
                        "a_nick_name": self.coreai.subbot.llm.claudeAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.claudeAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.claudeAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.claudeAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.claudeAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.claudeAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.claudeAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.claudeAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.claudeAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.claudeAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.claudeAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.claudeAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.claudeAPI.x_use_tools,
                    }

                elif (engine == 'openrt'):
                    self.data.engine_setting['openrt'] = {
                        "a_nick_name": self.coreai.subbot.llm.openrtAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.openrtAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.openrtAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.openrtAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.openrtAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.openrtAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.openrtAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.openrtAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.openrtAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.openrtAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.openrtAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.openrtAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.openrtAPI.x_use_tools,
                    }

                elif (engine == 'perplexity'):
                    self.data.engine_setting['perplexity'] = {
                        "a_nick_name": self.coreai.subbot.llm.perplexityAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.perplexityAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.perplexityAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.perplexityAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.perplexityAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.perplexityAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.perplexityAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.perplexityAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.perplexityAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.perplexityAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.perplexityAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.perplexityAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.perplexityAPI.x_use_tools,
                    }

                elif (engine == 'grok'):
                    self.data.engine_setting['grok'] = {
                        "a_nick_name": self.coreai.subbot.llm.grokAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.grokAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.grokAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.grokAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.grokAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.grokAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.grokAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.grokAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.grokAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.grokAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.grokAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.grokAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.grokAPI.x_use_tools,
                    }

                elif (engine == 'groq'):
                    self.data.engine_setting['groq'] = {
                        "a_nick_name": self.coreai.subbot.llm.groqAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.groqAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.groqAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.groqAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.groqAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.groqAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.groqAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.groqAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.groqAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.groqAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.groqAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.groqAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.groqAPI.x_use_tools,
                    }

                elif (engine == 'ollama'):
                    self.data.engine_setting['ollama'] = {
                        "a_nick_name": self.coreai.subbot.llm.ollamaAPI.a_nick_name,
                        "b_nick_name": self.coreai.subbot.llm.ollamaAPI.b_nick_name,
                        "v_nick_name": self.coreai.subbot.llm.ollamaAPI.v_nick_name,
                        "x_nick_name": self.coreai.subbot.llm.ollamaAPI.x_nick_name,
                        "max_wait_sec": str(self.coreai.subbot.llm.ollamaAPI.max_wait_sec),
                        "a_model": self.coreai.subbot.llm.ollamaAPI.a_model,
                        "a_use_tools": self.coreai.subbot.llm.ollamaAPI.a_use_tools,
                        "b_model": self.coreai.subbot.llm.ollamaAPI.b_model,
                        "b_use_tools": self.coreai.subbot.llm.ollamaAPI.b_use_tools,
                        "v_model": self.coreai.subbot.llm.ollamaAPI.v_model,
                        "v_use_tools": self.coreai.subbot.llm.ollamaAPI.v_use_tools,
                        "x_model": self.coreai.subbot.llm.ollamaAPI.x_model,
                        "x_use_tools": self.coreai.subbot.llm.ollamaAPI.x_use_tools,
                    }

                result = self.data.engine_setting[engine]
            else:
                result = {}

        except Exception as e:
            #print(e)
            raise HTTPException(status_code=500, detail='get_engine_setting error:' + str(e))
        return JSONResponse(content=result)

    async def post_engine_setting(self, data: postEngineSettingDataModel):
        # 設定情報を更新する
        engine = str(data.engine) if data.engine else ""
        max_wait_sec = str(data.max_wait_sec) if data.max_wait_sec else ""
        a_model = str(data.a_model) if data.a_model else ""
        a_use_tools = str(data.a_use_tools) if data.a_use_tools else ""
        b_model = str(data.b_model) if data.b_model else ""
        b_use_tools = str(data.b_use_tools) if data.b_use_tools else ""
        v_model = str(data.v_model) if data.v_model else ""
        v_use_tools = str(data.v_use_tools) if data.v_use_tools else ""
        x_model = str(data.x_model) if data.x_model else ""
        x_use_tools = str(data.x_use_tools) if data.x_use_tools else ""
        try:
            if (self.data is not None):
                self.data.engine_setting[engine] = {"max_wait_sec": str(max_wait_sec),
                                                    "a_model": a_model, "a_use_tools": a_use_tools,
                                                    "b_model": b_model, "b_use_tools": b_use_tools,
                                                    "v_model": v_model, "v_use_tools": v_use_tools,
                                                    "x_model": x_model, "x_use_tools": x_use_tools, }
                if (self.coreai is not None):

                    if (engine == 'chatgpt'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.chatgptAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'respo'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.respoAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'gemini'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.geminiAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'freeai'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.freeaiAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'claude'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.claudeAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'openrt'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.openrtAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'perplexity'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.perplexityAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'grok'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.grokAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'groq'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.groqAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

                    elif (engine == 'ollama'):
                        engine_set_thread = threading.Thread(
                            target=self.coreai.subbot.llm.ollamaAPI.set_models,
                            args=(max_wait_sec, a_model, a_use_tools, b_model, b_use_tools,
                                                v_model, v_use_tools, x_model, x_use_tools, ),
                            daemon=True, )
                        engine_set_thread.start()

        except Exception as e:
            #print(e)
            raise HTTPException(status_code=500, detail='post_engine_setting error:' + e)
        return JSONResponse(content={'message': 'post_engine_setting successfully'})

    async def get_addins_setting(self):
        # 設定情報を返す
        if (self.data is not None):
            result = self.data.addins_setting
        else:
            result = {}
        return JSONResponse(content=result)

    async def post_addins_setting(self, data: postAddinsDataModel):
        # 設定情報を更新する
        result_text_save = str(data.result_text_save) if data.result_text_save else ""
        speech_tts_engine = str(data.speech_tts_engine) if data.speech_tts_engine else ""
        speech_stt_engine = str(data.speech_stt_engine) if data.speech_stt_engine else ""
        text_clip_input = str(data.text_clip_input) if data.text_clip_input else ""
        text_url_execute = str(data.text_url_execute) if data.text_url_execute else ""
        text_pdf_execute = str(data.text_pdf_execute) if data.text_pdf_execute else ""
        image_ocr_execute = str(data.image_ocr_execute) if data.image_ocr_execute else ""
        image_yolo_execute = str(data.image_yolo_execute) if data.image_yolo_execute else ""
        if (self.data is not None):
            self.data.addins_setting = {"result_text_save": result_text_save,
                                        "speech_tts_engine": speech_tts_engine,
                                        "speech_stt_engine": speech_stt_engine, 
                                        "text_clip_input": text_clip_input, 
                                        "text_url_execute": text_url_execute, 
                                        "text_pdf_execute": text_pdf_execute, 
                                        "image_ocr_execute": image_ocr_execute, 
                                        "image_yolo_execute": image_yolo_execute, }
        return JSONResponse(content={'message': 'post_addins_setting successfully'})

    async def get_live_models(self, engine: str) -> Dict[str, str]:
        # 設定情報を返す
        if (self.data is not None):
            result = self.data.live_models[engine]
        else:
            result = {}
        return JSONResponse(content=result)

    async def get_live_voices(self, engine: str) -> Dict[str, str]:
        # 設定情報を返す
        if (self.data is not None):
            result = self.data.live_voices[engine]
        else:
            result = {}
        return JSONResponse(content=result)

    async def get_live_setting(self, engine: str):
        # 設定情報を返す
        if (self.data is not None):
            result = self.data.live_setting[engine]
        else:
            result = {}
        return JSONResponse(content=result)

    async def post_live_setting(self, data: postLiveDataModel):
        # 設定情報を更新する
        engine = str(data.engine) if data.engine else ""
        live_model = str(data.live_model) if data.live_model else ""
        live_voice = str(data.live_voice) if data.live_voice else ""
        shot_interval_sec = str(data.shot_interval_sec) if data.shot_interval_sec else ""
        clip_interval_sec = str(data.clip_interval_sec) if data.clip_interval_sec else ""
        if (self.data is not None):
            self.data.live_setting[engine] = {  "live_model": live_model,
                                                "live_voice": live_voice,
                                                "shot_interval_sec": shot_interval_sec,
                                                "clip_interval_sec": clip_interval_sec, }
        return JSONResponse(content={'message': 'post_live_setting successfully'})

    async def get_agent_engine(self, agent: str):
        result = {}
        if (self.data is not None):

            # webOperator設定情報を返す
            if   (agent == 'webOperator'):
                engine = self.data.webOperator_setting['engine']
                models = {}
                if (engine != ''):
                    models = self.data.webOperator_models[engine]
                result = {  "engine": engine,
                            "models": models, }

            # researchAgent設定情報を返す
            elif (agent == 'researchAgent'):
                engine = self.data.researchAgent_setting['engine']
                models = {}
                if (engine != ''):
                    models = self.data.researchAgent_models[engine]
                result = {  "engine": engine,
                            "models": models, }

        return JSONResponse(content=result)

    async def get_agent_setting(self, agent: str):
        result = {}
        if (self.data is not None):

            # webOperator設定情報を返す
            if   (agent == 'webOperator'):
                result = self.data.webOperator_setting

            # researchAgent設定情報を返す
            elif (agent == 'researchAgent'):
                result = self.data.researchAgent_setting

        return JSONResponse(content=result)

    async def post_agent_engine(self, data: postAgentEngine):
        agent = str(data.agent) if data.agent else ""
        engine = str(data.engine) if data.engine else ""
        if (self.data is not None):

            # webOperator設定
            if   (agent == 'webOperator'):
                self.data.webOperator_setting['engine'] = engine
                if (engine != ''):
                    self.data.webOperator_setting['model'] = list( self.data.webOperator_models[engine].keys() )[0]
                else:
                    self.data.webOperator_setting['model'] = ''

            # researchAgent設定
            elif (agent == 'researchAgent'):
                self.data.researchAgent_setting['engine'] = engine
                if (engine != ''):
                    self.data.researchAgent_setting['model'] = list( self.data.researchAgent_models[engine].keys() )[0]
                else:
                    self.data.researchAgent_setting['model'] = ''

        return JSONResponse(content={'message': 'post_agent_engine successfully'})

    async def post_agent_setting(self, data: postAgentSetting):
        agent = str(data.agent) if data.agent else ""
        engine = str(data.engine) if data.engine else ""
        model = str(data.model) if data.model else ""
        max_step = str(data.max_step) if data.max_step else ""
        browser = str(data.browser) if data.browser else ""
        if (self.data is not None):

            # webOperator設定
            if   (agent == 'webOperator'):
                self.data.webOperator_setting = {   "engine": engine,
                                                    "model": model,
                                                    "max_step": max_step,
                                                    "browser": browser, }

            # researchAgent設定
            elif (agent == 'researchAgent'):
                self.data.researchAgent_setting = { "engine": engine,
                                                    "model": model,
                                                    "max_step": max_step,
                                                    "browser": browser, }

        return JSONResponse(content={'message': 'post_agent_setting successfully'})

    async def post_set_react(self, data: setReactModel):
        filename = data.filename
        print(filename)
        from_file = qPath_reacts + filename
        to_file   = qPath_output + filename
        if (not os.path.isfile(from_file)):
            raise HTTPException(status_code=404, detail='post_set_react error')

        try:
            shutil.copy(from_file, to_file)
            if (not os.path.isfile(to_file)):
                raise HTTPException(status_code=404, detail='post_set_react error')

            # SandBox
            addin_module = self.addin.addin_modules.get('automatic_sandbox', None)
            if (addin_module is not None):

                dic = {}
                dic['runMode']   = self.runMode
                dic['file_path'] = filename
                dic['browser']   = 'no'
                json_dump = json.dumps(dic, ensure_ascii=False, )
                addin_func_proc  = addin_module['func_proc']
                res_json = addin_func_proc( json_dump )
                #args_dic = json.loads(res_json)

                # 表示更新
                _, ext = os.path.splitext(filename)
                if (ext.lower() in ['.zip', '.html']):
                    self.data.sandbox_update = True
                    self.data.sandbox_file = filename
                    if (ext.lower() == '.zip'):
                        extract_dir = os.path.basename(filename).replace('.zip', '')
                        filename = qPath_sandbox + extract_dir + '/package.json'
                        if (os.path.isfile(filename)):
                            self.data.sandbox_file = filename
                    if (ext.lower() == '.html'):
                        filename = qPath_sandbox + 'react_sandbox/public/index.html'
                        if (os.path.isfile(filename)):
                            self.data.sandbox_file = filename

                return JSONResponse(content={'message': 'post_set_react successfully'})

        except Exception as e:
            print('post_speech_json', e)
        raise HTTPException(status_code=503, detail='post_set_react error')

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

    coreai4 = main_class(   runMode='debug', qLog_fn='', 
                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)

    #while True:
    #    time.sleep(5)


