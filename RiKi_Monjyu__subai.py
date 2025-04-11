#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'subai'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)


import sys
import os
import time
import datetime
import codecs
import glob
import shutil

from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

import random

import threading

import requests
import pandas as pd

import socket
qHOSTNAME = socket.gethostname().lower()

# ファイルパス定義
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'
qPath_input  = 'temp/input/'
qPath_output = 'temp/output/'

# 共通ルーチンインポート
import RiKi_Monjyu__subbot

# 定数の定義
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30
BUSY_LIMIT = 1200

# データモデルの定義
class RequestDataModel(BaseModel):
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

# サブAIプロセスクラス
class SubAiProcess:
    def __init__(self, runMode: str = 'debug', qLog_fn: str = '', 
                 main=None, conf=None, data=None, addin=None, botFunc=None,
                 coreai=None,
                 core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48'):

        # 各種設定の初期化
        self.main      = main
        self.conf      = conf
        self.data      = data
        self.addin     = addin
        self.botFunc   = botFunc
        self.coreai    = coreai

        """ サブAIプロセスの初期化 """
        self.num_subais = int(num_subais)
        random_profile = random.sample(range(self.num_subais), self.num_subais)
        chat_class = {}
        subai_class = {}
        subai_thread = {}
        for n in range(self.num_subais):
            self_port = str(int(sub_base) + n + 1)
            subai_class[n] = SubAiClass(runMode=runMode, qLog_fn=qLog_fn, 
                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc,
                                        coreai=coreai,
                                        core_port=core_port, sub_base=sub_base, num_subais=str(num_subais),
                                        self_port=self_port, profile_number=random_profile[n])
            subai_thread[n] = threading.Thread(target=subai_class[n].run)
            subai_thread[n].daemon = True
            subai_thread[n].start()
        while True:
            time.sleep(5)

# サブAIクラス
class SubAiClass:
    """ サブAIクラス """
    def __init__(self, runMode: str = 'debug', qLog_fn: str = '', 
                 main=None, conf=None, data=None, addin=None, botFunc=None,
                 coreai=None,
                 core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48',
                 self_port: str = '8101', profile_number: Optional[int] = None):
        self.runMode = runMode

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug(f"init {self_port}")

        # 設定
        self.main       = main
        self.conf       = conf
        self.data       = data
        self.addin      = addin
        self.botFunc    = botFunc
        self.coreai     = coreai
        self.core_port  = core_port
        self.sub_base   = sub_base
        self.self_port  = self_port
        self.local_endpoint = f'http://localhost:{self.core_port}'
        self.core_endpoint = self.local_endpoint.replace('localhost', qHOSTNAME)
        self.webui_endpoint = self.core_endpoint.replace(f':{self.core_port}', f':{int(self.core_port) + 8}')
        self.profile_number = profile_number
        self.chat_class = RiKi_Monjyu__subbot.ChatClass(runMode=runMode, qLog_fn=qLog_fn, 
                                                        main=main, conf=conf, data=data, addin=addin, botFunc=botFunc,
                                                        coreai=coreai,
                                                        core_port=core_port, self_port=self_port)
        # スレッドロック
        self.thread_lock = threading.Lock()

        # サブAI情報の初期化
        self.info = {}
        self.info['status'] = 'READY'
        self.info['nick_name'] = self_port
        self.info['full_name'] = self_port
        self.info['info_text'] = self_port
        self.info['self_point'] = '50'
        self.info['self_prompt'] = 'あなたは美しい日本語を話す賢いアシスタントです。'
        self.get_profile_info(profile_number=self.profile_number)

        # 最後の処理要求/セッション/CANCEL要求
        self.last_proc_time = None
        self.last_session = None
        self.cancel_request = False

        # FastAPI/エンドポイントの設定
        self.app = FastAPI()
        self.app.get('/')(self.root)
        self.app.get('/get_info')(self.get_info)
        self.app.post('/post_cancel')(self.post_cancel)
        self.app.post('/post_request')(self.post_request)

    def get_profile_info(self, profile_number: int = None):
        """ プロフィール情報の取得 """
        try:
            df = pd.read_excel('_config/RiKi_Monjyu_profile.xlsx')
            row = df.iloc[profile_number - 1]
            if row["愛称"] is not None:
                self.info['nick_name'] = row["愛称"]
            if row["名前(フルネーム)"] is not None:
                self.info['full_name'] = row["名前(フルネーム)"]
            info_text = '【ニックネーム】\n'
            info_text += '　' + self.info['nick_name'] + '\n'
            if row["名前(フルネーム)"] is not None:
                info_text += '【名前(フルネーム)】\n'
                info_text += '　' + row["名前(フルネーム)"] + '\n'
            if row["得意分野"] is not None:
                info_text += '【得意分野】\n'
                info_text += '　' + row["得意分野"] + '\n'
            if row["業績"] is not None:
                info_text += '【業績】\n'
                info_text += '　' + row["業績"] + '\n'
            if row["性格"] is not None:
                info_text += '【性格】\n'
                info_text += '　' + row["性格"] + '\n'
            self.info['info_text'] = info_text
        except Exception as e:
            logger.error(f"Error retrieving profile info: {e}")

    async def root(self, request: Request):
        """ ルートエンドポイントのリダイレクト """
        return RedirectResponse(url=self.webui_endpoint + '/')

    async def get_info(self) -> Dict[str, str]:
        """ サブAIの情報取得(応答) """
        # エラー時の自動復帰
        if self.info['status'] != 'READY':
            if (self.last_proc_time is not None) and ((time.time() - self.last_proc_time) > BUSY_LIMIT):
                self.info['status'] = 'READY'
                self.last_proc_time = None
                self.last_session = None
                self.cancel_request = False
        return JSONResponse(content=self.info)

    async def post_cancel(self, request: Request):
        """ キャンセルリクエストを処理 """
        logger.warning('Cancel request received!')
        # キャンセル要求
        self.cancel_request = True
        self.chat_class.bot_cancel_request = True
        # ステータスをCANCELに設定
        self.info['status'] = 'CANCEL'
        return JSONResponse(content={'text': 'Cancel request received!'})

    async def post_request(self, data: RequestDataModel) -> Dict[str, str]:
        """ 処理開始リクエストを処理 """
        user_id = str(data.user_id)
        from_port = str(data.from_port)
        to_port = str(data.to_port)
        req_mode = str(data.req_mode)
        req_engine = str(data.req_engine)
        req_functions = str(data.req_functions)
        req_reset = str(data.req_reset)
        max_retry = str(data.max_retry)
        max_ai_count = str(data.max_ai_count)
        before_proc = str(data.before_proc)
        before_engine = str(data.before_engine)
        after_proc = str(data.after_proc)
        after_engine = str(data.after_engine)
        check_proc = str(data.check_proc)
        check_engine = str(data.check_engine)
        system_text = str(data.system_text)
        request_text = str(data.request_text)
        input_text = str(data.input_text)
        file_names = data.file_names
        result_savepath = str(data.result_savepath) 
        result_schema = str(data.result_schema) 
        if from_port != self.last_session:
            if self.info['status'] != 'READY':
                raise HTTPException(status_code=400, detail='Not available')
        if (req_mode not in ['serial', 'parallel', 'session']):
            self.info['status'] = 'CHAT'
        else:
            self.info['status'] = req_mode.upper()
        self.last_proc_time = time.time()
        self.cancel_request = False
        # ログ出力
        if   request_text.lower()[:6] == 'begin,':
            logger.info(f"{ user_id } : { from_port } -> { to_port } (begin)")
        elif request_text.lower()[:4] == 'bye,':
            logger.info(f"{ user_id } : { from_port } -> { to_port } (bye)")
        else:
            logger.info(f"{ user_id } : { from_port } -> { to_port } ({ req_mode })")
        # ファンクション設定
        self.function_modules = {}
        if self.botFunc is not None:
            for key, module_dic in self.botFunc.function_modules.items():
                if module_dic['onoff'] == 'on':
                    self.function_modules[key] = module_dic
        # チャット処理開始
        if req_mode not in ['serial', 'parallel']:
            thread = threading.Thread(target=self.chat_proc, 
                                      args=(user_id, from_port, to_port, 
                                            req_mode, req_engine,
                                            req_functions, req_reset,
                                            max_retry, max_ai_count,
                                            before_proc, before_engine,
                                            after_proc, after_engine, 
                                            check_proc, check_engine, 
                                            system_text, request_text, input_text, 
                                            file_names, result_savepath, result_schema, ))
        # アシスタント処理開始
        else:
            thread = threading.Thread(target=self.assistant_proc, 
                                      args=(user_id, from_port, to_port, 
                                            req_mode, req_engine, 
                                            req_functions, req_reset,
                                            max_retry, max_ai_count,
                                            before_proc, before_engine,
                                            after_proc, after_engine, 
                                            check_proc, check_engine, 
                                            system_text, request_text, input_text, 
                                            file_names, result_savepath, result_schema, ))
        thread.daemon = True
        thread.start()
        return JSONResponse(content={'text': 'Chat processing started'})

    def post_complete(self, user_id: str, from_port: str, to_port: str,
                            req_mode: str, system_text: str, request_text: str, input_text: str, 
                            result_savepath: str, result_schema: str,
                            output_text: str, output_data: str,
                            output_path: str, output_files: list[str],
                            status: str) -> str:
        """ チャット処理とアシスタント処理終了 """

        # ログ出力
        if not self.cancel_request:
            if   request_text.lower()[:6] == 'begin,':
                logger.info(f"{ user_id } : { from_port } <- { to_port } (begin)")
            elif request_text.lower()[:4] == 'bye,':
                logger.info(f"{ user_id } : { from_port } <- { to_port } (bye)")
            else:
                logger.info(f"{ user_id } : { from_port } <- { to_port } ({ req_mode })")
        else:
            logger.warning(f"{ user_id } : { from_port } <- { to_port } (cancel!)")

        try:
            response = requests.post(
                self.local_endpoint + '/post_complete', 
                json={'user_id': user_id, 'from_port': from_port, 'to_port': to_port,
                      'req_mode': req_mode,
                      'system_text': system_text, 'request_text': request_text, 'input_text': input_text,
                      'result_savepath': result_savepath, 'result_schema': result_schema,
                      'output_text': output_text, 'output_data': output_data,
                      'output_path': output_path, 'output_files': output_files,
                      'status': status},
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                logger.error(f"Error response ({self.core_port}/post_complete) : {response.status_code}")
                status = 'ERROR'
        except Exception as e:
            logger.error(f"Error communicating ({self.core_port}/post_complete) : {e}")
            status = 'ERROR'

        # ステータスを更新
        self.info['status'] = status
        return status

    def post_debug_log(self,user_id: str, from_port: str, to_port: str,
                            req_mode: str, system_text: str, request_text: str, input_text: str, 
                            result_savepath: str, result_schema: str,
                            output_text: str, output_data: str,
                            output_path: str, output_files: list[str],
                            status: str) -> str:
        """ チャットとアシスタントのデバッグログ """
        # ログ出力
        logger.info(f"{ user_id } : { from_port } <- { to_port } (debug_log)")
        self.last_proc_time = time.time()
        try:
            response = requests.post(
                self.local_endpoint + '/post_debug_log', 
                json={'user_id': user_id, 'from_port': from_port, 'to_port': to_port,
                      'req_mode': req_mode,
                      'system_text': system_text, 'request_text': request_text, 'input_text': input_text,
                      'result_savepath': result_savepath, 'result_schema': result_schema,
                      'output_text': output_text, 'output_data': output_data,
                      'output_path': output_path, 'output_files': output_files,
                      'status': status},
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                logger.error(f"Error response ({self.core_port}/post_debug_log) : {response.status_code}")
                status = 'ERROR'
        except Exception as e:
            logger.error(f"Error communicating ({self.core_port}/post_debug_log) : {e}")
            status = 'ERROR'
        return status

    def chat_proc(self, user_id: str, from_port: str, to_port: str,
                  req_mode: str, req_engine: str, req_functions: str, req_reset: str,
                  max_retry: str, max_ai_count: str, before_proc: str, before_engine: str, 
                  after_proc: str, after_engine: str, check_proc: str, check_engine: str, 
                  system_text: str, request_text: str, input_text: str,
                  file_names: list[str], result_savepath: str, result_schema: str, ) -> str:
        """ チャット処理 """
        # セッションの開始
        if request_text.lower()[:6] == 'begin,':
            self.last_session = from_port
            if self.chat_class is not None:
                if req_reset == 'yes,':
                    self.chat_class.history = []
            output_text = request_text
            output_data = input_text
            output_path = ''
            output_files = []
            status = 'SESSION'
            status = self.post_complete(user_id=user_id, from_port=from_port, to_port=to_port,
                                        req_mode=req_mode,
                                        system_text=system_text, request_text=request_text, input_text=input_text,
                                        result_savepath=result_savepath, result_schema=result_schema,
                                        output_text=output_text, output_data=output_data,
                                        output_path=output_path, output_files=output_files,
                                        status=status)
        # セッションの終了
        elif request_text.lower()[:4] == 'bye,':
            self.last_session = None
            if self.chat_class is not None:
                if req_reset == 'yes,':
                    self.chat_class.history = []
            output_text = request_text
            output_data = input_text
            output_path = ''
            output_files = []
            status = 'READY'
            status = self.post_complete(user_id=user_id, from_port=from_port, to_port=to_port,
                                        req_mode=req_mode, 
                                        system_text=system_text, request_text=request_text, input_text=input_text,
                                        result_savepath=result_savepath, result_schema=result_schema,
                                        output_text=output_text, output_data=output_data,
                                        output_path=output_path, output_files=output_files,
                                        status=status)
        # 会話処理
        else:
            if request_text.lower()[:6] == 'debug,':
                logger.warning('debug, ...')
            if self.chat_class is not None:
                if req_reset == 'yes,':
                    self.chat_class.history = []
                output_text, output_data, output_path, output_files = self.chat_class.proc_chat(
                    user_id=user_id, from_port=from_port, to_port=to_port,
                    req_mode=req_mode, req_engine=req_engine,
                    req_functions=req_functions, req_reset=req_reset,
                    max_retry=max_retry, max_ai_count=max_ai_count,
                    before_proc=before_proc, before_engine=before_engine, 
                    after_proc=after_proc, after_engine=after_engine,
                    check_proc=check_proc, check_engine=check_engine,
                    system_text=system_text, request_text=request_text, input_text=input_text,
                    file_names=file_names, result_savepath=result_savepath, result_schema=result_schema, parent_self=self)
                if not self.cancel_request:
                    if req_mode == 'session':
                        status = 'SESSION'
                    else:
                        status = 'READY'
                else:
                    status = 'CANCEL'
                    self.last_proc_time = time.time() - BUSY_LIMIT + 120  # 2分間停止
                    status = self.post_complete(user_id=user_id, from_port=from_port, to_port=to_port,
                                                req_mode=req_mode,
                                                system_text=system_text, request_text=request_text, input_text=input_text,
                                                result_savepath=result_savepath, result_schema=result_schema, 
                                                output_text=output_text, output_data=output_data,
                                                output_path=output_path, output_files=output_files,
                                                status=status)
            else:
                output_text = request_text
                output_data = input_text
                output_path = None
                output_files = []
                if not self.cancel_request:
                    if req_mode == 'session':
                        status = 'SESSION'
                    else:
                        status = 'READY'
                else:
                    status = 'CANCEL'
                status = self.post_complete(user_id=user_id, from_port=from_port, to_port=to_port,
                                            req_mode=req_mode,
                                            system_text=system_text, request_text=request_text, input_text=input_text,
                                            result_savepath=result_savepath, result_schema=result_schema, 
                                            output_text=output_text, output_data=output_data,
                                            output_path=output_path, output_files=output_files,
                                            status=status)
        return status

    def assistant_proc(self,user_id: str, from_port: str, to_port: str,
                            req_mode: str, req_engine: str, req_functions: str, req_reset: str,
                            max_retry: str, max_ai_count: str, before_proc: str, before_engine: str, 
                            after_proc: str, after_engine: str, check_proc: str, check_engine: str, 
                            system_text: str, request_text: str, input_text: str,
                            file_names: list[str], result_savepath: str, result_schema: str, ) -> str:
        """ アシスタント処理 """
        if request_text.lower()[:6] == 'debug,':
            logger.warning('debug, ...')
        if self.chat_class is not None:
            if req_reset == 'yes,':
                self.chat_class.history = []
            output_text, output_data, output_path, output_files = self.chat_class.proc_assistant(
                user_id=user_id, from_port=from_port, to_port=to_port,
                req_mode=req_mode, req_engine=req_engine,
                req_functions=req_functions, req_reset=req_reset,
                max_retry=max_retry, max_ai_count=max_ai_count,
                before_proc=before_proc, before_engine=before_engine, 
                after_proc=after_proc, after_engine=after_engine,
                check_proc=check_proc, check_engine=check_engine,
                system_text=system_text, request_text=request_text, input_text=input_text,
                file_names=file_names, result_savepath=result_savepath, result_schema=result_schema, parent_self=self)
            if not self.cancel_request:
                status = 'READY'
            else:
                status = 'CANCEL'
                self.last_proc_time = time.time() - BUSY_LIMIT + 120  # 2分間停止
                status = self.post_complete(user_id=user_id, from_port=from_port, to_port=to_port,
                                            req_mode=req_mode,
                                            system_text=system_text, request_text=request_text, input_text=input_text,
                                            result_savepath=result_savepath, result_schema=result_schema,
                                            output_text=output_text, output_data=output_data,
                                            output_path=output_path, output_files=output_files,
                                            status=status)
        else:
            output_text = request_text
            output_data = input_text
            if not self.cancel_request:
                status = 'READY'
            else:
                status = 'CANCEL'
            status = self.post_complete(user_id=user_id, from_port=from_port, to_port=to_port,
                                        req_mode=req_mode,
                                        system_text=system_text, request_text=request_text, input_text=input_text,
                                        result_savepath=result_savepath, result_schema=result_schema,
                                        output_text=output_text, output_data=output_data,
                                        output_path=output_path, output_files=output_files,
                                        status=status)
        return status



    def run(self) -> None:
        """ サーバー設定と起動 """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
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
    subai = SubAiProcess(runMode='debug', qLog_fn='', 
                         core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)
    # while True:
    #     time.sleep(5)
