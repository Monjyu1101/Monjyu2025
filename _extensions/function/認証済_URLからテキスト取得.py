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
from bs4 import BeautifulSoup

# 通常のリクエストでhtml取得

import requests
# SSLエラーを無視するための処理
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# seleniumでhtml取得

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "url_to_text"
        self.func_ver  = "v0.20240831"
        self.func_auth = "NO641knm6MCDTApklYb1LD6/HU9/aQcP808aO4XiKFc="

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
    
    def get_request_html(self, url_path='https://google.co.jp',):
        html_text = None        
        try:
            html_text = requests.get(url_path, timeout=(5,15), verify=False)
        except Exception as e:
            print(e)
        return html_text

    def get_selenium_html(self, url_path='https://ncode.syosetu.com/n4830bu/1/', narou_wait=False, ):
        html_text = None
        try:
            # Firefoxのオプションを設定
            firefox_options = Options()
            # ヘッドレスモードを有効にする
            firefox_options.add_argument("--headless")
            # WebDriverの設定
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
            # URLを開く
            driver.get(url_path)
            # なろう待機
            if narou_wait == True:
                # c-announce-box内のc-announceクラスの要素が表示されるまで待機
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".c-announce-box .c-announce"))
                )
            # ページのHTMLを取得
            html_text = driver.page_source
        except Exception as e:
            print(e)
        finally:
            driver.quit()
        return html_text

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
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # 処理
        res_okng = 'ng'
        res_text = None

        if (url_path is None) or (url_path == ''):
            pass

        else:

            text = ''
            try:

                # なろうページ？
                narou_pages = ''
                if (url_path[:26] == 'https://ncode.syosetu.com/'):
                    page_path = url_path[26:]
                    page_hit  = page_path.find('/')
                    # 最初の"/"
                    if (page_hit >= 0):
                        page_str = page_path[page_hit:]
                        try:
                            # ページ番号
                            page_n = int(page_str.replace('/',''))
                            narou_pages = '[なろう] ' + page_path[:page_hit] + ' ' + str(page_n)
                        except:
                            pass

                # -----------
                # 通常の手法
                # -----------
                if (text == '') and (narou_pages == ''):
                    html_text = self.get_request_html(url_path=url_path, )
                    html_content   = html_text.content
                    html_encording = html_text.encoding
                    # html.parser, html5lib, lxml,
                    soup = BeautifulSoup(html_content, 'html.parser', from_encoding=html_encording)
                    try:
                        for script in soup(["script", "style"]):
                            script.decompose()
                        t = soup.get_text()
                        for line in t.splitlines():
                            if (line.strip() != ''):
                                text += line.strip() + '\n'
                    except:
                        pass

                # -----------
                # なろう
                # -----------
                if (narou_pages != ''):
                    html_text = self.get_selenium_html(url_path=url_path, narou_wait=True, )
                    soup = BeautifulSoup(html_text, 'html.parser')

                    # タイトル
                    title = ''
                    try:
                        title = soup.select_one('.c-announce-box .c-announce span').text.strip()
                    except:
                        try:
                            title = soup.find('p', class_='chapter_title').get_text()
                        except:
                            try:
                                title = soup.find('p', class_='margin_r20').get_text()
                            except:
                                pass
                    if (title != ''):
                        text += 'タイトル：' + title + '\n'

                    # サブタイトル
                    sub_title = ''
                    try:
                        sub_title = soup.select_one('.p-novel__title').text.strip()
                    except:
                        try:
                            sub_title = soup.find('p', class_='novel_subtitle').get_text()
                        except:
                            pass
                    if (sub_title != ''):
                        text += sub_title + '\n'

                    # 本文
                    for l in range(1, 9999):
                        p_list = soup.find_all('p', id='L' + str(l))
                        if (len(p_list) == 0):
                            break
                        if (l == 1):
                            text += '本文：' + '\n'
                        for p in p_list:
                            text += p.get_text() + '\n'

                # -----------
                # 別の手法
                # -----------
                if (text == ''):
                    html_text = self.get_selenium_html(url_path=url_path, narou_wait=False, )
                    soup = BeautifulSoup(html_text, 'html.parser')

                    try:
                        t = soup.get_text()
                        for line in t.splitlines():
                            if (line.strip() != ''):
                                text += line.strip() + '\n'
                    except:
                        pass

            except Exception as e:
                print(e)
                text = '!'

            # 文書成形
            res_text = self.text_replace(text=text, )

        # 戻り
        dic = {}
        if (res_text is not None):
            if (res_text != ''):
                dic['result']      = 'ok'
                dic['result_text'] = res_text
            else:
                dic['result']      = 'ng'
        else:
            dic['result']      = 'ng'
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump



    def text_replace(self, text='', ):
        if (text.strip() == ''):
            return ''

        text = text.replace('\r', '')

        text = text.replace('。', '。\n')
        text = text.replace('?', '?\n')
        text = text.replace('？', '?\n')
        text = text.replace('!', '!\n')
        text = text.replace('！', '!\n')
        text = text.replace('。\n」','。」')
        text = text.replace('。\n"' ,'。"')
        text = text.replace("。\n'" ,"。'")
        text = text.replace('?\n」','?」')
        text = text.replace('?\n"' ,'?"')
        text = text.replace("?\n'" ,"?'")
        text = text.replace('!\n」','!」')
        text = text.replace('!\n"' ,'!"')
        text = text.replace("!\n'" ,"!'")
        text = text.replace("!\n=" ,"!=")
        text = text.replace("!\n--" ,"!--")

        text = text.replace('\n \n ' ,'\n')
        text = text.replace('\n \n' ,'\n')

        hit = True
        while (hit == True):
            if (text.find('\n\n')>0):
                hit = True
                text = text.replace('\n\n', '\n')
            else:
                hit = False

        return text.strip()



if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ "runMode" : "assistant" }'))

    print(ext.func_proc('{ ' \
                      + '"url_path" : "https://www.google.co.jp/"' \
                      + ' }'))

    print(ext.func_proc('{ ' \
                      + '"url_path" : "https://ncode.syosetu.com/n4830bu/1/"' \
                      + ' }'))
