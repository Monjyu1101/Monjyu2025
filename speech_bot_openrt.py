#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/konsan1101
# Thank you for keeping the rules.
# ------------------------------------------------

import sys
import os
import time
import datetime
import codecs
import shutil

import json
import queue
import base64

import requests



# openrt チャットボット
import openai

import speech_bot_openrt_key  as openrt_key



# base64 encode
def base64_encode(file_path):
    with open(file_path, "rb") as input_file:
        return base64.b64encode(input_file.read()).decode('utf-8')



class _openrtAPI:

    def __init__(self, ):
        self.log_queue              = None
        self.bot_auth               = None

        self.temperature            = 0.8

        self.openrt_api_type        = 'openrt'
        self.openrt_default_gpt     = 'auto'
        self.openrt_default_class   = 'auto'
        self.openrt_auto_continue   = 3
        self.openrt_max_step        = 10
        self.openrt_max_session     = 5
        self.openrt_max_wait_sec    = 120
       
        self.openrt_key_id          = None

        self.openrt_a_enable        = False
        self.openrt_a_nick_name     = ''
        self.openrt_a_model         = None
        self.openrt_a_token         = 0
        self.openrt_a_use_tools     = 'no'

        self.openrt_b_enable        = False
        self.openrt_b_nick_name     = ''
        self.openrt_b_model         = None
        self.openrt_b_token         = 0
        self.openrt_b_use_tools     = 'no'

        self.openrt_v_enable        = False
        self.openrt_v_nick_name     = ''
        self.openrt_v_model         = None
        self.openrt_v_token         = 0
        self.openrt_v_use_tools     = 'no'

        self.openrt_x_enable        = False
        self.openrt_x_nick_name     = ''
        self.openrt_x_model         = None
        self.openrt_x_token         = 0
        self.openrt_x_use_tools     = 'no'

        self.models                 = {}
        self.history                = []

        self.seq                    = 0
        self.reset()

    def init(self, log_queue=None, ):
        self.log_queue = log_queue
        return True

    def reset(self, ):
        self.history                = []
        return True

    def print(self, session_id='admin', text='', ):
        print(text, flush=True)
        if (session_id == 'admin') and (self.log_queue is not None):
            try:
                self.log_queue.put(['chatBot', text + '\n'])
            except:
                pass

    def stream(self, session_id='admin', text='', ):
        print(text, end='', flush=True)
        if (session_id == 'admin') and (self.log_queue is not None):
            try:
                self.log_queue.put(['chatBot', text])
            except:
                pass

    def authenticate(self, api,
                     openrt_api_type,
                     openrt_default_gpt, openrt_default_class,
                     openrt_auto_continue,
                     openrt_max_step, openrt_max_session,
                     openrt_max_wait_sec,

                     openrt_key_id,

                     openrt_a_nick_name, openrt_a_model, openrt_a_token, 
                     openrt_a_use_tools, 
                     openrt_b_nick_name, openrt_b_model, openrt_b_token, 
                     openrt_b_use_tools, 
                     openrt_v_nick_name, openrt_v_model, openrt_v_token, 
                     openrt_v_use_tools, 
                     openrt_x_nick_name, openrt_x_model, openrt_x_token, 
                     openrt_x_use_tools, 
                    ):

        # 認証
        self.bot_auth                   = None
        self.openrt_key_id              = openrt_key_id

        self.client = None
        if (openrt_key_id[:1] == '<'):
            return False
        try:
            self.client = openai.OpenAI(
                api_key=openrt_key_id,
                base_url="https://openrouter.ai/api/v1",
            )
        except Exception as e:
            print(e)
            return False

        # 設定
        self.openrt_default_gpt         = openrt_default_gpt
        self.openrt_default_class       = openrt_default_class
        if (str(openrt_auto_continue) not in ['', 'auto']):
            self.openrt_auto_continue   = int(openrt_auto_continue)
        if (str(openrt_max_step)      not in ['', 'auto']):
            self.openrt_max_step        = int(openrt_max_step)
        if (str(openrt_max_session)   not in ['', 'auto']):
            self.openrt_max_session     = int(openrt_max_session)
        if (str(openrt_max_wait_sec)  not in ['', 'auto']):
            self.openrt_max_wait_sec    = int(openrt_max_wait_sec)

        # モデル取得
        self.models                     = {}
        self.get_models()

        #ymd = datetime.date.today().strftime('%Y/%m/%d')
        ymd = 'default'

        # openrt チャットボット
        if (openrt_a_nick_name != ''):
            self.openrt_a_enable        = False
            self.openrt_a_nick_name     = openrt_a_nick_name
            self.openrt_a_model         = openrt_a_model
            self.openrt_a_token         = int(openrt_a_token)
            self.openrt_a_use_tools     = openrt_a_use_tools
            if (openrt_a_model not in self.models):
                self.models[openrt_a_model] = {"id": openrt_a_model, "token": str(openrt_a_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[openrt_a_model]['date'] = ymd

        if (openrt_b_nick_name != ''):
            self.openrt_b_enable        = False
            self.openrt_b_nick_name     = openrt_b_nick_name
            self.openrt_b_model         = openrt_b_model
            self.openrt_b_token         = int(openrt_b_token)
            self.openrt_b_use_tools     = openrt_b_use_tools
            if (openrt_b_model not in self.models):
                self.models[openrt_b_model] = {"id": openrt_b_model, "token": str(openrt_b_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[openrt_b_model]['date'] = ymd

        if (openrt_v_nick_name != ''):
            self.openrt_v_enable        = False
            self.openrt_v_nick_name     = openrt_v_nick_name
            self.openrt_v_model         = openrt_v_model
            self.openrt_v_token         = int(openrt_v_token)
            self.openrt_v_use_tools     = openrt_v_use_tools
            if (openrt_v_model not in self.models):
                self.models[openrt_v_model] = {"id": openrt_v_model, "token": str(openrt_v_token), "modality": "text+image?", "date": ymd, }
            #else:
            #    self.models[openrt_v_model]['date'] = ymd
            #    self.models[openrt_v_model]['modality'] = "text+image?"

        if (openrt_x_nick_name != ''):
            self.openrt_x_enable        = False
            self.openrt_x_nick_name     = openrt_x_nick_name
            self.openrt_x_model         = openrt_x_model
            self.openrt_x_token         = int(openrt_x_token)
            self.openrt_x_use_tools     = openrt_x_use_tools
            if (openrt_x_model not in self.models):
                self.models[openrt_x_model] = {"id": openrt_x_model, "token": str(openrt_x_token), "modality": "text+image?", "date": ymd, }
            #else:
            #    self.models[openrt_x_model]['date'] = ymd

        # モデル
        hit = False
        if (self.openrt_a_model != ''):
            self.openrt_a_enable = True
            hit = True
        if (self.openrt_b_model != ''):
            self.openrt_b_enable = True
            hit = True
        if (self.openrt_v_model != ''):
            self.openrt_v_enable = True
            hit = True
        if (self.openrt_x_model != ''):
            self.openrt_x_enable = True
            hit = True

        if (hit == True):
            self.bot_auth = True
            return True
        else:
            return False

    def get_models(self, ):
        try:
            headers = {
                "Authorization": f"Bearer {self.openrt_key_id}"
            }
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)

            if response.status_code == 200:
                self.models = {}
                models = response.json()
                for model in models['data']:
                    key = model["id"]
                    token = str(model["context_length"])
                    modality = model["architecture"]["modality"]
                    unix_timestamp = model["created"]
                    ymd = datetime.datetime.fromtimestamp(unix_timestamp).strftime("%Y/%m/%d")
                    #print(key, token, modality, )
                    self.models[key] = {"id":key, "token":token, "modality":modality, "date": ymd, }
        except Exception as e:
            print(e)
            return False
        return True

    def set_models(self, max_wait_sec='',
                         a_model='', a_use_tools='',
                         b_model='', b_use_tools='',
                         v_model='', v_use_tools='',
                         x_model='', x_use_tools='', ):
        try:
            if (max_wait_sec not in ['', 'auto']):
                if (str(max_wait_sec) != str(self.openrt_max_wait_sec)):
                    self.openrt_max_wait_sec = int(max_wait_sec)
            if (a_model != ''):
                if (a_model != self.openrt_a_model) and (a_model in self.models):
                    self.openrt_a_enable = True
                    self.openrt_a_model = a_model
                    self.openrt_a_token = int(self.models[a_model]['token'])
            if (a_use_tools != ''):
                self.openrt_a_use_tools = a_use_tools
            if (b_model != ''):
                if (b_model != self.openrt_b_model) and (b_model in self.models):
                    self.openrt_b_enable = True
                    self.openrt_b_model = b_model
                    self.openrt_b_token = int(self.models[b_model]['token'])
            if (b_use_tools != ''):
                self.openrt_b_use_tools = b_use_tools
            if (v_model != ''):
                if (v_model != self.openrt_v_model) and (v_model in self.models):
                    self.openrt_v_enable = True
                    self.openrt_v_model = v_model
                    self.openrt_v_token = int(self.models[v_model]['token'])
            if (v_use_tools != ''):
                self.openrt_v_use_tools = v_use_tools
            if (x_model != ''):
                if (x_model != self.openrt_x_model) and (x_model in self.models):
                    self.openrt_x_enable = True
                    self.openrt_x_model = x_model
                    self.openrt_x_token = int(self.models[x_model]['token'])
            if (x_use_tools != ''):
                self.openrt_x_use_tools = x_use_tools
        except Exception as e:
            print(e)
            return False
        return True

    def history_add(self, history=[], sysText=None, reqText=None, inpText='こんにちは', ):
        res_history = history

        # sysText, reqText, inpText -> history
        if (sysText is not None) and (sysText.strip() != ''):
            if (len(res_history) > 0):
                if (sysText.strip() != res_history[0]['content'].strip()):
                    res_history = []
            if (len(res_history) == 0):
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': 'system', 'name': '', 'content': sysText.strip() }
                res_history.append(dic)
        if (reqText is not None) and (reqText.strip() != ''):
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': reqText.strip() }
            res_history.append(dic)
        if (inpText.strip() != ''):
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': inpText.rstrip() }
            res_history.append(dic)

        return res_history

    def history_zip1(self, history=[]):
        res_history = history

        if (len(res_history) > 0):
            for h in reversed(range(len(res_history))):
                tm = res_history[h]['time']
                if ((time.time() - tm) > 900): #15分で忘れてもらう
                    if (h != 0):
                        del res_history[h]
                    else:
                        if (res_history[0]['role'] != 'system'):
                            del res_history[0]

        return res_history

    def history_zip2(self, history=[], leave_count=4, ):
        res_history = history

        if (len(res_history) > 6):
            for h in reversed(range(2, len(res_history) - leave_count)):
                del res_history[h]

        return res_history

    def history2msg_openrt(self, history=[], ):
        res_msg = []
        for h in range(len(history)):
            role    = history[h]['role']
            content = history[h]['content']
            name    = history[h]['name']
            if (role != 'function_call'):
            #if True:
                # openrouter用の処置!
                if (role not in ['system', 'user', 'assistant']):
                    role = 'user'
                if (name == ''):
                    dic = {'role': role, 'content': content }
                    res_msg.append(dic)
                else:
                    dic = {'role': role, 'name': name, 'content': content }
                    res_msg.append(dic)

        return res_msg

    def history2msg_vision(self, history=[], image_urls=[], ):
        res_msg = []
        last_h  = 0
        for h in range(len(history)):
            role    = history[h]['role']
            if (role != 'function_call') and (role != 'function'):
                last_h = h 

        for h in range(len(history)):
            role    = history[h]['role']
            content = history[h]['content']
            name    = history[h]['name']
            if (role != 'function_call') and (role != 'function'):
                con = []
                con.append({'type': 'text', 'text': content})
                if (h == last_h):
                    for image_url in image_urls:
                        con.append(image_url)
                if (name == ''):
                    dic = {'role': role, 'content': con }
                    res_msg.append(dic)
                else:
                    dic = {'role': role, 'name': name, 'content': con }
                    res_msg.append(dic)

        return res_msg



    def files_check(self, filePath=[], ):
        upload_files = []
        image_urls   = []

        # filePath確認
        if (len(filePath) > 0):
            try:

                for file_name in filePath:
                    if (os.path.isfile(file_name)):
                        # 2024/06/26 時点 max 10Mbyte 
                        if (os.path.getsize(file_name) <= 10000000):

                            upload_files.append(file_name)
                            file_ext = os.path.splitext(file_name)[1][1:].lower()
                            if (file_ext in ('jpg', 'jpeg', 'png')):
                                base64_text = base64_encode(file_name)
                                if (file_ext in ('jpg', 'jpeg')):
                                    url = {"url": f"data:image/jpeg;base64,{base64_text}"}
                                    image_url = {'type':'image_url', 'image_url': url}
                                    image_urls.append(image_url)
                                if (file_ext == 'png'):
                                    url = {"url": f"data:image/png;base64,{base64_text}"}
                                    image_url = {'type':'image_url', 'image_url': url}
                                    image_urls.append(image_url)

            except Exception as e:
                print(e)

        return upload_files, image_urls



    def run_gpt(self, chat_class='chat', model_select='auto',
                nick_name=None, model_name=None,
                session_id='admin', history=[], function_modules={},
                sysText=None, reqText=None, inpText='こんにちは',
                upload_files=[], image_urls=[], 
                temperature=0.8, max_step=10, jsonSchema=None, ):

        # 戻り値
        res_text        = ''
        res_path        = ''
        res_files       = []
        res_name        = None
        res_api         = None
        res_history     = history

        if (self.bot_auth is None):
            self.print(session_id, ' OpenRT : Not Authenticate Error !')
            return res_text, res_path, res_files, res_name, res_api, res_history

        # モデル 設定
        res_name  = self.openrt_a_nick_name
        res_api   = self.openrt_a_model
        use_tools = self.openrt_a_use_tools
        if  (chat_class == 'openrt'):
            if (self.openrt_b_enable == True):
                res_name  = self.openrt_b_nick_name
                res_api   = self.openrt_b_model
                use_tools = self.openrt_b_use_tools

        # モデル 補正 (assistant)
        if ((chat_class == 'assistant') \
        or  (chat_class == 'コード生成') \
        or  (chat_class == 'コード実行') \
        or  (chat_class == '文書検索') \
        or  (chat_class == '複雑な会話') \
        or  (chat_class == 'アシスタント') \
        or  (model_select == 'x')):
            if (self.openrt_x_enable == True):
                res_name  = self.openrt_x_nick_name
                res_api   = self.openrt_x_model
                use_tools = self.openrt_x_use_tools

        # model 指定
        if (self.openrt_a_nick_name != ''):
            if (inpText.strip()[:len(self.openrt_a_nick_name)+1].lower() == (self.openrt_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.openrt_a_nick_name)+1:]
        if (self.openrt_b_nick_name != ''):
            if (inpText.strip()[:len(self.openrt_b_nick_name)+1].lower() == (self.openrt_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.openrt_b_nick_name)+1:]
                if   (self.openrt_b_enable == True):
                        res_name  = self.openrt_b_nick_name
                        res_api   = self.openrt_b_model
                        use_tools = self.openrt_b_use_tools
        if (self.openrt_v_nick_name != ''):
            if (inpText.strip()[:len(self.openrt_v_nick_name)+1].lower() == (self.openrt_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.openrt_v_nick_name)+1:]
                if   (self.openrt_v_enable == True):
                    if  (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        res_name  = self.openrt_v_nick_name
                        res_api   = self.openrt_v_model
                        use_tools = self.openrt_v_use_tools
                elif (self.openrt_x_enable == True):
                        res_name  = self.openrt_x_nick_name
                        res_api   = self.openrt_x_model
                        use_tools = self.openrt_x_use_tools
        if (self.openrt_x_nick_name != ''):
            if (inpText.strip()[:len(self.openrt_x_nick_name)+1].lower() == (self.openrt_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.openrt_x_nick_name)+1:]
                if   (self.openrt_x_enable == True):
                        res_name  = self.openrt_x_nick_name
                        res_api   = self.openrt_x_model
                        use_tools = self.openrt_x_use_tools
                elif (self.openrt_b_enable == True):
                        res_name  = self.openrt_b_nick_name
                        res_api   = self.openrt_b_model
                        use_tools = self.openrt_b_use_tools
        if   (inpText.strip()[:5].lower() == ('riki,')):
            inpText = inpText.strip()[5:]
            if   (self.openrt_x_enable == True):
                        res_name  = self.openrt_x_nick_name
                        res_api   = self.openrt_x_model
                        use_tools = self.openrt_x_use_tools
            elif (self.openrt_b_enable == True):
                        res_name  = self.openrt_b_nick_name
                        res_api   = self.openrt_b_model
                        use_tools = self.openrt_b_use_tools
        elif (inpText.strip()[:7].lower() == ('vision,')):
            inpText = inpText.strip()[7:]
            if   (self.openrt_v_enable == True):
                if  (len(image_urls) > 0) \
                and (len(image_urls) == len(upload_files)):
                        res_name  = self.openrt_v_nick_name
                        res_api   = self.openrt_v_model
                        use_tools = self.openrt_v_use_tools
            elif (self.openrt_x_enable == True):
                        res_name  = self.openrt_x_nick_name
                        res_api   = self.openrt_x_model
                        use_tools = self.openrt_x_use_tools
        elif (inpText.strip()[:10].lower() == ('assistant,')):
            inpText = inpText.strip()[10:]
            if   (self.openrt_x_enable == True):
                        res_name  = self.openrt_x_nick_name
                        res_api   = self.openrt_x_model
                        use_tools = self.openrt_x_use_tools
            elif (self.openrt_b_enable == True):
                        res_name  = self.openrt_b_nick_name
                        res_api   = self.openrt_b_model
                        use_tools = self.openrt_b_use_tools
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
        elif (inpText.strip()[:5].lower() == ('groq,')):
            inpText = inpText.strip()[5:]
        elif (inpText.strip()[:7].lower() == ('ollama,')):
            inpText = inpText.strip()[7:]
        elif (inpText.strip()[:6].lower() == ('local,')):
            inpText = inpText.strip()[6:]

        # モデル 未設定時
        if (res_api is None):
            res_name  = self.openrt_a_nick_name
            res_api   = self.openrt_a_model
            use_tools = self.openrt_a_use_tools
            if (self.openrt_b_enable == True):
                if (len(upload_files) > 0) \
                or (len(inpText) > 1000):
                    res_name  = self.openrt_b_nick_name
                    res_api   = self.openrt_b_model
                    use_tools = self.openrt_b_use_tools

        # モデル 補正 (vision)
        if  (len(image_urls) > 0) \
        and (len(image_urls) == len(upload_files)):
            if   (self.openrt_v_enable == True):
                res_name  = self.openrt_v_nick_name
                res_api   = self.openrt_v_model
                use_tools = self.openrt_v_use_tools
            elif (self.openrt_x_enable == True):
                res_name  = self.openrt_x_nick_name
                res_api   = self.openrt_x_model
                use_tools = self.openrt_x_use_tools

        # history 追加・圧縮 (古いメッセージ)
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
        res_history = self.history_zip1(history=res_history, )

        # メッセージ作成
        if (model_select != 'v'):
            msg = self.history2msg_openrt(history=res_history, )
        else:
            msg = self.history2msg_vision(history=res_history, image_urls=image_urls,)

        # ストリーム実行?
        if (session_id == 'admin'):
            #stream = True
            print(' OpenRT : stream=False, ')
            stream = False
        else:
            stream = False

        # ツール設定
        tools = []
        #print(' OpenRT : tools=[], ')
        if True:
            if (use_tools.lower().find('yes') >= 0):
                functions = []
                for module_dic in function_modules.values():
                    functions.append(module_dic['function'])
                for f in range(len(functions)):
                    tools.append({"type": "function", "function": functions[f]})

        # 実行ループ
        #try:
        if True:

            n = 0
            function_name = ''
            while (function_name != 'exit') and (n < int(max_step)):

                # 結果
                res_role      = ''
                res_content   = ''
                tool_calls    = []

                # GPT
                n += 1
                self.print(session_id, f" OpenRT : { res_name.lower() }, { res_api }, pass={ n }, ")

                # 画像指定
                if   (res_name == self.openrt_v_nick_name) and (len(image_urls) > 0):
                    null_history = self.history_add(history=[], sysText=sysText, reqText=reqText, inpText=inpText, )
                    msg = self.history2msg_vision(history=null_history, image_urls=image_urls,)
                    response = self.client.chat.completions.create(
                            model           = res_api,
                            messages        = msg,
                            temperature     = float(temperature),
                            timeout         = self.openrt_max_wait_sec, 
                            stream          = stream, 
                            )

                # ツール指定
                elif (len(tools) != 0):
                    response = self.client.chat.completions.create(
                            model           = res_api,
                            messages        = msg,
                            temperature     = float(temperature),
                            tools           = tools, tool_choice = 'auto',
                            timeout         = self.openrt_max_wait_sec,
                            stream          = stream, 
                            )

                else:
                    # ノーマル
                    if (jsonSchema is None) or (jsonSchema == ''):                        
                        response = self.client.chat.completions.create(
                            model           = res_api,
                            messages        = msg,
                            temperature     = float(temperature),
                            timeout         = self.openrt_max_wait_sec,
                            stream          = stream, 
                            )
                    else:
                        schema = None
                        try:
                            schema = json.loads(jsonSchema)
                        except:
                            pass
                        # スキーマ指定無し
                        if (schema is None):
                            response = self.client.chat.completions.create(
                                model           = res_api,
                                messages        = msg,
                                temperature     = float(temperature),
                                timeout         = self.openrt_max_wait_sec, 
                                response_format = { "type": "json_object" },
                                stream          = stream, 
                                )
                        # スキーマ指定有り
                        else:
                            response = self.client.chat.completions.create(
                                model           = res_api,
                                messages        = msg,
                                temperature     = float(temperature),
                                timeout         = self.openrt_max_wait_sec, 
                                response_format = { "type": "json_schema", "json_schema": schema },
                                stream          = stream, 
                                )

                # Stream 表示
                if (stream == True):

                    chkTime     = time.time()
                    for chunk in response:
                        if ((time.time() - chkTime) > self.openrt_max_wait_sec):
                            break
                        delta   = chunk.choices[0].delta
                        if (delta is not None):
                            if (delta.content is not None):
                                #res_role    = delta.role
                                res_role    = 'assistant'
                                content     = delta.content
                                res_content += content
                                self.stream(session_id, content)

                            elif (delta.tool_calls is not None):
                                #res_role    = delta.role
                                res_role    = 'assistant'
                                tcchunklist = delta.tool_calls
                                for tcchunk in tcchunklist:
                                    if len(tool_calls) <= tcchunk.index:
                                        tool_calls.append({"id": "", "type": "function", "function": { "name": "", "arguments": "" } })
                                    tc = tool_calls[tcchunk.index]
                                    if tcchunk.id:
                                        tc["id"]                    += tcchunk.id
                                    if tcchunk.function.name:
                                        tc["function"]["name"]      += tcchunk.function.name
                                    if tcchunk.function.arguments:
                                        tc["function"]["arguments"] += tcchunk.function.arguments

                    # 改行
                    if (res_content != ''):
                        self.print(session_id, )

                # 通常実行
                if (stream == False):

                    # response 処理
                    try:
                        res_role    = str(response.choices[0].message.role)
                        res_content = str(response.choices[0].message.content)

                        # 新 function 
                        if (response.choices[0].finish_reason=='tool_calls'):
                            for tool_call in response.choices[0].message.tool_calls:
                                t_id     = str(tool_call.id)
                                f_name   = str(tool_call.function.name)
                                f_kwargs = str(tool_call.function.arguments)
                                try:
                                    wk_dic      = json.loads(f_kwargs)
                                    wk_text     = json.dumps(wk_dic, ensure_ascii=False, )
                                    f_kwargs = wk_text
                                except:
                                    pass
                                tool_calls.append({"id": t_id, "type": "function", "function": { "name": f_name, "arguments": f_kwargs } })

                    except Exception as e:
                        print(response)
                        #print(e)

                # function 指示?
                if (len(tool_calls) > 0):

                    self.print(session_id, )
                    for tc in tool_calls:
                        #print(tc)
                        f_id     = tc['id']
                        f_name   = tc['function'].get('name')
                        f_kwargs = tc['function'].get('arguments')

                        hit = False

                        for module_dic in function_modules.values():
                            if (f_name == module_dic['func_name']):
                                hit = True
                                self.print(session_id, f" OpenRT :   function_call '{ module_dic['script'] }' ({ f_name })")
                                self.print(session_id, f" OpenRT :   → { f_kwargs }")

                                # メッセージ追加格納
                                self.seq += 1
                                dic = {'seq': self.seq, 'time': time.time(), 'role': 'function_call', 'name': f_name, 'content': f_kwargs }
                                res_history.append(dic)

                                # function 実行
                                try:
                                    ext_func_proc  = module_dic['func_proc']
                                    res_json = ext_func_proc( f_kwargs )
                                except Exception as e:
                                    print(e)
                                    # エラーメッセージ
                                    dic = {}
                                    dic['error'] = e 
                                    res_json = json.dumps(dic, ensure_ascii=False, )

                                # tool_result
                                self.print(session_id, f" OpenRT :   → { res_json }")
                                self.print(session_id, )

                                # メッセージ追加格納
                                # dic = {'role': 'function', 'name': f_name, 'content': res_json }
                                # openrouter用の処置!
                                dic = {'role': 'user', 'name': f_name, 'content': res_json }
                                msg.append(dic)
                                self.seq += 1
                                dic = {'seq': self.seq, 'time': time.time(), 'role': 'function', 'name': f_name, 'content': res_json }
                                res_history.append(dic)

                                # パス情報確認
                                try:
                                    dic  = json.loads(res_json)
                                    path = dic['image_path']
                                    if (path is None):
                                        path = dic.get('excel_path')
                                    if (path is not None):
                                        res_path = path
                                        res_files.append(path)
                                        res_files = list(set(res_files))
                                except:
                                    pass

                                break

                        if (hit == False):
                            self.print(session_id, f" OpenRT :   function_call Error ! ({ f_name })")
                            print(res_role, res_content, f_name, f_kwargs, )
                            break

                # 実行終了
                elif (res_role == 'assistant') and (res_content != '' ):

                    function_name = 'exit'
                    if (res_content.strip() != ''):
                        res_text += res_content.rstrip() + '\n'

                        self.seq += 1
                        dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': res_content }
                        res_history.append(dic)

                else:
                    print('loop???', res_role, res_content)

            # 正常回答
            if (res_text != ''):
                self.print(session_id, f" OpenRT : { res_name.lower() }, complete.")
            else:
                self.print(session_id,  ' OpenRT : Error !')

        #except Exception as e:
        #    print(e)
        #    res_text = ''

        return res_text, res_path, res_files, res_name, res_api, res_history



    def chatBot(self, chat_class='auto', model_select='auto',
                session_id='admin', history=[], function_modules={},
                sysText=None, reqText=None, inpText='こんにちは', 
                filePath=[],
                temperature=0.8, max_step=10, jsonSchema=None,
                inpLang='ja-JP', outLang='ja-JP', ):

        # 戻り値
        res_text    = ''
        res_path    = ''
        res_files   = []
        nick_name   = None
        model_name  = None
        res_history = history

        if (sysText is None) or (sysText == ''):
            sysText = 'あなたは美しい日本語を話す賢いアシスタントです。'
        if (inpText is None) or (inpText == ''):
            inpText = reqText
            reqText = None

        if (self.bot_auth is None):
            self.print(session_id, ' OpenRT : Not Authenticate Error !')
            return res_text, res_path, res_files, nick_name, model_name, res_history

        # ファイル分離
        upload_files    = []
        image_urls      = []
        try:
            upload_files, image_urls = self.files_check(filePath=filePath, )
        except Exception as e:
            print(e)

        # 実行モデル判定
        #nick_name  = 'auto'
        #model_name = 'auto'

        # openrt
        res_text, res_path, res_files, nick_name, model_name, res_history = \
        self.run_gpt(   chat_class=chat_class, model_select=model_select,
                        nick_name=nick_name, model_name=model_name,
                        session_id=session_id, history=res_history, function_modules=function_modules,
                        sysText=sysText, reqText=reqText, inpText=inpText,
                        upload_files=upload_files, image_urls=image_urls,
                        temperature=temperature, max_step=max_step, jsonSchema=jsonSchema, )

        # 文書成形
        if (res_text.strip() == ''):
            res_text = '!'

        return res_text, res_path, res_files, nick_name, model_name, res_history



if __name__ == '__main__':

        #openrtAPI = speech_bot_openrt._openrtAPI()
        openrtAPI = _openrtAPI()

        api_type = openrt_key.getkey('openrt','openrt_api_type')
        print(api_type)

        log_queue = queue.Queue()
        res = openrtAPI.init(log_queue=log_queue, )

        res = openrtAPI.authenticate('openrt',
                            api_type,
                            openrt_key.getkey('openrt','openrt_default_gpt'), openrt_key.getkey('openrt','openrt_default_class'),
                            openrt_key.getkey('openrt','openrt_auto_continue'),
                            openrt_key.getkey('openrt','openrt_max_step'), openrt_key.getkey('openrt','openrt_max_session'),
                            openrt_key.getkey('openrt','openrt_max_wait_sec'),
                            openrt_key.getkey('openrt','openrt_key_id'),
                            openrt_key.getkey('openrt','openrt_a_nick_name'), openrt_key.getkey('openrt','openrt_a_model'), openrt_key.getkey('openrt','openrt_a_token'),
                            openrt_key.getkey('openrt','openrt_a_use_tools'),
                            openrt_key.getkey('openrt','openrt_b_nick_name'), openrt_key.getkey('openrt','openrt_b_model'), openrt_key.getkey('openrt','openrt_b_token'),
                            openrt_key.getkey('openrt','openrt_b_use_tools'),
                            openrt_key.getkey('openrt','openrt_v_nick_name'), openrt_key.getkey('openrt','openrt_v_model'), openrt_key.getkey('openrt','openrt_v_token'),
                            openrt_key.getkey('openrt','openrt_v_use_tools'),
                            openrt_key.getkey('openrt','openrt_x_nick_name'), openrt_key.getkey('openrt','openrt_x_model'), openrt_key.getkey('openrt','openrt_x_token'),
                            openrt_key.getkey('openrt','openrt_x_use_tools'),
                            )
        print('authenticate:', res, )
        if (res == True):
            
            function_modules = {}
            filePath         = []

            if True:
                import    speech_bot_function
                botFunc = speech_bot_function.botFunction()

                res, msg = botFunc.functions_load(
                    functions_path='_extensions/function/', secure_level='low', )
                if (res != True) or (msg != ''):
                    print(msg)
                    print()

                for key, module_dic in botFunc.function_modules.items():
                    if (module_dic['onoff'] == 'on'):
                        function_modules[key] = module_dic

            if True:
                sysText = None
                reqText = ''
                inpText = 'おはようございます。'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, openrtAPI.history = \
                    openrtAPI.chatBot(  chat_class='auto', model_select='auto', 
                                        session_id='admin', history=openrtAPI.history, function_modules=function_modules,
                                        sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                        inpLang='ja', outLang='ja', )
                print()
                print(f"[{ res_name }] ({ res_api })")
                print(str(res_text))
                print()

            if True:
                sysText = None
                reqText = ''
                inpText = 'ort-b,toolsで兵庫県三木市の天気を調べて'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, openrtAPI.history = \
                    openrtAPI.chatBot(  chat_class='auto', model_select='auto', 
                                        session_id='admin', history=openrtAPI.history, function_modules=function_modules,
                                        sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                        inpLang='ja', outLang='ja', )
                print()
                print(f"[{ res_name }] ({ res_api })")
                print(str(res_text))
                print()

            if True:
                sysText = None
                reqText = ''
                inpText = '添付画像を説明してください。'
                filePath = ['_icons/dog.jpg']
                #filePath = ['_icons/dog.jpg', '_icons/kyoto.png']
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, openrtAPI.history = \
                    openrtAPI.chatBot(  chat_class='auto', model_select='auto', 
                                        session_id='admin', history=openrtAPI.history, function_modules=function_modules,
                                        sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                        inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print('', res_text)
                print()

            if False:
                print('[History]')
                for h in range(len(openrtAPI.history)):
                    print(openrtAPI.history[h])
                openrtAPI.history = []



