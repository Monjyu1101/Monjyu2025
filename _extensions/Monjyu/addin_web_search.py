#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

import json
import importlib

webSearch = None
try:
    import      認証済_WEB検索してテキスト取得
    webSearch = 認証済_WEB検索してテキスト取得._class()
except:
    try:
        #loader = importlib.machinery.SourceFileLoader('認証済_WEB検索してテキスト取得.py', '_extensions/monjyu/認証済_WEB検索してテキスト取得.py')
        loader = importlib.machinery.SourceFileLoader('認証済_WEB検索してテキスト取得.py', '_extensions/function/認証済_WEB検索してテキスト取得.py')
        認証済_WEB検索してテキスト取得 = loader.load_module()
        webSearch  = 認証済_WEB検索してテキスト取得._class()
    except:
        print('★"認証済_WEB検索してテキスト取得"は利用できません！')



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "addin_web_search"
        self.func_ver  = "v0.20240831"
        self.func_auth = "jSSgYj7oFi0zU7X7ReIp+DvoM2d+kojYfdLoivAHG8g="

        self.function  = {
            "name": self.func_name,
            "description": \
"""
この機能は、Web検索,Google検索の指示があった場合のみ実行する。
この機能は、Google検索を実施し、リンク先のＵＲＬを取得するとともに、そのＵＲＬのページ内容をテキスト化して取得する
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "search_text": {
                        "type": "string",
                        "description": "検索文字列 例) 神戸 A-ZiP"
                    },
                },
                "required": ["runMode", "search_text"]
            }
        }

        # 初期設定
        self.runMode = 'assistant'
        self.func_reset()

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode  = None
        search_text = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode  = args_dic.get('runMode')
            search_text = args_dic.get('search_text')

        if (runMode is None) or (runMode == ''):
            runMode = self.runMode
        else:
            self.runMode = runMode

        # パラメータ不明
        if (search_text is None) or (search_text == ''):
            dic = {}
            dic['result'] = 'ng'
            json_dump = json.dumps(dic, ensure_ascii=False, )
            return json_dump

        # google 検索実行
        try:
            if (webSearch is not None):
                dic = {}
                dic['runMode']  = self.runMode
                dic['search_text'] = search_text
                json_dump = json.dumps(dic, ensure_ascii=False, )
                res_json = webSearch.func_proc(json_dump)
                args_dic = json.loads(res_json)
                return res_json
        except Exception as e:
            print(e)

        # エラー戻り
        dic = {}
        dic['result']      = 'ng'
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump



if __name__ == '__main__':

    ext = _class()

    print(ext.func_proc('{ ' \
                      + '"search_text" : "神戸 A-ZiP"' \
                      + ' }'))

