#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'coreai:2'

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
import base64

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
qPath_temp    = 'temp/'
qPath_log     = 'temp/_log/'
qPath_input   = 'temp/input/'
qPath_output  = 'temp/output/'
qPath_tts     = 'temp/s6_5tts_txt/'
qPath_sandbox = 'temp/sandbox/'

qPath_static    = '_webui/monjyu/static'
DEFAULT_ICON    = qPath_static + '/' + "icon_monjyu.gif"

# 定数の定義
DELETE_OUTPUTLOG_SEC  = 600
DELETE_DEBUGLOG_SEC   = 600
DELETE_HISTORIES_SEC  = 3600
LIST_RESULT_LIMITSEC = 1800
LIST_RESULT_AUTOCHECK = 120

# 結果データモデル
class ResultDataModel(BaseModel):
    user_id: str
    from_port: str
    to_port: str
    req_mode: str
    system_text: str
    request_text: str
    input_text: str
    result_savepath: str
    result_schema: str
    output_text: str
    output_data: str
    output_path: str
    output_files: list[str]
    status: str

# output_logモデル
class OutputLogModel(BaseModel):
    user_id: str
    output_text: str
    output_data: str


def txtsWrite(filename, txts=[''], encoding='utf-8', mode='w', ):
    try:
        w = codecs.open(filename, mode, encoding)
        for txt in txts:
            if (encoding != 'shift_jis'):
                w.write(txt + '\n')
            else:
                w.write(txt + '\r\n')
        w.close()
        w = None
        return True
    except Exception as e:
        w = None
        return False


class main_class:
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        # コアAIクラスの初期化とスレッドの開始
        coreai2 = coreai2_class(runMode=runMode, qLog_fn=qLog_fn,
                                main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                core_port=core_port, sub_base=sub_base, num_subais=num_subais, )
        coreai2_thread = threading.Thread(target=coreai2.run, daemon=True, )
        coreai2_thread.start()
        while True:
            time.sleep(5)


