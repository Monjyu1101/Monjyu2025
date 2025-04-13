#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'subbot'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)


import os
import time
import datetime

import requests
from typing import Dict, List, Tuple
import random

import socket
qHOSTNAME = socket.gethostname().lower()

# インターフェース
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'
qPath_input  = 'temp/input/'
qPath_output = 'temp/output/'

# 共通ルーチンインポート
import RiKi_Monjyu__llm

# 定数の定義
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30

MEMBER_RESULT_TIMEOUT  = 600
MEMBER_RESULT_INTERVAL = 2

class ChatClass:
    """
    チャットボットクラス
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreai=None,
                        core_port: str = '8000', self_port: str = '8101', ):
        """
        コンストラクタ
        Args:
            qLog_fn (str, optional): ログファイル名。
            runMode (str, optional): 実行モード。
            core_port (str, optional): メインポート番号。
            self_port (str, optional): 自分のポート番号。
        """
        self.runMode = runMode

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug(f"init {self_port}")

        # 設定
        self.main       = main
        self.conf       = conf
        self.data       = data
        self.addin      = addin
        self.coreai     = coreai
        self.botFunc    = botFunc
        self.mcpHost    = mcpHost
        self.core_port  = core_port
        self.self_port  = self_port
        self.local_endpoint = f'http://localhost:{ self.core_port }'
        self.core_endpoint = self.local_endpoint.replace('localhost', qHOSTNAME)
        self.llm = RiKi_Monjyu__llm.llm_class(  runMode=runMode, qLog_fn=qLog_fn, 
                                                main=main, conf=conf, data=data, addin=addin, botFunc=botFunc, mcpHost=mcpHost,
                                                coreai=coreai)

        # CANCEL要求
        self.bot_cancel_request = False


    def post_request(self,  user_id: str, from_port: str, to_port: str, 
                            req_mode: str, 
                            system_text: str, request_text: str, input_text: str,
                            file_names: list[str], result_savepath: str, result_schema: str, ) -> str:
        """
        AIメンバー要求送信
        """
        res_port = None
        try:
            response = requests.post(
                self.local_endpoint + '/post_req',
                json={'user_id': user_id, 'from_port': from_port, 'to_port': to_port,
                      'req_mode': req_mode, 
                      'system_text': system_text, 'request_text': request_text, 'input_text': input_text,
                      'file_names': file_names, 'result_savepath': result_savepath, 'result_schema': result_schema, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                res_port = str(response.json()['port'])
            else:
                logger.error(f"Error response ({self.core_port}/post_req) : {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error communicating ({self.core_port}/post_req) : {e}")
        return res_port

    def wait_result(self, user_id: str, member_port: Dict[int, str], parent_self=None, ) -> Dict[int, str]:
        """
        AIメンバー応答待機
        """
        out_text: Dict[int, str] = {n: '' for n in range(1, len(member_port))}

        # AIメンバー応答待機
        timeout = time.time() + MEMBER_RESULT_TIMEOUT
        all_done = False
        while time.time() < timeout and all_done == False:

            # キャンセル確認
            if  (parent_self is not None) \
            and (parent_self.cancel_request == True):
                break

            try:
                all_done = False
                response = requests.get(
                    self.local_endpoint + '/get_sessions_port?user_id=' + user_id + '&from_port=' + self.self_port,
                    timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
                )
                if response.status_code == 200:
                    results = response.json()
                    all_done = True
                    for n in range(1, len(member_port)):
                        key_val = f"{ user_id }:{ self.self_port }:{ member_port[n] }"
                        if key_val in results:
                            if results[key_val]["out_time"] is not None:
                                out_text[n] = str(results[key_val]["out_text"])
                            else:
                                all_done = False
                                break
                else:
                    logger.error(f"Error response ({self.core_port}/get_sessions_port) : {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Error communicating ({self.core_port}/get_sessions_port) : {e}")
            time.sleep(MEMBER_RESULT_INTERVAL)
        return out_text


    def proc_chat(self, user_id: str, from_port: str, to_port: str,
                        req_mode: str, req_engine: str, 
                        req_functions: str, req_reset: str,
                        max_retry: str, max_ai_count: str,
                        before_proc: str, before_engine: str,
                        after_proc: str, after_engine: str,
                        check_proc: str, check_engine: str,
                        system_text: str, request_text: str, input_text: str,
                        file_names: list[str], result_savepath: str, result_schema: str, parent_self=None, ) -> Tuple[str, str, str]:
        proc_cancel = False

        """
        デバッグ処理
        """
        if (request_text.lower()[:6] == 'debug,'):
            output_text = request_text
            output_data = input_text
            output_path = ''
            output_files = []

            # デバッグ報告
            if (parent_self is not None):
                _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                            from_port=from_port, to_port=to_port,
                                            system_text=system_text, request_text=request_text, input_text=input_text,
                                            result_savepath=result_savepath, result_schema=result_schema,
                                            output_text=output_text, output_data=output_data,
                                            output_path=output_path, output_files=output_files,
                                            status='', )

            # 10～30秒待機
            wait_sec = random.uniform(10, 30)
            chkTime = time.time()
            while ((time.time() - chkTime) < wait_sec):
                time.sleep(0.25)

                # キャンセル確認
                if  (parent_self is not None) \
                and (parent_self.cancel_request == True):
                    return '', '', '', []

            # 最終報告
            if (req_mode == 'session'):
                status = 'SESSION'
            else:
                status = 'READY'        
            if (parent_self is not None):
                _ = parent_self.post_complete(  user_id=user_id, req_mode=req_mode,
                                                from_port=from_port, to_port=to_port,
                                                system_text=system_text, request_text=request_text, input_text=input_text,
                                                result_savepath=result_savepath, result_schema=result_schema,
                                                output_text=output_text, output_data=output_data,
                                                output_path=output_path, output_files=output_files,
                                                status=status, )

            return output_text, output_data, output_path, output_files

        """
        チャット処理
        """

        # パラメータ設定
        if (req_mode == 'chat'):
            if (req_functions == ''):
                req_functions = 'yes,'
            if (max_retry == ''):
                max_retry = '1'
            if (before_proc == ''):
                if (parent_self is not None):
                    before_proc = 'profile,prompt,'
                else:
                    before_proc = 'prompt,'
            if (after_proc == ''):
                after_proc = 'all,'
        if (system_text.strip() != ''):
            system_text = system_text.rstrip() + '\n'
        if (request_text.strip() != ''):
            request_text = request_text.rstrip() + '\n'
        if (input_text.strip() != ''):
            input_text = input_text.rstrip() + '\n'

        # リトライ回数
        MAX_RETRY = 1
        if (max_retry.isdigit()):
            MAX_RETRY = int(max_retry)

        # function_modules 設定
        function_modules = {}
        if (req_functions == 'yes,'):
            if (parent_self is not None):
                function_modules = parent_self.function_modules

        # リセット 要求
        if (req_reset == 'yes,'):
            self.history = []

        # ファイル設定
        filePath = []
        for fname in file_names:
            fpath = qPath_input + os.path.basename(fname)
            if (os.path.isfile(fpath)):
                filePath.append(fpath)

        # ----------------------------------------
        # AIメンバー編成
        # ----------------------------------------
        AI_COUNT = 0
        full_name: Dict[int, str]     = {}
        member_prompt: Dict[int, str] = {}
        full_name[AI_COUNT]     = 'ASSISTANT'
        member_prompt[AI_COUNT] = ''

        # ----------------------------------------
        # シンプル実行
        # ----------------------------------------
        if  ((max_retry == '') or (max_retry == '0')) \
        and (before_proc.find('profile,' ) < 0) \
        and (before_proc.find('prompt,'  ) < 0) \
        and (after_proc.find('all,'     ) < 0) \
        and (after_proc.find('summary,' ) < 0) \
        and (after_proc.find('code,'    ) < 0):

            # キャンセル確認
            if (parent_self is not None) \
            and (parent_self.cancel_request == True):
                return '', '', '', []

            # chatBot処理
            res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
                self.llm.chatBot(   req_mode=req_mode, engine=req_engine,
                                chat_class='auto', model_select='auto', session_id=self.self_port, 
                                history=self.history, function_modules=function_modules,
                                sysText=system_text, reqText=request_text, inpText=input_text,
                                filePath=filePath, jsonSchema=result_schema, inpLang='ja', outLang='ja', )

            output_text = ''
            #output_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
            output_text += f"[{ res_engine }] ({ self.self_port }:{ res_api }) \n"
            output_text += res_text
            output_data = res_data
            output_path  = res_path
            output_files = res_files

            # 最終報告
            if (req_mode == 'session'):
                status = 'SESSION'
            else:
                status = 'READY'        
            if (parent_self is not None):
                _ = parent_self.post_complete(  user_id=user_id, req_mode=req_mode,
                                                from_port=from_port, to_port=to_port,
                                                system_text=system_text, request_text=request_text, input_text=input_text,
                                                result_savepath=result_savepath, result_schema=result_schema,
                                                output_text=output_text, output_data=output_data,
                                                output_path=output_path, output_files=output_files,
                                                status=status, )

            return output_text, output_data, output_path, output_files

        # ----------------------------------------
        # ユーザーの要求
        # ----------------------------------------
        user_text = \
"""
### [USER] ユーザーの要求 ###
$$$ request_text $$$$$$ input_text $$$
###
"""
        user_text = user_text.replace('$$$ request_text $$$', request_text)
        user_text = user_text.replace('$$$ input_text $$$', input_text)
        if (user_text.strip() != ''):
            user_text = user_text.rstrip() + '\n'
            user_text = user_text.replace('\n\n', '\n')
        assistant_text = ''

        # チャットテキスト
        sysText   = system_text
        chat_text = ''

        # ----------------------------------------
        # 前処理
        # ----------------------------------------
        if  (before_proc.find('profile,' ) < 0) \
        and (before_proc.find('prompt,'  ) < 0):
            inpText = \
"""
[SYSTEM]
$$$ system_text $$$
"""
            inpText = inpText.replace('$$$ system_text $$$', system_text)
            inpText = inpText.replace('\n\n', '\n')
            chat_text += inpText.rstrip() + '\n\n'

        else:

            # AI要求
            reqText = ''
            inpText = \
"""
[SYSTEM]
$$$ system_text $$$
$$$ system_text[0] $$$
"""
            if (before_proc.find('profile,') >= 0):
                full_name[0]     = parent_self.info['full_name']
                member_prompt[0] = ''
                inpText += \
"""
あなたは、AIですが歴史上の偉人 [$$$ full_name[0] $$$] として振舞ってください。
あなたは、最新情報まで知っている賢い賢者です。
あなたの回答は別のAIにより評価、採点されます。
ユーザーの要求には常に思慮深く考えて回答してください。
よろしくお願いします。
"""
            if (before_proc.find('prompt,') >= 0):
                inpText += \
"""
ユーザーの要求の意図を推察してください。
ユーザーの要求に明記されていない注意するべき点を見逃さないでください。
ユーザーの求めているもの（出力するべき内容）を推察してください。
ユーザーの要求は簡単な挨拶の返答の場合もあります。何を返答するべきか整理してください。
あなたの回答は別のAIにより評価、採点されます。
ユーザーの要求には常に思慮深く考えて回答してください。
$$$ user_text $$$
ユーザーの要求を誰でも解るように補足、修正をお願いします。
"""
            inpText = inpText.replace('$$$ system_text $$$', system_text)
            inpText = inpText.replace('$$$ system_text[0] $$$', member_prompt[0])
            inpText = inpText.replace('$$$ system_text $$$', system_text)
            inpText = inpText.replace('$$$ full_name[0] $$$', full_name[0])
            inpText = inpText.replace('$$$ user_text $$$', user_text)

            # キャンセル確認
            if (parent_self is not None) \
            and (parent_self.cancel_request == True):
                return '', '', '', []

            # chatBot処理
            res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
                self.llm.chatBot(   req_mode=req_mode, engine=before_engine,
                                chat_class='auto', model_select='auto', session_id=self.self_port, 
                                history=self.history, function_modules={},
                                sysText=sysText, reqText=reqText, inpText=inpText,
                                filePath=filePath, jsonSchema=None, inpLang='ja', outLang='ja', )

            if (res_text == '') or (res_text == '!'):
                proc_cancel = True
            else:
                res_text = res_text.replace('\n\n', '\n')
                if (before_proc.find('prompt,') >= 0):
                    assistant_text = \
"""
### ユーザーの要求の補足 ###
$$$ res_text $$$
###
"""
                    assistant_text = assistant_text.replace('$$$ res_text $$$', res_text)
                    assistant_text = assistant_text.replace('\n\n', '\n')

            # デバッグ報告
            if (parent_self is not None):
                _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                            from_port=from_port, to_port=to_port,
                                            system_text=system_text, request_text=before_proc, input_text=user_text,
                                            result_savepath=result_savepath, result_schema=result_schema,
                                            output_text=inpText, output_data=res_text,
                                            output_path='', output_files=[],
                                            status='', )

            chat_text += inpText.rstrip() + '\n\n'
            chat_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
            chat_text += res_text.rstrip() + '\n\n'

        # ----------------------------------------
        # チャットループ
        # ----------------------------------------
        if (proc_cancel == True):
            res_text ='!'
        else:
            run_count = 0
            while (run_count <= MAX_RETRY):
                run_count += 1

                # AI要求
                reqText = ''
                inpText = ''
                if (run_count == 1):
                    inpBase = \
"""
[SYSTEM]
あなたの回答は別のAIにより評価、採点されます。
ユーザーの要求には常に思慮深く考えて回答してください。
"""
                    inpText = chat_text + inpBase + user_text + assistant_text
                else:
                    inpBase = \
"""
[SYSTEM]
ユーザーの要求の意図は把握されていますか？
ユーザーの求めているもの（出力するべき内容）になっていますか？
それらを自己確認して、もう一度改善した結果の出力をお願いします。
"""
                    inpText = chat_text + inpBase + user_text

                # キャンセル確認
                if (parent_self is not None) \
                and (parent_self.cancel_request == True):
                    return '', '', '', []

                # エンジン変更
                engine = req_engine
                if (after_proc == '') and (run_count >= MAX_RETRY):
                    engine = after_engine

                # chatBot処理
                res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
                    self.llm.chatBot(   req_mode=req_mode, engine=engine,
                                    chat_class='auto', model_select='auto', session_id=self.self_port, 
                                    history=self.history, function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText,
                                    filePath=filePath, jsonSchema=result_schema, inpLang='ja', outLang='ja', )

                # デバッグ報告
                if (parent_self is not None):
                    _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                                from_port=from_port, to_port=to_port,
                                                system_text=system_text, request_text=inpBase, input_text=chat_text,
                                                result_savepath=result_savepath, result_schema=result_schema,
                                                output_text=inpText, output_data=res_text,
                                                output_path=res_path, output_files=res_files,
                                                status='', )

                chat_text += inpBase.rstrip() + '\n\n'
                chat_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
                res_text2 = res_text.replace('\n\n', '\n')
                chat_text += res_text2.rstrip() + '\n\n'

        output_raw  = res_text
        output_text = ''
        output_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
        output_text += res_text
        output_data = res_data
        output_path = res_path
        output_files = res_files

        # ----------------------------------------
        # 後処理
        # ----------------------------------------
        if (proc_cancel != True):
            if (after_proc.find('all,'     ) >= 0) \
            or (after_proc.find('summary,' ) >= 0) \
            or (after_proc.find('code,'    ) >= 0):

                # AI要求
                reqText = ''
                inpBase1 = \
"""
[SYSTEM]
回答予定内容の文章を整理し、最終回答文を作成します。
最終回答文は、他のシステムで利用しますので、不必要な説明は削除してください。
同様に、この文章に至った経緯も不要です。その部分も削除してください。
回答本文と思われる結果のみ、シンプルな文章にしてください。
"""
                inpBase2 = \
"""
あなたの回答は別のAIにより評価、採点されます。
適切な位置で改行して、読みやすい文章にしてください。
文章は、美しい日本語でお願いします。
"""
                if (after_proc.find('all,'     ) >= 0) \
                or (after_proc.find('code,'    ) >= 0):
                    inpBase2 += \
"""
ソースコードが含まれている場合、ソースコードのみ抽出してください。
執筆中の小説の原稿の場合、原稿部分のみ抽出してください。
"""
                if (after_proc.find('all,'     ) >= 0) \
                or (after_proc.find('summary,' ) >= 0):
                    inpBase2 += \
"""
ソースコードや執筆中の小説の原稿ではない場合、最大１分で読み切れる文章長さまで要約してください。
"""
                if  (after_proc.find('all,'     ) >= 0) \
                and (req_engine != after_engine):
                    inpBase2 += \
"""
最終回答文は別のAIで生成されました。ミスがあれば修正をお願いします。
"""
                inpText = \
"""
$$$ inpBase1 $$$

