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
import shutil
import glob
import codecs

import subprocess



import importlib

browser = None
try:
    import    認証済_browser連携202406
    browser = 認証済_browser連携202406._class()
except:
    try:
        #loader = importlib.machinery.SourceFileLoader('認証済_browser連携202406.py', '_extensions/clipngpt/認証済_browser連携202406.py')
        loader = importlib.machinery.SourceFileLoader('認証済_browser連携202406.py', '_extensions/function/認証済_browser連携202406.py')
        認証済_browser連携202406 = loader.load_module()
        browser = 認証済_browser連携202406._class()
    except:
        print('★"認証済_browser連携202406"は利用できません！')



# インターフェース
qPath_output  = 'temp/output/'
qPath_sandbox = 'temp/sandbox/'
qSandBox_name = 'react_sandbox'
win_code_path = 'C:/Program Files/Microsoft VS Code/Code.exe'

class sandbox_class:
    def __init__(self, ):
        self.react_proc    = None

        # 出力フォルダ用意
        if (not os.path.isdir(qPath_sandbox)):
            os.makedirs(qPath_sandbox)

        # main,data,addin,botFunc,
        self.main    = None
        self.data    = None
        self.addin   = None
        self.botFunc = None

        # react 準備
        self.abs_path     = os.path.abspath(qPath_sandbox)
        self.sandbox_start = qPath_sandbox + '_' + qSandBox_name + '_start'
        self.sandbox_stop  = qPath_sandbox + '_' + qSandBox_name + '_stop'
        if (os.name == 'nt'):
            self.sandbox_start = self.sandbox_start.replace('/', '\\') + '.bat'
            self.sandbox_stop  = self.sandbox_stop.replace('/', '\\') + '.bat'

        # react 開始
        txts = []
        if (os.name == 'nt'):
            txts.append('taskkill /f /im node.exe')
        txts.append('cd "' + self.abs_path + '"')
        txts.append('call npx create-react-app ' + qSandBox_name)
        txts.append('echo yes > _yes.txt')
        txts.append('cd "' + qSandBox_name + '"')
        txts.append('echo BROWSER=none > .env')
        txts.append('call npm run start --silent < ../_yes.txt')
        txts.append('exit')
        if (os.name == 'nt'):
            self.txtsWrite(filename=self.sandbox_start, txts=txts, encoding='shift_jis', )
        else:
            self.txtsWrite(filename=self.sandbox_start, txts=txts, )

        # react 停止
        txts = []
        if (os.name == 'nt'):
            txts.append('taskkill /f /im node.exe')
        txts.append('cd "' + self.abs_path + '"')
        txts.append('cd "' + qSandBox_name + '"')
        txts.append('call npm run stop --silent')
        txts.append('exit')
        if (os.name == 'nt'):
            self.txtsWrite(filename=self.sandbox_stop, txts=txts, encoding='shift_jis', )
        else:
            self.txtsWrite(filename=self.sandbox_stop, txts=txts, )

    def start(self, ):
        # react 準備
        if (not os.path.isdir(qPath_sandbox + qSandBox_name)) \
        or (not os.path.isfile(qPath_sandbox + '_yes.txt')):

            # 途中キャンセルはリセット
            if (os.path.isdir(qPath_sandbox + qSandBox_name)):
                shutil.rmtree(qPath_sandbox + qSandBox_name)
            if (os.path.isfile(qPath_sandbox + '_yes.txt')):
                os.remove(qPath_sandbox + '_yes.txt')

        # react 終了
        hit = False
        try:
            if (self.react_proc is not None):
                if (self.react_proc.poll() is None):
                    hit = True
                    # 強制停止
                    self.react_proc.terminate()
                    self.react_proc = None
                    time.sleep(1.00)
        except:
            pass

        # react 起動 実行
        if (os.name == 'nt'):
            self.react_proc = subprocess.Popen(['cmd', '/c', 'start', '/min', self.sandbox_start], shell=True, )
        else:
            self.react_proc = subprocess.Popen([self.sandbox_start])

        return True

    def react(self, extract_dir='HalloWorld', ):

        # フォルダ確認
        if (not os.path.isdir(qPath_sandbox + qSandBox_name)) \
        or (not os.path.isfile(qPath_sandbox + '_yes.txt')):
            res_okng = 'ng'
            res_msg  = 'react実行はできません。'
            return res_okng, res_msg

        # フォルダ構成確認
        from_dir     = qPath_sandbox + extract_dir
        from_json    = from_dir + 'package.json'
        to_dir       = qPath_sandbox + qSandBox_name + '/'
        to_json      = qPath_sandbox + qSandBox_name + '/package.json'
        if  (not os.path.isdir(from_dir)) \
        or  (not os.path.isdir(to_dir)):
            res_okng = 'ng'
            res_msg  = 'react実行準備に失敗しました。'
            return res_okng, res_msg

        if  (not os.path.isfile(from_json)) \
        or  (not os.path.isfile(to_json)):
            res_okng = 'ng'
            res_msg  = 'react実行でpackage.jsonが見つかりません。実行準備に失敗しました。'
            return res_okng, res_msg

        #if (os.path.isdir(qPath_sandbox + qSandBox_name)):
        #    shutil.rmtree(qPath_sandbox + qSandBox_name + '/*.*', ignore_errors=True, )

        # ファイルコピー
        #shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)

        # react 準備
        bat_start = qPath_sandbox + extract_dir[:-1] + '_start'
        bat_stop  = qPath_sandbox + extract_dir[:-1] + '_stop'
        if (os.name == 'nt'):
            bat_start = bat_start.replace('/', '\\') + '.bat'
            bat_stop  = bat_stop.replace('/', '\\') + '.bat'

        # react 開始
        txts = []
        if (os.name == 'nt'):
            txts.append('taskkill /f /im node.exe')
        txts.append('cd "' + self.abs_path + '"')
        #txts.append('xcopy /e/h/c/i/y ' + extract_dir[:-1] + ' ' + qSandBox_name)
        #txts.append('cd "' + qSandBox_name + '"')
        txts.append('cd "' + extract_dir[:-1] + '"')
        txts.append('echo BROWSER=none > .env')
        txts.append('call npm i')
        txts.append('call npm run start --silent < ../_yes.txt')
        txts.append('exit')
        if (os.name == 'nt'):
            self.txtsWrite(filename=bat_start, txts=txts, encoding='shift_jis', )
        else:
            self.txtsWrite(filename=bat_start, txts=txts, )
                
        # react 停止
        txts = []
        if (os.name == 'nt'):
            txts.append('taskkill /f /im node.exe')
        txts.append('cd "' + self.abs_path + '"')
        txts.append('cd "' + extract_dir[:-1] + '"')
        txts.append('call npm run stop --silent')
        txts.append('exit')
        if (os.name == 'nt'):
            self.txtsWrite(filename=bat_stop, txts=txts, encoding='shift_jis', )
        else:
            self.txtsWrite(filename=bat_stop, txts=txts, )

        # react 終了
        hit = False
        try:
            if (self.react_proc is not None):
                if (self.react_proc.poll() is None):
                    hit = True
                    # 強制停止
                    self.react_proc.terminate()
                    self.react_proc = None
                    time.sleep(1.00)
        except:
            pass

        # react 起動
        print()
        print(bat_start)
        if (os.name == 'nt'):
            self.react_proc = subprocess.Popen(['cmd', '/c', 'start', '/min', bat_start], shell=True, )
        else:
            self.react_proc = subprocess.Popen([bat_start])

        res_okng = 'ok'
        res_msg  = 'react実行中です。'
        return res_okng, res_msg

    def browser(self, url='index.html', ):
        if (browser is None):
            res_okng = 'ng'
            res_msg  = 'browser実行はできません。'
            return res_okng, res_msg

        # ブラウザ起動
        dic = {}
        dic['show_or_hide'] = 'show'
        dic['url']          = url
        #dic['browser']      = 'chrome'
        dic['browser']      = 'edge'
        dic['full_size']    = 'no'
        json_dump  = json.dumps(dic, ensure_ascii=False, )
        res_json   = browser.func_proc(json_dump)
        args_dic   = json.loads(res_json)
        res_okng   = args_dic.get('result')
        if (res_okng == 'ok'):
            res_msg = '確認表示を開始しました。ユーザーは確認中です。'
        else:
            res_msg = '確認表示に失敗しました。'
        return res_okng, res_msg

    def python(self, run_file='HalloWorld.py', ):
        # サブプロセスで、VS CODE 実行
        try:
            if (os.name == 'nt'):
                subprocess.Popen([win_code_path, run_file, ])
            else:
                subprocess.Popen(['code', run_file, ])
            res_okng = 'ok'
            res_msg  = '確認表示を開始しました。ユーザーは確認中です。'
        except Exception as e:
            print(e)
            res_okng = 'ng'
            res_msg  = '確認表示に失敗しました。'
        return res_okng, res_msg

    def txtsRead(self, filename, encoding='utf-8', exclusive=False, ):
        if (not os.path.exists(filename)):
            return False, ''

        encoding2 = encoding
        if (encoding2 == 'utf-8'):
            encoding2 =  'utf-8-sig'

        if (exclusive == False):
            try:
                txts = []
                txt  = ''
                r = codecs.open(filename, 'r', encoding2)
                for t in r:
                    t = t.replace('\n', '')
                    t = t.replace('\r', '')
                    txt  = (txt + ' ' + str(t)).strip()
                    txts.append(t)
                r.close
                r = None
                return txts, txt
            except Exception as e:
                r = None
                return False, ''
        else:
            f2 = filename[:-4] + '.txtsRead.tmp'
            res = self.remove(f2, )
            if (res == False):
                return False, ''
            else:
                try:
                    os.rename(filename, f2)
                    txts = []
                    txt  = ''
                    r = codecs.open(f2, 'r', encoding2)
                    for t in r:
                        t = t.replace('\n', '')
                        t = t.replace('\r', '')
                        txt = (txt + ' ' + str(t)).strip()
                        txts.append(t)
                    r.close
                    r = None
                    self.remove(f2, )
                    return txts, txt
                except Exception as e:
                    r = None
                    return False, ''

    def txtsWrite(self, filename, txts=[''], encoding='utf-8', exclusive=False, mode='w', ):
        if (exclusive == False):
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
                w = None
                return False
        else:
            res = self.remove(filename, )
            if (res == False):
                return False
            else:
                f2 = filename[:-4] + '.txtsWrite.tmp'
                res = self.remove(f2, )
                if (res == False):
                    return False
                else:
                    try:
                        w = codecs.open(f2, mode, encoding)
                        for txt in txts:
                            if (encoding != 'shift_jis'):
                                w.write(txt + '\n')
                            else:
                                w.write(txt + '\r\n')
                        w.close()
                        w = None
                        os.rename(f2, filename)
                        return True
                    except Exception as e:
                        w = None
                        return False



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "automatic_sandbox"
        self.func_ver  = "v0.20240630"
        self.func_auth = "qlRA8KERJOS0Xi7iwzDwxj47GRoGF7k78+525z/QNCo="
        self.function  = {
            "name": self.func_name,
            "description": "AIからダウンロードした内容が実行可能形式の場合、自動的にサンドボックス機能を呼び出す。",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "HalloWorld.zip"
                    },
                    "browser": {
                        "type": "string",
                        "description": "ブラウザ表示 auto,yes,no 例) auto"
                    },
                },
                "required": ["runMode", "file_path"]
            }
        }

        # 初期設定
        self.runMode = 'assistant'
        self.sandbox = sandbox_class()
        self.last_reset = 0
        self.func_reset()

    def func_reset(self, main=None, data=None, addin=None, botFunc=None, ):
        if (main is not None):
            self.sandbox.main = main
        if (data is not None):
            self.sandbox.data = data
        if (addin is not None):
            self.sandbox.addin = addin
        if (botFunc is not None):
            self.sandbox.botFunc = botFunc

        # 連続リセットは無視
        if ((time.time() - self.last_reset) < 60):
            return True

        try:
            if (not os.path.isdir(qPath_sandbox + qSandBox_name)):
                del self.sandbox
                self.sandbox = sandbox_class()
        except Exception as e:
            print(e)

        self.sandbox.start()
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode   = None
        file_path = None
        browser   = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode   = args_dic.get('runMode')
            file_path = args_dic.get('file_path')
            browser   = args_dic.get('browser', 'auto')

        if (runMode is None) or (runMode == ''):
            runMode = self.runMode
        else:
            self.runMode = runMode

        # 処理
        res_okng = 'ng'
        res_msg  = ''

        # パス確認
        if (file_path is None) or (file_path == ''):
            pass
        else:

            # ファイル確認
            file_name   = os.path.basename(file_path)
            if (not os.path.isfile(qPath_output + file_name)):
                pass
            else:

                # html 確認
                if (file_name[-5:].lower() == '.html'):
                    # react_sandbox起動中
                    to_file = qPath_sandbox + 'react_sandbox/public/index.html'
                    if (os.path.isfile(to_file)):
                        shutil.copy2(qPath_output + file_name, to_file)

                    else:
                        # ブラウザ 実行
                        if (browser != 'no'):
                            pass
                            # vscode

                # zip 確認
                elif (file_name[-4:].lower() == '.zip'):

                    extract_dir = file_name.replace('.zip', '') + '/'

                    # 解凍
                    if (os.path.isdir(qPath_sandbox + extract_dir)):
                        shutil.rmtree(qPath_sandbox + extract_dir, ignore_errors=True, )
                    shutil.unpack_archive(filename=qPath_output + file_name, extract_dir=qPath_sandbox + extract_dir, )

                    # フォルダ２重時、自動解消
                    path = qPath_sandbox + extract_dir
                    path_files = glob.glob(path + '*.*')
                    print('★files count (*.*) =', len(path_files))
                    if (len(path_files) == 0):
                        path_files = glob.glob(path + '*')
                        print('★files count (*) =', len(path_files))
                        if (len(path_files) == 1):
                            print('★path_files[0] =', path_files[0])
                            if (os.path.isdir(path_files[0])):
                                if (os.path.isdir(qPath_sandbox + extract_dir)):
                                    shutil.rmtree(qPath_sandbox + extract_dir, ignore_errors=True, )
                                shutil.unpack_archive(filename=qPath_output + file_name, extract_dir=qPath_sandbox, )
                                extract_dir = os.path.basename(path_files[0]) + '/'
                                print('★extract_dir =', extract_dir)

                    # フォルダ解析
                    one_file = None

                    path = qPath_sandbox + extract_dir
                    path_files = glob.glob(path + '*.*')
                    path_files.sort()
                    if (len(path_files) > 0):
                        for f in path_files:
                            if (os.path.isfile(f)):
                                base_name = os.path.basename(f)
                                if (one_file == None):
                                    one_file = base_name
                                else:
                                    if   (base_name == 'package.json'):
                                        one_file = base_name
                                    elif (one_file  == 'package.json'):
                                        pass
                                    elif (one_file  == 'index.html'):
                                        pass
                                    else:
                                        one_file = ''

                    # ファイル解析
                    if (one_file is None) or (one_file == ''):
                        pass
                    else:
                        file_ext = os.path.splitext(one_file)[1][1:].lower()

                        # react 実行
                        if (one_file == 'package.json'):

                            # react 実行
                            res_okng, res_msg = self.sandbox.react(extract_dir=extract_dir, )
                            if (res_okng == 'ok'):
                                time.sleep(5.00)
                                # ブラウザ 実行
                                if (browser == 'yes'):
                                    res_okng, res_msg = self.sandbox.browser(url='http://localhost:3000/', )

                        # html
                        elif (file_ext in ('html', 'htm')):
                            abs_path = os.path.abspath(qPath_sandbox + extract_dir)
                            if (os.name == 'nt'):
                                run_file = abs_path + '\\' + one_file
                            else:
                                run_file = abs_path + '/' + one_file
                            # ブラウザ 実行
                            if (browser != 'no'):
                                res_okng, res_msg = self.sandbox.browser(url=run_file, )

                        # python
                        elif (file_ext in ('py', 'ipynb')):
                            abs_path = os.path.abspath(qPath_sandbox + extract_dir)
                            if (os.name == 'nt'):
                                run_file = abs_path + '\\' + one_file
                            else:
                                run_file = abs_path + '/' + one_file

                            # flask ?
                            flask_hit = False
                            try:
                                _, txt = self.sandbox.txtsRead(filename=run_file, )
                                if (txt.lower().find(' flask') >= 0):
                                    flask_hit = True
                            except:
                                pass

                            # python 実行
                            res_okng, res_msg = self.sandbox.python(run_file=run_file, )
                            if (res_okng == 'ok') and (flask_hit == True):
                                # ブラウザ 実行
                                if (browser == 'yes'):
                                    res_okng, res_msg = self.sandbox.browser(url='http://localhost:5000/', )

        # 戻り
        dic = {}
        if (res_okng == 'ok'):
            dic['result'] = 'ok'
            if (res_msg is not None) and (res_msg != ''):
                dic['result_text'] = res_msg
        else:
            dic['result'] = 'ng'
            if (res_msg is not None) and (res_msg != ''):
                dic['error_text'] = res_msg
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump



if __name__ == '__main__':

    ext = _class()

    time.sleep(120.00)

    print(ext.func_proc('{ ' \
                      + '"runMode" : "assistant",' \
                      + '"file_path" : "react_sandbox.zip"' \
                      + ' }'))

    #print(ext.func_proc('{ ' \
    #                  + '"file_path" : "openai-realtime-console-main.zip"' \
    #                  + ' }'))

    time.sleep(180.00)

