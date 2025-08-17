#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'conf'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)


import os
import datetime


# 設定ファイルパス
CONFIG_FILE = 'RiKi_Monjyu_key.json'

# 共通キー管理クラスのインポートとインスタンス生成
import _v7__qRiKi_key
qRiKi_key = _v7__qRiKi_key.qRiKi_key_class()

# 一時ファイル保存用パス
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'


class _conf_class:
    def __init__(self):
        """
        設定クラスの初期化
        各種設定項目のデフォルト値を設定
        """
        logger.debug("_conf_class インスタンスを初期化します")
        # 設定項目
        self.runMode = 'debug'
        self.run_priority = 'auto'

        # 設定項目
        self.cgpt_secure_level = 'medium'
        self.cgpt_addins_path = '_extensions/Monjyu/'
        self.cgpt_functions_path = '_extensions/function/'
        self.cgpt_engine_greeting = 'auto'
        self.cgpt_engine_chat = 'auto'
        self.cgpt_engine_vision = 'auto'
        self.cgpt_engine_fileSearch = 'auto'
        self.cgpt_engine_webSearch = 'auto'
        self.cgpt_engine_serial = 'auto'
        self.cgpt_engine_parallel = 'auto'

        # APIキー関連設定
        self.openai_api_type = ''
        self.openai_organization = '< your openai organization >'
        self.openai_key_id = '< your openai key >'
        self.azure_endpoint = '< your azure endpoint base >'
        self.azure_version = 'yyyy-mm-dd'
        self.azure_key_id = '< your azure key >'
        self.gemini_key_id = '< your gemini key >'
        self.freeai_key_id = '< your freeai key >'
        self.claude_key_id = '< your claude key >'
        self.openrt_key_id = '< your openrt key >'
        self.perplexity_key_id = '< your perplexity key >'
        self.grok_key_id = '< your grok key >'
        self.groq_key_id = '< your groq key >'
        self.ollama_server = 'auto'
        self.ollama_port = 'auto'

    def init(self, runMode='debug', qLog_fn=''):
        """
        設定を初期化する関数
        設定ファイルの読み込みと、未設定時のデフォルト値設定を行う
        Args:
            runMode (str): 実行モード ('debug'など)
        Returns:
            bool: 初期化が成功したかどうか
        """
        # 初期化処理
        logger.debug(f"設定の初期化を開始: runMode={runMode}")
        self.runMode = runMode

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug('init')

        # 設定ファイルの読み込み
        logger.debug(f"設定ファイル '{CONFIG_FILE}' の読み込みを試行")
        res, dic = qRiKi_key.getCryptJson(config_file=CONFIG_FILE, auto_crypt=False)

        # 設定ファイルが存在しない場合、デフォルト値で初期化
        if not res:
            logger.warning(f"設定ファイル '{CONFIG_FILE}' が読み込めません。デフォルト値で初期化します")
            dic['_crypt_'] = 'none'
            dic['run_priority'] = self.run_priority
            dic['cgpt_secure_level'] = self.cgpt_secure_level
            dic['cgpt_addins_path'] = self.cgpt_addins_path
            dic['cgpt_functions_path'] = self.cgpt_functions_path
            dic['cgpt_engine_greeting'] = self.cgpt_engine_greeting
            dic['cgpt_engine_chat'] = self.cgpt_engine_chat
            dic['cgpt_engine_vision'] = self.cgpt_engine_vision
            dic['cgpt_engine_fileSearch'] = self.cgpt_engine_fileSearch
            dic['cgpt_engine_webSearch'] = self.cgpt_engine_webSearch
            dic['cgpt_engine_serial'] = self.cgpt_engine_serial
            dic['cgpt_engine_parallel'] = self.cgpt_engine_parallel
            dic['openai_api_type'] = self.openai_api_type
            dic['openai_organization'] = self.openai_organization
            dic['openai_key_id'] = self.openai_key_id
            dic['azure_endpoint'] = self.azure_endpoint
            dic['azure_version'] = self.azure_version
            dic['azure_key_id'] = self.azure_key_id
            dic['gemini_key_id'] = self.gemini_key_id
            dic['freeai_key_id'] = self.freeai_key_id
            dic['claude_key_id'] = self.claude_key_id
            dic['openrt_key_id'] = self.openrt_key_id
            dic['perplexity_key_id'] = self.perplexity_key_id
            dic['grok_key_id'] = self.grok_key_id
            dic['groq_key_id'] = self.groq_key_id
            dic['ollama_server'] = self.ollama_server
            dic['ollama_port'] = self.ollama_port
            logger.debug("デフォルト設定で設定ファイルを作成します")
            res = qRiKi_key.putCryptJson(config_file=CONFIG_FILE, put_dic=dic)
            if res:
                logger.info(f"設定ファイル '{CONFIG_FILE}' を作成しました")
                return True
            else:
                logger.error(f"設定ファイル '{CONFIG_FILE}' の作成に失敗しました")
                return False

        # 設定が読み込まれた場合の処理
        if res:
            logger.debug("設定ファイルから値を読み込みます")
            try:

                self.run_priority = dic['run_priority']
                self.cgpt_secure_level = dic['cgpt_secure_level']
                self.cgpt_addins_path = dic['cgpt_addins_path']
                self.cgpt_functions_path = dic['cgpt_functions_path']
                self.cgpt_engine_greeting = dic['cgpt_engine_greeting']
                self.cgpt_engine_chat = dic['cgpt_engine_chat']
                self.cgpt_engine_vision = dic['cgpt_engine_vision']
                self.cgpt_engine_fileSearch = dic['cgpt_engine_fileSearch']
                self.cgpt_engine_webSearch = dic['cgpt_engine_webSearch']
                self.cgpt_engine_serial = dic['cgpt_engine_serial']
                self.cgpt_engine_parallel = dic['cgpt_engine_parallel']
                self.openai_api_type = dic['openai_api_type']
                self.openai_organization = dic['openai_organization']
                self.openai_key_id = dic['openai_key_id']
                self.azure_endpoint = dic['azure_endpoint']
                self.azure_version = dic['azure_version']
                self.azure_key_id = dic['azure_key_id']
                self.gemini_key_id = dic['gemini_key_id']
                self.freeai_key_id = dic['freeai_key_id']
                self.claude_key_id = dic['claude_key_id']
                self.openrt_key_id = dic['openrt_key_id']
                self.perplexity_key_id = dic['perplexity_key_id']
                self.grok_key_id = dic['grok_key_id']
                self.groq_key_id = dic['groq_key_id']
                self.ollama_server = dic['ollama_server']
                self.ollama_port = dic['ollama_port']
                
                logger.debug("設定ファイルからの読み込みが完了しました")
                return True
            except Exception as e:
                logger.error(f"設定ファイルからの読み込みに失敗しました {e}")
                return False


if __name__ == '__main__':
    """
    メイン処理：テストコード
    """
    print()
    logger.info("【テスト開始】")

    # インスタンス化
    conf = _conf_class()

    # 初期化
    runMode = 'debug'
    logger.debug(f"runMode = {runMode} で初期化を実行します")
    conf.init(runMode=runMode)

    logger.info("【テスト終了】")