$$$ user_text $$$

### 回答予定内容 ###
$$$ output_text $$$
###

$$$ inpBase2 $$$
"""
                inpText = inpText.replace('$$$ inpBase1 $$$', inpBase1)
                inpText = inpText.replace('$$$ user_text $$$', user_text)
                inpText = inpText.replace('$$$ output_text $$$', output_raw)
                inpText = inpText.replace('$$$ inpBase2 $$$', inpBase2)

                # キャンセル確認
                if (parent_self is not None) \
                and (parent_self.cancel_request == True):
                    return '', '', '', []

                # chatBot処理
                res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
                    self.llm.chatBot(   req_mode=req_mode, engine=after_engine,
                                    chat_class='auto', model_select='auto', session_id=self.self_port, 
                                    history=self.history, function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText,
                                    filePath=filePath, jsonSchema=result_schema, inpLang='ja', outLang='ja', )

                chat_text += inpBase1.rstrip() + '\n' + inpBase2.rstrip() + '\n\n'
                chat_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
                res_text2 = res_text.replace('\n\n', '\n')
                chat_text += res_text2.rstrip() + '\n\n'

                output_raw  = res_text
                output_data = ''
                output_data += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
                output_data += res_data
                output_path  = res_path
                output_files = res_files

                # デバッグ報告
                if (parent_self is not None):
                    _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                                from_port=from_port, to_port=to_port,
                                                system_text=system_text, request_text=after_proc, input_text=inpText,
                                                result_savepath=result_savepath, result_schema=result_schema,
                                                output_text=output_text, output_data=output_data,
                                                output_path=output_path, output_files=output_files,
                                                status='', )

        # 最終報告
        if (req_mode == 'session'):
            status = 'SESSION'
        else:
            status = 'READY'        
        if (parent_self is not None):
            _ = parent_self.post_complete(  user_id=user_id, req_mode=req_mode,
                                            from_port=from_port, to_port=to_port,
                                            system_text=system_text, request_text=request_text, input_text=input_text,
                                            result_savepath=result_savepath, result_schema=result_schema,
                                            output_text=output_text, output_data=output_data,
                                            output_path=output_path, output_files=output_files,
                                            status=status, )

        # デバッグ報告(会話履歴)
        if (parent_self is not None):
            _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                        from_port=from_port, to_port=to_port,
                                        system_text=system_text, request_text='*** 会話履歴 ***', input_text=user_text,
                                        result_savepath=result_savepath, result_schema=result_schema,
                                        output_text=chat_text, output_data=output_data,
                                        output_path=output_path, output_files=output_files,
                                        status='', )

        return output_text, output_data, output_path, output_files

    def proc_assistant(self,user_id: str, from_port: str, to_port: str,
                            req_mode: str, req_engine: str, 
                            req_functions: str, req_reset: str,
                            max_retry: str, max_ai_count: str, 
                            before_proc: str, before_engine: str,
                            after_proc: str, after_engine: str,
                            check_proc: str, check_engine: str,
                            system_text: str, request_text: str, input_text: str,
                            file_names: list[str], result_savepath: str, result_schema: str, parent_self=None, ) -> Tuple[str, str, str]:
        proc_cancel = False

        """
        アシスタント処理
        """

        # パラメータ設定
        if (req_mode in ['serial', 'parallel']):
            if (req_functions == ''):
                req_functions = 'no,'
            if (max_retry == ''):
                max_retry = '1'
            if (before_proc == ''):
                if (parent_self is not None):
                    before_proc = 'profile,prompt,'
                else:
                    before_proc = 'prompt,'
            if (after_proc == ''):
                after_proc = 'all,'
        if (req_mode == 'serial'):
            if (max_ai_count.isdigit()):
                if (int(max_ai_count) != 0):
                    pass
                else:
                    max_ai_count = '1'
            else:                
                    max_ai_count = '1'

        if (system_text.strip() != ''):
            system_text = system_text.rstrip() + '\n'
        if (request_text.strip() != ''):
            request_text = request_text.rstrip() + '\n'
        if (input_text.strip() != ''):
            input_text = input_text.rstrip() + '\n'

        if (request_text.lower()[:6] == 'debug,'):
            before_proc = ''
            after_proc = ''

        # リトライ回数
        MAX_RETRY = 1
        if (max_retry.isdigit()):
            MAX_RETRY = int(max_retry)

        # AIメンバー数
        AI_MAX = 3
        if (max_ai_count.isdigit()):
            if (int(max_ai_count) != 0):
                AI_MAX = int(max_ai_count)

        # function_modules 設定
        function_modules = {}
        if (req_functions == 'yes,'):
            if (parent_self is not None):
                function_modules = parent_self.function_modules

        # リセット 要求
        if (req_reset == 'yes,'):
            self.history = []

        # ファイル設定
        filePath = []
        for fname in file_names:
            fpath = qPath_input + os.path.basename(fname)
            if (os.path.isfile(fpath)):
                filePath.append(fpath)

        # ----------------------------------------
        # AIメンバー編成
        # ----------------------------------------
        AI_COUNT = 0
        full_name: Dict[int, str]   = {}
        member_port: Dict[int, str] = {}
        member_inp: Dict[int, str]  = {}
        member_out: Dict[int, str]  = {}

        full_name[AI_COUNT]   = 'ASSISTANT'
        member_port[AI_COUNT] = self.self_port
        member_inp[AI_COUNT]  = None
        member_out[AI_COUNT]  = None

        for n in range(AI_MAX):

            # キャンセル確認
            if (parent_self is not None) \
            and (parent_self.cancel_request == True):
                return '', '', '', []

            # メンバー要求
            begin_text = 'begin,'
            res_port = self.post_request(   user_id=user_id, from_port=to_port, to_port='', 
                                            req_mode='session', 
                                            system_text='', request_text=begin_text, input_text='', 
                                            file_names=[], result_savepath='', result_schema='', )
            if res_port is not None:
                AI_COUNT += 1
                full_name[AI_COUNT]   = res_port
                member_port[AI_COUNT] = res_port
                member_inp[AI_COUNT]  = None
                member_out[AI_COUNT]  = None

        # メンバーゼロ
        if AI_COUNT == 0:

            # キャンセル確認
            if (parent_self is not None) \
            and (parent_self.cancel_request == True):
                return '', '', '', []

            # チャット処理
            output_text, output_data, output_path, output_files = self.proc_chat(
                user_id=user_id, from_port=from_port, to_port=to_port,
                req_mode=req_mode, req_engine=req_engine,
                req_functions=req_functions, req_reset=req_reset,
                max_retry=max_retry, max_ai_count=max_ai_count,
                before_proc=before_proc, before_engine=before_engine,
                after_proc=after_proc, after_engine=after_engine,
                check_proc=check_proc, check_engine=check_engine,
                system_text=system_text, request_text=request_text, input_text=input_text,
                file_names=file_names, result_savepath=result_savepath, result_schema=result_schema, parent_self=parent_self )

            return output_text, output_data, output_path, output_files

        # AIメンバー情報取得
        full_name: Dict[int, str]     = {}
        member_info: Dict[int, str]   = {}
        member_point: Dict[int, str]  = {}
        member_prompt: Dict[int, str] = {}
        for n in range(0, len(member_port)):
            full_name[n]     = member_port[n]
            member_info[n]   = ''
            member_point[n]  = '50'
            member_prompt[n] = ''

            # キャンセル確認
            if (parent_self is not None) \
            and (parent_self.cancel_request == True):
                return '', '', '', []

            # AIメンバー情報取得
            try:
                endpoint = self.local_endpoint.replace( f':{ self.core_port }', f':{ member_port[n] }' )
                response = requests.get(
                    endpoint + '/get_info',
                    timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
                )
                if response.status_code == 200:
                    full_name[n]     = response.json()['full_name']
                    member_info[n]   = response.json()['info_text']
                    member_point[n]  = response.json()['self_point']
                    member_prompt[n] = response.json()['self_prompt']
                    if (member_prompt[n].strip() == system_text.strip()):
                        member_prompt[n] = ''
                else:
                    logger.error(f"Error response ({member_port[n]}/get_info) : {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Error communicating ({member_port[n]}/get_info) : {e}")


        members_list = ''
        for n in range(1, len(member_port)):
            members_list += '[' + full_name[n] + '] \n'

        # ----------------------------------------
        # ユーザーの要求
        # ----------------------------------------
        user_text = \
"""
### [USER] ユーザーの要求 ###
$$$ request_text $$$$$$ input_text $$$
###
"""
        user_text = user_text.replace('$$$ request_text $$$', request_text)
        user_text = user_text.replace('$$$ input_text $$$', input_text)
        if (user_text.strip() != ''):
            user_text = user_text.rstrip() + '\n'
            user_text = user_text.replace('\n\n', '\n')
        assistant_text = ''

        # チャットテキスト
        sysText   = system_text
        chat_text = ''

        # ----------------------------------------
        # 前処理
        # ----------------------------------------
        if  (before_proc.find('profile,' ) < 0) \
        and (before_proc.find('prompt,'  ) < 0):
            inpText = \
"""
[SYSTEM]
$$$ system_text $$$
"""
            inpText = inpText.replace('$$$ system_text $$$', system_text)
            inpText = inpText.replace('\n\n', '\n')
            chat_text += inpText.rstrip() + '\n\n'

        else:

            # AI要求
            reqText = ''
            inpText = \
"""
[SYSTEM]
$$$ system_text $$$
$$$ system_text[0] $$$
あなたはAIリーダーに選出されました。
複数のAIでユーザーからの要求に対して最適解を出します。
"""
            if (before_proc.find('profile,') >= 0):
                full_name[0] = parent_self.info['full_name']
                inpText += \
"""
あなたは、AIですが歴史上の偉人 [$$$ full_name[0] $$$] として振舞ってください。
あなたは、最新情報まで知っている賢い賢者です。
あなたの回答は別のAIにより評価、採点されます。
ユーザーの要求には常に思慮深く考えて回答してください。
よろしくお願いします。
"""
            if (before_proc.find('prompt,') >= 0):
                inpText += \
"""
ユーザーの要求の意図を推察してください。
ユーザーの要求に明記されていない注意するべき点を見逃さないでください。
ユーザーの求めているもの（出力するべき内容）を推察してください。
ユーザーの要求は簡単な挨拶の返答の場合もあります。何を返答するべきか整理してください。
あなたの回答は別のAIにより評価、採点されます。
ユーザーの要求には常に思慮深く考えて回答してください。
$$$ user_text $$$
ユーザーの要求を誰でも解るように補足、修正をお願いします。

