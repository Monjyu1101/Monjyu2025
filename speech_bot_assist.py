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

import glob
import socket
qHOSTNAME = socket.gethostname().lower()

qPath_temp           = 'temp/'
qPath_output         = 'temp/output/'
qPath_chat_work      = 'temp/chat_work/'


# assistant チャットボット
import openai

import speech_bot_assist_key  as assist_key



# base64 encode
def base64_encode(file_path):
    with open(file_path, "rb") as input_file:
        return base64.b64encode(input_file.read()).decode('utf-8')



class _assistAPI:

    def __init__(self, ):
        self.log_queue              = None
        self.bot_auth               = None

        self.temperature            = 0.8

        self.assist_api_type        = 'openai'
        self.assist_default_gpt     = 'auto'
        self.assist_default_class   = 'auto'
        self.assist_auto_continue   = 3
        self.assist_max_step        = 10
        self.assist_max_session     = 5
        self.assist_max_wait_sec    = 120
       
        self.openai_organization    = None
        self.openai_key_id          = None
        self.azure_endpoint         = None
        self.azure_version          = None
        self.azure_key_id           = None

        self.assist_a_enable        = False
        self.assist_a_nick_name     = ''
        self.assist_a_model         = None
        self.assist_a_token         = 0
        self.assist_a_use_tools     = 'no'

        self.assist_b_enable        = False
        self.assist_b_nick_name     = ''
        self.assist_b_model         = None
        self.assist_b_token         = 0
        self.assist_b_use_tools     = 'no'

        self.assist_v_enable        = False
        self.assist_v_nick_name     = ''
        self.assist_v_model         = None
        self.assist_v_token         = 0
        self.assist_v_use_tools     = 'no'

        self.assist_x_enable        = False
        self.assist_x_nick_name     = ''
        self.assist_x_model         = None
        self.assist_x_token         = 0
        self.assist_x_use_tools     = 'no'

        self.models                 = {}
        self.history                = []

        self.seq                    = 0
        self.reset()

        self.assistant_name         = qHOSTNAME
        self.assistant_id           = {}
        self.thread_id              = {}

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
                     assist_api_type,
                     assist_default_gpt, assist_default_class,
                     assist_auto_continue,
                     assist_max_step, assist_max_session,
                     assist_max_wait_sec,

                     openai_organization, openai_key_id,
                     azure_endpoint, azure_version, azure_key_id,

                     assist_a_nick_name, assist_a_model, assist_a_token, 
                     assist_a_use_tools, 
                     assist_b_nick_name, assist_b_model, assist_b_token, 
                     assist_b_use_tools, 
                     assist_v_nick_name, assist_v_model, assist_v_token, 
                     assist_v_use_tools, 
                     assist_x_nick_name, assist_x_model, assist_x_token, 
                     assist_x_use_tools, 
                    ):

        # 認証
        self.bot_auth               = None
        self.assist_api_type        = assist_api_type
        self.openai_organization    = openai_organization
        self.openai_key_id          = openai_key_id
        self.azure_endpoint         = azure_endpoint
        self.azure_version          = azure_version
        self.azure_key_id           = azure_key_id

        self.client = None
        try:
            # openai
            if (assist_api_type != 'azure'):
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
        self.assist_default_gpt         = assist_default_gpt
        self.assist_default_class       = assist_default_class
        if (str(assist_auto_continue)   not in ['', 'auto']):
            self.assist_auto_continue   = int(assist_auto_continue)
        if (str(assist_max_step)        not in ['', 'auto']):
            self.assist_max_step        = int(assist_max_step)
        if (str(assist_max_session)     not in ['', 'auto']):
            self.assist_max_session     = int(assist_max_session)
        if (str(assist_max_wait_sec)    not in ['', 'auto']):
            self.assist_max_wait_sec    = int(assist_max_wait_sec)

        # モデル取得
        self.models                     = {}
        self.get_models()

        #ymd = datetime.date.today().strftime('%Y/%m/%d')
        ymd = 'default'

        # assistant チャットボット
        if (assist_a_nick_name != ''):
            self.assist_a_enable        = False
            self.assist_a_nick_name     = assist_a_nick_name
            self.assist_a_model         = assist_a_model
            self.assist_a_token         = int(assist_a_token)
            self.assist_a_use_tools     = assist_a_use_tools
            if (assist_a_model not in self.models):
                self.models[assist_a_model] = {"id": assist_a_model, "token": str(assist_a_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[assist_a_model]['date'] = ymd

        if (assist_b_nick_name != ''):
            self.assist_b_enable        = False
            self.assist_b_nick_name     = assist_b_nick_name
            self.assist_b_model         = assist_b_model
            self.assist_b_token         = int(assist_b_token)
            self.assist_b_use_tools     = assist_b_use_tools
            if (assist_b_model not in self.models):
                self.models[assist_b_model] = {"id": assist_b_model, "token": str(assist_b_token), "modality": "text?", "date": ymd, }
            #else:
            #    self.models[assist_b_model]['date'] = ymd

        if (assist_v_nick_name != ''):
            self.assist_v_enable        = False
            self.assist_v_nick_name     = assist_v_nick_name
            self.assist_v_model         = assist_v_model
            self.assist_v_token         = int(assist_v_token)
            self.assist_v_use_tools     = assist_v_use_tools
            if (assist_v_model not in self.models):
                self.models[assist_v_model] = {"id": assist_v_model, "token": str(assist_v_token), "modality": "text+image?", "date": ymd, }
            else:
                #self.models[assist_v_model]['date'] = ymd
                self.models[assist_v_model]['modality'] = "text+image?"

        if (assist_x_nick_name != ''):
            self.assist_x_enable        = False
            self.assist_x_nick_name     = assist_x_nick_name
            self.assist_x_model         = assist_x_model
            self.assist_x_token         = int(assist_x_token)
            self.assist_x_use_tools     = assist_x_use_tools
            if (assist_x_model not in self.models):
                self.models[assist_x_model] = {"id": assist_x_model, "token": str(assist_x_token), "modality": "text+image?", "date": ymd, }
            #else:
            #    self.models[assist_x_model]['date'] = ymd

        # モデル
        hit = False
        if (self.assist_a_model != ''):
            self.assist_a_enable = True
            hit = True
        if (self.assist_b_model != ''):
            self.assist_b_enable = True
            hit = True
        if (self.assist_v_model != ''):
            self.assist_v_enable = True
            hit = True
        if (self.assist_x_model != ''):
            self.assist_x_enable = True
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
                if (str(max_wait_sec) != str(self.assist_max_wait_sec)):
                    self.assist_max_wait_sec = int(max_wait_sec)
            if (a_model != ''):
                if (a_model != self.assist_a_model) and (a_model in self.models):
                    self.assist_a_enable = True
                    self.assist_a_model = a_model
                    self.assist_a_token = int(self.models[a_model]['token'])
            if (a_use_tools != ''):
                self.assist_a_use_tools = a_use_tools
            if (b_model != ''):
                if (b_model != self.assist_b_model) and (b_model in self.models):
                    self.assist_b_enable = True
                    self.assist_b_model = b_model
                    self.assist_b_token = int(self.models[b_model]['token'])
            if (b_use_tools != ''):
                self.assist_b_use_tools = b_use_tools
            if (v_model != ''):
                if (v_model != self.assist_v_model) and (v_model in self.models):
                    self.assist_v_enable = True
                    self.assist_v_model = v_model
                    self.assist_v_token = int(self.models[v_model]['token'])
            if (v_use_tools != ''):
                self.assist_v_use_tools = v_use_tools
            if (x_model != ''):
                if (x_model != self.assist_x_model) and (x_model in self.models):
                    self.assist_x_enable = True
                    self.assist_x_model = x_model
                    self.assist_x_token = int(self.models[x_model]['token'])
            if (x_use_tools != ''):
                self.assist_x_use_tools = x_use_tools
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



    def vectorStore_del(self, session_id='admin', assistant_id=None, assistant_name='', ):

        # 2024/04/21時点 azure 未対応
        if (self.assist_api_type == 'azure'):
            return False

        # vector store 削除
        vector_stores = self.client.vector_stores.list()
        for v in range(len(vector_stores.data)):
            vs_id   = vector_stores.data[v].id
            vs_name = vector_stores.data[v].name
            if (vs_name == assistant_name):

                vs_files = self.client.vector_stores.files.list(vector_store_id=vs_id)

                for f in range(len(vs_files.data)):
                    file_id   = vs_files.data[f].id
                    self.client.files.delete(file_id=file_id, )
                self.print(session_id, f"  vector store delete! ('{ vs_name }')")
                self.client.vector_stores.delete(vector_store_id=vs_id)

                break
        
        return True

    def vectorStore_set(self, session_id='admin', retrievalFiles_path='_extensions/retrieval_files/', assistant_id=None, assistant_name='', ):
        vectorStore_ids = []

        # 2024/04/21時点 azure 未対応
        if (self.assist_api_type == 'azure'):
            return vectorStore_ids

        # ファイル一覧
        proc_files = []
        path_files = glob.glob(retrievalFiles_path + '*.*')
        path_files.sort()
        if (len(path_files) > 0):
            for f in path_files:
                proc_files.append(os.path.basename(f))

        # マッチング検査 違いがあれば vector store 削除
        vector_stores = self.client.vector_stores.list()
        for v in range(len(vector_stores.data)):
            vs_id   = vector_stores.data[v].id
            vs_name = vector_stores.data[v].name
            # bug?
            if (vs_id in ['vs_67a9cb0bdd748191aa1a2892c6612d68']):
                #self.client.vector_stores.delete(vector_store_id=vs_id)
                pass
            else:
                if (vs_name == assistant_name):
                    vs_files = self.client.vector_stores.files.list(vector_store_id=vs_id)

                    vectorStore_ids = [vs_id]
                    if (len(proc_files) != len(vs_files.data)):
                        vectorStore_ids = []
                    else:
                        for f in range(len(vs_files.data)):
                            file_id   = vs_files.data[f].id
                            file_info = self.client.files.retrieve(file_id=file_id, )
                            file_name = file_info.filename
                            if (file_name not in proc_files):
                                vectorStore_ids = []
                                break

                    if (len(vectorStore_ids) == 0):
                        for f in range(len(vs_files.data)):
                            file_id   = vs_files.data[f].id
                            self.client.files.delete(file_id=file_id, )
                        self.print(session_id, f" Assist : Delete vector store = '{ vs_name }', ")
                        self.client.vector_stores.delete(vector_store_id=vs_id)

                    break

        # 転送不要
        if (len(vectorStore_ids) == len(proc_files)):
            return vectorStore_ids

        # vector store 作成
        if (len(proc_files) > 0):

            # ファイル
            upload_ids   = []
            for proc_file in proc_files:
                file_name = retrievalFiles_path + proc_file
                if (os.path.isfile(file_name)):

                    # アップロード済み確認
                    file_id = None
                    assist_files_list = self.client.files.list()
                    for n in range(len(assist_files_list.data)):
                        if (proc_file == assist_files_list.data[n].filename):
                            file_id   = assist_files_list.data[n].id
                            print(f" Assist : Hit file_name = '{ proc_file }', { file_id }")
                            break

                    # アップロード
                    if (file_id == None):
                        try:
                            # アップロード
                            file = open(file_name, 'rb')
                            upload = self.client.files.create(
                                        file    = file,
                                        purpose = 'assistants', )
                            file_id = upload.id
                            print(f" Assist : Upload file_name = '{ proc_file }', { file_id }")
                        except Exception as e:
                            print(e)

                    if (file_id != None):
                        upload_ids.append(file_id)

            # ベクターストア作成
            if (len(upload_ids) > 0):
                try:

                    vector_store = self.client.vector_stores.create(
                                        name = assistant_name,
                                        # 2025/02/01現在、1GByteまで無料
                                        #expires_after = {
                                        #   "anchor": "last_active_at",
                                        #   "days": 2
                                        #}
                                    )

                    file_batch = self.client.vector_stores.file_batches.create_and_poll(
                                        vector_store_id = vector_store.id,
                                        file_ids        = upload_ids,
                                    )

                    self.print(session_id, f" Assist : { file_batch.status }")

                    vectorStore_ids = [vector_store.id]

                except Exception as e:
                    print(e)

        # デバッグ用 アップロード確認
        if False:
            vector_stores = self.client.vector_stores.list()
            for v in range(len(vector_stores.data)):
                vs_id   = vector_stores.data[v].id
                vs_name = vector_stores.data[v].name
                if (vs_name == assistant_name):
                    self.print(session_id, vs_name)
                    vs_files = self.client.vector_stores.files.list(vector_store_id=vs_id)
                    for f in range(len(vs_files.data)):
                        file_id   = vs_files.data[f].id
                        file_info = self.client.files.retrieve(
                            file_id=file_id, )
                        file_name = file_info.filename
                        self.print(session_id, file_name)

        return vectorStore_ids

    def threadFile_del(self, session_id='admin', assistant_id=None, assistant_name='', ):

        # 2024/04/21時点 azure 未対応
        if (self.assist_api_type == 'azure'):
            return False

        assist_files_list = self.client.files.list()
        for f in range(len(assist_files_list.data)):
            file_id   = assist_files_list.data[f].id
            file_name = assist_files_list.data[f].filename

            x = len(assistant_name)
            if (file_name[:x] == assistant_name):
                res = self.client.files.delete(
                    file_id=file_id, )

        return True

    def threadFile_set(self, session_id='admin', upload_files=[], assistant_id=None, assistant_name='', ):
        upload_ids = []

        # 2024/04/21時点 azure 未対応
        if (self.assist_api_type == 'azure'):
            return upload_ids

        if (not os.path.isdir(qPath_chat_work)):
            os.makedirs(qPath_chat_work)
        for upload_file in upload_files:
            base_name   = os.path.basename(upload_file)
            work_name   = assistant_name + '_' + base_name
            upload_work = qPath_chat_work + work_name
            shutil.copy(upload_file, upload_work)

            # 既に存在なら、置換えの為、削除
            assist_files_list = self.client.files.list()
            for f in range(len(assist_files_list.data)):
                file_id   = assist_files_list.data[f].id
                file_name = assist_files_list.data[f].filename
                if (file_name == work_name):
                    res = self.client.files.delete(
                        file_id=file_id, )

            # アップロード
            upload = self.client.files.create(
                file = open(upload_work, 'rb'),
                purpose='assistants', )
            upload_ids.append(upload.id)

            self.print(session_id, f" Assist : Upload ... { upload.id }, { base_name },")

            # proc? wait
            #time.sleep(0.50)

        return upload_ids

    def threadFile_reset(self, session_id='admin', upload_ids=[], assistant_id=None, assistant_name='', ):

        # 2024/04/21時点 azure 未対応
        if (self.assist_api_type == 'azure'):
            return False

        # 削除
        for upload_id in upload_ids:
            try:
                res = self.client.files.delete(
                    file_id=upload_id, )
                self.print(session_id, f" Assist : Delete ... { upload_id },")
            except:
                pass

        return True

    def my_assistant_update(self, session_id='admin', my_assistant_id=None, my_assistant_name='',
                            model_name='gpt-4o', use_tools='yes', instructions='', 
                            function_list=[], vectorStore_ids=[], upload_ids=[], ):

        try:

            # ツール設定
            tools = []
            if (use_tools.lower().find('yes') >= 0):
                if (model_name[:1].lower() != 'o'): # o1, o3, ... 以外
                    tools.append({"type": "code_interpreter"})
                    if (len(vectorStore_ids) > 0):
                        tools.append({"type": "file_search"})
                if (len(function_list) != 0):
                    for f in range(len(function_list)):
                        tools.append({"type": "function", "function": function_list[f]})
            #print(tools)

            # アシスタント取得
            assistant = self.client.beta.assistants.retrieve(
                assistant_id = my_assistant_id, )
            try:
                as_vector_ids = []
                as_vector_ids = assistant.tool_resources.file_search.vector_store_ids
            except:
                pass
            try:
                as_file_ids   = []
                as_file_ids   = assistant.tool_resources.code_interpreter.file_ids
            except:
                pass

            # アシスタント更新
            change_flag = False
            if (model_name      != assistant.model):
                change_flag = True
                self.print(session_id, f" Assist : Change model, { model_name },")
            if (instructions    != assistant.instructions):
                change_flag = True
                self.print(session_id, f" Assist : Change instructions ...")
            if (len(tools)      != len(assistant.tools)):
                change_flag = True
                self.print(session_id, f" Assist : Change tools ...")
                #self.print(tools, )
                #self.print(assistant.tools, )
            if (vectorStore_ids != as_vector_ids):
                change_flag = True
                self.print(session_id, f" Assist : Change vector store ids ...")
            if (upload_ids      != as_file_ids):
                change_flag = True
                self.print(session_id, f" Assist : Change file ids ...")

            if (change_flag != True):
                return False
            else:
                self.print(session_id, f" Assist : Update assistant ( name='{ my_assistant_name }', model={ model_name }, ) ")

                # OPENAI
                if (self.assist_api_type != 'azure'):

                    tool_resources = {}
                    if (model_name[:1].lower() != 'o'): # o1, o3, ... 以外
                        if (len(vectorStore_ids) > 0):
                            tool_resources["file_search"] = { "vector_store_ids": vectorStore_ids }
                        if (len(upload_ids) > 0):
                            tool_resources["code_interpreter"] = { "file_ids": upload_ids }

                    assistant = self.client.beta.assistants.update(
                                        assistant_id = my_assistant_id,
                                        model        = model_name,
                                        instructions = instructions,
                                        tools        = tools,
                                        timeout      = self.assist_max_wait_sec,
                                        tool_resources = tool_resources,
                                    )

                # Azure
                else:

                    assistant = self.client.beta.assistants.update(
                                        assistant_id = my_assistant_id,
                                        model        = model_name,
                                        instructions = instructions,
                                        tools        = tools,
                                        timeout      = self.assist_max_wait_sec,

                                        # 2024/04/21時点 azure 未対応
                                        #tool_resources = {
                                        #    "file_search": {
                                        #        "vector_store_ids": vectorStore_ids
                                        #        },
                                        #    "code_interpreter": {
                                        #        "file_ids": upload_ids
                                        #        }
                                        #    },
                                    )

        except Exception as e:
            print(e)
            return False
        return True

    def run_assist(self, chat_class='assist', model_select='auto',
                      nick_name=None, model_name=None,
                      session_id='admin', history=[], function_modules={},
                      sysText=None, reqText=None, inpText='こんにちは',
                      upload_files=[], image_urls=[],
                      temperature=0.8, max_step=10, jsonSchema=None, ):

        function_list = []
        for module_dic in function_modules.values():
            function_list.append(module_dic['function'])

        # 戻り値
        res_text        = ''
        res_path        = ''
        res_files       = []
        res_name        = None
        res_api         = None
        res_history     = history

        if (self.bot_auth is None):
            self.print(session_id, ' Assist : Not Authenticate Error !')
            return res_text, res_path, res_files, res_name, res_api, res_history

        # モデル 設定
        res_name  = self.assist_a_nick_name
        res_api   = self.assist_a_model
        use_tools = self.assist_a_use_tools
        if  (chat_class == 'assist'):
            if (self.assist_b_enable == True):
                res_name  = self.assist_b_nick_name
                res_api   = self.assist_b_model
                use_tools = self.assist_b_use_tools

        # モデル 補正 (assist)
        if ((chat_class == 'assistant') \
        or  (chat_class == 'コード生成') \
        or  (chat_class == 'コード実行') \
        or  (chat_class == '文書検索') \
        or  (chat_class == '複雑な会話') \
        or  (chat_class == 'アシスタント') \
        or  (model_select == 'x')):
            if (self.assist_x_enable == True):
                res_name  = self.assist_x_nick_name
                res_api   = self.assist_x_model
                use_tools = self.assist_x_use_tools

        # model 指定
        if (self.assist_a_nick_name != ''):
            if (inpText.strip()[:len(self.assist_a_nick_name)+1].lower() == (self.assist_a_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.assist_a_nick_name)+1:]
        if (self.assist_b_nick_name != ''):
            if (inpText.strip()[:len(self.assist_b_nick_name)+1].lower() == (self.assist_b_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.assist_b_nick_name)+1:]
                if   (self.assist_b_enable == True):
                        res_name  = self.assist_b_nick_name
                        res_api   = self.assist_b_model
                        use_tools = self.assist_b_use_tools
        if (self.assist_v_nick_name != ''):
            if (inpText.strip()[:len(self.assist_v_nick_name)+1].lower() == (self.assist_v_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.assist_v_nick_name)+1:]
                if   (self.assist_v_enable == True):
                    if  (len(image_urls) > 0) \
                    and (len(image_urls) == len(upload_files)):
                        res_name  = self.assist_v_nick_name
                        res_api   = self.assist_v_model
                        use_tools = self.assist_v_use_tools
                elif (self.assist_x_enable == True):
                        res_name  = self.assist_x_nick_name
                        res_api   = self.assist_x_model
                        use_tools = self.assist_x_use_tools
        if (self.assist_x_nick_name != ''):
            if (inpText.strip()[:len(self.assist_x_nick_name)+1].lower() == (self.assist_x_nick_name.lower() + ',')):
                inpText = inpText.strip()[len(self.assist_x_nick_name)+1:]
                if   (self.assist_x_enable == True):
                        res_name  = self.assist_x_nick_name
                        res_api   = self.assist_x_model
                        use_tools = self.assist_x_use_tools
                elif (self.assist_b_enable == True):
                        res_name  = self.assist_b_nick_name
                        res_api   = self.assist_b_model
                        use_tools = self.assist_b_use_tools
        if   (inpText.strip()[:5].lower() == ('riki,')):
            inpText = inpText.strip()[5:]
            if   (self.assist_x_enable == True):
                        res_name  = self.assist_x_nick_name
                        res_api   = self.assist_x_model
                        use_tools = self.assist_x_use_tools
            elif (self.assist_b_enable == True):
                        res_name  = self.assist_b_nick_name
                        res_api   = self.assist_b_model
                        use_tools = self.assist_b_use_tools
        elif (inpText.strip()[:7].lower() == ('vision,')):
            inpText = inpText.strip()[7:]
            if   (self.assist_v_enable == True):
                if  (len(image_urls) > 0) \
                and (len(image_urls) == len(upload_files)):
                        res_name  = self.assist_v_nick_name
                        res_api   = self.assist_v_model
                        use_tools = self.assist_v_use_tools
            elif (self.assist_x_enable == True):
                        res_name  = self.assist_x_nick_name
                        res_api   = self.assist_x_model
                        use_tools = self.assist_x_use_tools
        elif (inpText.strip()[:10].lower() == ('assistant,')):
            inpText = inpText.strip()[10:]
            if   (self.assist_x_enable == True):
                        res_name  = self.assist_x_nick_name
                        res_api   = self.assist_x_model
                        use_tools = self.assist_x_use_tools
            elif (self.assist_b_enable == True):
                        res_name  = self.assist_b_nick_name
                        res_api   = self.assist_b_model
                        use_tools = self.assist_b_use_tools
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

        # history 追加・圧縮 (古いメッセージ)
        res_history = self.history_add(history=res_history, sysText=sysText, reqText=reqText, inpText=inpText, )
        res_history = self.history_zip1(history=res_history, )

        # 結果
        res_role      = None
        res_content   = None

        upload_ids    = []

        exit_status   = None
        last_status   = None

        # 動作設定
        instructions = sysText
        if (instructions is None) or (instructions == ''):
            instructions = 'あなたは美しい日本語を話す賢いアシスタントです。'

        # アシスタント確認
        my_assistant_name   = self.assistant_name + '-' + str(session_id)
        my_assistant_id     = self.assistant_id.get(str(session_id))

        # アシスタント検索
        assistants = self.client.beta.assistants.list(
            order = "desc",
            limit = "100", )
        for a in range(len(assistants.data)):
            assistant = assistants.data[a]
            if (assistant.name == my_assistant_name):
                my_assistant_id = assistant.id
                break

        # モデルの変更時は削除
        if (my_assistant_id is not None):
            if (res_api != assistant.model):
                self.print(session_id, f" Assist : Change model, { res_api },")

                for assistant in assistants.data:
                    if (assistant.name == my_assistant_name):
                        self.print(session_id, f" Assist : Delete assistant ( name='{ assistant.name }', ) ")

                        # アシスタント削除
                        try:
                            res = self.client.beta.assistants.delete(assistant_id = assistant.id, )
                        except:
                            pass
                        my_assistant_id = None
                        break

        # アシスタント生成
        if (my_assistant_id is None):

            # アシスタント検索
            assistants = self.client.beta.assistants.list(
                order = "desc",
                limit = "100", )

            # (最大セッション以上の)アシスタント削除
            if (self.assist_max_session > 0) and (len(assistants.data) > 0):
                for a in range(self.assist_max_session -1 , len(assistants.data)):
                    assistant = assistants.data[a]
                    self.print(session_id, f" Assist : Delete assistant ( name='{ assistant.name }', ) ")

                    # vector store 削除
                    res = self.vectorStore_del( session_id  = session_id,
                                                assistant_id   = my_assistant_id, 
                                                assistant_name = my_assistant_name, )

                    # ファイル 削除
                    res = self.threadFile_del(  session_id  = session_id,
                                                assistant_id   = my_assistant_id,
                                                assistant_name = my_assistant_name, )

                    # アシスタント削除
                    try:
                        res = self.client.beta.assistants.delete(assistant_id = assistant.id, )
                    except:
                        pass

            # アシスタント生成
            self.print(session_id, f" Assist : Create assistant ( name='{ my_assistant_name }', model={ res_api }, ) ")
            assistant = self.client.beta.assistants.create(
                    name     = my_assistant_name,
                    model    = res_api,
                    instructions = instructions,
                    tools    = [], )
            my_assistant_id = assistant.id
            self.assistant_id[str(session_id)] = my_assistant_id

        # アシスタント更新
        if (my_assistant_id is not None):

            # vector store 作成
            vectorStore_ids = self.vectorStore_set(     session_id      = session_id,
                                                        retrievalFiles_path = '_extensions/retrieval_files/',
                                                        assistant_id       = my_assistant_id, 
                                                        assistant_name     = my_assistant_name, )

            # ファイルアップロード
            upload_ids = self.threadFile_set(           session_id      = session_id,
                                                        upload_files    = upload_files,
                                                        assistant_id       = my_assistant_id,
                                                        assistant_name     = my_assistant_name, )
            #self.print(session_id, f"##{ upload_ids }##")
            # proc? wait
            #if (len(upload_files) > 0):
            #    time.sleep(1.00 * len(upload_files))

            res = self.my_assistant_update(                session_id        = session_id,
                                                        my_assistant_id   = my_assistant_id,
                                                        my_assistant_name = my_assistant_name,
                                                        model_name        = res_api, 
                                                        use_tools         = use_tools,
                                                        instructions      = instructions, 
                                                        function_list     = function_list,
                                                        vectorStore_ids   = vectorStore_ids,
                                                        upload_ids        = upload_ids, )

        # スレッド確認
        my_thread_id = self.thread_id.get(str(session_id))
        if (my_thread_id is None):

            # スレッド生成
            self.print(session_id, f" Assist : Create thread    ( name='{ my_assistant_name }', ) ")
            thread = self.client.beta.threads.create(
                metadata = {'assistant_name': my_assistant_name}, )
            my_thread_id = thread.id
            self.thread_id[str(session_id)] = my_thread_id

            # 過去メッセージ追加
            for m in range(len(res_history) - 1):
                role    = res_history[m].get('role','')
                content = res_history[m].get('content','')
                name    = res_history[m].get('name','')
                if (role != 'system'):
                    # 全てユーザーメッセージにて処理
                    if (name is None) or (name == ''):
                        msg_text = '(' + role + ')' + '\n' + content
                    else:
                        if (role == 'function_call'):
                            msg_text = '(function ' + name + ' call)'  + '\n' + content
                        else:
                            msg_text = '(function ' + name + ' result) ' + '\n' + content
                    #self.print(session_id, msg_text)
                    res = self.client.beta.threads.messages.create(
                        thread_id = my_thread_id,
                        role      = 'user',
                        content   = msg_text, )

        # メッセージ生成
        content_text = ''
        if (reqText is not None) and (reqText.strip() != ''):
            content_text += reqText.rstrip() + '\n'
        if (inpText is not None) and (inpText.strip() != ''):
            content_text += inpText.rstrip() + '\n'
        res = self.client.beta.threads.messages.create(
            thread_id = my_thread_id,
            role      = 'user',
            content   = content_text, )

        # ストリーム実行?
        if (session_id == 'admin'):
            #stream = True
            print(' Assist : stream=False, ')
            stream = False
        else:
            stream = False

        # 実行開始        
        #try:
        if True:

            # 実行開始
            run = self.client.beta.threads.runs.create(
                assistant_id = my_assistant_id,
                thread_id    = my_thread_id, )
            my_run_id = run.id

            # 実行ループ
            exit_status    = None
            last_status    = None
            count_run_step = 0
            messages = self.client.beta.threads.messages.list(
                        thread_id = my_thread_id, 
                        order     = 'asc', )
            last_msg_step = len(messages.data) # First msg is request
            last_message  = None
            
            chkTime       = time.time()
            while (exit_status is None) and ((time.time() - chkTime) < self.assist_max_wait_sec):

                # ステータス
                run = self.client.beta.threads.runs.retrieve(
                        thread_id = my_thread_id,
                        run_id    = my_run_id, )
                if (run.status != last_status):
                    last_status = run.status
                    chkTime     = time.time()
                    self.print(session_id, f" Assist : { last_status }")

                # 完了時は少し待機
                #if (last_status == 'completed'):
                #    time.sleep(0.25)

                # 実行ステップ確認
                #time.sleep(0.25)
                run_steps = self.client.beta.threads.runs.steps.list(
                        thread_id = my_thread_id,
                        run_id    = my_run_id,
                        order     = 'asc', )
                if (len(run_steps.data) > count_run_step):
                    for r in range(count_run_step, len(run_steps.data)):
                        step_details_type = run_steps.data[r].step_details.type
                        if (step_details_type != 'tool_calls'):
                            self.print(session_id, f" Assist : ({ step_details_type })")
                        else:
                            #self.print(session_id, run_steps.data[r].step_details)
                            step_details_tool_type = None
                            try:
                                step_details_tool_type = run_steps.data[r].step_details.tool_calls[0].type
                            except:
                                try:
                                    tc = run_steps.data[r].step_details.tool_calls[0]
                                    step_details_tool_type = tc.get('type')
                                except:
                                    pass
                            if (step_details_tool_type is not None):
                                self.print(session_id, f" Assist : ({ step_details_tool_type }...)")
                            else:
                                self.print(session_id, f" Assist : ({ step_details_type })")

                        if (step_details_type == 'message_creation'):
                            message_id = run_steps.data[r].step_details.message_creation.message_id
                            if (message_id is not None):
                                messages = self.client.beta.threads.messages.retrieve(
                                        thread_id  = my_thread_id, 
                                        message_id = message_id, )
                                for c in range(len(messages.content)):
                                    content_type = messages.content[c].type
                                    if (content_type == 'text'):
                                        content_value = messages.content[c].text.value
                                        if (content_value is not None) and (content_value != ''):
                                            if (last_status != 'completed'):
                                                if (content_value != last_message):
                                                    last_message = content_value 
                                                    self.print(session_id, last_message)
                                                    self.print(session_id, )

                    count_run_step = len(run_steps.data)

                # 最大ステップ  10step x (3auto+1) / 2 = 20
                limit_step = int((int(max_step) * (int(self.assist_auto_continue)+1)) / 2)
                if (count_run_step > limit_step):
                    exit_status = 'overstep'
                    self.print(session_id, f" Assist : overstep! (n={ count_run_step }!)")
                    break

                # 実行メッセージ確認
                #time.sleep(0.25)
                messages = self.client.beta.threads.messages.list(
                        thread_id = my_thread_id, 
                        order     = 'asc', )
                if (len(messages.data) > last_msg_step):
                    for m in range(last_msg_step, len(messages.data)):

                        res_role = messages.data[m].role
                        for c in range(len(messages.data[m].content)):
                            content_type = messages.data[m].content[c].type
                            #if (content_type == 'image_file'):
                            #    file_type   = content_type
                            #    file_id     = messages.data[m].content[c].image_file.file_id
                            #    if (file_id is not None):
                            #        self.print(session_id, f" Assist : ( { file_type }, { file_id } )")

                            if (content_type == 'text'):
                                content_value = messages.data[m].content[c].text.value
                                if (content_value is not None) and (content_value != ''):
                                    last_msg_step = m
                                    if (last_status != 'completed'):
                                        if (content_value != last_message):
                                            last_message = content_value 
                                            self.print(session_id, last_message)
                                            self.print(session_id, )
                                    else:
                                        res_content  = content_value

                                for a in range(len(messages.data[m].content[c].text.annotations)):
                                    try:
                                        file_type = messages.data[m].content[c].text.annotations[a].type
                                        file_text = messages.data[m].content[c].text.annotations[a].text
                                        file_id   = messages.data[m].content[c].text.annotations[a].file_path.file_id

                                        file_dic  = self.client.files.retrieve(file_id)
                                        filename = os.path.basename(file_dic.filename)
                                        content_file = self.client.files.content(file_id)
                                        data_bytes   = content_file.read()
                                        if (not os.path.isdir(qPath_output)):
                                            os.makedirs(qPath_output)
                                        with open(qPath_output + filename, "wb") as file:
                                            file.write(data_bytes)

                                        res_path = qPath_output + filename
                                        self.print(session_id, f" Assist : Download ... { file_text }")
                                    except:
                                        pass

                # 処理中
                if   (last_status is None):
                    self.print(session_id, ' Assist : status is None ???')

                elif (last_status == 'in_progress') \
                or   (last_status == 'queued') \
                or   (last_status == 'cancelling'):
                    pass

                # 終了
                elif (last_status == 'completed') \
                or   (last_status == 'cancelled') \
                or   (last_status == 'failed') \
                or   (last_status == 'expired'):
                    exit_status = last_status

                    # 正常終了
                    if (last_status == 'completed'):
                        break

                    # その他終了
                    else:
                        self.print(session_id, ' Assist : !')
                        break

                # ファンクション
                elif (last_status == 'requires_action'):
                    tool_result = []
                    upload_flag = False

                    self.print(session_id, )
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    for t in range(len(tool_calls)):
                        tool_call_id  = tool_calls[t].id
                        function_name = tool_calls[t].function.name
                        json_kwargs   = tool_calls[t].function.arguments

                        hit = False
                        for module_dic in function_modules.values():
                            if (function_name == module_dic['func_name']):
                                hit = True
                                self.print(session_id, f" Assist :   function_call '{ module_dic['script'] }' ({  function_name })")
                                self.print(session_id, f" Assist :   → { json_kwargs }")

                                chkTime     = time.time()

                                # メッセージ追加格納
                                self.seq += 1
                                dic = {'seq': self.seq, 'time': time.time(), 'role': 'function_call', 'name': function_name, 'content': json_kwargs }
                                res_history.append(dic)

                                # function 実行
                                try:
                                    ext_func_proc  = module_dic['func_proc']
                                    res_json       = ext_func_proc( json_kwargs )
                                except Exception as e:
                                    print(e)
                                    # エラーメッセージ
                                    dic = {}
                                    dic['error'] = e 
                                    res_json = json.dumps(dic, ensure_ascii=False, )

                                chkTime     = time.time()

                                # メッセージ追加格納
                                self.seq += 1
                                dic = {'seq': self.seq, 'time': time.time(), 'role': 'function', 'name': function_name, 'content': res_json }
                                res_history.append(dic)

                                # パス情報確認
                                try:
                                    dic  = json.loads(res_json)
                                    path = dic.get('image_path')
                                    if (path is None):
                                        path = dic.get('excel_path')
                                    if (path is not None):
                                        res_path = path
                                        res_files.append(path)
                                        upload_files.append(path)
                                        res_files    = list(set(res_files))
                                        upload_files = list(set(upload_files))

                                        # ファイルアップロード
                                        upload_ids = self.threadFile_set(session_id     = session_id,
                                                                        upload_files   = upload_files,
                                                                        assistant_id   = my_assistant_id,
                                                                        assistant_name = my_assistant_name, )
                                        upload_flag = True

                                except Exception as e:
                                    print(e)

                        if (hit == False):
                            self.print(session_id, f" Assist :   function_call Error ! ({ function_name })")
                            self.print(session_id, json_kwargs, )

                            dic = {}
                            dic['result'] = 'error' 
                            res_json = json.dumps(dic, ensure_ascii=False, )

                        # tool_result
                        self.print(session_id, f" Assist :   → { res_json }")
                        self.print(session_id, )
                        tool_result.append({"tool_call_id": tool_call_id, "output": res_json})

                    # 結果通知
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id    = my_thread_id,
                        run_id       = my_run_id,
                        tool_outputs = tool_result, )

                    # アシスタント更新
                    if (upload_flag == True):
                        res = self.my_assistant_update( session_id        = session_id,
                                                        my_assistant_id   = my_assistant_id,
                                                        my_assistant_name = my_assistant_name,
                                                        model_name        = res_api, 
                                                        instructions      = instructions, 
                                                        function_list     = function_list,
                                                        vectorStore_ids   = vectorStore_ids,
                                                        upload_ids        = upload_ids, )

                else:
                    self.print(session_id, run)
                    self.print(session_id, )
                    #time.sleep(0.50)

        #except Exception as e:
        #    print(e)
        #    res_content = None

        if (exit_status is None):
            exit_status = 'timeout'
            self.print(session_id, f" Assist : timeout! ({ self.assist_max_wait_sec }s)")
            #raise RuntimeError('assist run timeout !')
            
        # 結果確認
        if (exit_status == 'completed'):

            if (res_content is not None):
                #self.print(session_id, res_content.rstrip())
                res_text += res_content.rstrip() + '\n'

            # History 追加格納
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': res_role, 'name': '', 'content': res_text }
            res_history.append(dic)

        # 異常終了
        else:
            res_text = ''

            # History 追加格納
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'assist', 'name': '', 'content': exit_status }
            res_history.append(dic)

        # 実行キャンセル
        runs = self.client.beta.threads.runs.list(
            thread_id = my_thread_id, )
        for r in range(len(runs.data)):
            run_id     = runs.data[r].id
            run_status = runs.data[r].status
            if  (run_status != 'completed') \
            and (run_status != 'cancelled') \
            and (run_status != 'failed') \
            and (run_status != 'expired') \
            and (run_status != 'cancelling'):
                try:
                    run = self.client.beta.threads.runs.cancel(
                        thread_id = my_thread_id, 
                        run_id    = run_id, )
                    self.print(session_id, f" Assist : run cancel ... { run_id }")
                except:
                    pass

        # ファイル削除
        #res = self.threadFile_reset(session_id     = session_id,
        #                            upload_ids     = upload_ids,
        #                            assistant_id   = my_assistant_id,
        #                            assistant_name = my_assistant_name, )
        self.work_upload_ids     = upload_ids
        self.work_assistant_id   = my_assistant_id
        self.work_assistant_name = my_assistant_name

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
            self.print(session_id, ' Assist : Not Authenticate Error !')
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

        # assist
        res_text, res_path, res_files, nick_name, model_name, res_history = \
        self.run_assist( chat_class=chat_class, model_select=model_select,
                            nick_name=nick_name, model_name=model_name,
                            session_id=session_id, history=res_history, function_modules=function_modules,
                            sysText=sysText, reqText=reqText, inpText=inpText,
                            upload_files=upload_files, image_urls=image_urls,
                            temperature=temperature, max_step=max_step, jsonSchema=jsonSchema, )

        #res_text, res_path, res_files, nick_name, model_name, res_history = \
        #self.run_gpt(   chat_class=chat_class, model_select=model_select,
        #                nick_name=nick_name, model_name=model_name,
        #                session_id=session_id, history=res_history, function_modules=function_modules,
        #                sysText=sysText, reqText=reqText, inpText=inpText,
        #                upload_files=upload_files, image_urls=image_urls,
        #                temperature=temperature, max_step=max_step, jsonSchema=jsonSchema, )

        # 文書成形
        if (res_text.strip() == ''):
            res_text = '!'

        return res_text, res_path, res_files, nick_name, model_name, res_history



