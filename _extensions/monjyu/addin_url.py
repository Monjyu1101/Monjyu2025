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

url2text = None
try:
    import     認証済_URLからテキスト取得
    url2text = 認証済_URLからテキスト取得._class()
except:
    try:
        #loader = importlib.machinery.SourceFileLoader('認証済_URLからテキスト取得.py', '_extensions/monjyu/認証済_URLからテキスト取得.py')
        loader = importlib.machinery.SourceFileLoader('認証済_URLからテキスト取得.py', '_extensions/function/認証済_URLからテキスト取得.py')
        認証済_URLからテキスト取得 = loader.load_module()
        url2text  = 認証済_URLからテキスト取得._class()
    except:
        print('★"認証済_URLからテキスト取得"は利用できません！')



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "addin_url_to_text"
        self.func_ver  = "v0.20240831"
        self.func_auth = "UJAwyZNPM/pCQSZejbQ+5pSJ2RU5RrSop45IKCJXZkQ="

        self.function  = {
            "name": self.func_name,
            "description": \
"""
この機能は、ホームページのスクレイピング指示があった場合のみ実行する。
この機能は、ホームページアドレス(url_path)の内容をテキスト化して取得する
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "url_path": {
                        "type": "string",
                        "description": "https://www.google.co.jp/"
                    },
                },
                "required": ["runMode", "url_path"]
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
        url_path = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode  = args_dic.get('runMode')
            url_path = args_dic.get('url_path')

        if (runMode is None) or (runMode == ''):
            runMode = self.runMode
        else:
            self.runMode = runMode

        # パラメータ不明
        if (url_path is None) or (url_path == ''):
            dic = {}
            dic['result'] = 'ng'
            json_dump = json.dumps(dic, ensure_ascii=False, )
            return json_dump

        # url to text 実行
        try:
            if (url2text is not None):
                dic = {}
                dic['runMode']  = self.runMode
                dic['url_path'] = url_path
                json_dump = json.dumps(dic, ensure_ascii=False, )
                res_json = url2text.func_proc(json_dump)
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
                      + '"url_path" : "https://www.google.co.jp/"' \
                      + ' }'))