あなたは、AIメンバーに個別に作業依頼を出せます。作業依頼できるAIメンバーは以下のとおりです。
$$$ members_list $$$
AIメンバー毎に重複しても構わないし総合的なことでもよいので、作業依頼(指示)出しをお願いします。
"""
            inpText = inpText.replace('$$$ system_text $$$', system_text)
            inpText = inpText.replace('$$$ system_text[0] $$$', member_prompt[0])
            inpText = inpText.replace('$$$ full_name[0] $$$', full_name[0])
            inpText = inpText.replace('$$$ user_text $$$', user_text)
            inpText = inpText.replace('$$$ members_list $$$', members_list)

            # キャンセル確認
            if (parent_self is not None) \
            and (parent_self.cancel_request == True):
                return '', '', '', []

            # chatBot処理
            res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
                self.llm.chatBot(   req_mode=req_mode, engine=before_engine,
                                chat_class='auto', model_select='auto', session_id=self.self_port, 
                                history=self.history, function_modules={},
                                sysText=sysText, reqText=reqText, inpText=inpText,
                                filePath=filePath, jsonSchema=None, inpLang='ja', outLang='ja', )

            if (res_text == '') or (res_text == '!'):
                proc_cancel = True
            else:
                res_text = res_text.replace('\n\n', '\n')
                if (before_proc.find('prompt,') >= 0):
                    assistant_text = \
"""
### ユーザーの要求の補足 ###
$$$ res_text $$$
###
"""
                    assistant_text = assistant_text.replace('$$$ res_text $$$', res_text)
                    assistant_text = assistant_text.replace('\n\n', '\n')

            # デバッグ報告
            if (parent_self is not None):
                _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                            from_port=from_port, to_port=to_port,
                                            system_text=system_text, request_text=before_proc, input_text=user_text,
                                            result_savepath=result_savepath, result_schema=result_schema,
                                            output_text=inpText, output_data=res_text,
                                            output_path=res_path, output_files=res_files,
                                            status='', )

            chat_text += inpText.rstrip() + '\n\n'
            chat_text += f"[{ full_name[0] }] ({ member_port[0] }:{ res_api }) \n"
            chat_text += res_text.rstrip() + '\n\n'

        # ----------------------------------------
        # チャットループ
        # ----------------------------------------
        if (proc_cancel == True):
            res_text ='!'
        else:
            run_count = 0
            while (run_count <= MAX_RETRY):
                run_count += 1

                # AIメンバー要求
                sysText = system_text
                reqText = chat_text
                if (run_count == 1):
                    inpBase = \
"""
[SYSTEM]
あなたはAIメンバーに選出されました。
複数のAIでユーザーの要求に対して最適解を出します。
あなたは、AIですが歴史上の偉人 [### full_name[n] ###] として振舞ってください。
あなたは、最新情報まで知っている賢い賢者です。
ユーザーの要求を正しく理解し、AIリーダーの解釈とあなたへの依頼をもとに、やるべきことを行ってください。
あなたの回答は別のAIにより評価、採点されます。
ユーザーの要求には常に思慮深く考えて回答してください。
よろしくお願いします。
"""
                else:
                    inpBase = \
"""
[SYSTEM]
よく考えて、他のAIの意見も参考に、もう一度お願いします。
"""
                for n in range(1, len(member_port)):
                    inpText = inpBase.replace('### full_name[n] ###', full_name[n])
                    inpText += user_text
                    inpText += assistant_text
                    if (request_text.lower()[:6] == 'debug,'):
                        reqText = request_text

                    # キャンセル確認
                    if (parent_self is not None) \
                    and (parent_self.cancel_request == True):
                        return '', '', '', []

                    # メンバー要求
                    res_port = self.post_request(   user_id=user_id, from_port=to_port, to_port=member_port[n],
                                                    req_mode='session', 
                                                    system_text=sysText, request_text=reqText, input_text=inpText,
                                                    file_names=file_names, result_savepath=result_savepath, result_schema=result_schema, )

                    if res_port is not None:
                        member_inp[n] = inpText
                        member_out[n] = None

                # AIメンバー待機
                out_text = self.wait_result(user_id=user_id, member_port=member_port, parent_self=parent_self, )

                # キャンセル確認
                if (parent_self is not None) \
                and (parent_self.cancel_request == True):
                    return '', '', '', []

                # AIメンバー応答
                member_text = ''
                for n in range(1, len(member_port)):
                    if out_text[n] is not None:
                        #member_text += f"[{ full_name[n] }] ({ member_port[n] }) \n"
                        member_text += out_text[n].rstrip() + '\n\n'

                # 中間報告
                _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                            from_port=from_port, to_port=to_port,
                                            system_text=system_text, request_text=inpBase, input_text=chat_text,
                                            result_savepath=result_savepath, result_schema=result_schema,
                                            output_text=inpText, output_data='***回答検証中***\n\n' + member_text, 
                                            output_path='', output_files=[],
                                            status='', )

                chat_text += inpBase.rstrip() + '\n\n'
                chat_text += member_text.rstrip() + '\n\n'

                # AIリーダー要求
                sysText = system_text
                reqText = chat_text
                inpBase = \
"""
[SYSTEM]
あなたは、AIリーダー [$$$ full_name[0] $$$] ($$$ member_port[0] $$$) として、
あなたは、最初にAIメンバーに作業依頼(指示)出ししましたが、それは他のAIの回答を参考にするためです。
前記、これまでのAIメンバーの回答も参考にしつつ、適切な回答を行ってください。
$$$ user_text $$$
ユーザーの要求を推察、正しく解釈して、求められている回答を生成してください。
"""
                if (run_count != 1):
                    inpBase += \
"""
ユーザーの要求の意図は把握されていますか？
ユーザーの求めているもの（出力するべき内容）になっていますか？
それらを自己確認して、もう一度改善した結果の出力をお願いします。
"""
                inpBase = inpBase.replace('$$$ full_name[0] $$$', full_name[0])
                inpBase = inpBase.replace('$$$ member_port[0] $$$', member_port[0])
                inpText = inpBase.replace('$$$ user_text $$$', user_text)
                inpBase = inpBase.replace('$$$ user_text $$$', '')

                if (request_text.lower()[:6] == 'debug,'):
                    res_text = request_text
                    res_api  = 'debug'
                    res_path = ''
                    res_files = []
                else:

                    # キャンセル確認
                    if (parent_self is not None) \
                    and (parent_self.cancel_request == True):
                        return '', '', '', []

                    # エンジン変更
                    engine = req_engine
                    if (after_proc == '') and (run_count >= MAX_RETRY):
                        engine = after_engine

                    # chatBot 処理
                    res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
                        self.llm.chatBot(   req_mode=req_mode, engine=engine,
                                        chat_class='auto', model_select='auto', session_id=self.self_port, 
                                        history=self.history, function_modules=function_modules,
                                        sysText=sysText, reqText=reqText, inpText=inpText,
                                        filePath=filePath, jsonSchema=result_schema, inpLang='ja', outLang='ja', )

                    if (res_text == '') or (res_text == '!'):
                        proc_cancel = True
                        break

                # デバッグ報告
                if (parent_self is not None):
                    _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                                from_port=from_port, to_port=to_port,
                                                system_text=system_text, request_text=inpBase, input_text=chat_text,
                                                result_savepath=result_savepath, result_schema=result_schema,
                                                output_text=inpText, output_data=res_text,
                                                output_path=res_path, output_files=res_files,
                                                status='', )

                chat_text += inpBase.rstrip() + '\n\n'
                chat_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
                res_text2 = res_text.replace('\n\n', '\n')
                chat_text += res_text2.rstrip() + '\n\n'

        output_raw  = res_text
        output_text = ''
        output_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
        output_text += res_text
        output_data = ''
        output_data += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
        output_data += res_data
        output_path = res_path
        output_files = res_files

        if (request_text.lower()[:6] == 'debug,'):
            output_data = input_text

        # ----------------------------------------
        # 後処理
        # ----------------------------------------
        if (proc_cancel != True):
            if (after_proc.find('all,'     ) >= 0) \
            or (after_proc.find('summary,' ) >= 0) \
            or (after_proc.find('code,'    ) >= 0):

                # AI要求
                reqText = ''
                inpBase1 = \
"""
[SYSTEM]
回答予定内容の文章を整理し、最終回答文を作成します。
最終回答文は、他のシステムで利用しますので、不必要な説明は削除してください。
同様に、この文章に至った経緯も不要です。その部分も削除してください。
回答本文と思われる結果のみ、シンプルな文章にしてください。
"""
                inpBase2 = \
"""
あなたの回答は別のAIにより評価、採点されます。
適切な位置で改行して、読みやすい文章にしてください。
文章は、美しい日本語でお願いします。
"""
                if (after_proc.find('all,'     ) >= 0) \
                or (after_proc.find('code,'    ) >= 0):
                    inpBase2 += \
"""
ソースコードが含まれている場合、ソースコードのみ抽出してください。
執筆中の小説の原稿の場合、原稿部分のみ抽出してください。
"""
                if (after_proc.find('all,'     ) >= 0) \
                or (after_proc.find('summary,' ) >= 0):
                    inpBase2 += \
"""
ソースコードや執筆中の小説の原稿ではない場合、最大１分で読み切れる文章長さまで要約してください。
"""
                if  (after_proc.find('all,'     ) >= 0) \
                and (req_engine != after_engine):
                    inpBase2 += \
"""
最終回答文は別のAIで生成されました。ミスがあれば修正をお願いします。
"""
                inpText = \
"""
$$$ inpBase1 $$$

$$$ user_text $$$

### 回答予定内容 ###
$$$ output_text $$$
###

$$$ inpBase2 $$$
"""
                inpText = inpText.replace('$$$ inpBase1 $$$', inpBase1)
                inpText = inpText.replace('$$$ user_text $$$', user_text)
                inpText = inpText.replace('$$$ output_text $$$', output_raw)
                inpText = inpText.replace('$$$ inpBase2 $$$', inpBase2)

                # キャンセル確認
                if (parent_self is not None) \
                and (parent_self.cancel_request == True):
                    return '', '', '', []

                # chatBot処理
                res_text, res_data, res_path, res_files, res_engine, res_name, res_api, self.history = \
                    self.llm.chatBot(   req_mode=req_mode, engine=after_engine,
                                    chat_class='auto', model_select='auto', session_id=self.self_port, 
                                    history=self.history, function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText,
                                    filePath=filePath, jsonSchema=result_schema, inpLang='ja', outLang='ja', )

                chat_text += inpBase1.rstrip() + '\n' + inpBase2.rstrip() + '\n\n'
                chat_text += f"[{ full_name[0] }] ({ self.self_port }:{ res_api }) \n"
                res_text2 = res_text.replace('\n\n', '\n')
                chat_text += res_text2.rstrip() + '\n\n'

                output_raw  = res_text
                output_data = res_data
                output_path = res_path
                output_files = res_files

                # デバッグ報告
                if (parent_self is not None):
                    _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                                from_port=from_port, to_port=to_port,
                                                system_text=system_text, request_text=after_proc, input_text=inpText,
                                                result_savepath=result_savepath, result_schema=result_schema,
                                                output_text=output_text, output_data=output_data,
                                                output_path=output_path, output_files=output_files,
                                                status='', )

        # キャンセル確認
        if (parent_self is not None) \
        and (parent_self.cancel_request == True):
            return '', '', '', []

        # 最終報告
        if (req_mode == 'session'):
            status = 'SESSION'
        else:
            status = 'READY'        
        if (parent_self is not None):
            _ = parent_self.post_complete(  user_id=user_id, req_mode=req_mode,
                                            from_port=from_port, to_port=to_port,
                                            system_text=system_text, request_text=request_text, input_text=input_text,
                                            result_savepath=result_savepath, result_schema=result_schema,
                                            output_text=output_text, output_data=output_data,
                                            output_path=output_path, output_files=output_files,
                                            status=status, )

        # デバッグ報告(会話履歴)
        if (parent_self is not None):
            _ = parent_self.post_debug_log( user_id=user_id, req_mode=req_mode,
                                        from_port=from_port, to_port=to_port,
                                        system_text=system_text, request_text='*** 会話履歴 ***', input_text=user_text,
                                        result_savepath=result_savepath, result_schema=result_schema,
                                        output_text=chat_text, output_data=output_data,
                                        output_path=output_path, output_files=output_files,
                                        status='', )

        # ----------------------------------------
        # AIメンバー解散
        # ----------------------------------------
        for n in range(1, len(member_port)):

            # キャンセル確認
            if (parent_self is not None) \
            and (parent_self.cancel_request == True):
                return '', '', '', []

            # メンバー要求
            bye_text = 'bye,'
            res_port = self.post_request(user_id=user_id, from_port=to_port, to_port=member_port[n],
                                         req_mode='session', 
                                         system_text='', request_text=bye_text, input_text='',
                                         file_names=[], result_savepath='', result_schema='', )

        return output_text, output_data, output_path, output_files



if __name__ == '__main__':
    core_port = '8000'
    self_port = '8101'

    chat_class = ChatClass(runMode='debug', qLog_fn='', core_port=core_port, self_port=self_port)

    input_text = 'おはよう'
    output_text, _, _, _ = chat_class.proc_chat(    user_id='debug', from_port='debug', to_port='8001',
                                                    req_mode='chat', req_engine='',
                                                    req_functions='', req_reset='yes,',
                                                    max_retry='0', max_ai_count='0', 
                                                    before_proc='none,', before_engine='', 
                                                    after_proc='none,', after_engine='',
                                                    check_proc='none,', check_engine='',
                                                    system_text='', request_text='', input_text=input_text,
                                                    file_names=[], result_savepath='', result_schema='', parent_self=None, )
    print(output_text)
