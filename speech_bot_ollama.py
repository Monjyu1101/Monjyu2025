#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'ollama'

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
import queue
import base64
import subprocess
import requests


# API ライブラリ
import ollama

# API 情報のインポート
import speech_bot_ollama_key as ollama_key


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


class _ollamaAPI:
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
        self.api_type = 'ollama'
        self.default_gpt = 'auto'
        self.default_class = 'auto'
        self.auto_continue = 3
        self.max_step = 10
        self.max_session = 5
        self.max_wait_sec = 120
       
        # 接続情報
        self.server = 'localhost'
        self.port = '11434'

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

                     server, port,

                     a_nick_name, a_model, a_token, 
                     a_use_tools, 
                     b_nick_name, b_model, b_token, 
                     b_use_tools, 
                     v_nick_name, v_model, v_token, 
                     v_use_tools, 
                     x_nick_name, x_model, x_token, 
                     x_use_tools):
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

        # ollama サーバー
        if (str(server) not in ['', 'auto']):
            self.server = server
        if (str(port) not in ['', 'auto']):
            self.port = port

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

        # 認証とモデル情報の取得
        self.client = None
        self.auth()

        if (self.client is not None):
            ymd = datetime.date.today().strftime('%Y/%m/%d')

            # モデル取得
            self.get_models()
            for model_name in self.locals:
                if (model_name not in self.models):
                    self.models[model_name] = {"id": model_name, "token": "9999", "modality": "text?", "date": "local"}

            # モデルA設定
            if (a_nick_name != ''):
                self.a_enable = False
                self.a_nick_name = a_nick_name
                self.a_model = a_model
                self.a_token = int(a_token)
                self.a_use_tools = a_use_tools
                if (a_model not in self.models):
                    self.models[a_model] = {"id": a_model, "token": str(a_token), "modality": "text?", "date": "local"}

                if (self.a_model in self.models):
                    self.a_enable = True
                    self.bot_auth = True
                else:
                    self.a_enable = False
                    hit, model = self.model_load(model_name=self.a_model)
                    if (hit == True):
                        self.a_enable = True
                        self.a_model = model
                        self.bot_auth = True

            # モデルB設定
            if (b_nick_name != ''):
                self.b_enable = False
                self.b_nick_name = b_nick_name
                self.b_model = b_model
                self.b_token = int(b_token)
                self.b_use_tools = b_use_tools
                if (b_model not in self.models):
                    self.models[b_model] = {"id": b_model, "token": str(b_token), "modality": "text?", "date": "local"}

                if (self.b_model in self.models):
                    self.b_enable = True
                    self.bot_auth = True
                else:
                    self.b_enable = False
                    hit, model = self.model_load(model_name=self.b_model)
                    if (hit == True):
                        self.b_enable = True
                        self.b_model = model
                        self.bot_auth = True

            # モデルV設定
            if (v_nick_name != ''):
                self.v_enable = False
                self.v_nick_name = v_nick_name
                self.v_model = v_model
                self.v_token = int(v_token)
                self.v_use_tools = v_use_tools
                if (v_model not in self.models):
                    self.models[v_model] = {"id": v_model, "token": str(v_token), "modality": "text+image?", "date": "local"}

                if (self.v_model in self.models):
                    self.v_enable = True
                    self.bot_auth = True
                else:
                    self.v_enable = False
                    hit, model = self.model_load(model_name=self.v_model)
                    if (hit == True):
                        self.v_enable = True
                        self.v_model = model
                        self.bot_auth = True

            # モデルX設定
            if (x_nick_name != ''):
                self.x_enable = False
                self.x_nick_name = x_nick_name
                self.x_model = x_model
                self.x_token = int(x_token)
                self.x_use_tools = x_use_tools
                if (x_model not in self.models):
                    self.models[x_model] = {"id": x_model, "token": str(x_token), "modality": "text+image?", "date": "local"}

                if (self.x_model in self.models):
                    self.x_enable = True
                    self.bot_auth = True
                else:
                    self.x_enable = False
                    hit, model = self.model_load(model_name=self.x_model)
                    if (hit == True):
                        self.x_enable = True
                        self.x_model = model
                        self.bot_auth = True

        # 認証結果を返す
        if self.bot_auth:
            logger.debug("authenticate() 認証成功")
            return True
        else:
            logger.debug("authenticate() 認証失敗")
            return False

    def auth(self):
        """
        Ollamaサーバーに接続して認証する        
        Returns:
            bool: 認証が成功した場合はTrue、失敗した場合はFalse
        """
        self.client = None
        self.locals = []
        try:
            self.client = ollama.Client(host=f"http://{self.server}:{self.port}")
            get_models = self.client.list().get('models')
            for model in get_models:
                self.locals.append(model.get('model'))
            logger.debug(f"Connected to Ollama server at {self.server}:{self.port}")
        except:
            logger.warning(f"Ollama server ({self.server}) not enabled!")
            if (self.server == 'localhost'):
                self.client = None
            else:
                logger.debug("Trying to connect to localhost")
                try:
                    del self.client
                    self.client = ollama.Client(host="http://localhost:11434")
                    get_models = self.client.list().get('models')
                    for model in get_models:
                        self.locals.append(model.get('model'))
                    self.server = 'localhost'
                    self.port = '11434'
                    logger.debug("Successfully connected to localhost")
                except:
                    self.client = None
                    logger.warning("Failed to connect to localhost")

        if self.client is not None:
            return True
        else:
            return False

    def update_models(self):
        """
        Ollamaサーバーから利用可能なモデルのリストを更新する        
        Returns:
            bool: 更新が成功した場合はTrue
        """
        self.models = []
        get_models = self.client.list().get('models')
        for model in get_models:
            self.models.append(model.get('model'))
        logger.debug(f"Updated model list: {len(self.models)} models available")
        return True

    def model_load(self, model_name):
        """
        指定されたモデルをロードする。存在しない場合はダウンロードを試みる        
        Args:
            model_name (str): ロードするモデル名
        Returns:
            tuple: (成功したかどうか, 実際に使用するモデル名)
        """
        if (model_name in self.models):
            return True, model_name
        if (model_name.find(':') == 0):
            for olm_model in self.models:
                olm_model_hit = olm_model.find(':')
                if (olm_model_hit >= 0):
                    if (model_name == olm_model[:olm_model_hit]):
                        return True, olm_model
                else:
                    if (model_name == olm_model):
                        return True, olm_model
        logger.debug(f"Downloading model: {model_name}")
        logger.debug(f"Ollama: モデルダウンロード中... ({model_name})")

        def download(self, down_name):
            """
            モデルをダウンロードする内部関数            
            Args:
                down_name (str): ダウンロードするモデル名
            Returns:
                tuple: (成功したかどうか, 実際に使用するモデル名)
            """
            try:
                if (os.name == 'nt'):
                    try:
                        subprocess.call(['cmd.exe', '/c', 'ollama', 'pull', down_name])
                        self.client.pull(down_name)
                        time.sleep(2.00)
                        self.update_models()
                    except:
                        pass
                else:
                    self.client.pull(down_name)
                    time.sleep(2.00)
                    self.update_models()
                if (down_name in self.models):
                    if (down_name not in self.models):
                        self.models[down_name] = {"id": down_name, "token": "9999", "modality": "text?", "date": "local"}
                    logger.debug(f"Successfully downloaded model: {down_name}")
                    return True, down_name
            except:
                logger.warning(f"Failed to download model: {down_name}")
                pass
            return False, down_name

        hit = False
        model = model_name
        if (model_name.find(':') >= 0):
            hit, model = download(self=self, down_name=model_name)
        else:
            # 様々なサイズのモデルを試行
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':1b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':1.5b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':1.8b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':2b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':3b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':3.8b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':7b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':8b')
            if (hit == False):
                hit, model = download(self=self, down_name=model_name+':11b')

        if (hit == True):
            logger.debug(f"Model download completed: {model}")
            return True, model
        else:
            logger.error(f"Model download error: {model_name}")
            return False, model_name

    def get_models(self):
        """
        ollamadb.devからモデル情報を取得する        
        Returns:
            bool: 取得成功時True、失敗時False
        """
        logger.debug("get_models() モデル一覧を取得します")
        try:
            response = requests.get("https://ollamadb.dev/api/v1/models")
            if response.status_code == 200:
                self.models = {}
                models = response.json()
                for model in models['models']:
                    model_name = model["model_name"]
                    labels = model["labels"]
                    if model["capability"] is not None:
                        modality = model["capability"]
                    else:
                        modality = ''
                    ymd = model["last_updated"].replace('-', '/')
                    if (len(labels) != 0):
                        for label in labels:
                            key = model_name + ':' + label
                            self.models[key] = {"id":key, "token":"9999", "modality":modality, "date": ymd}
                    else:
                            key = model_name
                            self.models[key] = {"id":key, "token":"9999", "modality":modality, "date": ymd}
                logger.debug(f"get_models() {len(self.models)}個のモデルを取得しました")
                return True
            else:
                logger.error(f"get_models() モデル取得エラー!")
                return False
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
                    hit, model = self.model_load(a_model)
                    self.a_enable = hit
                    self.a_model = model
                    self.a_token = int(self.models[a_model]['token'])
                    logger.debug(f"モデルAを{a_model}に変更")
            if (a_use_tools != ''):
                self.a_use_tools = a_use_tools
                
            # モデルB設定 (拡張モデル)
            if (b_model != ''):
                if (b_model != self.b_model) and (b_model in self.models):
                    hit, model = self.model_load(b_model)
                    self.b_enable = hit
                    self.b_model = model
                    self.b_token = int(self.models[b_model]['token'])
                    logger.debug(f"モデルBを{b_model}に変更")
            if (b_use_tools != ''):
                self.b_use_tools = b_use_tools
                
            # モデルV設定更新
            if (v_model != ''):
                if (v_model != self.v_model) and (v_model in self.models):
                    hit, model = self.model_load(v_model)
                    self.v_enable = hit
                    self.v_model = model
                    self.v_token = int(self.models[v_model]['token'])
                    logger.debug(f"モデルVを{v_model}に変更")
            if (v_use_tools != ''):
                self.v_use_tools = v_use_tools
                
            # モデルX設定 (特殊モデル)
            if (x_model != ''):
                if (x_model != self.x_model) and (x_model in self.models):
                    hit, model = self.model_load(x_model)
                    self.x_enable = hit
                    self.x_model = model
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

    def history2msg_text(self, history=[]):
        """
        履歴をChatgpt API用のメッセージ形式に変換
        Args:
            history (list, optional): 会話履歴            
        Returns:
            list: API用に変換されたメッセージリスト
        """
        # 過去メッセージをテキストとして追加
        msg_text = ''
        if (len(history) > 2):
            msg_text += "''' これは過去の会話履歴です。\n"
            for m in range(len(history) - 2):
                role = history[m].get('role','')
                content = history[m].get('content','')
                name = history[m].get('name','')
                if (role != 'system'):
                    # 全てユーザーメッセージにて処理
                    if (name is None) or (name == ''):
                        msg_text += '(' + role + ')' + '\n' + content + '\n'
                    else:
                        if (role == 'function_call'):
                            msg_text += '(function ' + name + ' call)'  + '\n' + content + '\n'
                        else:
                            msg_text += '(function ' + name + ' result) ' + '\n' + content + '\n'
            msg_text += "''' 会話履歴はここまでです。\n"
            msg_text += "\n"
       
        # 最新のユーザーメッセージを追加
        m = len(history) - 1
        msg_text += history[m].get('content', '')

        return msg_text


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
        msg_text = ''
        if (sysText is not None) and (sysText != ''):
            msg_text += sysText + '\n'
        if (reqText is not None) and (reqText != ''):
            msg_text += reqText + '\n'
        msg_text += inpText
        messages = []

        # 画像無し
        if (len(image_urls) == 0) or (len(image_urls) != len(upload_files)):
            msg = {"role": "user", "content": msg_text}
            messages.append(msg)
        # 画像あり
        else:
            images = []
            for file_name in upload_files:
                if (os.path.isfile(file_name)):
                    if (os.path.getsize(file_name) <= 20000000):
                        file_ext = os.path.splitext(file_name)[1][1:].lower()
                        if (file_ext in ('jpg', 'jpeg', 'png')):
                            base64_text = base64_encode(file_name)
                            images.append(base64_text)
            if (len(images) == 0):
                msg = {"role": "user", "content": msg_text}
                messages.append(msg)
            else:
                msg = {"role": "user", "content": msg_text, "images": images}
                messages.append(msg)

        # ストリーミングモード無効
        stream = False

        # ツール（関数）設定
        functions = []
        # 2025/04/09時点 ツールに未対応です！

        # 実行ループ
        try:
            n = 0
            function_name = ''
            while (function_name != 'exit') and (n < int(max_step)):
                # 結果初期化
                res_role = None
                res_content = None

                # モデル実行
                n += 1
                logger.info(f"//Ollama// {res_name.lower()}, {res_api}, pass={n}, ")

                # API呼び出し
                content_text = None
                response = self.client.chat(
                    model=res_api,
                    messages=messages,
                    options={"temperature": float(temperature)},
                    stream=stream,
                )

                # ストリーム表示
                if (stream == True):
                    try:
                        chkTime = time.time()
                        for chunk in response:
                            if ((time.time() - chkTime) > self.max_wait_sec):
                                logger.warning("ストリーミング処理がタイムアウト")
                                break

                            content_text = response['message']['content']
                            if (content_text is not None) and (content_text != ''):
                                self.stream(session_id, content_text)
                                if (res_content is None):
                                    res_role = 'assistant'
                                    res_content = ''
                                res_content += content_text

                        # 改行
                        if (res_content is not None):
                            self.print(session_id)

                    except Exception as e:
                        logger.error(f"ストリーム処理エラー: {e}")

                # 通常レスポンス処理
                if (stream == False):
                    content_text = response['message']['content']
                    if (content_text is not None) and (content_text != ''):
                        res_role = 'assistant'
                        res_content = content_text

                # 会話終了
                function_name = 'exit'
                logger.info(f"//ollama// {res_name.lower()}, complete.")

            # 正常回答
            if (res_content is not None):
                res_text += res_content.rstrip()
            # 異常回答
            else:
                logger.error('//OpenRT// Error !')

            # History追加格納
            if (res_text.strip() != ''):
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': res_text}
                res_history.append(dic)

        except Exception as e:
            logger.error(f"Error in run_gpt: {e}")
            res_text = ''

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
        logger.debug(f"//Ollama// chat_class={chat_class}, model_select={model_select}")
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
    ollamaAPI = _ollamaAPI()

    # API種別を取得
    ollamaKEY = ollama_key._conf_class()
    ollamaKEY.init(runMode='debug')
    logger.info(f"api_type={ollamaKEY.api_type}")

    # ログキューの設定
    stream_queue = queue.Queue()
    res = ollamaAPI.init(stream_queue=stream_queue)

    # 認証処理
    res = ollamaAPI.authenticate('ollama',
                        ollamaKEY.api_type,
                        ollamaKEY.default_gpt, ollamaKEY.default_class,
                        ollamaKEY.auto_continue,
                        ollamaKEY.max_step, ollamaKEY.max_session,
                        ollamaKEY.max_wait_sec,

                        ollamaKEY.ollama_server, ollamaKEY.ollama_port,

                        ollamaKEY.a_nick_name, ollamaKEY.a_model, ollamaKEY.a_token,
                        ollamaKEY.a_use_tools,
                        ollamaKEY.b_nick_name, ollamaKEY.b_model, ollamaKEY.b_token,
                        ollamaKEY.b_use_tools,
                        ollamaKEY.v_nick_name, ollamaKEY.v_model, ollamaKEY.v_token,
                        ollamaKEY.v_use_tools,
                        ollamaKEY.x_nick_name, ollamaKEY.x_model, ollamaKEY.x_token,
                        ollamaKEY.x_use_tools,
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
            for model in ollamaAPI.models:
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
            res_text, res_path, res_files, res_name, res_api, ollamaAPI.history = \
                ollamaAPI.chatBot(  chat_class='auto', model_select='auto', 
                                    session_id=session_id, history=ollamaAPI.history,
                                    function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                    inpLang='ja', outLang='ja', )
            print(f"----------------------------")
            print(f"[{ res_name }] ({ res_api })")
            print(f"{  str(res_text.rstrip())  }")
            print(f"----------------------------")

        # テスト2: 画像認識
        if True:
            sysText = None
            reqText = ''
            #inpText = '添付画像を説明してください。'
            #inpText = '画像検索に利用できるように、この画像の内容を箇条書きで説明してください。'
            inpText = 'To help with image search, please provide a brief description of what this image does.'
            filePath = ['_icons/dog.jpg']
            #filePath = ['_icons/dog.jpg', '_icons/kyoto.png']
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, ollamaAPI.history = \
                ollamaAPI.chatBot(  chat_class='auto', model_select='auto', 
                                    session_id=session_id, history=ollamaAPI.history,
                                    function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                    inpLang='ja', outLang='ja', )
            print(f"----------------------------")
            print(f"[{ res_name }] ({ res_api })")
            print(f"{  str(res_text.rstrip())  }")
            print(f"----------------------------")

        # テスト3: ツール実行
        if False:
            import    speech_bot_function
            botFunc = speech_bot_function.botFunction()
            res, msg = botFunc.functions_load(
                functions_path='_extensions/function/', secure_level='low', )
            for key, module_dic in botFunc.function_modules.items():
                if (module_dic['onoff'] == 'on'):
                    function_modules[key] = module_dic

        if False:
          if function_modules:
            sysText = None
            reqText = ''
            inpText = 'ollama-b,toolsで兵庫県三木市の天気を調べて'
            filePath = []
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, ollamaAPI.history = \
                ollamaAPI.chatBot(  chat_class='auto', model_select='auto', 
                                    session_id=session_id, history=ollamaAPI.history,
                                    function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                    inpLang='ja', outLang='ja', )
            print(f"----------------------------")
            print(f"[{ res_name }] ({ res_api })")
            print(f"{  str(res_text.rstrip())  }")
            print(f"----------------------------")

        # 履歴表示（オプション）
        if False:
            logger.info("会話履歴の内容を表示")
            print(f"----------------------------")
            for history in ollamaAPI.history:
                print(history)
            print(f"----------------------------")
            geminiAPI.history = []

    logger.info("【テスト終了】")
