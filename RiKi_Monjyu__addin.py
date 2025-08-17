#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'addin'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)


import sys
import os
import time
import datetime
import codecs
import shutil
import glob
import importlib


# インターフェースのパス設定
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'

# 共通ルーチンのインポート
import _v7__qRiKi_key
qRiKi_key = _v7__qRiKi_key.qRiKi_key_class()

# アドイン管理クラス
class _addin_class:

    # 初期化
    def __init__(self):
        self.runMode = 'debug'
        self.addins_path = '_extensions/Monjyu/'
        self.secure_level = 'medium'
        self.organization_auth = ''
        self.addin_modules = {}

        # 各アドイン機能の初期化
        self.addin_directive = None
        self.addin_pdf = None
        self.addin_url = None
        self.addin_ocr = None
        self.addin_autoSandbox = None

    # 初期化メソッド
    def init(self, runMode='debug', qLog_fn='',
             addins_path='_extensions/Monjyu/',
             secure_level='medium', 
             organization_auth=''):
        self.runMode = runMode
        
        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'

        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug('init')

        # パラメータ設定
        self.addins_path = addins_path
        self.secure_level = secure_level
        self.organization_auth = organization_auth
        self.addin_modules = {}

    # アドインのロード
    def addins_load(self):
        res_load_all = True
        res_load_msg = ''
        self.addins_unload()
        path = self.addins_path
        path_files = glob.glob(path + '*.py')
        path_files.sort()
        
        if len(path_files) > 0:
            for f in path_files:
                base_name = os.path.basename(f)
                if  base_name[:4]   != '_v6_' \
                and base_name[:4]   != '_v7_' \
                and base_name[-10:] != '_pyinit.py' \
                and base_name[-10:] != '_python.py':
                    try:
                        # モジュールのロード
                        file_name = os.path.splitext(base_name)[0]
                        logger.info('Addins    Loading ... "' + file_name + '" ...')
                        loader = importlib.machinery.SourceFileLoader(file_name, f)
                        addin_script = file_name
                        addin_module = loader.load_module()
                        addin_onoff = 'off'
                        addin_class = addin_module._class()
                        
                        # クラスの情報取得
                        addin_version = addin_class.version
                        addin_func_name = addin_class.func_name
                        addin_func_ver = addin_class.func_ver
                        addin_func_auth = addin_class.func_auth
                        addin_function = addin_class.function
                        addin_func_reset = addin_class.func_reset
                        addin_func_proc = addin_class.func_proc
                        # コード認証
                        auth = False
                        if self.secure_level in ['low', 'medium']:
                            if addin_func_auth == '':
                                auth = '1' # 注意
                                if self.secure_level != 'low':
                                    res_load_msg += '"' + addin_script + '"が認証されていません。(Warning!)' + '\n'
                            else:
                                auth = qRiKi_key.decryptText(text=addin_func_auth)
                                if auth != addin_func_name + '-' + addin_func_ver and (self.organization_auth != '' and auth != self.organization_auth):
                                    if self.secure_level == 'low':
                                        auth = '1' # 注意
                                        res_load_msg += '"' + addin_script + '"は改ざんされたコードです。(Warning!)' + '\n'
                                    else:
                                        res_load_msg += '"' + addin_script + '"は改ざんされたコードです。Loadingはキャンセルされます。' + '\n'
                                        res_load_all = False
                                else:
                                    auth = '2' # 認証
                                    addin_onoff = 'on'
                        else:
                            if addin_func_auth == '':
                                res_load_msg += '"' + addin_script + '"が認証されていません。Loadingはキャンセルされます。' + '\n'
                                res_load_all = False
                            else:
                                auth = qRiKi_key.decryptText(text=addin_func_auth)
                                if auth != addin_func_name + '-' + addin_func_ver and (self.organization_auth != '' and auth != self.organization_auth):
                                    res_load_msg += '"' + addin_script + '"は改ざんされたコードです。Loadingはキャンセルされます。' + '\n'
                                    res_load_all = False
                                else:
                                    auth = '2' # 認証
                                    addin_onoff = 'on'
                        # モジュールの登録
                        if auth != False:
                            module_dic = {
                                'script': addin_script,
                                'module': addin_module,
                                'onoff': addin_onoff,
                                'class': addin_class,
                                'func_name': addin_func_name,
                                'func_ver': addin_func_ver,
                                'func_auth': addin_func_auth,
                                'function': addin_function,
                                'func_reset': addin_func_reset,
                                'func_proc': addin_func_proc
                            }
                            self.addin_modules[addin_func_name] = module_dic
                            logger.info('Addins    Loading ... "' + addin_script + '" (' + addin_class.func_name + ') ' + addin_onoff + '. ')
                            # 特定アドインのプロシージャを設定
                            if addin_script == 'addin_directive':
                                self.addin_directive = addin_func_proc
                            elif addin_script == 'addin_pdf':
                                self.addin_pdf = addin_func_proc
                            elif addin_script == 'addin_url':
                                self.addin_url = addin_func_proc
                            elif addin_script == 'addin_ocr':
                                self.addin_ocr = addin_func_proc
                            elif addin_script == 'addin_autoSandbox':
                                self.addin_autoSandbox = addin_func_proc
                    except Exception as e:
                        print(e)
        return res_load_all, res_load_msg

    # アドインのリセット
    def addins_reset(self):
        res_reset_all = True
        res_reset_msg = ''
        
        # アドインのリセット処理
        for module_dic in self.addin_modules.values():
            addin_script = module_dic['script']
            addin_func_name = module_dic['func_name']
            addin_func_reset = module_dic['func_reset']
            try:
                res = addin_func_reset()
                logger.info('Addins    Reset   ... "' + addin_script + '" (' + addin_func_name + ') OK. ')
            except:
                res = False
            if not res:
                module_dic['onoff'] = 'off'
                res_reset_all = False
                res_reset_msg += addin_func_name + 'のリセット中にエラーがありました。' + '\n'
        return res_reset_all, res_reset_msg

    # アドインのアンロード
    def addins_unload(self):
        res_unload_all = True
        res_unload_msg = ''
        # アドインのアンロード処理
        for module_dic in self.addin_modules.values():
            addin_script = module_dic['script']
            addin_func_name = module_dic['func_name']
            addin_module = module_dic['module']
            addin_class = module_dic['class']
            try:
                # クラスとモジュールの削除
                del addin_class
                del addin_module
                logger.info('Addins    Unload  ... "' + addin_script + '" (' + addin_func_name + ') OK. ')
            except:
                res_unload_all = False
                res_unload_msg += addin_func_name + 'の開放中にエラーがありました。' + '\n'
        self.addin_modules = {}
        return res_unload_all, res_unload_msg



# メイン処理
if __name__ == '__main__':
    print()
    addin = _addin_class()

    # addin 初期化
    runMode = 'debug'
    addin.init(qLog_fn='', runMode=runMode,
               addins_path='_extensions/Monjyu/', secure_level='low',
               organization_auth='')

    # アドインのロード
    res, msg = addin.addins_load()
    if not res or msg:
        print(msg)
        print()

    # アドインのリセット
    res, msg = addin.addins_reset()
    if not res or msg:
        print(msg)
        print()

    # アドインのアンロード
    res, msg = addin.addins_unload()
    if not res or msg:
        print(msg)
        print()

    time.sleep(10)