if __name__ == '__main__':

        #assistAPI = speech_bot_assist._assistAPI()
        assistAPI = _assistAPI()

        api_type = assist_key.getkey('assist','assist_api_type')
        print(api_type)

        log_queue = queue.Queue()
        res = assistAPI.init(log_queue=log_queue, )

        res = assistAPI.authenticate('assist',
                            api_type,
                            assist_key.getkey('assist','assist_default_gpt'), assist_key.getkey('assist','assist_default_class'),
                            assist_key.getkey('assist','assist_auto_continue'),
                            assist_key.getkey('assist','assist_max_step'), assist_key.getkey('assist','assist_max_session'),
                            assist_key.getkey('assist','assist_max_wait_sec'),

                            assist_key.getkey('assist','openai_organization'), 
                            assist_key.getkey('assist','openai_key_id'),
                            assist_key.getkey('assist','azure_endpoint'), 
                            assist_key.getkey('assist','azure_version'), 
                            assist_key.getkey('assist','azure_key_id'),

                            assist_key.getkey('assist','assist_a_nick_name'), assist_key.getkey('assist','assist_a_model'), assist_key.getkey('assist','assist_a_token'),
                            assist_key.getkey('assist','assist_a_use_tools'),
                            assist_key.getkey('assist','assist_b_nick_name'), assist_key.getkey('assist','assist_b_model'), assist_key.getkey('assist','assist_b_token'),
                            assist_key.getkey('assist','assist_b_use_tools'),
                            assist_key.getkey('assist','assist_v_nick_name'), assist_key.getkey('assist','assist_v_model'), assist_key.getkey('assist','assist_v_token'),
                            assist_key.getkey('assist','assist_v_use_tools'),
                            assist_key.getkey('assist','assist_x_nick_name'), assist_key.getkey('assist','assist_x_model'), assist_key.getkey('assist','assist_x_token'),
                            assist_key.getkey('assist','assist_x_use_tools'),
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

            session_id = 'admin'
            if True:
                sysText = None
                reqText = ''
                inpText = 'おはようございます。'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, assistAPI.history = \
                    assistAPI.chatBot(   chat_class='auto', model_select='auto', 
                                            session_id=session_id, history=assistAPI.history, function_modules=function_modules,
                                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                            inpLang='ja', outLang='ja', )
                print()
                print(f"[{ res_name }] ({ res_api })")
                print(str(res_text))
                print()

            if True:
                sysText = None
                reqText = ''
                inpText = 'assist-b,toolsで兵庫県三木市の天気を調べて'
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, assistAPI.history = \
                    assistAPI.chatBot(   chat_class='auto', model_select='auto', 
                                            session_id=session_id, history=assistAPI.history, function_modules=function_modules,
                                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                            inpLang='ja', outLang='ja', )
                print()
                print(f"[{ res_name }] ({ res_api })")
                print(str(res_text))
                print()

            if False:
                sysText = None
                reqText = ''
                inpText = '添付画像を説明してください。'
                filePath = ['_icons/dog.jpg']
                #filePath = ['_icons/dog.jpg', '_icons/kyoto.png']
                print()
                print('[Request]')
                print(reqText, inpText )
                print()
                res_text, res_path, res_files, res_name, res_api, assistAPI.history = \
                    assistAPI.chatBot(   chat_class='auto', model_select='auto', 
                                            session_id=session_id, history=assistAPI.history, function_modules=function_modules,
                                            sysText=sysText, reqText=reqText, inpText=inpText, filePath=filePath,
                                            inpLang='ja', outLang='ja', )
                print()
                print('[' + res_name + '] (' + res_api + ')' )
                print('', res_text)
                print()

            if False:
                print('[History]')
                for h in range(len(assistAPI.history)):
                    print(assistAPI.history[h])
                assistAPI.history = []



