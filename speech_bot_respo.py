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



# respo チャットボット
import openai

import speech_bot_respo_key  as respo_key



# base64 encode
def base64_encode(file_path):
    with open(file_path, "rb") as input_file:
        return base64.b64encode(input_file.read()).decode('utf-8')



class _respoAPI:

    def __init__(self, ):
        self.log_queue                  = None
        self.bot_auth                   = None

        self.temperature                = 0.8

        self.respo_api_type         = 'openai'
        self.respo_default_gpt      = 'auto'
        self.respo_default_class    = 'auto'
        self.respo_auto_continue    = 3
        self.respo_max_step         = 10
        self.respo_max_session      = 5
        self.respo_max_wait_sec     = 120
       
        self.openai_organization        = None
        self.openai_key_id              = None
        self.azure_endpoint             = None
        self.azure_version              = None
        self.azure_key_id               = None

        self.respo_a_enable         = False
        self.respo_a_nick_name      = ''
        self.respo_a_model          = None
        self.respo_a_token          = 0
        self.respo_a_use_tools      = 'no'

        self.respo_b_enable         = False
        self.respo_b_nick_name      = ''
        self.respo_b_model          = None
        self.respo_b_token          = 0
        self.respo_b_use_tools      = 'no'

        self.respo_v_enable         = False
        self.respo_v_nick_name      = ''
        self.respo_v_model          = None
        self.respo_v_token          = 0
        self.respo_v_use_tools      = 'no'

        self.respo_x_enable         = False
        self.respo_x_nick_name      = ''
        self.respo_x_model          = None
        self.respo_x_token          = 0
        self.respo_x_use_tools      = 'no'

        self.models                     = {}
        self.history                    = []

        self.seq                        = 0
        self.reset()

    def init(self, log_queue=None, ):
        self.log_queue = log_queue
        return True

    def reset(self, ):
        self.history                    = []
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
                     respo_api_type,
                     respo_default_gpt, respo_default_class,
                     respo_auto_continue,
                     respo_max_step, respo_max_session,
                     respo_max_wait_sec,

                     openai_organization, openai_key_id,
                     azure_endpoint, azure_version, azure_key_id,

                     respo_a_nick_name, respo_a_model, respo_a_token, 
                     respo_a_use_tools, 
                     respo_b_nick_name, respo_b_model, respo_b_token, 
                     respo_b_use_tools, 
                     respo_v_nick_name, respo_v_model, respo_v_token, 
                     respo_v_use_tools, 
                     respo_x_nick_name, respo_x_model, respo_x_token, 
                     respo_x_use_tools, 
                    ):

        # 認証
        self.bot_auth                   = None
        self.respo_api_type         = respo_api_type
        self.openai_organization        = openai_organization
        self.openai_key_id              = openai_key_id
        self.azure_endpoint             = azure_endpoint
        self.azure_version              = azure_version
        self.azure_key_id               = azure_key_id

        self.client = None
        try:
            # openai
            if (respo_api_type != 'azure'):
                if (openai_key_id[:1] == '<'):
                    return False
                else:
                    self.client = openai.OpenAI(organization=openai_organization,
                                                api_key=openai_key_id, )
            # azure
            else:
                if (azure_key_id[:1] == '<'):
                    return False
                else:
                    self.client = openai.AzureOpenAI(azure_endpoint=azure_endpoint,
                                                     api_version=azure_version,
                                                     api_key=azure_key_id, )
        except Exception as e:
            print(e)
            return False

        # 設定
        self.respo_default_gpt          = respo_default_gpt
        self.respo_default_class        = respo_default_class
        if (str(respo_auto_continue)    not in ['', 'auto']):
            self.respo_auto_continue    = int(respo_auto_continue)
        if (str(respo_max_step)         not in ['', 'auto']):
            self.respo_max_step         = int(respo_max_step)
        if (str(respo_max_session)      not in ['', 'auto']):
            self.respo_max_session      = int(respo_max_session)
        if (str(respo_max_wait_sec)     not in ['', 'auto']):
            self.respo_max_wait_sec     = int(respo_max_wait_sec)

        # モデル取得
        self.models                         = {}
        self.get_models()

        #ymd = datetime.date.today().strftime('%Y/%m/%d')
        ymd = 'default'

        # respo チャットボット
        if (respo_a_nick_name != ''):
            self.respo_a_enable         = False
            self.respo_a_nick_name      = respo_a_nick_name
            self.respo_a_model          = respo_a_model
            self.respo_a_token          = int(respo_a_token)
            self.respo_a_use_tools      = respo_a_use_tools
            if (respo_a_model not in self.models):
                self.models[respo_a_model] = {"id": respo_a_model, "token": str(respo_a_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[respo_a_model]['date'] = ymd

        if (respo_b_nick_name != ''):
            self.respo_b_enable         = False
            self.respo_b_nick_name      = respo_b_nick_name
            self.respo_b_model          = respo_b_model
            self.respo_b_token          = int(respo_b_token)
            self.respo_b_use_tools      = respo_b_use_tools
            if (respo_b_model not in self.models):
                self.models[respo_b_model] = {"id": respo_b_model, "token": str(respo_b_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[respo_b_model]['date'] = ymd

        if (respo_v_nick_name != ''):
            self.respo_v_enable         = False
            self.respo_v_nick_name      = respo_v_nick_name
            self.respo_v_model          = respo_v_model
            self.respo_v_token          = int(respo_v_token)
            self.respo_v_use_tools      = respo_v_use_tools
            if (respo_v_model not in self.models):
                self.models[respo_v_model] = {"id": respo_v_model, "token": str(respo_v_token), "modality": "text+image?", "date": ymd, }
            else:
                #self.models[respo_v_model]['date'] = ymd
                self.models[respo_v_model]['modality'] = "text+image?"

        if (respo_x_nick_name != ''):
            self.respo_x_enable         = False
            self.respo_x_nick_name      = respo_x_nick_name
            self.respo_x_model          = respo_x_model
            self.respo_x_token          = int(respo_x_token)
            self.respo_x_use_tools      = respo_x_use_tools
            if (respo_x_model not in self.models):
                self.models[respo_x_model] = {"id": respo_x_model, "token": str(respo_x_token), "modality": "text+image?", "date": ymd, }
            #else:
            #    self.models[respo_x_model]['date'] = ymd

        # モデル
        hit = False
        if (self.respo_a_model != ''):
            self.respo_a_enable = True
            hit = True
        if (self.respo_b_model != ''):
            self.respo_b_enable = True
            hit = True
        if (self.respo_v_model != ''):
            self.respo_v_enable = True
            hit = True
        if (self.respo_x_model != ''):
            self.respo_x_enable = True
            hit = True

        if (hit == True):
            self.bot_auth = True
            return True
        else:
            return False

    def get_models(self, ):
        try:
            models = self.client.models.list()
            self.models = {}
            for model in models:
                #print(model)
                key = model.id
                ymd = datetime.datetime.fromtimestamp(model.created).strftime("%Y/%m/%d")
                if (ymd >= '2025/01/01') \
                or (key.find('gpt-4o') >= 0) or (key.find('o1') >= 0) or (key.find('o3') >= 0):
                #if True:
                    #print(key, ymd, )
                    self.models[key] = {"id":key, "token":"9999", "modality":"text?", "date": ymd, }
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
                if (str(max_wait_sec) != str(self.respo_max_wait_sec)):
                    self.respo_max_wait_sec = int(max_wait_sec)
            if (a_model != ''):
                if (a_model != self.respo_a_model) and (a_model in self.models):
                    self.respo_a_enable = True
                    self.respo_a_model = a_model
                    self.respo_a_token = int(self.models[a_model]['token'])
            if (a_use_tools != ''):
                self.respo_a_use_tools = a_use_tools
            if (b_model != ''):
                if (b_model != self.respo_b_model) and (b_model in self.models):
                    self.respo_b_enable = True
                    self.respo_b_model = b_model
                    self.respo_b_token = int(self.models[b_model]['token'])
            if (b_use_tools != ''):
                self.respo_b_use_tools = b_use_tools
            if (v_model != ''):
                if (v_model != self.respo_v_model) and (v_model in self.models):
                    self.respo_v_enable = True
                    self.respo_v_model = v_model
                    self.respo_v_token = int(self.models[v_model]['token'])
            if (v_use_tools != ''):
                self.respo_v_use_tools = v_use_tools
            if (x_model != ''):
                if (x_model != self.respo_x_model) and (x_model in self.models):
                    self.respo_x_enable = True
                    self.respo_x_model = x_model
                    self.respo_x_token = int(self.models[x_model]['token'])
            if (x_use_tools != ''):
                self.respo_x_use_tools = x_use_tools
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

    def history2msg_respo(self, history=[], ):
        res_msg = []
        for h in range(len(history)):
            role    = history[h]['role']
            content = history[h]['content']
            name    = history[h]['name']
            if (role != 'function_call'):
            #if True:
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
                if (h != last_h):
                    if (name == ''):
                        dic = {'role': role, 'content': content }
                        res_msg.append(dic)
                    else:
                        dic = {'role': role, 'name': name, 'content': content }
                        res_msg.append(dic)
                else:
                    con = []
                    con.append({'type': 'input_text', 'text': content})
                    for image_url in image_urls:
                        con.append(image_url)
                    dic = {'role': role, 'content': con }
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
                        # 2025/03/15 時点 max 20Mbyte 
                        if (os.path.getsize(file_name) <= 20000000):

                            upload_files.append(file_name)
                            file_ext = os.path.splitext(file_name)[1][1:].lower()
                            if (file_ext in ('jpg', 'jpeg', 'png', 'gif')):
                                base64_text = base64_encode(file_name)
                                if   (file_ext in ('jpg', 'jpeg')):
                                    url = f"data:image/jpeg;base64,{base64_text}"
                                    image_url = {"type": "input_image", 'image_url': url, 'detail': 'high'}
                                    image_urls.append(image_url)
                                elif (file_ext == 'png'):
                                    url = f"data:image/png;base64,{base64_text}"
                                    image_url = {"type": "input_image", 'image_url': url, 'detail': 'high'}
                                    image_urls.append(image_url)
                                elif (file_ext == 'gif'):
                                    url = f"data:image/gif;base64,{base64_text}"
                                    image_url = {"type": "input_image", 'image_url': url, 'detail': 'high'}
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
            self.print(session_id, ' Respo : Not Authenticate Error !')
            return res_text, res_path, res_files, res_name, res_api, res_history

        # モデル 設定
        res_name  = self.respo_a_nick_name
        res_api   = self.respo_a_model
        use_tools = self.respo_a_use_tools
        if  (chat_class == 'respo'):
            if (self.respo_b_enable == True):
                res_name  = self.respo_b_nick_name
                res_api   = self.respo_b_model
                use_tools = self.respo_b_use_tools

        # モデル 補正 (assistant)
        if ((chat_class == 'assistant') \
        or  (chat_class == 'コード生成') \
        or  (chat_class == 'コード実行') \
        or  (chat_class == '文書検索') \
        or  (chat_class == '複雑な会話') \
        or  (chat_class == 'アシスタント') \
        or  (model_select == 'x')):
            if (self.respo_x_enable == True):
                res_name  = self.respo_x_nick_name
                res_api   = self.respo_x_model
                use_tools = self.respo_x_use_tools

        # model 指定
        if (self.respo_a_nick_name != ''):
            if (inpText.strip()[:len(self.respo_a_nick_name)+1].lower() == (self.respo_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.respo_a_nick_name)+1:]
        if (self.respo_b_nick_name != ''):
            if (inpText.strip()[:len(self.respo_b_nick_name)+1].lower() == (self.respo_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.respo_b_nick_name)+1:]
                if   (self.respo_b_enable == True):
                        res_name  = self.respo_b_nick_name
                        res_api   = self.respo_b_model
                        use_tools = self.respo_b_use_tools
        if (self.respo_v_nick_name != ''):
            if (inpText.strip()[:len(self.respo_v_nick_name)+1].lower() == (self.respo_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.respo_v_nick_name)+1:]
                if   (self.respo_v_enable == True):
                    if  (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        res_name  = self.respo_v_nick_name
                        res_api   = self.respo_v_model
                        use_tools = self.respo_v_use_tools
                elif (self.respo_x_enable == True):
                        res_name  = self.respo_x_nick_name
                        res_api   = self.respo_x_model
                        use_tools = self.respo_x_use_tools
        if (self.respo_x_nick_name != ''):
            if (inpText.strip()[:len(self.respo_x_nick_name)+1].lower() == (self.respo_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.respo_x_nick_name)+1:]
                if   (self.respo_x_enable == True):
                        res_name  = self.respo_x_nick_name
                        res_api   = self.respo_x_model
                        use_tools = self.respo_x_use_tools
                elif (self.respo_b_enable == True):
                        res_name  = self.respo_b_nick_name
                        res_api   = self.respo_b_model
                        use_tools = self.respo_b_use_tools
        if   (inpText.strip()[:5].lower() == ('riki,')):
            inpText = inpText.strip()[5:]
            if   (self.respo_x_enable == True):
                        res_name  = self.respo_x_nick_name
                        res_api   = self.respo_x_model
                        use_tools = self.respo_x_use_tools
            elif (self.respo_b_enable == True):
                        res_name  = self.respo_b_nick_name
                        res_api   = self.respo_b_model
                        use_tools = self.respo_b_use_tools
        elif (inpText.strip()[:7].lower() == ('vision,')):
            inpText = inpText.strip()[7:]
            if   (self.respo_v_enable == True):
                if  (len(image_urls) > 0) \
                and (len(image_urls) == len(upload_files)):
                        res_name  = self.respo_v_nick_name
                        res_api   = self.respo_v_model
                        use_tools = self.respo_v_use_tools
            elif (self.respo_x_enable == True):
                        res_name  = self.respo_x_nick_name
                        res_api   = self.respo_x_model
                        use_tools = self.respo_x_use_tools
        elif (inpText.strip()[:10].lower() == ('assistant,')):
            inpText = inpText.strip()[10:]
            if   (self.respo_x_enable == True):
                        res_name  = self.respo_x_nick_name
                        res_api   = self.respo_x_model
                        use_tools = self.respo_x_use_tools
            elif (self.respo_b_enable == True):
                        res_name  = self.respo_b_nick_name
                        res_api   = self.respo_b_model
                        use_tools = self.respo_b_use_tools
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
            res_name  = self.respo_a_nick_name
            res_api   = self.respo_a_model
            use_tools = self.respo_a_use_tools
            if (self.respo_b_enable == True):
                if (len(upload_files) > 0) \
                or (len(inpText) > 1000):
                    res_name  = self.respo_b_nick_name
                    res_api   = self.respo_b_model
                    use_tools = self.respo_b_use_tools

        # モデル 補正 (vision)
        if  (len(image_urls) > 0) \
        and (len(image_urls) == len(upload_files)):
            if   (self.respo_v_enable == True):
                res_name  = self.respo_v_nick_name
                res_api   = self.respo_v_model
                use_tools = self.respo_v_use_tools
            elif (self.respo_x_enable == True):
                res_name  = self.respo_x_nick_name
                res_api   = self.respo_x_model
                use_tools = self.respo_x_use_tools

        # history 追加・圧縮 (古いメッセージ)
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
        res_history = self.history_zip1(history=res_history, )

        # メッセージ作成
        if (model_select != 'v'):
            msg = self.history2msg_respo(history=res_history, )
        else:
            msg = self.history2msg_vision(history=res_history, image_urls=image_urls,)

        # ストリーム実行?
        if (session_id == 'admin'):
            #stream = True
            print(' Respo : stream=False, ')
            stream = False
        else:
            stream = False

        # ツール設定
        tools = []
        #print(' Respo : tools=[], ')
        if True:
            if (use_tools.lower().find('yes') >= 0):
                tools.append({"type": "web_search_preview"})
                #if (model_name[:1].lower() != 'o'): # o1, o3, ... 以外
                #    tools.append({"type": "code_interpreter"})
                #if (len(vectorStore_ids) > 0):
                #    tools.append({"type": "file_search"})
                for module_dic in function_modules.values():
                    func_dic = module_dic['function']
                    func_dic['type'] = "function"
                    tools.append(func_dic)
        #print(tools)

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
                self.print(session_id, f" Respo : { res_name.lower() }, { res_api }, pass={ n }, ")

                # 画像指定
                if   (res_name == self.respo_v_nick_name) and (len(image_urls) > 0):
                    null_history = self.history_add(history=[], sysText=sysText, reqText=reqText, inpText=inpText, )
                    msg = self.history2msg_vision(history=null_history, image_urls=image_urls,)
                    response = self.client.responses.create(
                                model           = res_api,
                                input           = msg,
                                #temperature     = float(temperature),
                                timeout         = self.respo_max_wait_sec, 
                                stream          = stream, 
                                )

                # ツール指定
                elif (len(tools) != 0):
                        # o3, o4, ... 以外
                        if (res_api[:2].lower() not in ['o3', 'o4']):
                            response = self.client.responses.create(
                                model           = res_api,
                                input           = msg,
                                #temperature     = float(temperature),
                                tools           = tools,
                                timeout         = self.respo_max_wait_sec,
                                stream          = stream, 
                                )
                        # o3, o4,
                        else:
                            print(" Respo : reasoning_effort='high', ")
                            response = self.client.responses.create(
                                model           = res_api,
                                input           = msg,
                                #temperature     = float(temperature),
                                tools           = tools,
                                timeout         = self.respo_max_wait_sec,
                                stream          = stream, 
                                reasoning_effort= 'high',
                                )

                else:
                    # ノーマル
                    if (jsonSchema is None) or (jsonSchema == ''):                        
                        # o3, o4, ... 以外
                        if (res_api[:2].lower() not in ['o3', 'o4']):
                            response = self.client.responses.create(
                                model           = res_api,
                                input           = msg,
                                #temperature     = float(temperature),
                                timeout         = self.respo_max_wait_sec,
                                stream          = stream, 
                                )
                        # o3, o4,
                        else:
                            print(" Respo : reasoning_effort='high', ")
                            response = self.client.responses.create(
                                model           = res_api,
                                input           = msg,
                                #temperature     = float(temperature),
                                timeout         = self.respo_max_wait_sec,
                                stream          = stream, 
                                reasoning_effort= 'high',
                                )
                    else:
                        schema = None
                        try:
                            schema = json.loads(jsonSchema)
                        except:
                            pass
                        # スキーマ指定無し
                        if (schema is None):
                            response = self.client.responses.create(
                                model           = res_api,
                                input           = msg,
                                #temperature     = float(temperature),
                                timeout         = self.respo_max_wait_sec, 
                                response_format = { "type": "json_object" },
                                stream          = stream, 
                                )
                        # スキーマ指定有り
                        else:
                            response = self.client.responses.create(
                                model           = res_api,
                                input           = msg,
                                #temperature     = float(temperature),
                                timeout         = self.respo_max_wait_sec, 
                                response_format = { "type": "json_schema", "json_schema": schema },
                                stream          = stream, 
                                )

                # Stream 表示 未実装
                if (stream == True):

                    chkTime     = time.time()
                    for event in response:
                        if ((time.time() - chkTime) > self.respo_max_wait_sec):
                            break
                        print(event)

                        #- `response.created`
                        #- `response.output_text.delta`
                        #- `response.completed`
                        #- `error`

                # 通常実行
                if (stream == False):

                    # response 処理
                    #try:
                    if True:
                        for output in response.output:
                            if   (output.type == 'message'):
                                res_role    = str(response.output[0].role)
                                res_content = str(response.output[0].content[0].text)

                            elif (output.type == 'function_call'):
                                o_id     = str(output.id)
                                f_id     = str(output.call_id)
                                f_name   = str(output.name)
                                f_kwargs = str(output.arguments)
                                try:
                                    wk_dic      = json.loads(f_kwargs)
                                    wk_text     = json.dumps(wk_dic, ensure_ascii=False, )
                                    f_kwargs = wk_text
                                except:
                                    pass
                                tool_calls.append({"id": f_id, "type": "function", "function": { "name": f_name, "arguments": f_kwargs } })

                                # メッセージ追加格納
                                dic = {'type': 'function_call', 'id': o_id, 'call_id': f_id, 'name': f_name, 'arguments': f_kwargs }
                                msg.append(dic)

                    #except Exception as e:
                    #    print(response)
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
                                self.print(session_id, f" Respo :   function_call '{ module_dic['script'] }' ({ f_name })")
                                self.print(session_id, f" Respo :   → { f_kwargs }")

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
                                    dic['error'] = str(e)
                                    res_json = json.dumps(dic, ensure_ascii=False, )

                                # tool_result
                                self.print(session_id, f" Respo :   → { res_json }")
                                self.print(session_id, )

                                # メッセージ追加格納
                                # dic = {'role': 'function', 'name': f_name, 'content': res_json }
                                dic = {'type': 'function_call_output', 'call_id': f_id, 'output': res_json }
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
                            self.print(session_id, f" Respo :   function_call Error ! ({ f_name })")
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
                self.print(session_id, f" Respo : { res_name.lower() }, complete.")
            else:
                self.print(session_id,  ' Respo : Error !')

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
            self.print(session_id, ' Respo : Not Authenticate Error !')
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

        # respo
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

        #respoAPI = speech_bot_respo._respoAPI()
        respoAPI = _respoAPI()

        api_type = respo_key.getkey('respo','respo_api_type')
        print(api_type)

        log_queue = queue.Queue()
        res = respoAPI.init(log_queue=log_queue, )

        res = respoAPI.authenticate('respo',
                            api_type,
                            respo_key.getkey('respo','respo_default_gpt'), respo_key.getkey('respo','respo_default_class'),
                            respo_key.getkey('respo','respo_auto_continue'),
                            respo_key.getkey('respo','respo_max_step'), respo_key.getkey('respo','respo_max_session'),
                            respo_key.getkey('respo','respo_max_wait_sec'),

                            respo_key.getkey('respo','openai_organization'), 
                            respo_key.getkey('respo','openai_key_id'),
                            respo_key.getkey('respo','azure_endpoint'), 
                            respo_key.getkey('respo','azure_version'), 
                            respo_key.getkey('respo','azure_key_id'),

                            respo_key.getkey('respo','respo_a_nick_name'), respo_key.getkey('respo','respo_a_model'), respo_key.getkey('respo','respo_a_token'),
                            respo_key.getkey('respo','respo_a_use_tools'),
                            respo_key.getkey('respo','respo_b_nick_name'), respo_key.getkey('respo','respo_b_model'), respo_key.getkey('respo','respo_b_token'),
                            respo_key.getkey('respo','respo_b_use_tools'),
                            respo_key.getkey('respo','respo_v_nick_name'), respo_key.getkey('respo','respo_v_model'), respo_key.getkey('respo','respo_v_token'),
                            respo_key.getkey('respo','respo_v_use_tools'),
                            respo_key.getkey('respo','respo_x_nick_name'), respo_key.getkey('respo','respo_x_model'), respo_key.getkey('respo','respo_x_token'),
                            respo_key.getkey('respo','respo_x_use_tools'),
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
                    #if (module_dic['onoff'] == 'on'):
                    if (module_dic['func_name'].find('weather') >= 0):
                        print(module_dic['func_name'])
                        function_modules[key] = module_dic

            if True:
                sysText = None
                reqText = ''
                inpText = 'おはようございます。'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, respoAPI.history = \
                    respoAPI.chatBot(   chat_class='auto', model_select='auto', 
                                            session_id='admin', history=respoAPI.history, function_modules=function_modules,
                                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                            inpLang='ja', outLang='ja', )
                print()
                print(f"[{ res_name }] ({ res_api })")
                print(str(res_text))
                print()

            if True:
                sysText = None
                reqText = ''
                inpText = 'toolsで兵庫県三木市の天気を調べて'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, respoAPI.history = \
                    respoAPI.chatBot(   chat_class='auto', model_select='auto', 
                                            session_id='admin', history=respoAPI.history, function_modules=function_modules,
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
                res_text, res_path, res_files, res_name, res_api, respoAPI.history = \
                    respoAPI.chatBot(   chat_class='auto', model_select='auto', 
                                            session_id='admin', history=respoAPI.history, function_modules=function_modules,
                                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print('', res_text)
                print()

            if False:
                print('[History]')
                for h in range(len(respoAPI.history)):
                    print(respoAPI.history[h])
                respoAPI.history = []



