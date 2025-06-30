#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'coreai:5'

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
import codecs

import json

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

# インターフェース
qIO_agent2live  = 'temp/monjyu_io_agent2live.txt'

# 定数の定義
DELETE_HISTORIES_SEC  = 3600
DELETE_DEBUGLOG_SEC   = 600

# クリップファイル名モデル
class postClipNamesModel(BaseModel):
    user_id: str
    clip_names: list[str]

# クリップテキストモデル
class postClipTextModel(BaseModel):
    user_id: str
    clip_text: str

# Live送信文字列モデル
class liveRequestModel(BaseModel):
    live_req: str
    live_text: str

# Agent送信文字列モデル
class agentRequestModel(BaseModel):
    request_text: str


class main_class:
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        # コアAIクラスの初期化とスレッドの開始
        coreai5 = coreai5_class(runMode=runMode, qLog_fn=qLog_fn,
                                main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                core_port=core_port, sub_base=sub_base, num_subais=num_subais, )
        coreai5_thread = threading.Thread(target=coreai5.run, daemon=True, )
        coreai5_thread.start()
        while True:
            time.sleep(5)


class coreai5_class:
    """
    コアAIクラス(5)
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreai=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        self.runMode = runMode
        self_port = str(int(core_port)+5)

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

        # FastAPI設定
        self.app = FastAPI()
        self.app.get("/")(self.root)
        self.app.get("/get_histories_all")(self.get_histories_all)
        self.app.get("/get_debug_log_all")(self.get_debug_log_all)
        self.app.post("/post_clip_names")(self.post_clip_names)
        self.app.post("/post_clip_text")(self.post_clip_text)
        self.app.post("/post_live_request")(self.post_live_request)

    async def root(self, request: Request):
        # Web UI にリダイレクト
        return RedirectResponse(url=self.webui_endpoint8 + '/')

    async def get_histories_all(self, user_id: str):
        """
        すべての結果を返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        with self.thread_lock:
            current_time = datetime.datetime.now()
            histories_to_delete = [
                key for key, value in self.data.subai_histories_all.items()
                if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_HISTORIES_SEC
            ]
            for key in histories_to_delete:
                del self.data.subai_histories_all[key]
        return JSONResponse(content=self.data.subai_histories_all)

    async def get_debug_log_all(self, user_id: str):
        """
        すべてのデバッグログを返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        with self.thread_lock:
            current_time = datetime.datetime.now()
            debug_log_to_delete = [
                key for key, value in self.data.subai_debug_log_all.items()
                if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_DEBUGLOG_SEC
            ]
            for key in debug_log_to_delete:
                del self.data.subai_debug_log_all[key]
        return JSONResponse(content=self.data.subai_debug_log_all)

    async def post_clip_names(self, postData: postClipNamesModel):
        """
        クリップファイル名処理
        """
        user_id = str(postData.user_id) if postData.user_id else "debug"
        clip_names = postData.clip_names

        input_text = ''
        for clip_file in clip_names:
            if (self.data is None):
                input_text += clip_file + '\n'

            else:
                _, ext = os.path.splitext(clip_file)

                # url 処理
                if (clip_file[:7] == 'http://') or (clip_file[:8] == 'https://'):
                    if (self.data.addins_setting['text_url_execute'] != 'no,'):

                        addin_module = self.addin.addin_modules.get('addin_url_to_text', None)
                        if (addin_module is not None):
                            if (addin_module['onoff'] == 'on'):
                                try:
                                    dic = {}
                                    dic['runMode']   = self.runMode
                                    dic['url_path'] = clip_file
                                    json_dump = json.dumps(dic, ensure_ascii=False, )
                                    func_proc = addin_module['func_proc']
                                    res_json  = func_proc(json_dump)
                                    res_dic   = json.loads(res_json)
                                    res_text  = res_dic.get('result_text')
                                    if (res_text is not None) and (res_text != '') and (res_text != '!'):
                                        input_text += "''' " + clip_file + "\n"
                                        input_text += res_text.rstrip() + "\n"
                                        input_text += "'''\n"
                                except Exception as e:
                                    #print(e)
                                    pass

                else:

                    # pdf 処理
                    if  (ext.lower() in ['.pdf']) \
                    and (self.data.addins_setting['text_pdf_execute'] != 'no,'):

                        addin_module = self.addin.addin_modules.get('pdf_to_text', None)
                        if (addin_module is not None):
                            if (addin_module['onoff'] == 'on'):
                                try:
                                    dic = {}
                                    dic['runMode']   = self.runMode
                                    dic['file_path'] = clip_file
                                    json_dump = json.dumps(dic, ensure_ascii=False, )
                                    func_proc = addin_module['func_proc']
                                    res_json  = func_proc(json_dump)
                                    res_dic   = json.loads(res_json)
                                    res_text  = res_dic.get('result_text')
                                    if (res_text is not None) and (res_text != '') and (res_text != '!'):
                                        input_text += "''' " + os.path.basename(clip_file) + "\n"
                                        input_text += res_text.rstrip() + "\n"
                                        input_text += "'''\n"
                                except Exception as e:
                                    #print(e)
                                    pass

                    # ocr 処理
                    if  (ext.lower() in ['.png', '.jpg']) \
                    and (self.data.addins_setting['image_ocr_execute'] != 'no,'):

                        addin_module = self.addin.addin_modules.get('image_to_text', None)
                        if (addin_module is not None):
                            if (addin_module['onoff'] == 'on'):
                                try:
                                    dic = {}
                                    dic['runMode']   = self.runMode
                                    dic['file_path'] = clip_file
                                    json_dump = json.dumps(dic, ensure_ascii=False, )
                                    func_proc = addin_module['func_proc']
                                    res_json  = func_proc(json_dump)
                                    res_dic   = json.loads(res_json)
                                    res_text  = res_dic.get('result_text')
                                    if (res_text is not None) and (res_text != '') and (res_text != '!'):
                                        input_text += "''' [OCR] " + os.path.basename(clip_file) + "\n"
                                        input_text += res_text.rstrip() + "\n"
                                        input_text += "'''\n"
                                except Exception as e:
                                    #print(e)
                                    pass

                    # yolo 処理
                    if  (ext.lower() in ['.png', '.jpg']) \
                    and (self.data.addins_setting['image_yolo_execute'] == 'yes,'):

                        addin_module = self.addin.addin_modules.get('image_detect_to_text', None)
                        if (addin_module is not None):
                            if (addin_module['onoff'] == 'on'):
                                try:
                                    dic = {}
                                    dic['runMode']   = self.runMode
                                    dic['file_path'] = clip_file
                                    json_dump = json.dumps(dic, ensure_ascii=False, )
                                    func_proc = addin_module['func_proc']
                                    res_json  = func_proc(json_dump)
                                    res_dic   = json.loads(res_json)
                                    json_str  = res_dic['result_text']
                                    res_text  = ''
                                    if (json_str is not None):
                                        res_val = json.loads(json_str)
                                        for key, val in res_val.items():
                                            res_text += key + ': ' + val + '\n'
                                    if (res_text != ''):
                                        input_text += "''' [YOLO] " + os.path.basename(clip_file) + "\n"
                                        input_text += res_text.rstrip() + "\n"
                                        input_text += "'''\n"
                                except Exception as e:
                                    #print(e)
                                    pass

        if (input_text != ''):
            self._clip_text(user_id=user_id, clip_text=input_text, )

        return JSONResponse(content={'message': 'post_clip_names successfully'})

    async def post_clip_text(self, postData: postClipTextModel):
        """
        クリップテキスト処理
        """
        user_id = str(postData.user_id) if postData.user_id else "debug"
        clip_text = postData.clip_text
        
        if (self.data is not None):
            if (self.data.addins_setting['text_clip_input'] == 'yes,'):
                self._clip_text(user_id=user_id, clip_text=clip_text, )

        return JSONResponse(content={'message': 'post_clip_text successfully'})

    def _clip_text(self, user_id: str, clip_text: str):
        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        with self.thread_lock:
            self.data.subai_input_log_key += 1
            self.data.subai_input_log_all[self.data.subai_input_log_key] = {
                    "user_id": user_id, "from_port": self.core_port, "to_post": self.core_port,
                    "req_mode": 'clip',
                    "inp_time": now_time, 
                    "sys_text": 'same,', 
                    "req_text": 'same,', 
                    "inp_text": clip_text,
                    "upd_time": now_time, "dsp_time": None, }
        return True

    async def post_live_request(self, data: liveRequestModel):
        live_req  = str(data.live_req) if data.live_req else ""
        live_text = str(data.live_text) if data.live_text else ""

        # live送信
        filename = qIO_agent2live
        text = ''
        if (live_req != ''):
            text += live_req.rstrip() + '\n'
        if (live_text != ''):
            text += live_text.rstrip() + '\n'

        try:
            w = codecs.open(filename, 'w', 'utf-8')
            w.write(text)
            w.close()
            w = None
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='post_live_request error:' + e)

        return JSONResponse({'message': 'post_live_request successfully'})

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

    coreai5 = main_class(   runMode='debug', qLog_fn='', 
                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)

    #while True:
    #    time.sleep(5)


