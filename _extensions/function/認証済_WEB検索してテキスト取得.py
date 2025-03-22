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

import requests
# SSLエラーを無視するための処理
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

import ssl
# SSLエラーを無視するための処理
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

from bs4 import BeautifulSoup
from urllib.parse import parse_qs  # 追加

# 検索除外アドレス
NOT_SEARCH = ['google.com',
              'google.co.jp',
              'en-gage.net',
              'hnavi.co.jp',
              'ipros.jp',
              'ikazuchi.biz',
              'mynavi.jp',
              'gbiz.go.jp',
              ]

import importlib

url2text = None
try:
    import     認証済_URLからテキスト取得
    url2text = 認証済_URLからテキスト取得._class()
except:
    try:
        loader = importlib.machinery.SourceFileLoader('認証済_URLからテキスト取得.py', '_extensions/function/認証済_URLからテキスト取得.py')
        認証済_URLからテキスト取得 = loader.load_module()
        url2text  = 認証済_URLからテキスト取得._class()
    except:
        print('★認証済_URLからテキスト取得は利用できません！')

class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "webSearch_to_text"
        self.func_ver  = "v0.20240831"
        self.func_auth = "IQXBL0+5HMQTAktHpmhzeW9Od94FHwHEnXthFU+WO78="

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
        url_links = {}
        try:
            url_path = "https://google.com/search?q=" + search_text

            html = requests.get(url_path, timeout=(5,15), verify=False)
            html_content   = html.content
            html_encording = html.encoding
            # html.parser, html5lib, lxml,
            soup = BeautifulSoup(html_content, 'html.parser', from_encoding=html_encording)

            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.startswith('/url?'):  # google検索結果のリンクは/url?から始まる
                    # クエリパラメータを解析して、qパラメータの値を取得する
                    query_params = parse_qs(href.replace('/url?', ''))
                    if 'q' in query_params:
                        # 抽出したリンクの文字列の先頭がhttp://またはhttps://で始まる場合のみ追加
                        link_url = query_params['q'][0]
                        if link_url.startswith('http://') or link_url.startswith('https://'):
                            hit = False
                            for not_search in NOT_SEARCH:
                                if (link_url.find(not_search) >= 0): # 除外確認
                                    hit = True
                                    break
                            if hit == False:
                                url_links[link_url] = link_url
        except Exception as e:
            print(e)

        # 内容取得
        res_path = ''
        res_text = ''
        for url_link in url_links.keys():

            # url2text
            try:
                if (url2text is not None):
                    dic = {}
                    dic['runMode']  = self.runMode
                    dic['url_path'] = url_link
                    json_dump = json.dumps(dic, ensure_ascii=False, )
                    res_json = url2text.func_proc(json_dump)
                    args_dic = json.loads(res_json)
                    text = args_dic.get('result_text')
                    if (text is not None):
                        if (text != '') and (text != '!'):
                            res_path += url_link + '\n'
                            res_text += "''' " + url_link + '\n'
                            res_text += text.rstrip() + '\n'
                            res_text += "''' \n"
                else:
                    print('★addin_urlは利用できません！')
                    print(url_path)
            except Exception as e:
                print(e)

        #print(res_path)
        #print(res_text)

        # 戻り
        dic = {}
        if (res_text != ''):
            dic['result']      = 'ok'
            dic['result_text'] = res_text
            dic['result_path'] = res_path
        else:
            dic['result']      = 'ng'
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump



if __name__ == '__main__':

    ext = _class()

    print(ext.func_proc('{ ' \
                      + '"search_text" : "神戸 A-ZiP"' \
                      + ' }'))