class coreai2_class:
    """
    コアAIクラス(2)
    FastAPIサーバーの管理を行う。
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreai=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', ):
        self.runMode = runMode
        self_port = str(int(core_port)+2)

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
        self.last_output_log_user = None
        self.last_debug_log_user = None
        self.last_output_files = None

        # FastAPI設定
        self.app = FastAPI()
        self.app.get("/")(self.root)
        self.app.get("/get_output_log_user")(self.get_output_log_user)
        self.app.get("/get_debug_log_user")(self.get_debug_log_user)
        self.app.get("/get_default_image")(self.get_default_image)
        self.app.get("/get_image_info")(self.get_image_info)
        self.app.post("/post_complete")(self.post_complete)
        self.app.post("/post_debug_log")(self.post_debug_log)
        self.app.post("/post_output_log")(self.post_output_log)
        self.app.post("/post_histories")(self.post_histories)
        self.app.get("/get_output_list")(self.get_output_list)

    async def root(self, request: Request):
        # Web UI にリダイレクト
        return RedirectResponse(url=self.webui_endpoint8 + '/')

    async def get_output_log_user(self, user_id: str):
        """
        最新の1件の出力ログを返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        result = self.last_output_log_user
        result_hit = False
        with self.thread_lock:
            now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            for key, value in self.data.subai_output_log_all.items():
                if (value['user_id'] == user_id):
                    if (value['dsp_time'] == None):
                        result = {}
                        result['output_text'] = ''
                        result['output_data'] = ''
                        if value['out_text'] is not None:
                            result['output_text'] = value['out_text']
                        if value['out_data'] is not None:
                            result['output_data'] = value['out_data']
                        value['dsp_time'] = now_time
                        self.last_output_log_user = result
                        result_hit = True
            # 応答なしの合間に古いデータ削除
            if (result_hit == False):
                current_time = datetime.datetime.now()
                # output log 整理
                output_log_to_delete = [
                    key for key, value in self.data.subai_output_log_all.items()
                    if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_OUTPUTLOG_SEC
                ]
                for key in output_log_to_delete:
                    del self.data.subai_output_log_all[key]
                # histories 整理
                histories_to_delete = [
                    key for key, value in self.data.subai_histories_all.items()
                    if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_HISTORIES_SEC
                ]
                for key in histories_to_delete:
                    del self.data.subai_histories_all[key]
        return JSONResponse(content=result)

    async def get_debug_log_user(self, user_id: str):
        """
        最新の1件のデバッグログを返す。
        """
        if (self.data is None):
            return JSONResponse(content={})

        result = self.last_debug_log_user
        result_hit = False
        with self.thread_lock:
            now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            for key, value in self.data.subai_debug_log_all.items():
                if (value['user_id'] == user_id):
                    if (value['dsp_time'] == None):
                        result = {}
                        result['debug_text'] = ''
                        result['debug_data'] = ''
                        if value['out_text'] is not None:
                            result['debug_text'] = value['out_text']
                        if value['out_data'] is not None:
                            result['debug_data'] = value['out_data']
                        value['dsp_time'] = now_time
                        self.last_debug_log_user = result
                        result_hit = True
            # 応答なしの合間に古いデータ削除
            if (result_hit == False):
                current_time = datetime.datetime.now()
                debug_log_to_delete = [
                    key for key, value in self.data.subai_debug_log_all.items()
                    if (current_time - datetime.datetime.strptime(value['upd_time'], "%Y/%m/%d %H:%M:%S")).total_seconds() > DELETE_DEBUGLOG_SEC
                ]
                for key in debug_log_to_delete:
                    del self.data.subai_debug_log_all[key]
        return JSONResponse(content=result)

    async def get_default_image(self):
        # デフォルト画像データの取得
        image_data = self._get_image_data(DEFAULT_ICON)
        _, image_ext = os.path.splitext(DEFAULT_ICON.lower())
        return JSONResponse(content={"image_data": image_data, "image_ext": image_ext})

    async def get_image_info(self):
        # 次回表示する画像データの取得
        image_data = None
        image_ext  = None
        if (self.coreai is not None):
            if ((time.time() - self.coreai.last_image_time) > 60):
                self.coreai.last_image_file = None
                self.coreai.last_image_time = 0
            if (self.coreai.last_image_file is not None):
                image_data = self._get_image_data(self.coreai.last_image_file)
                if (image_data is not None):
                    _, image_ext = os.path.splitext(self.coreai.last_image_file.lower())
        return JSONResponse(content={"image_data": image_data, "image_ext": image_ext})

    def _get_image_data(self, image_path):
        # 画像ファイルをBase64エンコードしてデータURIスキーマ形式で返す
        image_data = None
        _, image_ext = os.path.splitext(image_path.lower())
        if (image_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            try:
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    image_data = f"data:image/png;base64,{encoded_string}"
            except Exception as e:
                print(e)
        return image_data

    async def post_complete(self, postData: ResultDataModel):
        """
        サブAIから結果を受信する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = str(postData.user_id) if postData.user_id else "debug"
        from_port = str(postData.from_port) if postData.from_port else "?"
        to_port = str(postData.to_port) if postData.to_port else "?"
        req_mode = str(postData.req_mode) if postData.req_mode else "?"
        system_text = postData.system_text
        request_text = postData.request_text
        input_text  = postData.input_text
        result_savepath = postData.result_savepath
        result_schema = postData.result_schema
        output_text = postData.output_text
        output_data = postData.output_data
        output_path = postData.output_path
        output_files = postData.output_files
        status = postData.status
        self._post_complete(    user_id=user_id, from_port=from_port, to_port=to_port,
                                req_mode=req_mode,
                                system_text=system_text, request_text=request_text, input_text=input_text,
                                result_savepath=result_savepath, result_schema=result_schema,
                                output_text=output_text, output_data=output_data,
                                output_path=output_path, output_files=output_files,
                                status=status, )                            
        return JSONResponse(content={'message': 'post_complete received'})

    def _post_complete(self,    user_id: str, from_port: str, to_port: str,
                                req_mode: str,
                                system_text: str, request_text: str, input_text: str,
                                result_savepath: str, result_schema: str,
                                output_text: str, output_data: str,
                                output_path: str, output_files: list[str],
                                status: str, ):
        begin_bye_flag = False
        if (output_text[:6] == 'begin,') \
        or (output_text[:4] == 'bye,'):
            begin_bye_flag = True
        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        if (status != ''):
            if (to_port in self.data.subai_info.keys()):
                with self.thread_lock:
                    self.data.subai_info[to_port]['status'] = status
                    self.data.subai_info[to_port]['upd_time'] = now_time
        key_val = f"{user_id}:{from_port}:{to_port}"
        with self.thread_lock:
            if (begin_bye_flag != True):
                if (status == 'READY'):
                    self.data.subai_debug_log_key += 1
                    self.data.subai_debug_log_all[self.data.subai_debug_log_key] = {
                            "key_val": key_val,
                            "user_id": user_id, "from_port": from_port, "to_post": to_port,
                            "req_mode": req_mode,
                            "inp_time": now_time, "sys_text": system_text, "req_text": request_text, "inp_text": input_text,
                            "out_time": now_time, "out_text": output_text, "out_data": output_data,
                            "status": status,
                            "upd_time": now_time, "dsp_time": None, }
                    #if (req_mode in ['chat', 'vision', 'websearch', 'serial', 'parallel']):
                    if (req_mode != 'session'):
                        self.data.subai_output_log_key += 1
                        self.data.subai_output_log_all[self.data.subai_output_log_key] = {
                                "key_val": key_val,
                                "user_id": user_id, "from_port": from_port, "to_post": to_port,
                                "req_mode": req_mode,
                                "out_time": now_time, "out_text": output_text, "out_data": output_data, 
                                "status": status,
                                "upd_time": now_time, "dsp_time": None, }
                    self.data.subai_histories_key += 1
                    self.data.subai_histories_all[self.data.subai_histories_key] = {
                                "key_val": key_val,
                                "user_id": user_id, "from_port": from_port, "to_post": to_port,
                                "req_mode": req_mode,
                                "inp_time": now_time, "sys_text": system_text, "req_text": request_text, "inp_text": input_text,
                                "out_time": now_time, "out_text": output_text, "out_data": output_data, 
                                "status": status,
                                "upd_time": now_time, "dsp_time": None, }
                if key_val in self.data.subai_sessions_all:
                    self.data.subai_sessions_all[key_val]["out_time"] = now_time
                    self.data.subai_sessions_all[key_val]["out_text"] = output_text
                    self.data.subai_sessions_all[key_val]["out_data"] = output_data
                    self.data.subai_sessions_all[key_val]["status"]  = status
                    self.data.subai_sessions_all[key_val]["upd_time"] = now_time
                    self.data.subai_sessions_all[key_val]["dsp_time"] = None
            if key_val in self.data.subai_sessions_all:
                self.data.subai_sessions_all[key_val]["upd_time"] = now_time
   
        # 結果保存
        if (begin_bye_flag != True):
            if (self.data.addins_setting['result_text_save'] == 'yes,') \
            or (result_savepath != ''):
                to_write_proc = threading.Thread(target=self.to_write, args=(user_id, output_text, output_data, result_savepath), daemon=True, )
                to_write_proc.start()

        # 音声フィードバック
        if (begin_bye_flag != True):
            if (req_mode == 'voice'):
                to_tts_proc = threading.Thread(target=self.to_tts, args=(user_id, output_text, output_data), daemon=True, )
                to_tts_proc.start()
   
        # メモ帳コピー
        if (begin_bye_flag != True):
            if True:
                to_memo_proc = threading.Thread(target=self.to_memo, args=(user_id, output_text, output_data), daemon=True, )
                to_memo_proc.start()

        # ファイル有
        if (begin_bye_flag != True):
            if (output_path != ''):
                out_path_proc = threading.Thread(target=self.out_path, args=(user_id, output_path), daemon=True, )
                out_path_proc.start()

        return True

    def to_write(self, user_id: str, output_text: str, output_data: str, result_savepath: str, ):
        filename = ''
        if (result_savepath != ''):
            filename = qPath_output + os.path.basename(result_savepath)
        else:
            nowTime  = datetime.datetime.now()
            stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
            filename = qPath_output + stamp + '.output.txt'
        try:
            text = output_text.strip()
            if (output_data != ''):
                text = output_data.strip()
            if (text[:1] == '[') and (text.find('\n') >= 0):
                text = text[text.find('\n')+1:]
            txtsWrite(filename, txts=[text], encoding='utf-8', mode='w', )
        except Exception as e:
            print(e)

    def to_tts(self, user_id: str, output_text: str, output_data: str, ):
        addin_module = self.addin.addin_modules.get('extension_UI_TTS', None)
        if (addin_module is not None):
            if (addin_module['onoff'] == 'on'):
                try:
                    text = output_text.strip()
                    if (output_data != ''):
                        text = output_data.strip()
                    if (text[:1] == '[') and (text.find('\n') >= 0):
                        text = text[text.find('\n')+1:]
                    if (len(text) >= 2) and (len(text) <= 100):
                        nowTime  = datetime.datetime.now()
                        stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
                        filename = qPath_tts + stamp + '.coreai_tts.txt'
                        txtsWrite(filename, txts=[text], encoding='utf-8', mode='w', )
                except Exception as e:
                    print(e)

    def to_memo(self, user_id: str, output_text: str, output_data: str, ):
        addin_module = self.addin.addin_modules.get('monjyu_UI_ClipnMonjyu', None)
        if (addin_module is not None):
            if (addin_module['onoff'] == 'on'):
                try:
                    dic = {}
                    dic['runMode']  = self.runMode
                    dic['userId']   = user_id
                    dic['sendText'] = output_text
                    if (output_data != ''):
                        dic['sendText'] = output_data
                    json_dump = json.dumps(dic, ensure_ascii=False, )
                    func_proc = addin_module['func_proc']
                    res_json  = func_proc(json_dump)
                except Exception as e:
                    print(e)

    def out_path(self, user_id: str, output_path: str, ):
        _, ext = os.path.splitext(output_path)
        if (ext.lower() in ['.zip', '.html', '.py']):
            # 自動サンドボックス
            addin_module = self.addin.addin_modules.get('automatic_sandbox', None)
            if (addin_module is not None):
                res_json = None
                try:
                    if (addin_module['onoff'] == 'on'):
                        dic = {}
                        dic['file_path'] = output_path
                        dic['browser'] = "no"
                        json_dump = json.dumps(dic, ensure_ascii=False, )
                        func_proc = addin_module['func_proc']
                        res_json  = func_proc(json_dump)

                        # 表示更新
                        if (ext.lower() in ['.zip', '.html']):
                            self.data.sandbox_update = True
                            self.data.sandbox_file = output_path
                            if (ext.lower() == '.zip'):
                                extract_dir = os.path.basename(output_path).replace('.zip', '')
                                filename = qPath_sandbox + extract_dir + '/package.json'
                                if (os.path.isfile(filename)):
                                    self.data.sandbox_file = filename
                            if (ext.lower() == '.html'):
                                filename = qPath_sandbox + 'react_sandbox/public/index.html'
                                if (os.path.isfile(filename)):
                                    self.data.sandbox_file = filename

                except Exception as e:
                    print(e)
                    res_json = None

    async def post_debug_log(self, postData: ResultDataModel):
        """
        サブAIから途中経過を受信する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = str(postData.user_id) if postData.user_id else "debug"
        from_port = str(postData.from_port) if postData.from_port else "?"
        to_port = str(postData.to_port) if postData.to_port else "?"
        req_mode = str(postData.req_mode) if postData.req_mode else "?"
        system_text = postData.system_text
        request_text = postData.request_text
        input_text  = postData.input_text
        result_savepath = postData.result_savepath
        result_schema = postData.result_schema
        output_text = postData.output_text
        output_data = postData.output_data
        status = postData.status
        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        if (to_port in self.data.subai_info.keys()):
            with self.thread_lock:
                self.data.subai_info[to_port]['upd_time'] = now_time
        key_val = f"{user_id}:{from_port}:{to_port}"
        with self.thread_lock:
            self.data.subai_debug_log_key += 1
            self.data.subai_debug_log_all[self.data.subai_debug_log_key] = {
                    "key_val": key_val,
                    "user_id": user_id, "from_port": from_port, "to_post": to_port,
                    "req_mode": req_mode,
                    "inp_time": now_time, "sys_text": system_text, "req_text": request_text, "inp_text": input_text,
                    "out_time": now_time, "out_text": output_text, "out_data": output_data,
                    "status": status,
                    "upd_time": now_time, "dsp_time": None, }
            if key_val in self.data.subai_sessions_all:
                self.data.subai_sessions_all[key_val]["upd_time"] = now_time
        return JSONResponse(content={'message': 'post_debug_log received'})

    async def post_output_log(self, postData: OutputLogModel):
        """
        output_logを更新する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = postData.user_id
        output_text = postData.output_text
        output_data = postData.output_data
        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        with self.thread_lock:
            self.data.subai_output_log_key += 1
            self.data.subai_output_log_all[self.data.subai_output_log_key] = {
                "user_id": user_id, "from_port": self.core_port, "to_post": self.core_port,
                "req_mode": 'log',
                "out_time": now_time, "out_text": output_text, "out_data": output_data,
                "status": None,
                "upd_time": now_time, "dsp_time": None, }

        # 処理結果
        return JSONResponse(content={'message': 'post_input_log successfully'})

    async def post_histories(self, postData: ResultDataModel):
        """
        エージェントから結果を受信する。
        """
        if (self.data is None):
            raise HTTPException(status_code=503, detail='Service Unavailable')

        user_id = str(postData.user_id) if postData.user_id else "debug"
        from_port = str(postData.from_port) if postData.from_port else "?"
        to_port = str(postData.to_port) if postData.to_port else "?"
        req_mode = str(postData.req_mode) if postData.req_mode else "?"
        system_text = postData.system_text
        request_text = postData.request_text
        input_text  = postData.input_text
        result_savepath = postData.result_savepath
        result_schema = postData.result_schema
        output_text = postData.output_text
        output_data = postData.output_data
        output_path = postData.output_path
        output_files = postData.output_files
        status = postData.status

        now_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        key_val = f"{user_id}:{from_port}:{to_port}"
        with self.thread_lock:
            self.data.subai_histories_key += 1
            self.data.subai_histories_all[self.data.subai_histories_key] = {
                "key_val": key_val,
                "user_id": user_id, "from_port": from_port, "to_post": to_port,
                "req_mode": req_mode,
                "inp_time": now_time, "sys_text": system_text, "req_text": request_text, "inp_text": input_text,
                "out_time": now_time, "out_text": output_text, "out_data": output_data, 
                "status": status,
                "upd_time": now_time, "dsp_time": None, }
   
        # 処理結果
        return JSONResponse(content={'message': 'post_histories successfully'})

    async def get_output_list(self):
        # 出力ディレクトリ内のファイル一覧を取得
        now = datetime.datetime.now()
        file_table = [
            (f, os.path.getmtime(os.path.join(qPath_output, f)))
            for f in os.listdir(qPath_output)
            if os.path.isfile(os.path.join(qPath_output, f))
        ]
        file_table.sort(key=lambda x: x[1], reverse=True)
        output_files = []
        image_file = ''
    
        for f, mod_time in file_table:
            if (now - datetime.datetime.fromtimestamp(mod_time)) < datetime.timedelta(seconds=LIST_RESULT_LIMITSEC):
                file_path = os.path.join(qPath_output, f)
                if (now - datetime.datetime.fromtimestamp(mod_time)) < datetime.timedelta(seconds=LIST_RESULT_AUTOCHECK):
                    checked = True # 時間内全てチェック
                    if (image_file == ''):
                        image_file = file_path
                else:
                    checked = False
                output_files.append(
                    #f"{f} {datetime.datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S')} {checked}"
                    {"file_name": f, "upd_time": datetime.datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S'), "checked": checked}
                )
            else:
                break
        
        if (self.last_output_files != output_files):
            self.last_output_files = output_files
            if (self.coreai is not None):
                self.coreai.last_image_file = image_file
                self.coreai.last_image_time = time.time()
        return JSONResponse(content={"files": output_files})

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

    coreai2 = main_class(   runMode='debug', qLog_fn='', 
                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)

    #while True:
    #    time.sleep(5)


