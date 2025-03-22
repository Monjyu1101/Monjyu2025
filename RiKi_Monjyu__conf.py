#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/konsan1101
# Thank you for keeping the rules.
# ------------------------------------------------

# RiKi_Monjyu__conf.py

import sys
import os
import time
import datetime
import codecs
import glob
import shutil

# 一時ファイル保存用パス
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'

# ログクラスのインポートとインスタンス生成
import _v6__qLog
qLog = _v6__qLog.qLog_class()

# 共通キー管理クラスのインポートとインスタンス生成
import _v6__qRiKi_key
qRiKi_key = _v6__qRiKi_key.qRiKi_key_class()

# 設定ファイルパス
config_file = 'RiKi_Monjyu_key.json'

class _conf_class:
    def __init__(self):

        # 初期設定
        self.runMode = 'debug'
        self.run_priority = 'auto'

        # 設定項目
        self.cgpt_secure_level = 'medium'
        self.cgpt_addins_path = '_extensions/monjyu/'
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

        # 初期化処理
        self.proc_name = 'conf'
        self.proc_id = '{0:10s}'.format(self.proc_name).replace(' ', '_')

        # ログディレクトリの確認・作成
        if not os.path.isdir(qPath_log):
            os.makedirs(qPath_log)

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        qLog.init(mode='logger', filename=qLog_fn)
        qLog.log('info', self.proc_id, 'init')

        # 設定ファイルの読み込み
        res, dic = qRiKi_key.getCryptJson(config_file=config_file, auto_crypt=False)

        # 設定ファイルが存在しない場合、デフォルト値で初期化
        if not res:
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
            res = qRiKi_key.putCryptJson(config_file=config_file, put_dic=dic)

        # 設定が読み込まれた場合の処理
        if res:
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
        self.runMode = runMode

        return True



if __name__ == '__main__':
    conf = _conf_class()

    # conf 初期化
    runMode = 'debug'
    conf.init(qLog_fn='', runMode=runMode)

    # テスト出力
    print(conf.runMode)


