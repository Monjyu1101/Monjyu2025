#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'gemini'

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
import queue


# API ライブラリ
from google import genai
from google.genai import types

# モジュールインポート
import speech_bot__common
bot_common = speech_bot__common._bot_common()
import speech_bot_gemini_key as gemini_key

# インターフェース
qPath_output = 'temp/output/'


class _geminiAPI:
    """
    APIを操作するクラス
    APIを使用したチャットボット機能を提供
    """

    def __init__(self):
        """
        APIクラスのコンストラクタ
        各種設定値の初期化を行う
        """
        logger.debug("APIクラスを初期化")

        # ログとアクセス関連
        self.stream_queue = None
        self.bot_auth = None

        # 生成パラメータ
        self.temperature = 0.8

        # デフォルト設定
        self.api_type = 'gemini'
        self.default_gpt = 'auto'
        self.default_class = 'auto'
        self.auto_continue = 3
        self.max_step = 10
        self.max_session = 5
        self.max_wait_sec = 120
       
        # API認証情報
        self.key_id = None

        # モデルA設定 (基本モデル)
        self.a_enable = False
        self.a_nick_name = ''
        self.a_model = None
        self.a_token = 0
        self.a_use_tools = 'no'

        # モデルB設定 (拡張モデル)
        self.b_enable = False
        self.b_nick_name = ''
        self.b_model = None
        self.b_token = 0
        self.b_use_tools = 'no'

        # モデルV設定 (ビジョン対応モデル)
        self.v_enable = False
        self.v_nick_name = ''
        self.v_model = None
        self.v_token = 0
        self.v_use_tools = 'no'

        # モデルX設定 (特殊モデル)
        self.x_enable = False
        self.x_nick_name = ''
        self.x_model = None
        self.x_token = 0
        self.x_use_tools = 'no'

        # セーフティ設定
        self.safety_settings = [
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        # モデル情報とセッション管理
        self.models = {}
        self.history = []

        self.seq = 0
        self.reset()

    def init(self, stream_queue=None):
        """
        インスタンスの初期化、ストリームQの設定
        Args:
            stream_queue (Queue, optional): ログメッセージを送るキュー
        Returns:
            bool: 常にTrue
        """
        logger.debug(f"init() ストリームQを設定: {stream_queue is not None}")
        self.stream_queue = stream_queue
        return True

    def reset(self):
        """
        会話履歴をリセットする
        Returns:
            bool: 常にTrue
        """
        logger.debug("reset() 会話履歴をリセットします")
        self.history = []
        return True

    def print(self, session_id='admin', text=''):
        """
        ストリームQにテキストを出力する
        Args:
            session_id (str, optional): セッションID
            text (str, optional): 出力するテキスト
        """
        if (session_id == 'admin') and (self.stream_queue is not None):
            try:
                self.stream_queue.put(['chatBot', text + '\n'])
            except Exception as e:
                logger.error(f"ストリームQへの出力に失敗: {e}")

    def stream(self, session_id='admin', text=''):
        """
        ストリームQにテキストを出力する（文字）
        Args:
            session_id (str, optional): セッションID
            text (str, optional): 出力するテキスト
        """
        if (session_id == 'admin') and (self.stream_queue is not None):
            try:
                self.stream_queue.put(['chatBot', text])
            except Exception as e:
                logger.error(f"ストリームQへの出力に失敗: {e}")

    def authenticate(self, api,
                     api_type,
                     default_gpt, default_class,
                     auto_continue,
                     max_step, max_session,
                     max_wait_sec,

                     key_id,

                     a_nick_name, a_model, a_token, 
                     a_use_tools, 
                     b_nick_name, b_model, b_token, 
                     b_use_tools, 
                     v_nick_name, v_model, v_token, 
                     v_use_tools, 
                     x_nick_name, x_model, x_token, 
                     x_use_tools, 
                    ):
        """
        APIの認証と設定を行う
        Args:
            api (str): API識別子
            api_type (str): APIタイプ
            その他多数のパラメータ: 各種モデル設定、認証情報等
        Returns:
            bool: 認証成功時True、失敗時False
        """
        logger.debug(f"authenticate() APIタイプ: {api_type}")

        # 認証状態初期化
        self.bot_auth = None
        self.api_type = api_type
        self.key_id = key_id
 
        # APIクライアントの初期化
        self.client = None
        try:
            # API認証
            if (key_id[:1] == '<'):
                logger.warning("APIキーが未設定です")
                return False
            else:
                logger.debug("APIクライアントを初期化します")
                self.client = genai.Client(api_key=key_id)
        except Exception as e:
            logger.error(f"APIクライアント初期化エラー: {e}")
            return False

        # 設定パラメータの保存
        logger.debug("設定パラメータを適用")
        self.default_gpt = default_gpt
        self.default_class = default_class
        # 数値設定の処理（'auto'の場合は変更しない）
        if (str(auto_continue) not in ['', 'auto']):
            self.auto_continue = int(auto_continue)
        if (str(max_step) not in ['', 'auto']):
            self.max_step = int(max_step)
        if (str(max_session) not in ['', 'auto']):
            self.max_session = int(max_session)
        if (str(max_wait_sec) not in ['', 'auto']):
            self.max_wait_sec = int(max_wait_sec)

        # モデル情報の取得
        self.models = {}
        self.get_models()

        # デフォルト日付（実際はモデル作成日を使用）
        ymd = 'default'

        # モデルA設定 (基本モデル)
        if (a_nick_name != ''):
            logger.debug(f"モデルA設定: {a_model}")
            self.a_enable = False
            self.a_nick_name = a_nick_name
            self.a_model = a_model
            self.a_token = int(a_token)
            self.a_use_tools = a_use_tools
            if (a_model not in self.models):
                self.models[a_model] = {"id": a_model, "token": str(a_token), "modality": "text?", "date": ymd}
            else:
                self.models[a_model]['date'] = ymd

        # モデルB設定 (拡張モデル)
        if (b_nick_name != ''):
            logger.debug(f"モデルB設定: {b_model}")
            self.b_enable = False
            self.b_nick_name = b_nick_name
            self.b_model = b_model
            self.b_token = int(b_token)
            self.b_use_tools = b_use_tools
            if (b_model not in self.models):
                self.models[b_model] = {"id": b_model, "token": str(b_token), "modality": "text?", "date": ymd}
            else:
                self.models[b_model]['date'] = ymd

        # モデルV設定 (ビジョン対応モデル)
        if (v_nick_name != ''):
            logger.debug(f"モデルV設定: {v_model}")
            self.v_enable = False
            self.v_nick_name = v_nick_name
            self.v_model = v_model
            self.v_token = int(v_token)
            self.v_use_tools = v_use_tools
            if (v_model not in self.models):
                self.models[v_model] = {"id": v_model, "token": str(v_token), "modality": "text+image?", "date": ymd}
            else:
                self.models[v_model]['date'] = ymd
                self.models[v_model]['modality'] = "text+image?"

        # モデルX設定 (特殊モデル)
        if (x_nick_name != ''):
            logger.debug(f"モデルX設定: {x_model}")
            self.x_enable = False
            self.x_nick_name = x_nick_name
            self.x_model = x_model
            self.x_token = int(x_token)
            self.x_use_tools = x_use_tools
            if (x_model not in self.models):
                self.models[x_model] = {"id": x_model, "token": str(x_token), "modality": "text+image?", "date": ymd}
            else:
                self.models[x_model]['date'] = ymd

        # 有効なモデルの存在確認
        hit = False
        if (self.a_model != ''):
            self.a_enable = True
            hit = True
        if (self.b_model != ''):
            self.b_enable = True
            hit = True
        if (self.v_model != ''):
            self.v_enable = True
            hit = True
        if (self.x_model != ''):
            self.x_enable = True
            hit = True

        # 認証結果を返す
        if hit:
            logger.debug("authenticate() 認証成功")
            self.bot_auth = True
            return True
        else:
            logger.debug("authenticate() 認証失敗")
            return False

    def get_models(self):
        """
        利用可能なモデルの一覧を取得する
        Returns:
            bool: 取得成功時True、失敗時False
        """
        logger.debug("get_models() モデル一覧を取得します")
        try:
            models = self.client.models.list()
            self.models = {}
            for model in models:
                if ("generateContent" in model.supported_actions):
                    key = model.name.replace('models/', '')
                    if (key.find('gemini-2') >= 0) or (key.find('gemini-exp') >= 0):
                        token = model.input_token_limit
                        self.models[key] = {"id": key, "token": str(token), "modality": str(model.supported_actions), "date": '????/??/??'}
            logger.debug(f"get_models() {len(self.models)}個のモデルを取得しました")
            return True
        except Exception as e:
            logger.error(f"get_models() モデル取得エラー: {e}")
            return False

    def set_models(self, max_wait_sec='',
                         a_model='', a_use_tools='',
                         b_model='', b_use_tools='',
                         v_model='', v_use_tools='',
                         x_model='', x_use_tools=''):
        """
        モデル設定を変更する
        Args:
            max_wait_sec (str, optional): 最大待機時間
            a_model (str, optional): Aモデル名
            a_use_tools (str, optional): Aモデルのツール使用設定
            b_model (str, optional): Bモデル名
            b_use_tools (str, optional): Bモデルのツール使用設定
            v_model (str, optional): Vモデル名
            v_use_tools (str, optional): Vモデルのツール使用設定
            x_model (str, optional): Xモデル名
            x_use_tools (str, optional): Xモデルのツール使用設定
        Returns:
            bool: 設定成功時True、失敗時False
        """
        logger.debug("set_models() モデル設定を更新します")
        try:
            # 最大待機時間の設定
            if (max_wait_sec not in ['', 'auto']):
                if (str(max_wait_sec) != str(self.max_wait_sec)):
                    self.max_wait_sec = int(max_wait_sec)
                    logger.debug(f"最大待機時間を{max_wait_sec}秒に設定")

            # モデルA設定 (基本モデル)
            if (a_model != ''):
                if (a_model != self.a_model) and (a_model in self.models):
                    self.a_enable = True
                    self.a_model = a_model
                    self.a_token = int(self.models[a_model]['token'])
                    logger.debug(f"モデルAを{a_model}に変更")
            if (a_use_tools != ''):
                self.a_use_tools = a_use_tools

            # モデルB設定 (拡張モデル)
            if (b_model != ''):
                if (b_model != self.b_model) and (b_model in self.models):
                    self.b_enable = True
                    self.b_model = b_model
                    self.b_token = int(self.models[b_model]['token'])
                    logger.debug(f"モデルBを{b_model}に変更")
            if (b_use_tools != ''):
                self.b_use_tools = b_use_tools

            # モデルV設定 (ビジョン対応モデル)
            if (v_model != ''):
                if (v_model != self.v_model) and (v_model in self.models):
                    self.v_enable = True
                    self.v_model = v_model
                    self.v_token = int(self.models[v_model]['token'])
                    logger.debug(f"モデルVを{v_model}に変更")
            if (v_use_tools != ''):
                self.v_use_tools = v_use_tools
                
            # モデルX設定 (特殊モデル)
            if (x_model != ''):
                if (x_model != self.x_model) and (x_model in self.models):
                    self.x_enable = True
                    self.x_model = x_model
                    self.x_token = int(self.models[x_model]['token'])
                    logger.debug(f"モデルXを{x_model}に変更")
            if (x_use_tools != ''):
                self.x_use_tools = x_use_tools
                
            logger.debug("set_models() モデル設定を更新しました")
            return True
        except Exception as e:
            logger.error(f"set_models() モデル設定更新エラー: {e}")
            return False

    def run_gpt(self, chat_class='chat', model_select='auto',
                nick_name=None, model_name=None,
                session_id='admin', history=[],
                function_modules={},
                sysText=None, reqText=None, inpText='こんにちは',
                upload_files=[], image_urls=[],
                temperature=0.8, max_step=10, jsonSchema=None):
        """レスポンスを生成"""
        # 戻り値の初期化
        res_text = ''
        res_path = ''
        res_files = []
        res_name = None
        res_api = None
        res_history = history

        # 認証状態確認
        if (self.bot_auth is None):
            logger.error("API認証されていません!")
            return res_text, res_path, res_files, res_name, res_api, res_history

        # モデル選択
        inpText, res_name, res_api, use_tools = bot_common.select_model(
                chat_class, model_select, inpText, upload_files, image_urls,
                self.a_nick_name, self.a_model, self.a_use_tools,
                self.b_nick_name, self.b_model, self.b_use_tools,
                self.v_nick_name, self.v_model, self.v_use_tools,
                self.x_nick_name, self.x_model, self.x_use_tools)

        # 履歴の追加と圧縮
        res_history = bot_common.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText)
        res_history = bot_common.history_zip1(history=res_history)

        # メッセージの作成
        msg_text = bot_common.history2msg_text(history=res_history)

        # アップロードファイルの処理
        req_files = []
        for file_name in upload_files:
            if (os.path.isfile(file_name)):
                # ファイルが既にアップロード済みかチェック
                hit = False
                up_files = self.client.files.list()
                for upf in up_files:
                    if (upf.display_name == os.path.basename(file_name)):
                        hit = True
                        upload_obj = self.client.files.get(name=upf.name)
                        req_files.append(types.Part.from_uri(file_uri=upload_obj.uri, mime_type=upload_obj.mime_type))
                        break

                # 特別処理: 毎回ファイルを送信
                if True:
                    # ファイルアップロード
                    logger.info(f"//Gemini// Upload file '{file_name}'.")
                    upload_file = self.client.files.upload(file=file_name)
                    upload_obj = self.client.files.get(name=upload_file.name)
                    
                    # アップロード処理完了を待機
                    logger.info(f"//Gemini// Upload processing ... '{upload_file.name}'.")
                    chkTime = time.time()
                    while ((time.time() - chkTime) < 120) and (upload_file.state.name == "PROCESSING"):
                        time.sleep(5.00)
                    if (upload_file.state.name == "PROCESSING"):
                        logger.error("//Gemini// Upload timeout. (120s)")
                        return res_text, res_path, res_files, res_name, res_api, res_history
                        
                    # アップロード完了
                    logger.info("//Gemini// Upload complete.")
                    req_files.append(types.Part.from_uri(file_uri=upload_obj.uri, mime_type=upload_obj.mime_type))

        # ストリーミングモード無効
        stream = False

        # ツール（関数）設定
        tools = []
        if (use_tools.lower().find('yes') >= 0):
            function_declarations = []
            for module_name, module_dic in function_modules.items():
                func_dic = module_dic['function']
                not_support = False
                properties = func_dic['parameters'].get('properties', {})
                for field in properties:
                    if properties[field]['type'] in ['array', 'boolean']:
                        not_support = True
                if not_support == False:
                    function_declarations.append(func_dic)
                    #print(func_dic)
            if (len(function_declarations) > 0):
                tools.append({"function_declarations": function_declarations})

        # API設定
        if (jsonSchema is None) or (jsonSchema == ''):
            if (res_api.find('image-gen') < 0):
                # 通常モデル
                if (len(image_urls) <= 0):
                    generation_config = types.GenerateContentConfig(
                        temperature=temperature,
                        top_p=0.95,
                        top_k=32,
                        max_output_tokens=8192,
                        tools=tools,
                        response_mime_type="text/plain")
                # 画像認識モデル
                else:
                    generation_config = types.GenerateContentConfig(
                        temperature=temperature,
                        top_p=0.95,
                        top_k=32,
                        max_output_tokens=8192,
                        response_mime_type="text/plain")
            # イメージ生成モデル
            else:
                generation_config = types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=0.95,
                    top_k=32,
                    max_output_tokens=8192,
                    response_mime_type="text/plain",
                    response_modalities=["Image", "Text"])
        else:
            # JSONスキーマモード（2024/09/04時点ではツール使用不可）
            tools = []
            generation_config = types.GenerateContentConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=32,
                max_output_tokens=8192,
                tools=tools,
                response_mime_type="application/json")

        # リクエスト作成
        request = []
        parts = []
        parts.append(types.Part.from_text(text=msg_text))
        for file_obj in req_files:
            parts.append(file_obj)
        request.append(types.Content(role="user", parts=parts))

        # 実行ループ
        if True:
            n = 0
            function_name = ''
            while (function_name != 'exit') and (n < int(max_step)):
                # 結果初期化
                res_role = ''
                res_content = ''
                tool_calls = []

                # モデル実行
                n += 1
                logger.info(f"//Gemini// {res_name.lower()}, {res_api}, pass={n}, ")

                # 結果初期化
                content_text = ''
                content_parts = None

                # ストリーミング実行
                if (stream == True):
                    chkTime = time.time()
                    streams = self.client.models.generate_content_stream(
                        model=res_api,
                        contents=request,
                        config=generation_config,
                    )

                    # ストリーム処理
                    for chunk in streams:
                        if ((time.time() - chkTime) > self.max_wait_sec):
                            logger.warning("ストリーミング処理がタイムアウト")
                            break

                        # 各パートの処理
                        for p in range(len(chunk.candidates[0].content.parts)):
                            # テキスト部分
                            delta_text = chunk.candidates[0].content.parts[p].text
                            if (delta_text is not None):
                                if (delta_text != ''):
                                    self.stream(session_id, delta_text)
                                    content_text += delta_text
                            # インラインデータ（画像など）
                            else:
                                inline_data = chunk.candidates[0].content.parts[p].inline_data
                                if (inline_data is not None):
                                    data = inline_data.data
                                    mime_type = inline_data.mime_type
                                    try:
                                        # 画像ファイル出力
                                        nowTime = datetime.datetime.now()
                                        output_path = qPath_output + nowTime.strftime('%Y%m%d.%H%M%S') + '.image.png'
                                        logger.info(f"//Gemini// Save image to '{output_path}'.")
                                        f = open(output_path, 'wb')
                                        f.write(data)
                                        f.close()
                                        res_path = output_path
                                        res_files.append(res_path)
                                    except Exception as e:
                                        logger.error(f"画像保存エラー: {e}")

                        # コンテンツパーツの処理
                        if (content_text == '') and (res_path == ''):
                            content_parts = chunk.candidates[0].content.parts

                    # 改行処理
                    if (content_text != ''):
                        self.print(session_id)

                # 通常実行（ストリームなし）
                if (stream == False):
                    response = self.client.models.generate_content(
                        model=res_api,
                        contents=request,
                        config=generation_config,
                    )

                    # レスポンス処理
                    for p in range(len(response.candidates[0].content.parts)):
                        # テキスト部分
                        chunk_text = response.candidates[0].content.parts[p].text
                        if (chunk_text is not None):
                            if (chunk_text.strip() != ''):
                                self.print(session_id, chunk_text)
                                if (content_text != ''):
                                    content_text += '\n'
                                content_text += chunk_text
                        # インラインデータ（画像など）
                        else:
                            inline_data = response.candidates[0].content.parts[p].inline_data
                            if (inline_data is not None):
                                data = inline_data.data
                                mime_type = inline_data.mime_type
                                try:
                                    # 画像ファイル出力
                                    nowTime = datetime.datetime.now()
                                    output_path = qPath_output + nowTime.strftime('%Y%m%d.%H%M%S') + '.image.png'
                                    logger.info(f"//Gemini// Save image to '{output_path}'.")
                                    f = open(output_path, 'wb')
                                    f.write(data)
                                    f.close()
                                    res_path = output_path
                                    res_files.append(res_path)
                                except Exception as e:
                                    logger.error(f"画像保存エラー: {e}")

                    # コンテンツパーツの処理
                    if (content_text == '') and (res_path == ''):
                        content_parts = response.candidates[0].content.parts

                # テキスト処理
                if (content_text != ''):
                    # Python以外か、完全なPythonコードブロックでない場合は通常処理
                    if (content_text[:9] != "```python") \
                    or (content_text[-3:] != "```"):
                        res_role = 'assistant'
                    else:
                        # Pythonコードブロックの場合は少し待機
                        time.sleep(5.00)
                    res_content += content_text + '\n'
                else:
                    # 画像のみの場合
                    if (res_path != ''):
                        res_role = 'assistant'
                        res_content += res_path + '\n'

                # 関数呼び出し処理
                if (content_parts is not None):
                    try:
                        for parts in content_parts:
                            function_call = parts.function_call
                            if (function_call is not None):
                                f_name = function_call.name
                                f_args = function_call.args
                                f_kwargs = None
                                if (f_name is not None) and (f_args is not None):
                                    # 引数をJSON形式に変換
                                    json_dic = {}
                                    for key, value in f_args.items():
                                        json_dic[key] = value
                                    f_kwargs = json.dumps(json_dic, ensure_ascii=False)
                                    tool_calls.append({"id": parts, "type": "function", "function": {"name": f_name, "arguments": f_kwargs}})
                    except Exception as e:
                        logger.error(f"関数呼び出し解析エラー: {e}")

                # 通常の応答処理
                if (len(tool_calls) <= 0):
                    if (res_role == 'assistant') and (res_content != ''):
                        function_name = 'exit'

                # ツール実行処理
                else:

                    # 新しいリクエスト作成
                    request = []

                    # 各関数呼び出しを処理
                    for tc in tool_calls:
                        f_id = tc.get('id')
                        f_name = tc['function'].get('name')
                        f_kwargs = tc['function'].get('arguments')

                        # 登録された関数モジュールを検索
                        module_dic = function_modules.get(f_name)
                        if (module_dic is None):
                            logger.error(f"//Gemini//   function not found Error ! ({f_name})")
                            break
                                
                        else:
                            hit = True
                            logger.info(f"//Gemini//   function_call '{module_dic['script']}' ({f_name})")
                            logger.info(f"//Gemini//   → {f_kwargs}")

                            # メッセージ追加格納
                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'function_call', 'name': f_name, 'content': f_kwargs}
                            res_history.append(dic)

                            # ツール実行
                            try:
                                ext_func_proc = module_dic['func_proc']
                                if (module_dic['script'] != 'mcp'):
                                    res_json = ext_func_proc(f_kwargs)
                                else:
                                    res_json = ext_func_proc(f_name, f_kwargs)
                            except Exception as e:
                                logger.error(f"ツール実行エラー: {e}")
                                # エラーメッセージ作成
                                res_json = json.dumps({'error': str(e)}, ensure_ascii=False)

                            # 実行結果を表示
                            logger.info(f"//Gemini//   → {res_json}")

                            # 関数応答を作成
                            res_dic = json.loads(res_json)
                            res_list = []
                            for key, value in res_dic.items():
                                res_list.append({"key": key, "value": {"string_value": value}})
                            parts = {"function_response": {"name": f_name, "response": {"fields": res_list} } }
                            request.append(parts)

                            # 履歴に関数結果を追加
                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'function', 'name': f_name, 'content': res_json}
                            res_history.append(dic)

                            # パス情報の抽出（画像やExcelなど）
                            try:
                                dic = json.loads(res_json)
                                path = dic.get('image_path')
                                if (path is None):
                                    path = dic.get('excel_path')
                                if (path is not None):
                                    res_path = path
                                    res_files.append(path)
                                    res_files = list(set(res_files))
                                    logger.debug(f"ファイルパスを検出: {path}")
                            except Exception as e:
                                logger.error(f"パス情報エラー: {e}")

            # 応答結果の確認
            if (res_content != ''):
                res_text += res_content.rstrip()


        # 最終応答結果の確認
        if (res_text != ''):
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': res_text}
            res_history.append(dic)
            logger.info(f"//Gemini// {res_name.lower()}, complete.")
        else:
            logger.error('//Gemini// Error !')

        return res_text, res_path, res_files, res_name, res_api, res_history

    def chatBot(self, chat_class='auto', model_select='auto',
                session_id='admin', history=[],
                function_modules={},
                sysText=None, reqText=None, inpText='こんにちは', 
                filePath=[],
                temperature=0.8, max_step=10, jsonSchema=None,
                inpLang='ja-JP', outLang='ja-JP'):
        """チャットボット機能のメインエントリーポイント"""
        logger.debug("ChatBotの実行を開始")

        # 戻り値の初期化
        res_text = ''
        res_path = ''
        res_files = []
        nick_name = None
        model_name = None
        res_history = history

        # デフォルト設定
        if (sysText is None) or (sysText == ''):
            sysText = 'あなたは美しい日本語を話す賢いアシスタントです。'
        if (inpText is None) or (inpText == ''):
            inpText = reqText
            reqText = None

        # 認証状態確認
        if (self.bot_auth is None):
            logger.error("API認証されていません!")
            return res_text, res_path, res_files, nick_name, model_name, res_history

        # ファイル処理
        upload_files = []
        image_urls = []
        try:
            upload_files, image_urls = bot_common.files_check(filePath=filePath)
        except Exception as e:
            logger.error(f"ファイル処理エラー: {e}")

        # モデル実行
        logger.debug(f"//Gemini// chat_class={chat_class}, model_select={model_select}")
        res_text, res_path, res_files, nick_name, model_name, res_history = \
            self.run_gpt(chat_class=chat_class, model_select=model_select,
                        nick_name=nick_name, model_name=model_name,
                        session_id=session_id, history=res_history,
                        function_modules=function_modules,
                        sysText=sysText, reqText=reqText, inpText=inpText,
                        upload_files=upload_files, image_urls=image_urls,
                        temperature=temperature, max_step=max_step, jsonSchema=jsonSchema)

        # 空応答の処理
        if (res_text.strip() == ''):
            res_text = '!'

        return res_text, res_path, res_files, nick_name, model_name, res_history


