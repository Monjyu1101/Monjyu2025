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

# groq チャットボット
import groq

import speech_bot_groq_key  as groq_key



# base64 encode
def base64_encode(file_path):
    with open(file_path, "rb") as input_file:
        return base64.b64encode(input_file.read()).decode('utf-8')



class _groqAPI:

    def __init__(self, ):
        self.log_queue              = None
        self.bot_auth               = None

        self.temperature            = 0.8

        self.groq_api_type          = 'groq'
        self.groq_default_gpt       = 'auto'
        self.groq_default_class     = 'auto'
        self.groq_auto_continue     = 3
        self.groq_max_step          = 10
        self.groq_max_session       = 5
        self.groq_max_wait_sec      = 120
       
        self.groq_key_id            = None

        self.groq_a_enable          = False
        self.groq_a_nick_name       = ''
        self.groq_a_model           = None
        self.groq_a_token           = 0
        self.groq_a_use_tools       = 'no'

        self.groq_b_enable          = False
        self.groq_b_nick_name       = ''
        self.groq_b_model           = None
        self.groq_b_token           = 0
        self.groq_a_use_tools       = 'no'

        self.groq_v_enable          = False
        self.groq_v_nick_name       = ''
        self.groq_v_model           = None
        self.groq_v_token           = 0
        self.groq_v_use_tools       = 'no'

        self.groq_x_enable          = False
        self.groq_x_nick_name       = ''
        self.groq_x_model           = None
        self.groq_x_token           = 0
        self.groq_x_use_tools       = 'no'

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
                     groq_api_type,
                     groq_default_gpt, groq_default_class,
                     groq_auto_continue,
                     groq_max_step, groq_max_session,
                     groq_max_wait_sec,

                     groq_key_id,

                     groq_a_nick_name, groq_a_model, groq_a_token, 
                     groq_a_use_tools,
                     groq_b_nick_name, groq_b_model, groq_b_token, 
                     groq_b_use_tools,
                     groq_v_nick_name, groq_v_model, groq_v_token, 
                     groq_v_use_tools,
                     groq_x_nick_name, groq_x_model, groq_x_token, 
                     groq_x_use_tools,
                    ):

        # 認証
        self.bot_auth                   = None
        self.groq_key_id                = groq_key_id

        self.client = None
        if (groq_key_id[:1] == '<'):
            return False
        try:
            self.client  = groq.Groq(
                api_key=groq_key_id,
            )
        except Exception as e:
            print(e)
            return False

        # 設定
        self.groq_default_gpt           = groq_default_gpt
        self.groq_default_class         = groq_default_class
        if (str(groq_auto_continue)   not in ['', 'auto']):
            self.groq_auto_continue     = int(groq_auto_continue)
        if (str(groq_max_step)        not in ['', 'auto']):
            self.groq_max_step          = int(groq_max_step)
        if (str(groq_max_session)     not in ['', 'auto']):
            self.groq_max_session       = int(groq_max_session)
        if (str(groq_max_wait_sec)    not in ['', 'auto']):
            self.groq_max_wait_sec      = int(groq_max_wait_sec)

        # モデル取得
        self.models                     = {}
        self.get_models()

        #ymd = datetime.date.today().strftime('%Y/%m/%d')
        ymd = 'default'

        # groq チャットボット
        if (groq_a_nick_name != ''):
            self.groq_a_enable          = False
            self.groq_a_nick_name       = groq_a_nick_name
            self.groq_a_model           = groq_a_model
            self.groq_a_token           = int(groq_a_token)
            self.groq_a_use_tools       = groq_a_use_tools
            if (groq_a_model not in self.models):
                self.models[groq_a_model] = {"id": groq_a_model, "token": str(groq_a_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[groq_a_model]['date'] = ymd

        if (groq_b_nick_name != ''):
            self.groq_b_enable          = False
            self.groq_b_nick_name       = groq_b_nick_name
            self.groq_b_model           = groq_b_model
            self.groq_b_token           = int(groq_b_token)
            self.groq_b_use_tools       = groq_b_use_tools
            if (groq_b_model not in self.models):
                self.models[groq_b_model] = {"id": groq_b_model, "token": str(groq_b_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[groq_b_model]['date'] = ymd

        if (groq_v_nick_name != ''):
            self.groq_v_enable          = False
            self.groq_v_nick_name       = groq_v_nick_name
            self.groq_v_model           = groq_v_model
            self.groq_v_token           = int(groq_v_token)
            self.groq_v_use_tools       = groq_v_use_tools
            if (groq_v_model not in self.models):
                self.models[groq_v_model] = {"id": groq_v_model, "token": str(groq_v_token), "modality": "text+image?", "date": ymd, }
            else:
                #self.models[groq_v_model]['date'] = ymd
                self.models[groq_v_model]['modality'] = "text+image?"

        if (groq_x_nick_name != ''):
            self.groq_x_enable          = False
            self.groq_x_nick_name       = groq_x_nick_name
            self.groq_x_model           = groq_x_model
            self.groq_x_token           = int(groq_x_token)
            self.groq_x_use_tools       = groq_x_use_tools
            if (groq_x_model not in self.models):
                self.models[groq_x_model] = {"id": groq_x_model, "token": str(groq_x_token), "modality": "text+image?", "date": ymd, }
            #else:
            #    self.models[groq_x_model]['date'] = ymd

        # モデル
        hit = False
        if (self.groq_a_model != ''):
            self.groq_a_enable = True
            hit = True
        if (self.groq_b_model != ''):
            self.groq_b_enable = True
            hit = True
        if (self.groq_v_model != ''):
            self.groq_v_enable = True
            hit = True
        if (self.groq_x_model != ''):
            self.groq_x_enable = True
            hit = True

        if (hit == True):
            self.bot_auth = True
            return True
        else:
            return False

    def get_models(self, ):
        try:
            models = self.client.models.list()
            for model in models.data:
                #print(model, )
                key = model.id
                token = model.context_window
                unix_timestamp = model.created
                ymd = datetime.datetime.fromtimestamp(unix_timestamp).strftime("%Y/%m/%d")
                #print(key, )
                self.models[key] = {"id":key, "token": str(token), "modality":"text?", "date": ymd, }
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
                if (str(max_wait_sec) != str(self.groq_max_wait_sec)):
                    self.groq_max_wait_sec = int(max_wait_sec)
            if (a_model != ''):
                if (a_model != self.groq_a_model) and (a_model in self.models):
                    self.groq_a_enable = True
                    self.groq_a_model = a_model
                    self.groq_a_token = int(self.models[a_model]['token'])
            if (a_use_tools != ''):
                self.groq_a_use_tools = a_use_tools
            if (b_model != ''):
                if (b_model != self.groq_b_model) and (b_model in self.models):
                    self.groq_b_enable = True
                    self.groq_b_model = b_model
                    self.groq_b_token = int(self.models[b_model]['token'])
            if (b_use_tools != ''):
                self.groq_b_use_tools = b_use_tools
            if (v_model != ''):
                if (v_model != self.groq_v_model) and (v_model in self.models):
                    self.groq_v_enable = True
                    self.groq_v_model = v_model
                    self.groq_v_token = int(self.models[v_model]['token'])
            if (v_use_tools != ''):
                self.groq_v_use_tools = v_use_tools
            if (x_model != ''):
                if (x_model != self.groq_x_model) and (x_model in self.models):
                    self.groq_x_enable = True
                    self.groq_x_model = x_model
                    self.groq_x_token = int(self.models[x_model]['token'])
            if (x_use_tools != ''):
                self.groq_x_use_tools = x_use_tools
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

    def history2msg_gpt(self, history=[], ):
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
            self.print(session_id, ' Groq : Not Authenticate Error !')
            return res_text, res_path, res_files, res_name, res_api, res_history

        # モデル 設定
        res_name  = self.groq_a_nick_name
        res_api   = self.groq_a_model
        use_tools = self.groq_a_use_tools
        if  (chat_class == 'groq'):
            if (self.groq_b_enable == True):
                res_name  = self.groq_b_nick_name
                res_api   = self.groq_b_model
                use_tools = self.groq_b_use_tools

        # モデル 補正 (assistant)
        if ((chat_class == 'assistant') \
        or  (chat_class == 'コード生成') \
        or  (chat_class == 'コード実行') \
        or  (chat_class == '文書検索') \
        or  (chat_class == '複雑な会話') \
        or  (chat_class == 'アシスタント') \
        or  (model_select == 'x')):
            if (self.groq_x_enable == True):
                res_name  = self.groq_x_nick_name
                res_api   = self.groq_x_model
                use_tools = self.groq_x_use_tools

        # model 指定
        if (self.groq_a_nick_name != ''):
            if (inpText.strip()[:len(self.groq_a_nick_name)+1].lower() == (self.groq_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.groq_a_nick_name)+1:]
        if (self.groq_b_nick_name != ''):
            if (inpText.strip()[:len(self.groq_b_nick_name)+1].lower() == (self.groq_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.groq_b_nick_name)+1:]
                if   (self.groq_b_enable == True):
                        res_name  = self.groq_b_nick_name
                        res_api   = self.groq_b_model
                        use_tools = self.groq_b_use_tools
        if (self.groq_v_nick_name != ''):
            if (inpText.strip()[:len(self.groq_v_nick_name)+1].lower() == (self.groq_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.groq_v_nick_name)+1:]
                if   (self.groq_v_enable == True):
                    if  (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        res_name  = self.groq_v_nick_name
                        res_api   = self.groq_v_model
                        use_tools = self.groq_v_use_tools
                elif (self.groq_x_enable == True):
                        res_name  = self.groq_x_nick_name
                        res_api   = self.groq_x_model
                        use_tools = self.groq_x_use_tools
        if (self.groq_x_nick_name != ''):
            if (inpText.strip()[:len(self.groq_x_nick_name)+1].lower() == (self.groq_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.groq_x_nick_name)+1:]
                if   (self.groq_x_enable == True):
                        res_name  = self.groq_x_nick_name
                        res_api   = self.groq_x_model
                        use_tools = self.groq_x_use_tools
                elif (self.groq_b_enable == True):
                        res_name  = self.groq_b_nick_name
                        res_api   = self.groq_b_model
                        use_tools = self.groq_b_use_tools
        if   (inpText.strip()[:5].lower() == ('riki,')):
            inpText = inpText.strip()[5:]
            if   (self.groq_x_enable == True):
                        res_name  = self.groq_x_nick_name
                        res_api   = self.groq_x_model
                        use_tools = self.groq_x_use_tools
            elif (self.groq_b_enable == True):
                        res_name  = self.groq_b_nick_name
                        res_api   = self.groq_b_model
                        use_tools = self.groq_b_use_tools
        elif (inpText.strip()[:7].lower() == ('vision,')):
            inpText = inpText.strip()[7:]
            if   (self.groq_v_enable == True):
                if  (len(image_urls) > 0) \
                and (len(image_urls) == len(upload_files)):
                        res_name  = self.groq_v_nick_name
                        res_api   = self.groq_v_model
                        use_tools = self.groq_v_use_tools
            elif (self.groq_x_enable == True):
                        res_name  = self.groq_x_nick_name
                        res_api   = self.groq_x_model
                        use_tools = self.groq_x_use_tools
        elif (inpText.strip()[:10].lower() == ('assistant,')):
            inpText = inpText.strip()[10:]
            if   (self.groq_x_enable == True):
                        res_name  = self.groq_x_nick_name
                        res_api   = self.groq_x_model
                        use_tools = self.groq_x_use_tools
            elif (self.groq_b_enable == True):
                        res_name  = self.groq_b_nick_name
                        res_api   = self.groq_b_model
                        use_tools = self.groq_b_use_tools
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
            res_name  = self.groq_a_nick_name
            res_api   = self.groq_a_model
            use_tools = self.groq_a_use_tools
            if (self.groq_b_enable == True):
                if (len(upload_files) > 0) \
                or (len(inpText) > 1000):
                    res_name  = self.groq_b_nick_name
                    res_api   = self.groq_b_model
                    use_tools = self.groq_b_use_tools

        # モデル 補正 (vision)
        if  (len(image_urls) > 0) \
        and (len(image_urls) == len(upload_files)):
            if   (self.groq_v_enable == True):
                res_name  = self.groq_v_nick_name
                res_api   = self.groq_v_model
                use_tools = self.groq_v_use_tools
            elif (self.groq_x_enable == True):
                res_name  = self.groq_x_nick_name
                res_api   = self.groq_x_model
                use_tools = self.groq_x_use_tools

        # history 追加・圧縮 (古いメッセージ)
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
        res_history = self.history_zip1(history=res_history, )

        # メッセージ作成
        if (model_select != 'v'):
            msg = self.history2msg_gpt(history=res_history, )
        else:
            msg = self.history2msg_vision(history=res_history, image_urls=image_urls,)

        # ストリーム実行?
        if (session_id == 'admin'):
            #stream = True
            print(' Groq : stream=False, ')
            stream = False
        else:
            stream = False

        # ツール設定
        print(' Groq : functions=[], ')
        functions = []

        # 実行ループ
        #try:
        if True:

            n = 0
            function_name = ''
            while (function_name != 'exit') and (n < int(max_step)):

                # 結果
                res_role      = ''
                res_content   = ''

                # GPT
                n += 1
                self.print(session_id, f" Groq : { res_name.lower() }, { res_api }, pass={ n }, ")

                # Stream 表示
                if (stream == True):
                    response = self.client.chat.completions.create(
                            model           = res_api,
                            messages        = msg,
                            temperature     = float(temperature),
                            timeout         = self.groq_max_wait_sec,
                            stream          = stream, 
                            )

                    chkTime     = time.time()
                    for chunk in response:
                        if ((time.time() - chkTime) > self.groq_max_wait_sec):
                            break
                        delta   = chunk.choices[0].delta
                        if (delta is not None):
                            if (delta.content is not None):
                                #res_role    = delta.role
                                res_role    = 'assistant'
                                content     = delta.content
                                res_content += content
                                self.stream(session_id, content)

                    # 改行
                    if (res_content != ''):
                        self.print(session_id, )

                # 通常実行
                if (stream == False):

                    if   (model_select == 'v') and (len(image_urls) > 0):
                        null_history = self.history_add(history=[], sysText=sysText, reqText=reqText, inpText=inpText, )
                        msg = self.history2msg_vision(history=null_history, image_urls=image_urls,)
                        response = self.client.chat.completions.create(
                                model           = res_api,
                                messages        = msg,
                                temperature     = float(temperature),
                                timeout         = self.groq_max_wait_sec, 
                                stream          = stream, 
                                )

                    elif (len(functions) != 0):
                        # ツール設定
                        tools = []
                        for f in range(len(functions)):
                            tools.append({"type": "function", "function": functions[f]})
                            response = self.client.chat.completions.create(
                                model           = res_api,
                                messages        = msg,
                                temperature     = float(temperature),
                                tools           = tools,
                                tool_choice     = 'auto',
                                timeout         = self.groq_max_wait_sec,
                                stream          = stream, 
                                )

                    else:
                        # ノーマル
                        if (jsonSchema is None) or (jsonSchema == ''):                        
                            response = self.client.chat.completions.create(
                                model           = res_api,
                                messages        = msg,
                                temperature     = float(temperature),
                                timeout         = self.groq_max_wait_sec,
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
                                    timeout         = self.groq_max_wait_sec, 
                                    response_format = { "type": "json_object" },
                                    stream          = stream, 
                                    )
                            # スキーマ指定有り
                            else:
                                response = self.client.chat.completions.create(
                                    model           = res_api,
                                    messages        = msg,
                                    temperature     = float(temperature),
                                    timeout         = self.groq_max_wait_sec, 
                                    response_format = { "type": "json_schema", "json_schema": schema },
                                    stream          = stream, 
                                    )

                    # response 処理
                    try:
                        res_role    = str(response.choices[0].message.role)
                        res_content = str(response.choices[0].message.content)
                    except:
                        pass

                # 実行終了
                function_name = 'exit'
                if (res_content.strip() != ''):
                    res_text += res_content.rstrip() + '\n'

                    self.seq += 1
                    dic = {'seq': self.seq, 'time': time.time(), 'role': 'assistant', 'name': '', 'content': res_content }
                    res_history.append(dic)

            # 正常回答
            if (res_text != ''):
                self.print(session_id, f" Groq : { res_name.lower() }, complete.")
            else:
                self.print(session_id,  ' Groq : Error !')

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
            self.print(session_id, ' Groq : Not Authenticate Error !')
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

        # groq
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

        #groqAPI = speech_bot_groq._groqAPI()
        groqAPI = _groqAPI()

        api_type = groq_key.getkey('groq','groq_api_type')
        print(api_type)

        log_queue = queue.Queue()
        res = groqAPI.init(log_queue=log_queue, )

        res = groqAPI.authenticate('groq',
                            api_type,
                            groq_key.getkey('groq','groq_default_gpt'), groq_key.getkey('groq','groq_default_class'),
                            groq_key.getkey('groq','groq_auto_continue'),
                            groq_key.getkey('groq','groq_max_step'), groq_key.getkey('groq','groq_max_session'),
                            groq_key.getkey('groq','groq_max_wait_sec'),
                            groq_key.getkey('groq','groq_key_id'),
                            groq_key.getkey('groq','groq_a_nick_name'), groq_key.getkey('groq','groq_a_model'), groq_key.getkey('groq','groq_a_token'),
                            groq_key.getkey('groq','groq_a_use_tools'),
                            groq_key.getkey('groq','groq_b_nick_name'), groq_key.getkey('groq','groq_b_model'), groq_key.getkey('groq','groq_b_token'),
                            groq_key.getkey('groq','groq_b_use_tools'),
                            groq_key.getkey('groq','groq_v_nick_name'), groq_key.getkey('groq','groq_v_model'), groq_key.getkey('groq','groq_v_token'),
                            groq_key.getkey('groq','groq_v_use_tools'),
                            groq_key.getkey('groq','groq_x_nick_name'), groq_key.getkey('groq','groq_x_model'), groq_key.getkey('groq','groq_x_token'),
                            groq_key.getkey('groq','groq_x_use_tools'),
                            )
        print('authenticate:', res, )
        if (res == True):
            
            function_modules = {}
            filePath         = []

            if True:
                sysText = None
                reqText = ''
                inpText = 'おはようございます。'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, groqAPI.history = \
                    groqAPI.chatBot(    chat_class='auto', model_select='auto', 
                                        session_id='admin', history=groqAPI.history, function_modules=function_modules,
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
                res_text, res_path, res_files, res_name, res_api, groqAPI.history = \
                    groqAPI.chatBot(    chat_class='auto', model_select='auto', 
                                        session_id='admin', history=groqAPI.history, function_modules=function_modules,
                                        sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                        inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print('', res_text)
                print()

            if False:
                print('[History]')
                for h in range(len(groqAPI.history)):
                    print(groqAPI.history[h])
                groqAPI.history = []



