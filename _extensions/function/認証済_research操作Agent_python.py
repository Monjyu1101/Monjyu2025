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

import sys
import os
import time
import datetime
import codecs
import glob

from playsound3 import playsound
import threading
import requests

import subprocess

import gradio_client

# インターフェース
qPath_input       = 'temp/input/'
qPath_output      = 'temp/output/'

qText_ready       = 'Research-Agent function ready!'
qText_start       = 'Research-Agent function start!'
qText_complete    = 'Research-Agent function complete!'
qIO_func2py       = 'temp/research操作Agent_func2py.txt'
qIO_py2func       = 'temp/research操作Agent_py2func.txt'
qIO_liveAiRun     = 'temp/monjyu_live_ai_run.txt'
qIO_agent2live    = 'temp/monjyu_io_agent2live.txt'

qPath_sandbox     = 'temp/sandbox/'
qWebUI_name       = 'web-ui-main'

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

def txtsWrite(filename, txts=[''], encoding='utf-8', mode='w', ):
    try:
        w = codecs.open(filename, mode, encoding)
        for txt in txts:
            if (encoding != 'shift_jis'):
                w.write(txt + '\n')
            else:
                w.write(txt + '\r\n')
        w.close()
        w = None
        return True
    except Exception as e:
        print(e)
    w = None
    return False



