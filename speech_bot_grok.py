#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'grok'

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
import base64
import requests


# API ライブラリ
import openai

# APIキー情報のインポート
import speech_bot_grok_key as grok_key


# Base64エンコード機能
def base64_encode(file_path):
    """
    ファイルをBase64エンコードする関数
    Args:
        file_path (str): エンコードするファイルのパス
    Returns:
        str: Base64エンコードされた文字列
    """
    with open(file_path, "rb") as input_file:
        logger.debug(f"ファイル '{file_path}' をBase64エンコード")
        return base64.b64encode(input_file.read()).decode('utf-8')


class _grokAPI:
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
        self.api_type = 'grok'
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
                self.client = openai.OpenAI(
                    api_key=key_id,
                    base_url="https://api.x.ai/v1",
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
                self.models[a_model] = {"id": a_model, "token": str(a_token), "modality": "text?", "date": ymd}

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
                key = model.id
                if True:
                    ymd = datetime.datetime.fromtimestamp(model.created).strftime("%Y/%m/%d")
                    self.models[key] = {"id":key, "token":"9999", "modality":"text?", "date": ymd, }
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

    def history_add(self, history=[], sysText=None, reqText=None, inpText='こんにちは'):
        """
        会話履歴にメッセージを追加する
        Args:
            history (list, optional): 既存の会話履歴
            sysText (str, optional): システムテキスト
            reqText (str, optional): 要求テキスト
            inpText (str, optional): 入力テキスト
        Returns:
            list: 更新された会話履歴
        """
        res_history = history

        # sysTextの処理 (システムテキスト)
        if (sysText is not None) and (sysText.strip() != ''):
            # 既存履歴のシステムメッセージと異なる場合は履歴をリセット
            if (len(res_history) > 0):
                # 既存の履歴にシステムと新しいものと異なる場合は履歴をクリア
                if (sysText.strip() != res_history[0]['content'].strip()):
                    res_history = []
            # システムテキストを追加
            if (len(res_history) == 0):
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': 'system', 'name': '', 'content': sysText.strip()}
                res_history.append(dic)
        
        # reqTextの処理 (要求テキスト)
        if (reqText is not None) and (reqText.strip() != ''):
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': reqText.strip()}
            res_history.append(dic)

        # inpTextの処理 (入力テキスト)
        if (inpText.strip() != ''):
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': inpText.rstrip()}
            res_history.append(dic)

        return res_history

    def history_zip1(self, history=[]):
        """
        会話履歴から古いメッセージを削除する（時間ベース）
        15分以上経過したメッセージを削除
        Args:
            history (list, optional): 圧縮する会話履歴
        Returns:
            list: 圧縮された会話履歴
        """
        res_history = history

        if (len(res_history) > 0):
            for h in reversed(range(len(res_history))):
                tm = res_history[h]['time']
                # 15分（900秒）以上前のメッセージは削除対象
                if ((time.time() - tm) > 900):
                    if (h != 0):
                        del res_history[h]
                    else:
                        # インデックス0はシステムメッセージのみ維持
                        if (res_history[0]['role'] != 'system'):
                            del res_history[0]

        return res_history

    def history_zip2(self, history=[], leave_count=4):
        """
        会話履歴から古いメッセージを削除する（カウントベース）
        最新のleave_count件とシステムメッセージを残して削除
        Args:
            history (list, optional): 圧縮する会話履歴
            leave_count (int, optional): 残すメッセージの数
        Returns:
            list: 圧縮された会話履歴
        """
        res_history = history

        if (len(res_history) > 6):
            for h in reversed(range(2, len(res_history) - leave_count)):
                del res_history[h]

        return res_history

    def history2msg_gpt(self, history=[]):
        """
        履歴をChatgpt API用のメッセージ形式に変換
        Args:
            history (list, optional): 会話履歴            
        Returns:
            list: API用に変換されたメッセージリスト
        """
        res_msg = []
        for h in range(len(history)):
            role = history[h]['role']
            content = history[h]['content']
            name = history[h]['name']

            # function_call以外の通常メッセージを変換
            if (role != 'function_call'):
                if (role not in ['system', 'user', 'assistant']):
                    role = 'user'
                if (name == ''):
                    dic = {'role': role, 'content': content}
                    res_msg.append(dic)
                else:
                    dic = {'role': role, 'name': name, 'content': content}
                    res_msg.append(dic)

        return res_msg

    def history2msg_vision(self, history=[], image_urls=[]):
        """
        履歴をVision API用のメッセージ形式に変換（画像付き）        
        Args:
            history (list, optional): 会話履歴
            image_urls (list, optional): 画像URL情報のリスト
        Returns:
            list: Vision API用に変換されたメッセージリスト
        """
        res_msg = []
        last_h = 0
        
        # 最後の通常メッセージのインデックスを検索
        for h in range(len(history)):
            role = history[h]['role']
            if (role != 'function_call') and (role != 'function'):
                last_h = h 

        # メッセージ変換処理
        for h in range(len(history)):
            role = history[h]['role']
            content = history[h]['content']
            name = history[h]['name']

            # 通常メッセージの処理
            if (role != 'function_call') and (role != 'function'):
                con = []
                con.append({'type': 'text', 'text': content})
                if (h == last_h):
                    for image_url in image_urls:
                        con.append(image_url)
                if (name == ''):
                    dic = {'role': role, 'content': con}
                    res_msg.append(dic)
                else:
                    dic = {'role': role, 'name': name, 'content': con}
                    res_msg.append(dic)

        return res_msg


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

        # モデル選択の補正（アシスタント用）
        if ((chat_class == 'assistant') \
        or (chat_class == 'コード生成') \
        or (chat_class == 'コード実行') \
        or (chat_class == '文書検索') \
        or (chat_class == '複雑な会話') \
        or (chat_class == 'アシスタント') \
        or (model_select == 'x')):
            if (self.x_enable == True):
                res_name = self.x_nick_name
                res_api = self.x_model
                use_tools = self.x_use_tools

        # ニックネーム指定によるモデル選択
        if (self.a_nick_name != ''):
            if (inpText.strip()[:len(self.a_nick_name)+1].lower() == (self.a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.a_nick_name)+1:]
        if (self.b_nick_name != ''):
            if (inpText.strip()[:len(self.b_nick_name)+1].lower() == (self.b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.b_nick_name)+1:]
                if (self.b_enable == True):
                    res_name = self.b_nick_name
                    res_api = self.b_model
                    use_tools = self.b_use_tools
        if (self.v_nick_name != ''):
            if (inpText.strip()[:len(self.v_nick_name)+1].lower() == (self.v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.v_nick_name)+1:]
                if (self.v_enable == True):
                    if (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        res_name = self.v_nick_name
                        res_api = self.v_model
                        use_tools = self.v_use_tools
                elif (self.x_enable == True):
                    res_name = self.x_nick_name
                    res_api = self.x_model
                    use_tools = self.x_use_tools
        if (self.x_nick_name != ''):
            if (inpText.strip()[:len(self.x_nick_name)+1].lower() == (self.x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.x_nick_name)+1:]
                if (self.x_enable == True):
                    res_name = self.x_nick_name
                    res_api = self.x_model
                    use_tools = self.x_use_tools
                elif (self.b_enable == True):
                    res_name = self.b_nick_name
                    res_api = self.b_model
                    use_tools = self.b_use_tools

        # 特殊プレフィックスによるモデル選択
        if (inpText.strip()[:5].lower() == ('riki,')):
            inpText = inpText.strip()[5:]
            if (self.x_enable == True):
                res_name = self.x_nick_name
                res_api = self.x_model
                use_tools = self.x_use_tools
            elif (self.b_enable == True):
                res_name = self.b_nick_name
                res_api = self.b_model
                use_tools = self.b_use_tools
        elif (inpText.strip()[:7].lower() == ('vision,')):
            inpText = inpText.strip()[7:]
            if (self.v_enable == True):
                if (len(image_urls) > 0) \
                and (len(image_urls) == len(upload_files)):
                    res_name = self.v_nick_name
                    res_api = self.v_model
                    use_tools = self.v_use_tools
            elif (self.x_enable == True):
                res_name = self.x_nick_name
                res_api = self.x_model
                use_tools = self.x_use_tools
        elif (inpText.strip()[:10].lower() == ('assistant,')):
            inpText = inpText.strip()[10:]
            if (self.x_enable == True):
                res_name = self.x_nick_name
                res_api = self.x_model
                use_tools = self.x_use_tools
            elif (self.b_enable == True):
                res_name = self.b_nick_name
                res_api = self.b_model
                use_tools = self.b_use_tools
        elif (inpText.strip()[:7].lower() == ('openai,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:6].lower() == ('azure,')):
            inpText = inpText.strip()[6:]
        elif (inpText.strip()[:8].lower() == ('chatgpt,')):
            inpText = inpText.strip()[8:]
        elif (inpText.strip()[:7].lower() == ('assist,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:6].lower() == ('respo,')):
            inpText = inpText.strip()[6:]
        elif (inpText.strip()[:7].lower() == ('gemini,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:7].lower() == ('freeai,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:5].lower() == ('free,')):
            inpText = inpText.strip()[5:]
        elif (inpText.strip()[:7].lower() == ('claude,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:11].lower() == ('openrouter,')):
            inpText = inpText.strip()[11:]
        elif (inpText.strip()[:7].lower() == ('openrt,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:11].lower() == ('perplexity,')):
            inpText = inpText.strip()[11:]
        elif (inpText.strip()[:5].lower() == ('pplx,')):
            inpText = inpText.strip()[5:]
        elif (inpText.strip()[:5].lower() == ('grok,')):
            inpText = inpText.strip()[5:]
        elif (inpText.strip()[:5].lower() == ('groq,')):
            inpText = inpText.strip()[5:]
        elif (inpText.strip()[:7].lower() == ('ollama,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:6].lower() == ('local,')):
            inpText = inpText.strip()[6:]

        # モデル未設定時の自動選択
        if (res_api is None):
            res_name = self.a_nick_name
            res_api = self.a_model
            use_tools = self.a_use_tools

            # テキスト長または添付ファイルに基づくモデル選択
            if (self.b_enable == True):
                if (len(upload_files) > 0) \
                or (len(inpText) > 1000):
                    res_name = self.b_nick_name
                    res_api = self.b_model
                    use_tools = self.b_use_tools

        # 画像処理のためのモデル補正
        if (len(image_urls) > 0) \
        and (len(image_urls) == len(upload_files)):
            if (self.v_enable == True):
                res_name = self.v_nick_name
                res_api = self.v_model
                use_tools = self.v_use_tools
            elif (self.x_enable == True):
                res_name = self.x_nick_name
                res_api = self.x_model
                use_tools = self.x_use_tools

        # 履歴の追加と圧縮
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText)
        res_history = self.history_zip1(history=res_history)

        # メッセージの作成
        if (model_select != 'v'):
            msg = self.history2msg_gpt(history=res_history)
        else:
            msg = self.history2msg_vision(history=res_history, image_urls=image_urls)

        # ストリーミングモード無効
        stream = False

        # ツール（関数）設定
        tools = []
        if (use_tools.lower().find('yes') >= 0):
            functions = []
            for module_dic in function_modules.values():
                functions.append(module_dic['function'])
            for f in range(len(functions)):
                tools.append({"type": "function", "function": functions[f]})

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
                logger.info(f"//Grok// {res_name.lower()}, {res_api}, pass={n}, ")

                # APIリクエスト作成と実行
                # 1. 画像処理モード
                if (res_name == self.v_nick_name) and (len(image_urls) > 0):
                    null_history = self.history_add(history=[], sysText=sysText, reqText=reqText, inpText=inpText)
                    msg = self.history2msg_vision(history=null_history, image_urls=image_urls)
                    response = self.client.chat.completions.create(
                            model=res_api,
                            messages=msg,
                            temperature = float(temperature),
                            timeout=self.max_wait_sec,
                            stream=stream,
                            )

                # 2. ツール使用モード
                elif (len(tools) != 0):
                    response = self.client.chat.completions.create(
                        model=res_api,
                        messages=msg,
                        temperature = float(temperature),
                        tools=tools, tool_choice='auto',
                        timeout=self.max_wait_sec,
                        stream=stream,
                        )

                # 3. 通常モード
                else:
                    # JSONスキーマなしの場合
                    if (jsonSchema is None) or (jsonSchema == ''):
                        response = self.client.chat.completions.create(
                            model=res_api,
                            messages=msg,
                            temperature = float(temperature),
                            timeout=self.max_wait_sec,
                            stream=stream,
                            )
                    # JSONスキーマありの場合
                    else:
                        schema = None
                        try:
                            schema = json.loads(jsonSchema)
                        except Exception as e:
                            logger.warning(f"JSONスキーマの解析に失敗: {e}")
                            
                        # スキーマ指定なし
                        if (schema is None):
                            response = self.client.chat.completions.create(
                                model=res_api,
                                messages=msg,
                                temperature = float(temperature),
                                timeout=self.max_wait_sec,
                                response_format={"type": "json_object"},
                                stream=stream,
                                )
                        # スキーマ指定あり
                        else:
                            response = self.client.chat.completions.create(
                                model=res_api,
                                messages=msg,
                                temperature = float(temperature),
                                timeout=self.max_wait_sec,
                                response_format={"type": "json_schema", "json_schema": schema},
                                stream=stream,
                                )

                # ストリーミング応答処理
                if (stream == True):
                    logger.debug("ストリーミング応答の処理開始")
                    chkTime = time.time()
                    for chunk in response:
                        if ((time.time() - chkTime) > self.max_wait_sec):
                            logger.error("ストリーミング処理がタイムアウト")
                            break
                        delta = chunk.choices[0].delta
                        if (delta is not None):
                            # テキストコンテンツの処理
                            if (delta.content is not None):
                                res_role = 'assistant'
                                content = delta.content
                                res_content += content
                                self.stream(session_id, content)

                            # ツール呼び出しの処理
                            elif (delta.tool_calls is not None):
                                res_role = 'assistant'
                                tcchunklist = delta.tool_calls
                                for tcchunk in tcchunklist:
                                    if len(tool_calls) <= tcchunk.index:
                                        tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                                    tc = tool_calls[tcchunk.index]
                                    if tcchunk.id:
                                        tc["id"] += tcchunk.id
                                    if tcchunk.function.name:
                                        tc["function"]["name"] += tcchunk.function.name
                                    if tcchunk.function.arguments:
                                        tc["function"]["arguments"] += tcchunk.function.arguments

                    # 改行処理
                    if (res_content != ''):
                        self.print(session_id)

                # 通常実行（ストリームなし）
                if (stream == False):
                    # レスポンス処理
                    try:
                        # 通常メッセージ
                        res_role = str(response.choices[0].message.role)
                        res_content = str(response.choices[0].message.content)

                        # 関数呼び出しの処理
                        if (response.choices[0].finish_reason == 'tool_calls'):
                            for tool_call in response.choices[0].message.tool_calls:
                                f_id = str(tool_call.id)
                                f_name = str(tool_call.function.name)
                                f_kwargs = str(tool_call.function.arguments)

                                # 引数のJSON整形
                                try:
                                    wk_dic = json.loads(f_kwargs)
                                    wk_text = json.dumps(wk_dic, ensure_ascii=False)
                                    f_kwargs = wk_text
                                except Exception as e:
                                    #logger.warning(f"run_gpt() 関数引数のJSON整形に失敗: {e}")
                                    f_kwargs ="{}"

                                # ツールコール追加
                                tool_calls.append({
                                    "id": f_id, 
                                    "type": "function", 
                                    "function": {
                                        "name": f_name, 
                                        "arguments": f_kwargs
                                    }
                                })

                    except Exception as e:
                        logger.error(f"応答処理エラー: {e}")

                # ツール実行処理
                if (len(tool_calls) > 0):
                    for tc in tool_calls:
                        f_id = tc['id']
                        f_name = tc['function']['name']
                        f_kwargs = tc['function']['arguments']

                        # 登録された関数モジュールを検索
                        module_dic = function_modules.get(f_name)
                        if (module_dic is None):
                            logger.error(f"//Grok//   function_not found Error ! ({f_name})")
                            break

                        else:
                            logger.info(f"//Grok//   function_call '{module_dic['script']}' ({f_name})")
                            logger.info(f"//Grok//   → {f_kwargs}")

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
                            logger.info(f"//Grok//   → {res_json}")

                            # メッセージ追加格納
                            dic = {'role': 'user', 'name': f_name, 'content': res_json}
                            msg.append(dic)

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
                elif (res_role == 'assistant') and (res_content != ''):
                    function_name = 'exit'
                    if (res_content.strip() != ''):
                        res_text += res_content.rstrip() + '\n'

                        # 応答結果を履歴に追加
                        self.seq += 1
                        dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': res_content}
                        res_history.append(dic)

                # その他の状態（通常は発生しない）
                else:
                    logger.warning(f"loop??? {res_role}, {res_content[:50]}...")

        # 最終応答結果の確認
        if (res_text != ''):
            logger.info(f"//Grok// {res_name.lower()}, complete.")
        else:
            logger.error('//Grok// Error !')

        return res_text, res_path, res_files, res_name, res_api, res_history


    def files_check(self, filePath=[]):
        """
        アップロードされたファイルを処理し、画像ファイルをbase64エンコードする
        Args:
            filePath (list, optional): ファイルパスのリスト
        Returns:
            tuple: (アップロードファイルリスト, 画像URLリスト)
        """
        upload_files = []
        image_urls = []

        # 添付ファイルの確認と処理
        if (len(filePath) > 0):
            logger.debug(f"files_check() {len(filePath)}個のファイルを処理します")
            try:
                for file_name in filePath:
                    if (os.path.isfile(file_name)):
                        # 2025/03/15時点でのサイズ上限 20Mbyte
                        file_size = os.path.getsize(file_name)
                        if (file_size <= 20000000):
                            upload_files.append(file_name)

                            # 画像ファイルの場合、base64エンコードしてURL形式に変換
                            file_ext = os.path.splitext(file_name)[1][1:].lower()
                            if (file_ext in ('jpg', 'jpeg', 'png', 'gif')):
                                base64_text = base64_encode(file_name)
                                # 画像フォーマット別の処理
                                if (file_ext in ('jpg', 'jpeg')):
                                    url = {"url": f"data:image/jpeg;base64,{base64_text}"}
                                    image_url = {'type': 'image_url', 'image_url': url}
                                    image_urls.append(image_url)
                                elif (file_ext == 'png'):
                                    url = {"url": f"data:image/png;base64,{base64_text}"}
                                    image_url = {'type': 'image_url', 'image_url': url}
                                    image_urls.append(image_url)
                                elif (file_ext == 'gif'):
                                    url = {"url": f"data:image/gif;base64,{base64_text}"}
                                    image_url = {'type': 'image_url', 'image_url': url}
                                    image_urls.append(image_url)
                        else:
                            logger.warning(f"files_check() ファイルサイズが上限を超えています: {file_name} ({file_size} bytes)")

            except Exception as e:
                logger.error(f"files_check() ファイル処理エラー: {e}")

        return upload_files, image_urls

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
            upload_files, image_urls = self.files_check(filePath=filePath)
        except Exception as e:
            logger.error(f"ファイル処理エラー: {e}")

        # モデル実行
        logger.debug(f"//Grok// chat_class={chat_class}, model_select={model_select}")
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
    grokAPI = _grokAPI()

    # API種別を取得
    grokKEY = grok_key._conf_class()
    grokKEY.init(runMode='debug')
    logger.info(f"api_type={grokKEY.api_type}")

    # ログキューの設定
    stream_queue = queue.Queue()
    res = grokAPI.init(stream_queue=stream_queue)

    # 認証処理
    res = grokAPI.authenticate('grok',
                        grokKEY.api_type,
                        grokKEY.default_gpt, grokKEY.default_class,
                        grokKEY.auto_continue,
                        grokKEY.max_step, grokKEY.max_session,
                        grokKEY.max_wait_sec,

                        grokKEY.grok_key_id,

                        grokKEY.a_nick_name, grokKEY.a_model, grokKEY.a_token,
                        grokKEY.a_use_tools,
                        grokKEY.b_nick_name, grokKEY.b_model, grokKEY.b_token,
                        grokKEY.b_use_tools,
                        grokKEY.v_nick_name, grokKEY.v_model, grokKEY.v_token,
                        grokKEY.v_use_tools,
                        grokKEY.x_nick_name, grokKEY.x_model, grokKEY.x_token,
                        grokKEY.x_use_tools,
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
            for model in grokAPI.models:
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
            res_text, res_path, res_files, res_name, res_api, grokAPI.history = \
                grokAPI.chatBot(chat_class='auto', model_select='auto', 
                                    session_id=session_id, history=grokAPI.history,
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
            res_text, res_path, res_files, res_name, res_api, grokAPI.history = \
                grokAPI.chatBot(chat_class='auto', model_select='auto', 
                                    session_id=session_id, history=grokAPI.history,
                                    function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                    inpLang='ja', outLang='ja')
            print(f"----------------------------")
            print(f"[{ res_name }] ({ res_api })")
            print(f"{  str(res_text.rstrip())  }")
            print(f"----------------------------")

        # テスト3: ツール実行
        if True:
            import    speech_bot_function
            botFunc = speech_bot_function.botFunction()
            res, msg = botFunc.functions_load(
                functions_path='_extensions/function/', secure_level='low', )
            for key, module_dic in botFunc.function_modules.items():
                if (module_dic['onoff'] == 'on'):
                    function_modules[key] = module_dic

        if function_modules:
            sysText = None
            reqText = ''
            inpText = 'grok-b,toolsで兵庫県三木市の天気を調べて'
            filePath = []
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, grokAPI.history = \
                grokAPI.chatBot(chat_class='auto', model_select='auto', 
                                    session_id=session_id, history=grokAPI.history,
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
            for history in grokAPI.history:
                print(history)
            print(f"----------------------------")
            grokAPI.history = []

    logger.info("【テスト終了】")
