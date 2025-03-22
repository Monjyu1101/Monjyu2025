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
import codecs

# インターフェース
qIO_func2py       = 'temp/web操作Agent_func2py.txt'



def io_text_write(filename='', text='', ):
    try:
        w = codecs.open(filename, 'w', 'utf-8')
        w.write(text)
        w.close()
        w = None
        return True
    except:
        pass
    return False



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "operate_notebookLM"
        self.func_ver  = "v0.20250113"
        self.func_auth = "KhaudOdG4POdafGghCZSwvm5R+QA+5jZtRGV19HYg0k="
        self.function  = {
            "name": self.func_name,
            "description": \
"""
この機能は、NotebookLM (ノートブックLM) を操作する機能です。
この機能から、自律的にウェブ操作が可能なAIエージェント Web-Operator(ウェブオペレーター: web_operation_agent ) に操作指示して実行します。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "operate_text": {
                            "type": "string",
                            "description": "操作内容 (例) 資料の重要な内容を要約"
                    },
                },
                "required": ["operate_text"]
            }
        }

        res = self.func_reset()

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        operate_text = None
        if (json_kwargs != None):
            args_dic = json.loads(json_kwargs)
            operate_text = args_dic.get('operate_text')

        # 操作内容生成
        req_text = ''
        if (operate_text != ''):
            req_text += "NotebookLMの操作を実行してください。\n"
            req_text += "URLは、'https://notebooklm.google.com/notebook/5fdac0ad-8d9b-4d56-8ff4-7086258ce476'にアクセスしてください。\n"
            req_text += "画面下部の入力欄に以下を入力してください。\n"
            req_text += "\n" + operate_text + "\n"

        # 操作
        res_okng = 'ng'
        res_msg  = "NotebookLMの操作が失敗しました。" 
        if (req_text != ''):
            req_dic = {}
            req_dic['useBrowser']   = 'chrome'
            req_dic['request_text'] = req_text
            req_dump = json.dumps(req_dic, ensure_ascii=False, )
            res = io_text_write(filename=qIO_func2py, text=req_dump, )
            if (res == True):
                res_okng = 'ok'
                res_msg  = "AIエージェント Web-Operator(ウェブオペレーター) に、NotebookLMの操作を依頼しました。\n" 
                res_msg += "しばらくお待ちください。\n"

        # JSON化
        dic = {}
        dic['result'] = res_okng
        if (res_msg is not None):
            dic['message'] = res_msg
        json_dump = json.dumps(dic, ensure_ascii=False, )
        return json_dump



if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ "operate_text" : "資料の重要な内容を要約" }'))