class _researchAgent_class:
    def __init__(self, ):
        self.monjyu = _monjyu_class(runMode='agent', )

        # 接続
        self.client = None

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

        # browser-use
        os.environ['ANONYMIZED_TELEMETRY'] = 'false'
        #os.environ['BROWSER_USE_LOGGING_LEVEL'] = 'debug'
        os.environ['BROWSER_USE_LOGGING_LEVEL'] = 'info'
        if (os.name == 'nt'):
            os.environ['CHROME_PATH']='C:/Program Files/Google/Chrome/Application/chrome.exe'
            os.environ['CHROME_USER_DATA']='C:/Users/admin/AppData/Local/Google/Chrome/User Data'
        else:
            os.environ['CHROME_PATH']='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            os.environ['CHROME_USER_DATA']='/Users/<YourUsername>/Library/Application Support/Google/Chrome/<profile name>'

        # WebUI 環境準備
        self.abs_path  = os.path.abspath(qPath_sandbox)
        self.webui_bat = qPath_sandbox + '_' + qWebUI_name + '_bat'
        if (os.name == 'nt'):
            self.webui_bat = self.webui_bat.replace('/', '\\') + '.bat'

        txts = []
        txts.append('cd "' + self.abs_path + '"')
        txts.append('cd "' + qWebUI_name + '"')
        txts.append('python webui.py')
        txts.append('exit')
        if (os.name == 'nt'):
            txtsWrite(filename=self.webui_bat, txts=txts, encoding='shift_jis', )
        else:
            txtsWrite(filename=self.webui_bat, txts=txts, )

        # WebUI Start!
        print('Research start ...')
        if (os.name == 'nt'):
            webui_proc = subprocess.Popen(['cmd', '/c', f"start /min { self.webui_bat }"], shell=True, )
        else:
            webui_proc = subprocess.Popen([f"{ self.webui_bat }"])

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

    def client_open(self):
        if (self.client is None):
            try:
                self.client = gradio_client.Client("http://localhost:7788/")
                return self.client
            except Exception as e:
                print('gradio_client open error!', e)
                self.client = None
        return self.client

    def stop_agent(self):
        client = self.client_open()
        if (client is None):
            print('gradio_client not open error!')
            return False
        try:
            result = client.predict(api_name="/stop_agent")
            print(result)
            return True
        except Exception as e:
            print(e)
        return False

    def stop_research_agent(self):
        client = self.client_open()
        if (client is None):
            print('gradio_client not open error!')
            return False
        try:
            result = client.predict(api_name="/stop_research_agent")
            print(result)
            return True
        except Exception as e:
            print(e)
        return False

    def close_global_browser(self):
        client = self.client_open()
        if (client is None):
            print('gradio_client not open error!')
            return False
        try:
            result = client.predict(api_name="/close_global_browser")
            print(result)
            result = client.predict(api_name="/close_global_browser_1")
            print(result)
            return True
        except Exception as e:
            print(e)
        return False

    def request(self, request_text='', ):
        #print('Research-Agent : (request) ')
        #print(request_text)

        # スレッド処理
        #self.deep_search(request_text=request_text, )
        agent_thread = threading.Thread(
            target=self.run_deep_search,args=(request_text, ),
            daemon=True,
        )
        agent_thread.start()

        return True

    def run_deep_search(self, request_text='',):
        client = self.client_open()
        if (client is None):
            print('gradio_client not open error!')
            return False

        # 開始音
        self.play(outFile='_sounds/_sound_accept.mp3')

        # 旧中断
        self.stop_agent()
        self.stop_research_agent()
        self.close_global_browser()

        # パラメータ
        if   (self.agent_engine == 'openai'):
            provider = 'openai'
            api_key  = self.openai_key_id
        elif (self.agent_engine == 'claude'):
            provider = 'anthropic'
            api_key  = self.claude_key_id
        else:
            provider = 'google'
            api_key  = self.freeai_key_id
        if (self.agent_browser == 'chrome'):
            use_own_browser = True
            headless = False
        else:
            use_own_browser = False
            headless = False

        # 実行
        result = client.predict(
                api_name="/run_deep_search",
                research_task=request_text,
                max_search_iteration_input=int(self.agent_max_step),
                max_query_per_iter_input=1,

                llm_provider=provider,
                llm_model_name=self.agent_model,
                #llm_temperature=1,
                #llm_base_url="",
                llm_api_key=api_key,
                use_vision=True,

                use_own_browser=use_own_browser,
                headless=headless,
                )

        # 結果抽出
        result_text = ''
        for res in result:
            #print("#" + res + "#")
            if (res is None):
                break
            if (res != '') and (res != '[]'):
                if (res[:2] != 'C:'):
                    result_text += res + '\n'
            else:
                break

        # 終了
        self.stop_research_agent()
        self.close_global_browser()

        # live, Monjyu, 連携
        self._result(result_text=result_text, )

        # 終了音
        if (result_text != '') and (result_text != '!'):
            self.play(outFile='_sounds/_sound_ok.mp3')
        else:
            self.play(outFile='_sounds/_sound_ng.mp3')
        return True

    def run_with_stream(self, request_text='',):
        client = self.client_open()
        if (client is None):
            print('gradio_client not open error!')
            return False

        # 開始音
        self.play(outFile='_sounds/_sound_accept.mp3')

        # 旧中断
        self.stop_agent()
        self.stop_research_agent()
        #self.close_global_browser()

        # パラメータ
        if   (self.agent_engine == 'openai'):
            provider = 'openai'
            api_key  = self.openai_key_id
        elif (self.agent_engine == 'claude'):
            provider = 'anthropic'
            api_key  = self.claude_key_id
        else:
            provider = 'google'
            api_key  = self.freeai_key_id
        if (self.agent_browser == 'chrome'):
            use_own_browser = True
        else:
            use_own_browser = False

        # 実行
        result = client.predict(
                api_name="/run_with_stream",
                task=request_text,
                add_infos="Hello!!",
                max_steps=int(self.agent_max_step),
                max_actions_per_step=10,

                agent_type="custom",
                llm_provider=provider,
                llm_model_name=self.agent_model,
                #llm_temperature=1,
                #llm_base_url="",
                llm_api_key=api_key,
                use_vision=True,
                tool_calling_method="auto",

                use_own_browser=use_own_browser,
                keep_browser_open=True,
                headless=False,
                disable_security=True,
                window_w=1280,
                window_h=900,
                #save_recording_path="./tmp/record_videos",
                #save_agent_history_path="./tmp/agent_history",
                #save_trace_path="./tmp/traces",
                #enable_recording=True,
                )

        # 結果抽出
        result_text = ''
        for res in result:
            #print("#" + res + "#")
            if (res != '') and (res != '[]'):
                if (res[:3] != '<h1'):
                    result_text += res + '\n'
            else:
                break

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
        return True

    def _result(self, request_text='', result_text='', ):
        try:
            #print('Research-Agent : (result)')
            #print(result_text)

            # Monjyu 連携 (結果通知)
            reqText = request_text.rstrip() + '\n'
            inpText = ''
            outText = f"[Research-Agent] ({ self.agent_engine }/{ self.agent_model })\n"
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
                text = f"[RESULT] AIエージェント Research-Agent(リサーチエージェント: browser-use/web-ui/{ self.agent_engine }/{ self.agent_model }) \n"
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
                inpText = f"[Research-Agent] ({ self.agent_engine }/{ self.agent_model })\n"
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
        self.local_endpoint = f'http://localhost:{ CORE_PORT }'
        self.user_id = 'admin'

    def post_output_log(self, outText='', outData=''):
        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint + '/post_output_log',
                json={'user_id': self.user_id, 
                      'output_text': outText,
                      'output_data': outData, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                print('error', f"Error response ({ CORE_PORT }/post_output_log) : {response.status_code} - {response.text}")
        except Exception as e:
            print('error', f"Error communicating ({ CORE_PORT }/post_output_log) : {e}")
            return False
        return True

    def post_histories(self, reqText='', inpText='', outText='', outData=''):
        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint + '/post_histories',
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
                print('error', f"Error response ({ CORE_PORT }/post_histories) : {response.status_code} - {response.text}")
        except Exception as e:
            print('error', f"Error communicating ({ CORE_PORT }/post_histories) : {e}")
            return False
        return True

    def request(self, req_mode='chat', user_id='admin', sysText='', reqText='', inpText='', ):
        res_port = None

        # ファイル添付
        file_names = []

        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint + '/post_req',
                json={'user_id': user_id, 'from_port': CORE_PORT, 'to_port': '',
                    'req_mode': req_mode,
                    'system_text': sysText, 'request_text': reqText, 'input_text': inpText,
                    'file_names': file_names, 'result_savepath': '', 'result_schema': '', },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                res_port = str(response.json()['port'])
            else:
                print('Research-Agent :', f"Error response ({ CORE_PORT }/post_req) : {response.status_code}")
        except Exception as e:
            print('Research-Agent :', f"Error communicating ({ CORE_PORT }/post_req) : {e}")
        return res_port



if __name__ == '__main__':

    # 初期設定
    researchAgent = _researchAgent_class()

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
                    researchAgent.agent_engine   = engine
                    researchAgent.agent_model    = model
                    researchAgent.agent_max_step = max_step
                if (browser != ''):
                    researchAgent.agent_browser = browser
                researchAgent.request(request_text=request_text)

                # 結果
                res_text  = 'AIエージェント Research-Agent(リサーチエージェント) が非同期で実行を開始しました。\n'
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