if __name__ == '__main__':
    """
    テスト用コード
    """
    logger.setLevel(logging.INFO)
    logger.info("【テスト開始】")

    # APIクラスの初期化
    geminiAPI = _geminiAPI()

    # API種別を取得
    geminiKEY = gemini_key._conf_class()
    geminiKEY.init(runMode='debug')
    logger.info(f"api_type={geminiKEY.api_type}")

    # ログキューの設定
    stream_queue = queue.Queue()
    res = geminiAPI.init(stream_queue=stream_queue)

    print('debug model setting!')
    geminiKEY.a_model = 'gemini-2.0-flash-exp'
    geminiKEY.b_model = 'gemini-2.0-flash-exp'
    geminiKEY.v_model = 'gemini-2.0-flash-exp'
    geminiKEY.x_model = 'gemini-2.0-flash-exp'

    # 認証処理
    res = geminiAPI.authenticate('google',
                        geminiKEY.api_type,
                        geminiKEY.default_gpt, geminiKEY.default_class,
                        geminiKEY.auto_continue,
                        geminiKEY.max_step, geminiKEY.max_session,
                        geminiKEY.max_wait_sec,

                        geminiKEY.gemini_key_id,

                        geminiKEY.a_nick_name, geminiKEY.a_model, geminiKEY.a_token,
                        geminiKEY.a_use_tools,
                        geminiKEY.b_nick_name, geminiKEY.b_model, geminiKEY.b_token,
                        geminiKEY.b_use_tools,
                        geminiKEY.v_nick_name, geminiKEY.v_model, geminiKEY.v_token,
                        geminiKEY.v_use_tools,
                        geminiKEY.x_nick_name, geminiKEY.x_model, geminiKEY.x_token,
                        geminiKEY.x_use_tools,
                        )
    logger.info(f"Authentication={res}")

    # 認証成功時のみテスト実行
    if (res == True):

        function_modules = {}
        filePath = []
        session_id = 'admin'

        # モデル一覧（オプション）
        if True:
            logger.info("モデル一覧")
            print(f"----------------------------")
            for model in geminiAPI.models:
                print(model)
            print(f"----------------------------")

        # テスト1: 通常のテキスト会話
        if True:
            sysText = None
            reqText = ''
            inpText = 'おはようございます。'
            filePath = []
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, geminiAPI.history = \
                geminiAPI.chatBot(chat_class='auto', model_select='auto', 
                                 session_id=session_id, history=geminiAPI.history,
                                 function_modules=function_modules,
                                 sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                 inpLang='ja', outLang='ja')
            print(f"----------------------------")
            print(f"[{ res_name }] ({ res_api })")
            print(f"{  str(res_text.rstrip())  }")
            print(f"----------------------------")

        # テスト2: 画像認識
        if True:
            sysText = None
            reqText = ''
            inpText = '添付画像を説明してください。'
            filePath = ['_icons/dog.jpg']
            #filePath = ['_icons/dog.jpg', '_icons/kyoto.png']
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, geminiAPI.history = \
                geminiAPI.chatBot(chat_class='auto', model_select='auto', 
                                 session_id=session_id, history=geminiAPI.history,
                                 function_modules=function_modules,
                                 sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                 inpLang='ja', outLang='ja')
            print(f"----------------------------")
            print(f"[{ res_name }] ({ res_api })")
            print(f"{  str(res_text.rstrip())  }")
            print(f"----------------------------")

        # テスト3: ツール実行
        if True:
            import    speech_bot__function
            botFunc = speech_bot__function.botFunction()
            res, msg = botFunc.functions_load(
                functions_path='_extensions/function/', secure_level='low', )
            for key, module_dic in botFunc.function_modules.items():
                if (module_dic['onoff'] == 'on'):
                    function_modules[key] = module_dic

        if function_modules:
            sysText = None
            reqText = ''
            inpText = 'flash,toolsで兵庫県三木市の天気を調べて'
            filePath = []
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, geminiAPI.history = \
                geminiAPI.chatBot(chat_class='auto', model_select='auto', 
                                 session_id=session_id, history=geminiAPI.history,
                                 function_modules=function_modules,
                                 sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                 inpLang='ja', outLang='ja')
            print(f"----------------------------")
            print(f"[{ res_name }] ({ res_api })")
            print(f"{  str(res_text.rstrip())  }")
            print(f"----------------------------")

        # 履歴表示（オプション）
        if False:
            logger.info("会話履歴の内容を表示")
            print(f"----------------------------")
            for history in geminiAPI.history:
                print(history)
            print(f"----------------------------")
            geminiAPI.history = []

    logger.info("【テスト終了】")
