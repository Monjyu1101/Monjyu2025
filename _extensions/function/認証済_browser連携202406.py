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
import os
import time

from selenium.webdriver import Edge
from selenium.webdriver import Chrome
from selenium.webdriver import Firefox
from selenium.webdriver import Safari
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



class browser_class:
    def __init__(self, ):
        self.run_list = []

    def __del__(self, ):
        for run_dic in self.run_list:
            run_engine = run_dic['engine']
            try:
                run_engine.quit()
                run_engine = None
            except:
                pass

    def browser_open(self, url='https://www.google.com/', browser='edge', full_size='yes', ):

        # 起動済？
        engine = None
        for run_dic in self.run_list:
            run_engine = run_dic['engine']
            current_url = run_engine.current_url
            if (current_url == url):
                engine = run_engine
                break

        # 新たな起動
        if (engine is None):
            try:
                # ブラウザ
                if (browser != None):
                    browser = browser.lower()
                if (os.name == 'nt'):
                    if   (browser == 'chrome'):
                        engine = Chrome()
                    elif (browser == 'firefox'):
                        engine = Firefox()
                    elif (browser == 'safari'):
                        engine = Safari()
                    else:
                        engine = Edge()
                else:
                    if   (browser == 'safari'):
                        engine = Safari()
                    elif (browser == 'edge'):
                        engine = Edge()
                    elif (browser == 'firefox'):
                        engine = Firefox()
                    else:
                        engine = Chrome()

                run_dic = {}
                run_dic['engine'] = engine
                self.run_list.append(run_dic)

                # 最大化
                if (full_size != 'no'):
                    engine.maximize_window()

            except Exception as e:
                print(e)

        # WEB ページ開く
        if (engine is not None):
 
            try:
                current_url = engine.current_url
                if (current_url != url):

                    # ページ更新
                    engine.get(url)

                    # 全要素取得待機
                    engine_wait = WebDriverWait(engine, 10)
                    element = engine_wait.until(EC.visibility_of_all_elements_located)

                return True

            except Exception as e:
                print(e)

        return False



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "execute_open_web_from_url"
        self.func_ver  = "v0.20230820"
        self.func_auth = "WCHTl5lwkJCIhIVDzAYvEr3JeWl9JYRNz5uKLD5txXacgVSLf0GCFF5aPYtFON1u"
        self.function  = {
            "name": self.func_name,
            "description": \
"""
この機能は、操作するurlの指示があった場合に実行する。
ユーザーから指定されたブラウザでurlのウェブページを表示できる。
この機能で表示されたページを閉じることもできる。
この機能には、AIエージェント能力は無い。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "show_or_hide": {
                        "type": "string",
                        "description": "表示または消去の指定 show,hide (例) show"
                    },
                    "useBrowser": {
                        "type": "string",
                        "description": "利用ブラウザーの選択 edge,chrome,firefox,safari (例) edge"
                    },
                    "url": {
                        "type": "string",
                        "description": "ウェブページのurl (例) https://openai.com/blog/chatgpt"
                    },
                    "full_size": {
                        "type": "string",
                        "description": "全画面表示選択 yes,no (例) yes"
                    },
                },
                "required": ["show_or_hide"]
            }
        }

        self.browser = browser_class()
        self.func_reset()

    def func_reset(self, ):
        del self.browser
        self.browser = browser_class()
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        show_or_hide = None
        useBrowser   = None
        url          = None
        full_size    = None
        if (json_kwargs != None):
            args_dic = json.loads(json_kwargs)
            show_or_hide = args_dic.get('show_or_hide')
            useBrowser   = args_dic.get('useBrowser')
            url          = args_dic.get('url')
            full_size    = args_dic.get('full_size')

        # ブラウザ表示
        if (show_or_hide == 'show'):

            res = self.browser.browser_open(url=url, browser=useBrowser, full_size=full_size, )
            if (res == True):
                dic = {}
                dic['result'] = "ok" 
                dic['result_message'] = "ブラウザ表示しました" 
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print('  --> ', json_dump)
                return json_dump
            else:
                dic = {}
                dic['result'] = "ng" 
                dic['error_message'] = "ブラウザ表示に失敗しました" 
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print('  --> ', json_dump)
                return json_dump

        # ブラウザ消去
        if (show_or_hide == 'hide'):

            # リセット
            self.func_reset()

            dic = {}
            dic['result'] = "ok" 
            dic['result_message'] = "ブラウザ表示を消去しました" 
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump


if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ ' \
                      + '"show_or_hide" : "show",' \
                      + '"useBrowser" : "edge",' \
                      + '"url" : "https://openai.com/index/chatgpt/"' \
                      + ' }'))
    time.sleep(10.00)

    print(ext.func_proc('{ ' \
                      + '"show_or_hide" : "show",' \
                      + '"useBrowser" : "edge",' \
                      + '"url" : "https://openai.com/index/chatgpt/"' \
                      + ' }'))
    time.sleep(10.00)

    print(ext.func_proc('{ ' \
                      + '"show_or_hide" : "hide"' \
                      + ' }'))
    time.sleep(2.00)

