#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'webui:8'

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
import codecs

import json
import re

from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from fastapi import Form
from typing import List
import uvicorn
from pydantic import BaseModel
import chardet

import threading
import subprocess

import socket
qHOSTNAME = socket.gethostname().lower()

# 各種ディレクトリパスの設定
qPath_log       = 'temp/_log/'
qPath_input     = 'temp/input/'
qPath_output    = 'temp/output/'
qPath_tts       = 'temp/s6_5tts_txt/'
qPath_templates = '_webui/monjyu'
qPath_static    = '_webui/monjyu/static'
win_code_path   = 'C:/Program Files/Microsoft VS Code/Code.exe'


# 音声合成文字列モデル
class ttsTextModel(BaseModel):
    speech_text: str

# speech json 文字列モデル
class speechJsonModel(BaseModel):
    speech_json: str
    speaker_male1: str
    speaker_male2: str
    speaker_female1: str
    speaker_female2: str
    speaker_etc: str
    tts_yesno: str


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


class WebUiProcess:
    """
    Web UIプロセスの管理クラス
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreai=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', 
                        self_port: str = '8008'):

        # Web UIクラスのインスタンス化とスレッドの開始
        webui_class = WebUiClass(   runMode=runMode, qLog_fn=qLog_fn,
                                    main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                    coreai=coreai,
                                    core_port=core_port, sub_base=sub_base, num_subais=num_subais, 
                                    self_port=self_port, )
        webui_thread = threading.Thread(target=webui_class.run)
        webui_thread.daemon = True
        webui_thread.start()

        # 永続的な実行
        while True:
            time.sleep(5)

class WebUiClass:
    """
    ウェブUIクラス
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreai=None,
                        core_port: str = '8000', sub_base: str = '8100', num_subais: str = '48', 
                        self_port: str = '8008', ):
        self.runMode = runMode

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug('init')

        # 各種設定の初期化
        self.main       = main
        self.conf       = conf
        self.data       = data
        self.addin      = addin
        self.botFunc    = botFunc
        self.mcpHost    = mcpHost
        self.coreai     = coreai
        self.core_port  = core_port
        self.core_port0 = str(int(core_port) + 0)
        self.core_port1 = str(int(core_port) + 1)
        self.core_port2 = str(int(core_port) + 2)
        self.core_port4 = str(int(core_port) + 4)
        self.core_port5 = str(int(core_port) + 5)
        self.sub_base  = sub_base
        self.self_port = self_port
        self.num_subais = int(num_subais)
        self.core_endpoint0 = f'http://{ qHOSTNAME }:{ self.core_port0 }'
        self.core_endpoint1 = f'http://{ qHOSTNAME }:{ self.core_port1 }'
        self.core_endpoint2 = f'http://{ qHOSTNAME }:{ self.core_port2 }'
        self.core_endpoint4 = f'http://{ qHOSTNAME }:{ self.core_port4 }'
        self.core_endpoint5 = f'http://{ qHOSTNAME }:{ self.core_port5 }'

        # スレッドロックの初期化
        self.thread_lock = threading.Lock()

        # FastAPIの設定
        self.app = FastAPI()

        # APIエンドポイントの設定
        self.app.get("/")(self.root)
        self.app.get("/{filename}.html")(self.html_serve)
        self.app.post("/post_text_files")(self.post_text_files)
        self.app.post("/post_drop_files")(self.post_drop_files)
        self.app.get("/get_output_file/{filename}")(self.get_output_file)
        self.app.get("/get_source")(self.get_source)
        self.app.post("/post_tts_text")(self.post_tts_text)
        self.app.post("/post_tts_csv")(self.post_tts_csv)
        self.app.post("/post_files_out2inp")(self.post_files_out2inp)
        self.app.get("/get_stt")(self.get_stt)
        self.app.get("/get_url_to_text")(self.get_url_to_text)
        self.app.post("/post_speech_json")(self.post_speech_json)
        self.app.get("/get_sandbox_update")(self.get_sandbox_update)
        self.app.post("/post_sandbox_open")(self.post_sandbox_open)

        # テンプレートとスタティックファイルのマウント
        self.app.mount("/", StaticFiles(directory=qPath_templates), name="root")
        self.app.mount("/static", StaticFiles(directory=qPath_static), name="static")

    async def root(self, request: Request):
        return RedirectResponse(url="/index.html")

    async def html_serve(self, filename: str, request: Request):
        # HTMLファイルのパスを構築
        file_path = f"_webui/monjyu/{filename}.html"        
        # ファイルが存在するか確認
        if not os.path.isfile(file_path):
            return HTMLResponse(content="File not found", status_code=404)
        # ファイルを読み込む
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        # コンテンツ一部書き換え
        html_content = html_content.replace("http://localhost:8000", self.core_endpoint0)
        html_content = html_content.replace("http://localhost:8001", self.core_endpoint1)
        html_content = html_content.replace("http://localhost:8002", self.core_endpoint2)
        html_content = html_content.replace("http://localhost:8004", self.core_endpoint4)
        html_content = html_content.replace("http://localhost:8005", self.core_endpoint5)
        if (filename == 'statuses'):
            subai_ports = [str(port) for port in range(int(self.sub_base) + 1, int(self.sub_base) + 1 + self.num_subais)]
            subai_divs = "\n".join([f'<div class="subai NONE" id="subai-{port}">{port}<span class="tooltip"></span></div>' for port in subai_ports])
            html_content = html_content.replace("{subai_divs}", subai_divs)
        # 返信
        return HTMLResponse(content=html_content)

    async def post_text_files(self, drop_target: str = Form(...), files: list[UploadFile] = File(...)):
        # アップロードされた複数ファイルを解析してテキストを返す
        drop_text = ''
        for file in files:
            _, file_extension = os.path.splitext(file.filename.lower())
            if (file_extension in [".py", ".txt", ".html", ".json", ".csv", ".bas", ".vba"]):
                file_content = await file.read()
                encoding = chardet.detect(file_content)['encoding']
                text = file_content.decode(encoding)
                if (drop_target == 'system_text'):
                    drop_text += f"\n{ text.rstrip() }\n"
                else:
                    drop_text += f"\n''' { file.filename }\n{ text.rstrip() }\n'''"
        return JSONResponse(content={ "drop_text": drop_text })

    async def post_drop_files(self, files: List[UploadFile] = File(...)):
        # アップロードされたファイルを入力ディレクトリに保存
        for file in files:
            contents = await file.read()
            with open(os.path.join(qPath_input, file.filename), "wb") as f:
                f.write(contents)
        return JSONResponse(content={'message': 'post_drop_files successfully'})

    async def get_output_file(self, filename: str):
        # 指定された出力ファイルをダウンロード用に返す
        file_path = os.path.join(qPath_output, filename)
        return FileResponse(file_path, filename=filename)

    async def get_source(self, source_name: str):
        # ソースコードを取得する
        try:
            res_content = f"''' { source_name }\n"
            with open(source_name, 'r', encoding='utf-8') as f:
                source_code = f.read()
            res_content += source_code
            res_content = res_content.strip() + "\n'''\n"
            return JSONResponse(content={"source_text": res_content})
        except FileNotFoundError:
            raise HTTPException(status_code=503, detail='get_source error:' + str(source_name))

    async def post_tts_text(self, data: ttsTextModel):
        speech_text = str(data.speech_text) if data.speech_text else ""

        # 音声合成
        addin_module = self.addin.addin_modules.get('extension_UI_TTS', None)
        nowTime  = datetime.datetime.now()
        stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
        file_seq = 0

        if (addin_module is not None):
            try:
                # [で始まる１行目削除
                speech_text = speech_text.strip()
                if (speech_text[:1] == '[') and (speech_text.find('\n') >= 0):
                    speech_text = speech_text[speech_text.find('\n')+1:]
                # エンジン指定
                text = speech_text
                if (self.data is not None):
                    engine = self.data.addins_setting['speech_tts_engine']
                    if (engine != ''):
                        text = engine + ',\n' + speech_text
                # TTS
                #file_seq += 1
                seq = '{:04}'.format(file_seq)
                filename = qPath_tts + stamp + '.' + seq + '.tts_text.txt'
                txtsWrite(filename, txts=[text], encoding='utf-8', mode='w', )
            except Exception as e:
                print(e)

        return JSONResponse({'message': 'post_tts_text successfully'})

    async def post_tts_csv(self, data: ttsTextModel):
        speech_text = str(data.speech_text) if data.speech_text else ""

        # 音声合成
        addin_module = self.addin.addin_modules.get('extension_UI_TTS', None)
        nowTime  = datetime.datetime.now()
        stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
        file_seq = 0

        if (addin_module is not None):
            try:
                # [で始まる１行目削除
                speech_text = speech_text.strip()
                if (speech_text[:1] == '[') and (speech_text.find('\n') >= 0):
                    speech_text = speech_text[speech_text.find('\n')+1:]
                # 行分割
                text_list = speech_text.splitlines()
                # TTS
                for text in text_list:
                    if (text.strip() != ''):
                        file_seq += 1
                        seq = '{:04}'.format(file_seq)
                        filename = qPath_tts + stamp + '.' + seq + '.tts_csv.txt'
                        txtsWrite(filename, txts=[text], encoding='utf-8', mode='w', )
            except Exception as e:
                print(e)

        return JSONResponse({'message': 'post_tts_csv successfully'})

    async def post_files_out2inp(self):
        # コピーしたファイル数をカウント
        copied_count = 0

        try:
            # 出力ディレクトリ内のファイル一覧を取得
            file_table = [
                (f, os.path.getctime(os.path.join(qPath_output, f)))
                for f in os.listdir(qPath_output)
                if os.path.isfile(os.path.join(qPath_output, f))
            ]
                        
            # 現在時刻を取得
            now = datetime.datetime.now()
            # 5分前の時刻を計算
            five_minutes_ago = now - datetime.timedelta(minutes=5)
            
            # 各ファイルについて処理
            for f, create_time in file_table:
                # ファイルの作成日時が5分以内かチェック
                if datetime.datetime.fromtimestamp(create_time) >= five_minutes_ago:
                    src_path = os.path.join(qPath_output, f)
                    dst_path = os.path.join(qPath_input, f)
                    
                    # ファイルをコピー（メタデータを保持）
                    shutil.copy2(src_path, dst_path)
                    copied_count += 1
            
        except Exception as e:
            print(e)
        return JSONResponse({'message': f'post_files_out2inp successfully: {copied_count} files copied'})

    async def get_stt(self, input_field: str ):
        # 音声入力
        addin_module = self.botFunc.function_modules.get('execute_speech_to_text', None)
        if (addin_module is not None):
            try:
                dic = {}
                dic['runMode']  = self.runMode
                dic['api']      = 'auto' # auto, google, openai,
                dic['language'] = 'auto'
                # エンジン指定
                if (self.data is not None):
                    engine = self.data.addins_setting['speech_stt_engine']
                    if (engine != ''):
                        dic['api'] = engine
                json_dump = json.dumps(dic, ensure_ascii=False, )
                addin_func_proc  = addin_module['func_proc']
                res_json = addin_func_proc( json_dump )
                args_dic = json.loads(res_json)
                recognition_text = args_dic.get('recognition_text')
                return JSONResponse(content={"recognition_text": recognition_text})
            except Exception as e:
                print(e)
                recognition_text = '!'
        raise HTTPException(status_code=503, detail='get_stt error')

    async def get_url_to_text(self, url_path: str ):
        # URLからテキスト取得
        addin_module = self.botFunc.function_modules.get('url_to_text', None)
        if (addin_module is not None):
            try:
                dic = {}
                dic['runMode']  = self.runMode
                dic['url_path'] = url_path
                json_dump = json.dumps(dic, ensure_ascii=False, )
                addin_func_proc  = addin_module['func_proc']
                res_json = addin_func_proc( json_dump )
                args_dic = json.loads(res_json)
                result_text = args_dic.get('result_text')
                return JSONResponse(content={"result_text": result_text})
            except Exception as e:
                print(e)
                result_text = '!'
        raise HTTPException(status_code=503, detail='get_url_to_text error')

    async def post_speech_json(self, data: speechJsonModel):
        # speech json 音声合成
        speech_json = data.speech_json
        speaker_male1 = data.speaker_male1
        speaker_male2 = data.speaker_male2
        speaker_female1 = data.speaker_female1
        speaker_female2 = data.speaker_female2
        speaker_etc = data.speaker_etc
        tts_yesno = data.tts_yesno

        # 音声合成
        addin_module = self.addin.addin_modules.get('extension_UI_TTS', None)
        nowTime  = datetime.datetime.now()
        stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
        file_seq = 0

        # 正規表現を使用してJSONを抽出
        json_match = re.search(r'\{.*\}', speech_json, re.DOTALL)
        if not json_match:
            raise HTTPException(status_code=503, detail='post_speech_json error')

        try:
            json_text = json_match.group()
            speech_dic = json.loads( json_text.replace('\n', '') )

            # 話者分類
            male = 0
            female = 0
            speaker = {}
            for speech in speech_dic['speech']:
                gender = speech['gender']
                if (speech['who'] not in speaker.keys()):
                    if (gender.lower() in ['男', 'male']):
                        male += 1
                        speaker[ speech['who'] ] = '男' + str(male).strip()
                    if (gender.lower() in ['女', 'female']):
                        female += 1
                        speaker[ speech['who'] ] = '女' + str(female).strip()

            # 話者変換
            for key in speaker.keys():
                if   (speaker[key][:2] == '男1'):
                    if (speaker_male1 != 'none'):
                        if (speaker_male1 == ''):
                            speaker[key] = '青山龍星'
                        else:
                            speaker[key] = speaker_male1
                elif (speaker[key][:1] == '男'):
                    if (speaker_male2 != 'none'):
                        if (speaker_male2 == ''):
                            speaker[key] = '玄野武宏'
                        else:
                            speaker[key] = speaker_male2
                elif (speaker[key][:2] == '女1'):
                    if (speaker_female1 != 'none'):
                        if (speaker_female1 == ''):
                            speaker[key] = '四国めたん'
                        else:
                            speaker[key] = speaker_female1
                elif (speaker[key][:2] == '女2'):
                    if (speaker_female2 != 'none'):
                        if (speaker_female2 == ''):
                            speaker[key] = '九州そら'
                        else:
                            speaker[key] = speaker_female2
                else:
                    if (speaker_etc != 'none'):
                        if (speaker_etc == ''):
                            speaker[key] = 'ずんだもん'
                        else:
                            speaker[key] = speaker_etc

            # 読み上げ
            speech_text = ''
            for speech in speech_dic['speech']:
                gender = speech['gender']
                if (gender.lower() in ['男', 'male']):
                    gender = '男'
                if (gender.lower() in ['女', 'female']):
                    gender = '女'
                name = speech['who']
                if (name in speaker.keys()):
                    name = speaker[ name ]
                text = speech['text']
                text = text.replace('\n',' ')
                text = text.replace('。','. ')
                tts_text = f'{ name },"{ text }"\n'
                speech_text += tts_text

                # TTS
                if (addin_module is not None):
                    if (tts_yesno == 'yes'):
                        try:
                            text = tts_text.strip()
                            file_seq += 1
                            seq = '{:04}'.format(file_seq)
                            filename = qPath_tts + stamp + '.' + seq + '.speech_json.txt'
                            txtsWrite(filename, txts=[text], encoding='utf-8', exclusive=False, mode='w', )
                        except Exception as e:
                            print(e)

            # 結果出力
            nowTime  = datetime.datetime.now()
            stamp    = nowTime.strftime('%Y%m%d.%H%M%S')
            filename = qPath_output + stamp + '.speech.csv'
            txtsWrite(filename, txts=[speech_text], encoding='utf-8', mode='w', )

            return JSONResponse(content={'message': 'post_speech_json successfully', 'speech_text': speech_text})

        except Exception as e:
            print('post_speech_json', e)
        raise HTTPException(status_code=503, detail='post_speech_json error')

    async def get_sandbox_update(self):
        filename = self.data.sandbox_file
        if (filename is not None):
            filename = os.path.basename(filename)
        result = {  "sandbox_update": self.data.sandbox_update,
                    "sandbox_file": filename,
                 }
        self.data.sandbox_update = False
        return JSONResponse(content=result)

    async def post_sandbox_open(self):
        try:
            if (self.data.sandbox_file is None):
                raise HTTPException(status_code=404, detail='post_sandbox_open error')
            if (not os.path.isfile(self.data.sandbox_file)):
                raise HTTPException(status_code=404, detail='post_sandbox_open error')

            print(self.data.sandbox_file)
            self.code = subprocess.Popen([win_code_path, self.data.sandbox_file, ])
            return JSONResponse(content={'message': 'post_sandbox_open successfully'})
        except Exception as e:
            print('post_sandbox_open', e)
        raise HTTPException(status_code=503, detail='post_sandbox_open error')

    def run(self):
        # サーバー設定と起動
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # フロントエンドのオリジンを指定
            allow_credentials=True,
            allow_methods=["*"],  # すべてのHTTPメソッドを許可
            allow_headers=["*"],  # すべてのヘッダーを許可
        )

        # ウェブUIを起動する
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

    # Web UIプロセスの開始
    webui = WebUiProcess(   runMode='debug', qLog_fn='', 
                            core_port=core_port, sub_base=sub_base, num_subais=numSubAIs)



