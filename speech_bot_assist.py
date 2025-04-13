#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'assist'

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
import queue
import base64
import glob


# API ライブラリ
import openai

# APIキー情報のインポート
import speech_bot_assist_key as assist_key

# パス設定
qPath_temp = 'temp/'
qPath_output = 'temp/output/'
qPath_chat_work = 'temp/chat_work/'

# グローバル変数
import socket
qHOSTNAME = socket.gethostname().lower()


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


class _assistAPI:
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
        self.api_type = 'openai'
        self.default_gpt = 'auto'
        self.default_class = 'auto'
        self.auto_continue = 3
        self.max_step = 10
        self.max_session = 5
        self.max_wait_sec = 120
       
        # API認証情報
        self.openai_organization = None
        self.openai_key_id = None
        self.azure_endpoint = None
        self.azure_version = None
        self.azure_key_id = None

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

        # モデルV設定 (Vision対応モデル)
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

        # アシスタント設定
        self.assistant_name = qHOSTNAME
        self.assistant_id = {}
        self.thread_id = {}

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

                     openai_organization, openai_key_id,
                     azure_endpoint, azure_version, azure_key_id,

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
        self.openai_organization = openai_organization
        self.openai_key_id = openai_key_id
        self.azure_endpoint = azure_endpoint
        self.azure_version = azure_version
        self.azure_key_id = azure_key_id

        # APIクライアントの初期化
        self.client = None
        try:
            # API認証
            if (api_type != 'azure'):
                if (openai_key_id[:1] == '<'):
                    logger.warning("APIキーが未設定です")
                    return False
                else:
                    logger.debug("APIクライアントを初期化します")
                    self.client = openai.OpenAI(organization=openai_organization,
                                                api_key=openai_key_id)
            # Azure OpenAI API認証
            else:
                if (azure_key_id[:1] == '<'):
                    logger.warning("APIキーが未設定です")
                    return False
                else:
                    logger.debug("APIクライアントを初期化します")
                    self.client = openai.AzureOpenAI(azure_endpoint=azure_endpoint,
                                                     api_version=azure_version,
                                                     api_key=azure_key_id)
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
            for model in models:
                key = model.id
                ymd = datetime.datetime.fromtimestamp(model.created).strftime("%Y/%m/%d")
                # 2025年以降のモデルやGPT-4o系を対象
                if (ymd >= '2025/01/01') \
                or (key.find('gpt-4o') >= 0) or (key.find('o1') >= 0) or (key.find('o3') >= 0):
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

    def vectorStore_del(self, session_id='admin', assistant_id=None, assistant_name='', ):
        # ベクターストアの削除
        
        # 2024/04/21時点 azure 未対応
        if (self.api_type == 'azure'):
            return False

        # vector store 削除
        vector_stores = self.client.vector_stores.list()
        for v in range(len(vector_stores.data)):
            vs_id = vector_stores.data[v].id
            vs_name = vector_stores.data[v].name
            if (vs_name == assistant_name):
                vs_files = self.client.vector_stores.files.list(vector_store_id=vs_id)

                for f in range(len(vs_files.data)):
                    file_id = vs_files.data[f].id
                    self.client.files.delete(file_id=file_id, )
                logger.debug(f"Deleted vector store: {vs_name}")
                self.client.vector_stores.delete(vector_store_id=vs_id)

                break
        
        return True

    def vectorStore_set(self, session_id='admin', retrievalFiles_path='_extensions/retrieval_files/', assistant_id=None, assistant_name='', ):
        # ベクターストアの設定
        vectorStore_ids = []

        # 2024/04/21時点 azure 未対応
        if (self.api_type == 'azure'):
            return vectorStore_ids

        # ファイル一覧
        proc_files = []
        path_files = glob.glob(retrievalFiles_path + '*.*')
        path_files.sort()
        if (len(path_files) > 0):
            for f in path_files:
                proc_files.append(os.path.basename(f))

        # マッチング検査 違いがあれば vector store 削除
        vector_stores = self.client.vector_stores.list()
        for v in range(len(vector_stores.data)):
            vs_id = vector_stores.data[v].id
            vs_name = vector_stores.data[v].name
            # bug?
            if (vs_id in ['vs_67a9cb0bdd748191aa1a2892c6612d68']):
                pass
            else:
                if (vs_name == assistant_name):
                    vs_files = self.client.vector_stores.files.list(vector_store_id=vs_id)

                    vectorStore_ids = [vs_id]
                    if (len(proc_files) != len(vs_files.data)):
                        vectorStore_ids = []
                    else:
                        for f in range(len(vs_files.data)):
                            file_id = vs_files.data[f].id
                            file_info = self.client.files.retrieve(file_id=file_id, )
                            file_name = file_info.filename
                            if (file_name not in proc_files):
                                vectorStore_ids = []
                                break

                    if (len(vectorStore_ids) == 0):
                        for f in range(len(vs_files.data)):
                            file_id = vs_files.data[f].id
                            self.client.files.delete(file_id=file_id, )
                        logger.debug(f"Deleted non-matching vector store: {vs_name}")
                        self.client.vector_stores.delete(vector_store_id=vs_id)

                    break

        # 転送不要
        if (len(vectorStore_ids) == len(proc_files)):
            return vectorStore_ids

        # vector store 作成
        if (len(proc_files) > 0):

            # ファイル
            upload_ids = []
            for proc_file in proc_files:
                file_name = retrievalFiles_path + proc_file
                if (os.path.isfile(file_name)):

                    # アップロード済み確認
                    file_id = None
                    files_list = self.client.files.list()
                    for n in range(len(files_list.data)):
                        if (proc_file == files_list.data[n].filename):
                            file_id = files_list.data[n].id
                            logger.debug(f"Found existing file: '{proc_file}', {file_id}")
                            break

                    # アップロード
                    if (file_id == None):
                        try:
                            # アップロード
                            file = open(file_name, 'rb')
                            upload = self.client.files.create(
                                        file = file,
                                        purpose = 'assistants', )
                            file_id = upload.id
                            logger.info(f"Uploaded file: '{proc_file}', {file_id}")
                        except Exception as e:
                            logger.error(f"File upload error: {e}")

                    if (file_id != None):
                        upload_ids.append(file_id)

            # ベクターストア作成
            if (len(upload_ids) > 0):
                try:
                    vector_store = self.client.vector_stores.create(
                                        name = assistant_name,
                                    )

                    file_batch = self.client.vector_stores.file_batches.create_and_poll(
                                        vector_store_id = vector_store.id,
                                        file_ids = upload_ids,
                                    )

                    logger.debug(f"Created vector store with status: {file_batch.status}")

                    vectorStore_ids = [vector_store.id]

                except Exception as e:
                    logger.error(f"Vector store creation error: {e}")

        return vectorStore_ids

    def threadFile_del(self, session_id='admin', assistant_id=None, assistant_name='', ):
        # スレッドファイルの削除

        # 2024/04/21時点 azure 未対応
        if (self.api_type == 'azure'):
            return False

        files_list = self.client.files.list()
        for f in range(len(files_list.data)):
            file_id = files_list.data[f].id
            file_name = files_list.data[f].filename

            x = len(assistant_name)
            if (file_name[:x] == assistant_name):
                res = self.client.files.delete(
                    file_id=file_id, )
                logger.debug(f"Deleted thread file: {file_name}")

        return True

    def threadFile_set(self, session_id='admin', upload_files=[], assistant_id=None, assistant_name='', ):
        # スレッドファイルの設定
        upload_ids = []

        # 2024/04/21時点 azure 未対応
        if (self.api_type == 'azure'):
            return upload_ids

        if (not os.path.isdir(qPath_chat_work)):
            os.makedirs(qPath_chat_work)
        for upload_file in upload_files:
            base_name = os.path.basename(upload_file)
            work_name = assistant_name + '_' + base_name
            upload_work = qPath_chat_work + work_name
            shutil.copy(upload_file, upload_work)

            # 既に存在なら、置換えの為、削除
            files_list = self.client.files.list()
            for f in range(len(files_list.data)):
                file_id = files_list.data[f].id
                file_name = files_list.data[f].filename
                if (file_name == work_name):
                    res = self.client.files.delete(
                        file_id=file_id, )
                    logger.debug(f"Deleted existing file: {file_name}")

            # アップロード
            upload = self.client.files.create(
                file = open(upload_work, 'rb'),
                purpose='assistants', )
            upload_ids.append(upload.id)

            logger.info(f"Uploaded thread file: { upload.id }, { base_name },")

        return upload_ids

    def threadFile_reset(self, session_id='admin', upload_ids=[], assistant_id=None, assistant_name='', ):
        # スレッドファイルのリセット

        # 2024/04/21時点 azure 未対応
        if (self.api_type == 'azure'):
            return False

        # 削除
        for upload_id in upload_ids:
            try:
                res = self.client.files.delete(
                    file_id=upload_id, )
                logger.debug(f"Reset thread file: {upload_id}")
            except:
                pass

        return True

    def my_assistant_update(self, session_id='admin', my_assistant_id=None, my_assistant_name='',
                            model_name='gpt-4o', use_tools='yes', instructions='', 
                            function_list=[], vectorStore_ids=[], upload_ids=[], ):
        # アシスタントの更新

        try:
            # ツール設定
            tools = []
            if (use_tools.lower().find('yes') >= 0):
                if (model_name[:1].lower() != 'o'): # o1, o3, ... 以外
                    tools.append({"type": "code_interpreter"})
                    if (len(vectorStore_ids) > 0):
                        tools.append({"type": "file_search"})
                if (len(function_list) != 0):
                    for f in range(len(function_list)):
                        tools.append({"type": "function", "function": function_list[f]})

            # アシスタント取得
            assistant = self.client.beta.assistants.retrieve(
                assistant_id = my_assistant_id, )
            try:
                as_vector_ids = []
                as_vector_ids = assistant.tool_resources.file_search.vector_store_ids
            except:
                pass
            try:
                as_file_ids = []
                as_file_ids = assistant.tool_resources.code_interpreter.file_ids
            except:
                pass

            # アシスタント更新
            change_flag = False
            if (model_name != assistant.model):
                change_flag = True
                logger.debug(f"Model change detected: {model_name}")
            if (instructions != assistant.instructions):
                change_flag = True
                logger.debug("Instructions change detected")
            if (len(tools) != len(assistant.tools)):
                change_flag = True
                logger.debug("Tools change detected")
            if (vectorStore_ids != as_vector_ids):
                change_flag = True
                logger.debug("Vector store IDs change detected")
            if (upload_ids != as_file_ids):
                change_flag = True
                logger.debug("File IDs change detected")

            if (change_flag != True):
                return False
            else:
                logger.debug(f"Updating assistant: ( name='{ my_assistant_name }', model={ model_name }, ) ")

                # OPENAI
                if (self.api_type != 'azure'):
                    tool_resources = {}
                    if (model_name[:1].lower() != 'o'): # o1, o3, ... 以外
                        if (len(vectorStore_ids) > 0):
                            tool_resources["file_search"] = { "vector_store_ids": vectorStore_ids }
                        if (len(upload_ids) > 0):
                            tool_resources["code_interpreter"] = { "file_ids": upload_ids }

                    assistant = self.client.beta.assistants.update(
                                        assistant_id = my_assistant_id,
                                        model = model_name,
                                        instructions = instructions,
                                        tools = tools,
                                        timeout = self.max_wait_sec,
                                        tool_resources = tool_resources,
                                    )

                # Azure
                else:
                    assistant = self.client.beta.assistants.update(
                                        assistant_id = my_assistant_id,
                                        model = model_name,
                                        instructions = instructions,
                                        tools = tools,
                                        timeout = self.max_wait_sec,
                                    )

        except Exception as e:
            logger.error(f"Assistant update error: {e}")
            return False
        return True


    def run_assist(self, chat_class='assist', model_select='auto',
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
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
        res_history = self.history_zip1(history=res_history, )

        # 関数リストの準備
        function_list = []
        for module_dic in function_modules.values():
            function_list.append(module_dic['function'])

        # 結果の初期化
        res_role = None
        res_content = None
        upload_ids = []
        exit_status = None
        last_status = None

        # 動作設定
        instructions = sysText
        if (instructions is None) or (instructions == ''):
            instructions = 'あなたは美しい日本語を話す賢いアシスタントです。'

        # アシスタント確認
        my_assistant_name = self.assistant_name + '-' + str(session_id)
        my_assistant_id = self.assistant_id.get(str(session_id))

        # アシスタント検索
        assistants = self.client.beta.assistants.list(
            order = "desc",
            limit = "100", )
        for a in range(len(assistants.data)):
            assistant = assistants.data[a]
            if (assistant.name == my_assistant_name):
                my_assistant_id = assistant.id
                logger.debug(f"Found existing assistant: {my_assistant_name}")
                break

        # モデルの変更時は削除
        if (my_assistant_id is not None):
            if (res_api != assistant.model):
                logger.debug(f"Model change detected from {assistant.model} to {res_api}")

                for assistant in assistants.data:
                    if (assistant.name == my_assistant_name):
                        logger.debug(f"Deleting assistant due to model change: {assistant.name}")

                        # アシスタント削除
                        try:
                            res = self.client.beta.assistants.delete(assistant_id = assistant.id, )
                        except Exception as e:
                            logger.error(f"Failed to delete assistant: {e}")
                        my_assistant_id = None
                        break

        # アシスタント生成
        if (my_assistant_id is None):
            # アシスタント検索
            assistants = self.client.beta.assistants.list(
                order = "desc",
                limit = "100", )

            # (最大セッション以上の)アシスタント削除
            if (self.max_session > 0) and (len(assistants.data) > 0):
                for a in range(self.max_session -1 , len(assistants.data)):
                    assistant = assistants.data[a]
                    logger.debug(f"Deleting excess assistant: {assistant.name}")

                    # vector store 削除
                    res = self.vectorStore_del(session_id = session_id,
                                              assistant_id = my_assistant_id, 
                                              assistant_name = my_assistant_name, )

                    # ファイル 削除
                    res = self.threadFile_del(session_id = session_id,
                                             assistant_id = my_assistant_id,
                                             assistant_name = my_assistant_name, )

                    # アシスタント削除
                    try:
                        res = self.client.beta.assistants.delete(assistant_id = assistant.id, )
                    except Exception as e:
                        logger.error(f"Failed to delete excess assistant: {e}")

            # アシスタント生成
            logger.debug(f"Creating new assistant: name={my_assistant_name}, model={res_api}")
            assistant = self.client.beta.assistants.create(
                    name = my_assistant_name,
                    model = res_api,
                    instructions = instructions,
                    tools = [], )
            my_assistant_id = assistant.id
            self.assistant_id[str(session_id)] = my_assistant_id

        # アシスタント更新
        if (my_assistant_id is not None):
            # vector store 作成
            vectorStore_ids = self.vectorStore_set(session_id = session_id,
                                                 retrievalFiles_path = '_extensions/retrieval_files/',
                                                 assistant_id = my_assistant_id, 
                                                 assistant_name = my_assistant_name, )

            # ファイルアップロード
            upload_ids = self.threadFile_set(session_id = session_id,
                                           upload_files = upload_files,
                                           assistant_id = my_assistant_id,
                                           assistant_name = my_assistant_name, )

            res = self.my_assistant_update(session_id = session_id,
                                         my_assistant_id = my_assistant_id,
                                         my_assistant_name = my_assistant_name,
                                         model_name = res_api, 
                                         use_tools = use_tools,
                                         instructions = instructions, 
                                         function_list = function_list,
                                         vectorStore_ids = vectorStore_ids,
                                         upload_ids = upload_ids, )

        # スレッド確認
        my_thread_id = self.thread_id.get(str(session_id))
        if (my_thread_id is None):
            # スレッド生成
            logger.debug(f"Creating new thread for assistant: name={my_assistant_name}")
            thread = self.client.beta.threads.create(
                metadata = {'assistant_name': my_assistant_name}, )
            my_thread_id = thread.id
            self.thread_id[str(session_id)] = my_thread_id

            # 過去メッセージ追加
            for m in range(len(res_history) - 1):
                role = res_history[m].get('role','')
                content = res_history[m].get('content','')
                name = res_history[m].get('name','')
                if (role != 'system'):
                    # 全てユーザーメッセージにて処理
                    if (name is None) or (name == ''):
                        msg_text = '(' + role + ')' + '\n' + content
                    else:
                        if (role == 'function_call'):
                            msg_text = '(function ' + name + ' call)'  + '\n' + content
                        else:
                            msg_text = '(function ' + name + ' result) ' + '\n' + content
                    res = self.client.beta.threads.messages.create(
                        thread_id = my_thread_id,
                        role = 'user',
                        content = msg_text, )

        # メッセージ生成
        content_text = ''
        if (reqText is not None) and (reqText.strip() != ''):
            content_text += reqText.rstrip() + '\n'
        if (inpText is not None) and (inpText.strip() != ''):
            content_text += inpText.rstrip() + '\n'
        res = self.client.beta.threads.messages.create(
            thread_id = my_thread_id,
            role = 'user',
            content = content_text, )

        # ストリーミングモード無効
        stream = False

        # 実行開始        
        if True:
            # 実行開始
            run = self.client.beta.threads.runs.create(
                assistant_id = my_assistant_id,
                thread_id = my_thread_id, )
            my_run_id = run.id

            # 実行ループ
            exit_status = None
            last_status = None
            count_run_step = 0
            messages = self.client.beta.threads.messages.list(
                        thread_id = my_thread_id, 
                        order = 'asc', )
            last_msg_step = len(messages.data) # First msg is request
            last_message = None
            
            chkTime = time.time()
            while (exit_status is None) and ((time.time() - chkTime) < self.max_wait_sec):
                # ステータス
                run = self.client.beta.threads.runs.retrieve(
                        thread_id = my_thread_id,
                        run_id = my_run_id, )
                if (run.status != last_status):
                    last_status = run.status
                    chkTime = time.time()
                    logger.info(f"//Assist// ({last_status})")

                # 実行ステップ確認
                run_steps = self.client.beta.threads.runs.steps.list(
                        thread_id = my_thread_id,
                        run_id = my_run_id,
                        order = 'asc', )
                if (len(run_steps.data) > count_run_step):
                    for r in range(count_run_step, len(run_steps.data)):
                        step_details_type = run_steps.data[r].step_details.type
                        if (step_details_type != 'tool_calls'):
                            logger.info(f"//Assist// ({step_details_type})")
                        else:
                            step_details_tool_type = None
                            try:
                                step_details_tool_type = run_steps.data[r].step_details.tool_calls[0].type
                            except:
                                try:
                                    tc = run_steps.data[r].step_details.tool_calls[0]
                                    step_details_tool_type = tc.get('type')
                                except:
                                    pass
                            if (step_details_tool_type is not None):
                                logger.info(f"//Assist// ({step_details_tool_type})")
                            else:
                                logger.info(f"//Assist// ({step_details_type})")

                        if (step_details_type == 'message_creation'):
                            message_id = run_steps.data[r].step_details.message_creation.message_id
                            if (message_id is not None):
                                messages = self.client.beta.threads.messages.retrieve(
                                        thread_id = my_thread_id, 
                                        message_id = message_id, )
                                for c in range(len(messages.content)):
                                    content_type = messages.content[c].type
                                    if (content_type == 'text'):
                                        content_value = messages.content[c].text.value
                                        if (content_value is not None) and (content_value != ''):
                                            if (last_status != 'completed'):
                                                if (content_value != last_message):
                                                    last_message = content_value 
                                                    logger.info(last_message)

                    count_run_step = len(run_steps.data)

                # 最大ステップ確認
                limit_step = int((int(max_step) * (int(self.auto_continue)+1)) / 2)
                if (count_run_step > limit_step):
                    exit_status = 'overstep'
                    logger.warning(f"//Assist// overstep! (n={ count_run_step }!)")
                    break

                # 実行メッセージ確認
                messages = self.client.beta.threads.messages.list(
                        thread_id = my_thread_id, 
                        order = 'asc', )
                if (len(messages.data) > last_msg_step):
                    for m in range(last_msg_step, len(messages.data)):
                        res_role = messages.data[m].role
                        for c in range(len(messages.data[m].content)):
                            content_type = messages.data[m].content[c].type
                            if (content_type == 'text'):
                                content_value = messages.data[m].content[c].text.value
                                if (content_value is not None) and (content_value != ''):
                                    last_msg_step = m
                                    if (last_status != 'completed'):
                                        if (content_value != last_message):
                                            last_message = content_value 
                                            logger.info(last_message)
                                    else:
                                        res_content = content_value

                                annotations=messages.data[m].content[c].text.annotations
                                for annotation in annotations:
                                    try:
                                        file_type = annotation.type
                                        file_text = annotation.text
                                        file_id = annotation.file_path.file_id

                                        file_dic = self.client.files.retrieve(file_id)
                                        filename = os.path.basename(file_dic.filename)
                                        content_file = self.client.files.content(file_id)
                                        data_bytes = content_file.read()
                                        if (not os.path.isdir(qPath_output)):
                                            os.makedirs(qPath_output)
                                        with open(qPath_output + filename, "wb") as file:
                                            file.write(data_bytes)

                                        res_path = qPath_output + filename
                                        logger.info(f"//Assist// Downloaded file {filename}")
                                    except Exception as e:
                                        logger.error(f"File download error: {e}")

                # 処理中
                if (last_status is None):
                    logger.warning("Run status is None")
                elif (last_status == 'in_progress') \
                or (last_status == 'queued') \
                or (last_status == 'cancelling'):
                    pass
                # 終了
                elif (last_status == 'completed') \
                or (last_status == 'cancelled') \
                or (last_status == 'failed') \
                or (last_status == 'expired'):
                    exit_status = last_status
                    # 正常終了
                    if (last_status == 'completed'):
                        logger.debug("Run completed successfully")
                        break
                    # その他終了
                    else:
                        logger.warning(f"Run ended with status: {last_status}")
                        break
                # ファンクション
                elif (last_status == 'requires_action'):
                    tool_result = []
                    upload_flag = False

                    # ツール実行処理
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    for tc in tool_calls:
                        f_id  = tc.id
                        f_name = tc.function.name
                        f_kwargs = tc.function.arguments

                        hit = False

                        # 登録された関数モジュールを検索
                        module_dic = function_modules.get(f_name)
                        if (module_dic is not None):
                                hit = True
                                logger.info(f"//Assist//   function_call '{ module_dic['script'] }' ({  f_name })")
                                logger.info(f"//Assist//   → { f_kwargs }")

                                chkTime = time.time()

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
                                logger.info(f"//Assist//   → { res_json }")
                                tool_result.append({"tool_call_id": f_id, "output": res_json})

                                chkTime = time.time()

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
                                        upload_files.append(path)
                                        upload_files = list(set(upload_files))
                                        logger.debug(f"ファイルパスを検出: {path}")

                                        # ファイルアップロード
                                        upload_ids = self.threadFile_set(session_id = session_id,
                                                                      upload_files = upload_files,
                                                                      assistant_id = my_assistant_id,
                                                                      assistant_name = my_assistant_name, )
                                        upload_flag = True

                                except Exception as e:
                                    logger.error(f"パス情報エラー: {e}")

                        # 関数が見つからない場合
                        if (hit == False):
                            dic = {'error': f"function not found Error ! ({f_name})"}
                            res_json = json.dumps(dic, ensure_ascii=False, )

                            # tool_result
                            logger.info(f"//Assist//   → { res_json }")
                            tool_result.append({"tool_call_id": f_id, "output": res_json})

                            logger.error(f"//Assist//   function not found Error ! ({f_name})")
                            break

                    # 結果通知
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id = my_thread_id,
                        run_id = my_run_id,
                        tool_outputs = tool_result, )
                    logger.debug("Tool outputs submitted")

                    # アシスタント更新
                    if (upload_flag == True):
                        res = self.my_assistant_update(session_id = session_id,
                                                    my_assistant_id = my_assistant_id,
                                                    my_assistant_name = my_assistant_name,
                                                    model_name = res_api, 
                                                    instructions = instructions, 
                                                    function_list = function_list,
                                                    vectorStore_ids = vectorStore_ids,
                                                    upload_ids = upload_ids, )
                        logger.debug("Assistant updated with new files")

                else:
                    logger.info(run)

        if (exit_status is None):
            exit_status = 'timeout'
            logger.error(f"Run timeout after {self.max_wait_sec}s")
            
        # 結果確認
        if (exit_status == 'completed'):
            if (res_content is not None):
                res_text += res_content.rstrip() + '\n'

            # 履歴に応答を追加
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': res_role, 'name': '', 'content': res_text }
            res_history.append(dic)

        # 異常終了
        else:
            res_text = ''
            # 履歴に終了状態を追加
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'assist', 'name': '', 'content': exit_status }
            res_history.append(dic)

        # 実行キャンセル
        runs = self.client.beta.threads.runs.list(
            thread_id = my_thread_id, )
        for r in range(len(runs.data)):
            run_id = runs.data[r].id
            run_status = runs.data[r].status
            if (run_status != 'completed') \
            and (run_status != 'cancelled') \
            and (run_status != 'failed') \
            and (run_status != 'expired') \
            and (run_status != 'cancelling'):
                try:
                    run = self.client.beta.threads.runs.cancel(
                        thread_id = my_thread_id, 
                        run_id = run_id, )
                    logger.debug(f"Canceled run: {run_id}")
                except:
                    pass

        # 後片付け用の情報を保存
        self.work_upload_ids = upload_ids
        self.work_assistant_id = my_assistant_id
        self.work_assistant_name = my_assistant_name

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
        logger.debug(f"//Assist// chat_class={chat_class}, model_select={model_select}")
        res_text, res_path, res_files, nick_name, model_name, res_history = \
            self.run_assist(chat_class=chat_class, model_select=model_select,
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
    assistAPI = _assistAPI()

    # API種別を取得
    assistKEY = assist_key._conf_class()
    assistKEY.init(runMode='debug')
    logger.info(f"api_type={assistKEY.api_type}")

    # ログキューの設定
    stream_queue = queue.Queue()
    res = assistAPI.init(stream_queue=stream_queue)

    # 認証処理
    res = assistAPI.authenticate('assist',
                        assistKEY.api_type,
                        assistKEY.default_gpt, assistKEY.default_class,
                        assistKEY.auto_continue,
                        assistKEY.max_step, assistKEY.max_session,
                        assistKEY.max_wait_sec,

                        assistKEY.openai_organization, assistKEY.openai_key_id,
                        assistKEY.azure_endpoint, assistKEY.azure_version, assistKEY.azure_key_id,

                        assistKEY.a_nick_name, assistKEY.a_model, assistKEY.a_token,
                        assistKEY.a_use_tools,
                        assistKEY.b_nick_name, assistKEY.b_model, assistKEY.b_token,
                        assistKEY.b_use_tools,
                        assistKEY.v_nick_name, assistKEY.v_model, assistKEY.v_token,
                        assistKEY.v_use_tools,
                        assistKEY.x_nick_name, assistKEY.x_model, assistKEY.x_token,
                        assistKEY.x_use_tools,
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
            for model in assistAPI.models:
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
            res_text, res_path, res_files, res_name, res_api, assistAPI.history = \
                assistAPI.chatBot(chat_class='auto', model_select='auto', 
                                        session_id=session_id, history=assistAPI.history,
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
            inpText = '添付画像を説明してください。'
            filePath = ['_icons/dog.jpg']
            #filePath = ['_icons/dog.jpg', '_icons/kyoto.png']
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, assistAPI.history = \
                assistAPI.chatBot(chat_class='auto', model_select='auto', 
                                        session_id=session_id, history=assistAPI.history,
                                        function_modules=function_modules,
                                        sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                        inpLang='ja', outLang='ja', )
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
            inpText = 'assist-b,toolsで兵庫県三木市の天気を調べて'
            filePath = []
            if reqText:
                logger.info(f"ReqText : {reqText.rstrip()}")
            if inpText:
                logger.info(f"inpText : {inpText.rstrip()}")
            res_text, res_path, res_files, res_name, res_api, assistAPI.history = \
                    assistAPI.chatBot(   chat_class='auto', model_select='auto', 
                                            session_id=session_id, history=assistAPI.history,
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
            for history in assistAPI.history:
                print(history)
            print(f"----------------------------")
            assistAPI.history = []

    logger.info("【テスト終了】")
