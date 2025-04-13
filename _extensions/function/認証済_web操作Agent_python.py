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
import codecs

from playsound3 import playsound

import threading
import asyncio

import langchain_openai
import langchain_anthropic
import langchain_google_genai


# browser-use
os.environ['ANONYMIZED_TELEMETRY'] = 'false'
#os.environ['BROWSER_USE_LOGGING_LEVEL'] = 'debug'
os.environ['BROWSER_USE_LOGGING_LEVEL'] = 'info'
if (os.name == 'nt'):
    os.environ['CHROME_PATH']='C:/Program Files/Google/Chrome/Application/chrome.exe'
    os.environ['CHROME_USER_DATA']='C:/Users/admin/AppData/Local/Google/Chrome/User Data'
#else:
#    os.environ['CHROME_PATH']='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
#    os.environ['CHROME_USER_DATA']='/Users/<YourUsername>/Library/Application Support/Google/Chrome/<profile name>'

from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig, BrowserContextConfig

# インターフェース
qPath_input       = 'temp/input/'
qPath_output      = 'temp/output/'

qText_ready       = 'Web-Operator function ready!'
qText_start       = 'Web-Operator function start!'
qText_complete    = 'Web-Operator function complete!'
qIO_func2py       = 'temp/web操作Agent_func2py.txt'
qIO_py2func       = 'temp/web操作Agent_py2func.txt'
qIO_liveAiRun     = 'temp/monjyu_live_ai_run.txt'
qIO_agent2live    = 'temp/monjyu_io_agent2live.txt'

# Monjyu連携
import requests

# 定数の定義
CORE_PORT = '8000'
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30



def io_text_read(filename=''):
    text = ''
    file1 = filename
    file2 = filename[:-4] + '.@@@'
    try:
        while (os.path.isfile(file2)):
            os.remove(file2)
            time.sleep(0.10)
        if (os.path.isfile(file1)):
            os.rename(file1, file2)
            time.sleep(0.10)
        if (os.path.isfile(file2)):
            r = codecs.open(file2, 'r', 'utf-8-sig')
            for t in r:
                t = t.replace('\r', '')
                text += t
            r.close
            r = None
            time.sleep(0.25)
        while (os.path.isfile(file2)):
            os.remove(file2)
            time.sleep(0.10)
    except:
        pass
    return text

def io_text_write(filename='', text='', encoding='utf-8', mode='w', ):
    try:
        w = codecs.open(filename, mode, encoding)
        w.write(text)
        w.close()
        w = None
        return True
    except Exception as e:
        print(e)
    w = None
    return False



