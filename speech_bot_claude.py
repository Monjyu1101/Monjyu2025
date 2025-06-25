#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'claude'

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
import json
import queue


# API ライブラリ
import anthropic

# モジュールインポート
import speech_bot__common
bot_common = speech_bot__common._bot_common()
import speech_bot_claude_key as claude_key


class _claudeAPI:
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
        self.api_type = 'claude'
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
                self.client = anthropic.Anthropic(
                    api_key=key_id,
                )
        except Exception as e:
            logger.error(f"APIクライアント初期化エラー: {e}")
            return False

        # 設定パラメータの保存
        logger.debug("設定パラメータを適用")
        self.default_gpt = default_gpt
        self.default_class = default_class
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
                self.models[a_model] = {"id": a_model, "token": str(a_token), "modality": "text?", "date": ymd, }

        # モデルB設定 (拡張モデル)
        if (b_nick_name != ''):
            logger.debug(f"モデルB設定: {b_model}")
            self.b_enable = False
            self.b_nick_name = b_nick_name
            self.b_model = b_model
            self.b_token = int(b_token)
            self.b_use_tools = b_use_tools
            if (b_model not in self.models):
                self.models[b_model] = {"id": b_model, "token": str(b_token), "modality": "text?", "date": ymd, }

        # モデルV設定 (ビジョン対応モデル)
        if (v_nick_name != ''):
            logger.debug(f"モデルV設定: {v_model}")
            self.v_enable = False
            self.v_nick_name = v_nick_name
            self.v_model = v_model
            self.v_token = int(v_token)
            self.v_use_tools = v_use_tools
            if (v_model not in self.models):
                self.models[v_model] = {"id": v_model, "token": str(v_token), "modality": "text+image?", "date": ymd, }
            else:
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
                self.models[x_model] = {"id": x_model, "token": str(x_token), "modality": "text+image?", "date": ymd, }

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
            for model in models.data:
                key = model.id
                ymd = model.created_at.strftime("%Y/%m/%d")
                self.models[key] = {"id": key, "token": "9999", "modality": "text?", "date": ymd}
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
        res_think = ''
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

        # 送信データの準備
        messages = []
        contents = []
        if (len(image_urls) == 0) \
        or (len(image_urls) != len(upload_files)):
            contents.append({"type":"text", "text": msg_text})
            messages.append({"role": "user", "content": contents})
        # 送信データの準備（画像あり）
        else:
            for file_name in upload_files:
                if (os.path.isfile(file_name)):
                    if (os.path.getsize(file_name) <= 20000000):
                        file_ext = os.path.splitext(file_name)[1][1:].lower()
                        image_b64 = bot_common._base64_encode(file_path=file_name)
                        if (file_ext in ('jpg', 'jpeg')):
                            contents.append({"type":"image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}})
                        if (file_ext in ('png')):
                            contents.append({"type":"image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}})
            contents.append({"type":"text", "text": msg_text})
            messages.append({"role": "user", "content": contents})

        # ストリーミングモード無効
        stream = False

        # ツール（関数）設定
        tools = []
        if (use_tools.lower().find('yes') >= 0):
            for module_dic in function_modules.values():
                func_dic = module_dic['function']
                func_str = json.dumps(func_dic, ensure_ascii=False)
                func_str = func_str.replace('"parameters"', '"input_schema"')
                func = json.loads(func_str)
                tools.append(func)

        # 実行ループ
        if True:
            n = 0
            function_name = ''
            while (function_name != 'exit') and (n < int(max_step)):
                # 結果初期化
                res_role = ''
                res_content = ''
                res_thinking = ''
                tool_calls = []

                # モデル実行
                n += 1
                logger.info(f"//Claude// {res_name.lower()}, {res_api}, pass={n}, ")

                # max_tokensの設定
                max_tokens = 20000
                if (res_api.lower().find('opus') >= 0):
                    max_tokens = 4096
                    logger.warning(f"//Claude// (opus) max_tokens = { max_tokens }, ")
                if (res_api.lower().find('haiku') >= 0):
                    max_tokens = 8192
                    logger.warning(f"//Claude// (haiku) max_tokens = { max_tokens }, ")

                # パラメータ
                parm_kwargs = {
                    "model": res_api, 
                    "max_tokens": max_tokens,
                    "system": sysText,
                    "messages": messages,
                    "tools": tools,
                }

                # 推論モデル以外 temperature設定
                if (res_name not in [self.v_nick_name, self.x_nick_name]):
                    parm_kwargs["temperature"] = float(temperature)

                # 推論モデル Thinking設定
                if (res_name in [self.v_nick_name, self.x_nick_name]):
                    budget_tokens = 2000
                    logger.warning(f"//Claude// (thinking) budget_tokens = { budget_tokens }, ")
                    parm_kwargs.update({
                        "thinking": {
                            "type": "enabled",
                            "budget_tokens": budget_tokens
                        }
                    })

                # ストリーム処理
                if (stream == True):
                    chkTime = time.time()
                    with self.client.messages.stream(**parm_kwargs) as streams:
                        # ストリームデータの処理
                        hit_thinking = False
                        hit_string = False
                        for chunk in streams:
                            if ((time.time() - chkTime) > self.max_wait_sec):
                                logger.error("ストリーミング処理がタイムアウト")
                                break

                            try:
                                content_type = chunk.type
                                if (content_type == 'content_block_delta'):
                                    try:
                                        # Thinking出力処理
                                        if (chunk.delta.type == 'thinking'):
                                            delta_thinking = chunk.delta.thinking
                                            delta_thinking = delta_thinking.replace('\n\n', '\n')
                                            delta_thinking = delta_thinking.replace('\n\n', '\n')
                                            if (hit_thinking == False):
                                                self.stream(session_id, "<think>\n")
                                                if (delta_thinking[:1] == '\n'):
                                                    delta_thinking = delta_thinking[1:]
                                            if (delta_thinking.strip() != ''):
                                                hit_thinking = True
                                                self.stream(session_id, delta_thinking)

                                        # テキスト出力処理
                                        elif (chunk.delta.type == 'text'):
                                            delta_text = chunk.delta.text
                                            delta_text = delta_text.replace('\n\n', '\n')
                                            delta_text = delta_text.replace('\n\n', '\n')
                                            if (hit_string == False):
                                                if (hit_thinking == True):
                                                    self.stream(session_id, "</think>\n")
                                                if (delta_text[:1] == '\n'):
                                                    delta_text = delta_text[1:]
                                            if (delta_text.strip() != ''):
                                                hit_string = True
                                                self.stream(session_id, delta_text)
                                    except Exception as e:
                                        logger.error(f"コンテンツブロックデルタ処理エラー: {e}")
                                        pass

                                elif (content_type == 'content_block_stop'):
                                    try:
                                        block_type = chunk.content_block.type
                                        if (block_type == 'text'):
                                            if (hit_string == True):
                                                # 改行
                                                self.print(session_id)
                                                hit_string = False
                                    except Exception as e:
                                        logger.error(f"コンテンツブロック停止処理エラー: {e}")
                                        pass

                                elif (content_type == 'message_stop'):
                                    response = chunk.message

                            except Exception as e:
                                logger.error(f"ストリームチャンク処理エラー: {e}")

                # 通常実行（ストリームなし）
                if (stream == False):
                    response = self.client.messages.create(**parm_kwargs)

                # レスポンス処理
                res_role = response.role
                contents = response.content

                # メッセージを次のリクエスト用に保存
                msg = {"role": res_role, "content": contents}
                messages.append(msg)

                # コンテンツ処理
                for c in range(len(contents)):
                    c_type = response.content[c].type
                    # Thinking処理
                    if (c_type == 'thinking'):
                        c_thinking = response.content[c].thinking
                        c_thinking = c_thinking.replace('\n\n', '\n')

                        # 履歴に追加
                        if (c_thinking.strip() != ''):
                            if (stream == False):
                                self.print(session_id, c_thinking)
                            res_think += c_thinking.rstrip() + '\n'

                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': c_thinking}
                            res_history.append(dic)

                    # テキスト処理
                    elif (c_type == 'text'):
                        c_text = response.content[c].text

                        # 履歴に追加
                        if (c_text.strip() != ''):
                            if (stream == False):
                                self.print(session_id, c_text)
                            res_text += c_text.rstrip() + '\n'

                            self.seq += 1
                            dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': c_text}
                            res_history.append(dic)

                    # 関数呼び出し処理
                    elif (c_type == 'tool_use'):
                        f_id = response.content[c].id
                        f_name = response.content[c].name
                        f_kwargs = json.dumps(response.content[c].input, ensure_ascii=False)
                        tool_calls.append({"id": f_id, "type": "function", "function": {"name": f_name, "arguments": f_kwargs}})

                # ツール実行処理
                contents = []
                if (len(tool_calls) > 0):

                    for tc in tool_calls:
                        f_id = tc.get('id')
                        f_name = tc['function'].get('name')
                        f_kwargs = tc['function'].get('arguments')

                        # 登録された関数モジュールを検索
                        module_dic = function_modules.get(f_name)
                        if (module_dic is None):
                            logger.error(f"//Claude//   function not found Error ! ({f_name})")
                            break
                                
                        else:
                            logger.info(f"//Claude//   function_call '{module_dic['script']}' ({f_name})")
                            logger.info(f"//Claude//   → {f_kwargs}")

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
                                dic = {}
                                dic['error'] = str(e)
                                res_json = json.dumps(dic, ensure_ascii=False)

                            # 実行結果を表示
                            logger.info(f"//Claude//   → {res_json}")

                            # 結果を次のリクエストに追加
                            contents.append({"type": "tool_result", "tool_use_id": f_id, "content": [{"type": "text", "text": res_json}]})

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

                # 関数結果をリクエストに追加して継続
                if (len(contents) > 0):
                    msg = {"role": "user", "content": contents}
                    messages.append(msg)
                # 実行終了
                else:
                    function_name = 'exit'

        # 最終応答結果の確認
        if (res_text != ''):
            if (res_think != ''):
                wk_text = '<think>\n' + res_think.rstrip() + '\n</think>\n'
                wk_text += res_text
                res_text = wk_text
            logger.info(f"//Claude// {res_name.lower()}, complete.")
        else:
            logger.error('//Claude// Error !')

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
        logger.debug(f"//Claude// chat_class={chat_class}, model_select={model_select}")
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
    claudeAPI = _claudeAPI()

    # API種別を取得
    claudeKEY = claude_key._conf_class()
    claudeKEY.init(runMode='debug')
    logger.info(f"api_type={claudeKEY.api_type}")

    # ログキューの設定
    stream_queue = queue.Queue()
    res = claudeAPI.init(stream_queue=stream_queue)

    # 認証処理
    res = claudeAPI.authenticate('anthropic',
                        claudeKEY.api_type,
                        claudeKEY.default_gpt, claudeKEY.default_class,
                        claudeKEY.auto_continue,
                        claudeKEY.max_step, claudeKEY.max_session,
                        claudeKEY.max_wait_sec,

                        claudeKEY.claude_key_id,

                        claudeKEY.a_nick_name, claudeKEY.a_model, claudeKEY.a_token,
                        claudeKEY.a_use_tools,
                        claudeKEY.b_nick_name, claudeKEY.b_model, claudeKEY.b_token,
                        claudeKEY.b_use_tools,
                        claudeKEY.v_nick_name, claudeKEY.v_model, claudeKEY.v_token,
                        claudeKEY.v_use_tools,
                        claudeKEY.x_nick_name, claudeKEY.x_model, claudeKEY.x_token,
                        claudeKEY.x_use_tools,
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
            for model in claudeAPI.models:
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
            res_text, res_path, res_files, res_name, res_api, claudeAPI.history = \
                claudeAPI.chatBot(chat_class='auto', model_select='auto', 
                                session_id=session_id, history=claudeAPI.history,
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
            res_text, res_path, res_files, res_name, res_api, claudeAPI.history = \
                claudeAPI.chatBot(chat_class='auto', model_select='auto', 
                                session_id=session_id, history=claudeAPI.history,
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
            inpText = 'claude-x,toolsで兵庫県三木市の天気を調べて'
            filePath = []
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, claudeAPI.history = \
                claudeAPI.chatBot(chat_class='auto', model_select='auto', 
                                session_id=session_id, history=claudeAPI.history,
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
            for history in claudeAPI.history:
                print(history)
            print(f"----------------------------")
            geminiAPI.history = []

    logger.info("【テスト終了】")
