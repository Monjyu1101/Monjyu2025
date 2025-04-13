#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'coreai:1'

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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

import threading

import socket
qHOSTNAME = socket.gethostname().lower()

# パスの設定
qPath_temp    = 'temp/'
qPath_log     = 'temp/_log/'


# 定数の定義
DELETE_INPUTLOG_SEC   = 600

# ユーザーIDモデル
class UserIdModel(BaseModel):
    user_id: str

# input_logモデル
class InputLogModel(BaseModel):
    user_id: str
    request_text: str
    input_text: str


class main_class:
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        # コアAIクラスの初期化とスレッドの開始
        coreai1 = coreai1_class(runMode=runMode, qLog_fn=qLog_fn,
                                main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                core_port=core_port, sub_base=sub_base, num_subais=num_subais, )
        coreai1_thread = threading.Thread(target=coreai1.run, daemon=True, )
        coreai1_thread.start()
        while True:
            time.sleep(5)


class coreai1_class:
    """
    コアAIクラス(0)
    FastAPIサーバーの管理を行う。
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreai=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        self.runMode = runMode
        self_port = str(int(core_port)+1)

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
        self.last_input_log_user = None

        # FastAPI設定
        self.app = FastAPI()
        self.app.get("/")(self.root)
        self.app.get("/get_input_log_user")(self.get_input_log_user)
        self.app.post("/post_reset")(self.post_reset)
        self.app.post("/post_cancel")(self.post_cancel)
        self.app.post("/post_clear")(self.post_clear)
        self.app.post("/post_input_log")(self.post_input_log)

    async def root(self, request: Request):
        # Web UI にリダイレクト
        return RedirectResponse(url=self.webui_endpoint8 + '/')

    async def get_input_log_user(self, user_id: str):
        """
        最新の1件の入力ログを返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        result = self.last_input_log_user
        result_hit = False
        with self.thread_lock:
            now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            for key, value in self.data.subai_input_log_all.items():
                if (value['user_id'] == user_id):
                    if (value['dsp_time'] == None):
                        result = {}
                        result['system_text'] = ''
                        result['request_text'] = ''
                        result['input_text'] = ''
                        if value['sys_text'] is not None:
                            result['system_text'] = value['sys_text']
                        if value['req_text'] is not None:
                            result['request_text'] = value['req_text']
                        if value['inp_text'] is not None:
                            result['input_text'] = value['inp_text']
                        value['dsp_time'] = now_time
                        self.last_input_log_user = result
                        result_hit = True
            # 応答なしの合間に古いデータ削除
            if (result_hit == False):
                current_time = datetime.datetime.now()
                # input log 整理
                input_log_to_delete = [
                    key for key, value in self.data.subai_input_log_all.items()
                    if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_INPUTLOG_SEC
                ]
                for key in input_log_to_delete:
                    del self.data.subai_input_log_all[key]
        return JSONResponse(content=result)

    async def post_reset(self, postData: UserIdModel):
        """
        全サブAIのリセットを送信する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = postData.user_id
        # 表示消去
        self.history = []
        self._text_clear(user_id=user_id, req_mode='RESET')
        # リセット設定
        if (self.data is not None):
            self.data.reset(user_id=user_id)
        return JSONResponse(content={'message': 'post_reset successfully'})

    async def post_cancel(self, postData: UserIdModel):
        """
        サブAIのキャンセルを送信する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = postData.user_id
        # サブAI CANCEL 処理
        if (self.data is not None):
            self.data.cancel(user_id=user_id)
        return JSONResponse(content={'message': 'post_cancel successfully'})

    async def post_clear(self, postData: UserIdModel):
        """
        表示内容をクリアする。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = postData.user_id
        # 表示消去
        self._text_clear(user_id=user_id, req_mode='CLEAR')
        return JSONResponse(content={'message': 'post_clear successfully'})

    def _text_clear(self, user_id: str, req_mode: str):
        """
        ログと表示内容のクリア処理。
        """
        if (self.data is None):
            return False

        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        # log 消去
        self.data.subai_debug_log_all = {}
        # 表示消去
        with self.thread_lock:
            if (req_mode == 'RESET'):
                self.data.subai_input_log_key += 1
                self.data.subai_input_log_all[self.data.subai_input_log_key] = {
                        "user_id": user_id, "from_port": self.core_port, "to_post": self.core_port,
                        "req_mode": req_mode,
                        "inp_time": now_time, 
                        "sys_text": 'あなたは美しい日本語を話す賢いアシスタントです。', 
                        "req_text": '', 
                        "inp_text": '',
                        "upd_time": now_time, "dsp_time": None, }
            self.data.subai_output_log_key += 1
            self.data.subai_output_log_all[self.data.subai_output_log_key] = {
                "user_id": user_id, "from_port": self.core_port, "to_post": self.core_port,
                "req_mode": req_mode,
                "out_time": now_time, "out_text": '', "out_data": '',
                "status": None,
                "upd_time": now_time, "dsp_time": None, }
            self.data.subai_debug_log_key += 1
            self.data.subai_debug_log_all[self.data.subai_debug_log_key] = {
                "user_id": user_id, "from_port": self.core_port, "to_post": self.core_port,
                "req_mode": req_mode,
                "inp_time": now_time, "sys_text": '', "req_text": req_mode, "inp_text": '',
                "out_time": now_time, "out_text": '', "out_data": '',
                "status": '',
                "upd_time": now_time, "dsp_time": None, }
        return True

    async def post_input_log(self, postData: InputLogModel):
        """
        input_logを更新する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = postData.user_id
        request_text = postData.request_text
        input_text = postData.input_text
        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        with self.thread_lock:
            self.data.subai_input_log_key += 1
            self.data.subai_input_log_all[self.data.subai_input_log_key] = {
                    "user_id": user_id, "from_port": self.core_port, "to_post": self.core_port,
                    "req_mode": 'log',
                    "inp_time": now_time, 
                    "sys_text": 'あなたは美しい日本語を話す賢いアシスタントです。', 
                    "req_text": request_text, 
                    "inp_text": input_text,
                    "upd_time": now_time, "dsp_time": None, }

        # 処理結果
        return JSONResponse(content={'message': 'post_input_log successfully'})

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

    coreai1 = main_class(   runMode='debug', qLog_fn='', 
                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)

    #while True:
    #    time.sleep(5)