class _webOperator_class:
    def __init__(self, ):
        self.monjyu = _monjyu_class(runMode='agent', )

        # APIキーを取得
        self.openai_organization = os.environ.get('OPENAI_ORGANIZATION', '< ? >')
        self.openai_key_id = os.environ.get('OPENAI_API_KEY', '< ? >')
        self.freeai_key_id = os.environ.get('FREEAI_API_KEY', '< ? >')
        self.claude_key_id = os.environ.get('ANTHROPIC_API_KEY', '< ? >')

        # engine,model他
        self.agent_engine   = "freeai" # freeai, openai, claude,
        self.agent_model    = "gemini-2.0-flash-exp"
        self.agent_max_step = "20"
        self.agent_browser  = "chromium" # chromium, chrome,

        # 設定
        self.request_queue = None
        self.main_running = False
        self.break_flag = False
        self.error_flag = False

        # タスク
        self.main_task = None

    def play(self, outFile='temp/_work/sound.mp3', ):
        if (outFile is None) or (outFile == ''):
            return False
        if (not os.path.isfile(outFile)):
            return False
        try:
            # 再生
            playsound(sound=outFile, block=True, )
            return True
        except Exception as e:
            print(e)
        return False

    def start(self, ):
        return asyncio.run( self.start_async() )

    async def start_async(self):
        # 初期化
        self.request_queue = asyncio.Queue()
        self.main_running = True
        self.break_flag = False
        self.error_flag = False

        # スレッド処理
        def main_thread():
            print(f" Browser-use : [START] { self.agent_engine } / { self.agent_model } ")
            try:
                asyncio.run( self._main() )
            except Exception as e:
                print(f"main_thread: {e}")
            finally:
                self.break_flag = True
                print(" Browser-use : [END] ")

        # 起動
        self.main_task = threading.Thread(target=main_thread, daemon=True)
        self.main_task.start()
        return True

    def stop(self, ):
        print(" Browser-use : [STOP] ")
        # 停止
        self.break_flag = True
        if (self.main_task is not None):
            self.main_task.join()
            self.main_task = None
        return True

    def request(self, request_text='',):
        return asyncio.run( self.request_async(request_text) )

    async def request_async(self, request_text='',):
        if (self.main_running == False):
            await self.start_async()
        try:
            if (request_text is not None) and (request_text != ''):
                print(f" User(text): { request_text }")
                if (not self.break_flag):

                    # テキスト送信
                    await self.request_queue.put(request_text)

        except Exception as e:
            print(f"request_async: {e}")
            self.error_flag = True
            return False
        return True

    async def _main(self):
        try:
            browser = None
            browser_context = None

            while (not self.break_flag):
                if self.request_queue.empty():
                    await asyncio.sleep(0.25)
                else:
                    request_text = await self.request_queue.get()
                    if request_text is not None:

                        # チェック
                        new_flag = False
                        if browser_context is None:
                            new_flag = True
                        else:
                            try:
                                check = await browser_context.refresh_page()
                            except Exception as e:
                                print(e)
                                new_flag = True
                            #new_flag = True

                        # オープン
                        if (new_flag == True):
                            if browser_context is not None:
                                await browser_context.close()
                            if browser is not None:
                                await browser.close()
                            new_context_config=BrowserContextConfig(
                                disable_security=True,
                                minimum_wait_page_load_time=1,  # 3 on prod
                                maximum_wait_page_load_time=20,  # 20 on prod
                                browser_window_size={
                                    'width': 1280,
                                    'height': 900,
                                },
                            ),

                            # chrome
                            if (self.agent_browser == 'chrome'):
                                if (os.name == 'nt'):
                                    chrome_instance_path='C:/Program Files/Google/Chrome/Application/chrome.exe'
                                else:
                                    chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                                browser = Browser(
                                    config=BrowserConfig(
                                        headless=False,  # UIを表示
                                        disable_security=True,
                                        chrome_instance_path=chrome_instance_path,
                                        new_context_config=new_context_config,
                                    )
                                )

                            # chromium
                            else:
                                browser = Browser(
                                    config=BrowserConfig(
                                        headless=False,  # UIを表示
                                        disable_security=True,
                                        new_context_config=new_context_config,
                                    )
                                )

                            browser_context = await browser.new_context()

                        #print('Web-Operator : (request)')
                        #print(request_text)

                        # 開始音
                        self.play(outFile='_sounds/_sound_accept.mp3')

                        # モデル設定
                        if   (self.agent_engine == 'openai'):
                            llm = langchain_openai.ChatOpenAI(model=self.agent_model, api_key=self.openai_key_id, )
                        elif (self.agent_engine == 'claude'):
                            llm = langchain_anthropic.ChatAnthropic(model=self.agent_model, api_key=self.claude_key_id)
                        else:
                            llm = langchain_google_genai.ChatGoogleGenerativeAI(model=self.agent_model, api_key=self.freeai_key_id)
                        controller = Controller()

                        # agent実行
                        agent = Agent(
                            task=request_text,
                            llm=llm,
                            controller=controller,
                            browser_context=browser_context,
                        )
                        results = await agent.run(max_steps=int(self.agent_max_step), )

                        # 結果
                        result_text = '!'
                        try:
                            final_result = results.final_result()
                            if (final_result is not None) and (final_result != ''):
                                result_text = final_result
                        except Exception as e:
                            #print(e)
                            pass

                        # Monjyu, Live, 連携
                        #self._result(request_text=request_text, result_text=result_text, )
                        result_thread = threading.Thread(
                            target=self._result,args=(request_text, result_text, ),
                            daemon=True
                        )
                        result_thread.start()

                        # 終了音
                        if (result_text != '') and (result_text != '!'):
                            self.play(outFile='_sounds/_sound_ok.mp3')
                        else:
                            self.play(outFile='_sounds/_sound_ng.mp3')

        except Exception as e:
            print(f"_main: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
            await browser_context.close()
            await browser.close()
            self.main_running = False
        return True

    def _result(self, request_text='', result_text='', ):
        try:
            #print('Web-Operator : (result)')
            #print(result_text)

            # Monjyu 連携 (結果通知)
            reqText = request_text.rstrip() + '\n'
            inpText = ''
            outText = f"[Web-Operator] ({ self.agent_engine }/{ self.agent_model })\n"
            outText += result_text.rstrip() + '\n'
            outData = result_text.rstrip() + '\n'

            # (output_log)
            try:
                self.monjyu.post_output_log(outText=outText, outData=outText)
            except Exception as e:
                print(e)

            # (histories)
            try:
                self.monjyu.post_histories(reqText=reqText, inpText=inpText, outText=outText, outData=outData)
            except Exception as e:
                print(e)

            # Live 連携
            if (os.path.isfile(qIO_liveAiRun)):
                text = f"[RESULT] AIエージェント Web-Operator(ウェブオペレーター: browser-use/{ self.agent_engine }/{ self.agent_model }) \n"
                if (request_text.rstrip() != ''):
                    text += request_text.rstrip() + '\nについて、'
                text += "以下が結果報告です。要約して日本語で報告してください。\n"
                text += result_text.rstrip() + '\n\n'
                res = io_text_write(qIO_agent2live, text)

            # Monjyu 連携 (tts指示)
            else:
                sysText = 'あなたは美しい日本語を話す賢いアシスタントです。'
                reqText = "gpt,\n"
                reqText += "AIエージェントの実行結果の報告です。\n"
                if (request_text.rstrip() != ''):
                    reqText += request_text.rstrip() + '\nについて、'
                reqText += "以下が結果報告です。要約した結果を、日本語で音声合成してください。\n"
                inpText = f"[Web-Operator] ({ self.agent_engine }/{ self.agent_model })\n"
                inpText += result_text.rstrip() + '\n'
                try:
                    res_port = self.monjyu.request(req_mode='chat', user_id='admin', sysText=sysText, reqText=reqText, inpText=inpText, )
                except Exception as e:
                    print(e)

        except Exception as e:
            print(f"_result: {e}")
            return False
        return True



class _monjyu_class:
    def __init__(self, runMode='assistant' ):
        self.runMode = runMode

        # ポート設定等
        self.local_endpoint0 = f'http://localhost:{ int(CORE_PORT) + 0 }'
        self.local_endpoint2 = f'http://localhost:{ int(CORE_PORT) + 2 }'
        self.user_id = 'admin'

    def post_output_log(self, outText='', outData=''):
        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint2 + '/post_output_log',
                json={'user_id': self.user_id, 
                      'output_text': outText,
                      'output_data': outData, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                print('error', f"Error response (/post_output_log) : {response.status_code} - {response.text}")
        except Exception as e:
            print('error', f"Error communicating (/post_output_log) : {e}")
            return False
        return True

    def post_histories(self, reqText='', inpText='', outText='', outData=''):
        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint2 + '/post_histories',
                json={'user_id': self.user_id, 'from_port': "web", 'to_port': "web",
                      'req_mode': "agent",
                      'system_text': "", 'request_text': reqText, 'input_text': inpText,
                      'result_savepath': "", 'result_schema': "",
                      'output_text': outText, 'output_data': outData,
                      'output_path': "", 'output_files': [],
                      'status': "READY"},
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                print('error', f"Error response (/post_histories) : {response.status_code} - {response.text}")
        except Exception as e:
            print('error', f"Error communicating (/post_histories) : {e}")
            return False
        return True

    def request(self, req_mode='chat', user_id='admin', sysText='', reqText='', inpText='', ):
        res_port = None

        # ファイル添付
        file_names = []

        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint0 + '/post_req',
                json={'user_id': user_id, 'from_port': CORE_PORT, 'to_port': '',
                    'req_mode': req_mode,
                    'system_text': sysText, 'request_text': reqText, 'input_text': inpText,
                    'file_names': file_names, 'result_savepath': '', 'result_schema': '', },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                res_port = str(response.json()['port'])
            else:
                print('Research-Agent :', f"Error response (/post_req) : {response.status_code}")
        except Exception as e:
            print('Research-Agent :', f"Error communicating (/post_req) : {e}")
        return res_port



if __name__ == '__main__':

    # 初期設定
    webOperator = _webOperator_class()

    # 指示受信クリア
    dummy = io_text_read(qIO_func2py)
    dummy = io_text_read(qIO_agent2live)

    # 出力フォルダ用意
    try:
        os.makedirs(qPath_output)
    except:
        pass

    # 準備完了
    print(qText_ready)
    res = io_text_write(qIO_py2func, qText_ready)

    # 処理ループ
    #debug1 = False
    #debug2 = False
    while True:

        # 指示受信
        json_kwargs = io_text_read(qIO_func2py)

        # debug !
        if False:
            if (debug2 == False) and (debug1 == True):
                debug2 = True
                time.sleep(60)
                request_text = "今日のニュースを検索して報告。"
                json_kwargs= '{ "request_text" : "' + request_text + '" }'
            if (debug1 == False):
                debug1 = True
                time.sleep(5)
                request_text = "Google検索のページ(https://google.co.jp/)を表示して停止。"
                json_kwargs= '{ "request_text" : "' + request_text + '" }'

        # 処理
        if (json_kwargs.strip() != ''):
            res = io_text_write(qIO_py2func, qText_start)

            # (念のため)指示受信クリア
            dummy = io_text_read(qIO_func2py)
            dummy = io_text_read(qIO_agent2live)

            # 1秒待機
            time.sleep(1.00)

            # 引数
            runMode      = None
            request_text = None
            engine       = None
            model        = None
            max_step     = None
            browser      = None
            if (json_kwargs is not None):
                args_dic = json.loads(json_kwargs)
                runMode      = args_dic.get('runMode', 'agent')
                request_text = args_dic.get('request_text', '')
                engine       = args_dic.get('engine', '')
                model        = args_dic.get('model', '')
                max_step     = args_dic.get('max_step', '')
                browser      = args_dic.get('browser', '')

            # パラメータ不明
            if (request_text == ''):
                dic = {}
                dic['result'] = 'ng'
                json_dump = json.dumps(dic, ensure_ascii=False, )
                print(json_dump + '\n' + qText_complete + '\n')
                res = io_text_write(qIO_py2func, json_dump + '\n' + qText_complete)

            else:

                # agent 実行
                if (engine != '') and (model != '') and (max_step != ''):
                    webOperator.agent_engine   = engine
                    webOperator.agent_model    = model
                    webOperator.agent_max_step = max_step
                if (browser != ''):
                    webOperator.agent_browser = browser
                webOperator.request(request_text=request_text)

                # 結果
                res_text  = 'AIエージェント Web-Operator(ウェブオペレーター) が非同期で実行を開始しました。\n'
                res_text += '結果は即答ではありません。別途回答します。\n'

                # 戻り
                dic = {}
                if (res_text != ''):
                    dic['result']      = 'ok'
                    dic['result_text'] = res_text
                else:
                    dic['result']      = 'ng'
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print(json_dump + '\n' + qText_complete + '\n')
                res = io_text_write(qIO_py2func, json_dump + '\n' + qText_complete)

        time.sleep(0.25)


