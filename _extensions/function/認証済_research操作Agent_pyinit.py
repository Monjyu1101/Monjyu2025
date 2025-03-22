#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

# 静的インストール
import sys
import os
import time
import datetime
import codecs

import shutil
import subprocess

# インターフェース
qText_ready       = 'Research-Agent function ready!'
qText_start       = 'Research-Agent function start!'
qText_complete    = 'Research-Agent function complete!'
qIO_func2py       = 'temp/research操作Agent_func2py.txt'
qIO_py2func       = 'temp/research操作Agent_py2func.txt'

B_USE_VERSION     = '0.1.37'

qPath_sandbox     = 'temp/sandbox/'
qWebUI_name       = 'web-ui-main'
qWebUI_zip        = '_datas/reacts/web-ui-main.zip'



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

# 動的インストール
def pip_install(module='', ver=None):
    try:
        if ver is None:
            pip_parm = ['python', '-m', 'pip', 'install', '--upgrade', module]
            install_proc = subprocess.call(pip_parm, shell=True, )
        else:
            pip_parm = ['python', '-m', 'pip', 'install', '--upgrade', '{}=={}'.format(module, ver)]
            install_proc = subprocess.call(pip_parm, shell=True, )
    except:
        print("pip install error!: {}".format(module))



if __name__ == '__main__':

    # 出力フォルダ用意
    if (not os.path.isdir('temp')):
        os.makedirs('temp')

    # インストール確認
    try:
        import_flag = False
        from playsound3 import playsound
        import playwright
        import gradio
        import json_repair
    except:
        import_flag = True

    # 動的インストール
    if (import_flag == True) \
    or (not os.path.isdir(qPath_sandbox + qWebUI_name)):

        print('install start...')

        # 解凍
        if (os.path.isfile(qWebUI_zip)):
            if (os.path.isdir(qPath_sandbox + qWebUI_name)):
                shutil.rmtree(qPath_sandbox + qWebUI_name, ignore_errors=True, )
            os.makedirs(qPath_sandbox + qWebUI_name)
            shutil.unpack_archive(filename=qWebUI_zip, extract_dir=qPath_sandbox, )

        # インストール
        print('pip install ...')
        pip_install('pip')
        pip_install('wheel')
        pip_install('setuptools')

        pip_install('playsound3')
        pip_install('playwright')

        # browser-use
        pip_install('langchain-openai')
        pip_install('langchain-anthropic')
        pip_install('langchain-google-genai')
        #pip_install('browser-use')
        pip_install('browser-use', '0.1.40')

        requirement_file = qPath_sandbox + qWebUI_name + '/requirements.txt'
        if (not os.path.isfile(requirement_file)):

            # web-ui
            #pip_install('browser-use')
            #pip_install('browser-use', B_USE_VERSION)
            pip_install('pyperclip')
            pip_install('gradio')
            pip_install('json-repair')
            pip_install('langchain-mistralai')

        if (os.path.isfile(requirement_file)):
            print('requirements install ...')
            if (os.name == 'nt'):
                install_proc2 = subprocess.call(['cmd', '/c', f"pip install -r { requirement_file }"], shell=True, )
            else:
                install_proc2 = subprocess.call([f"pip install -r { requirement_file }"])

        if (os.name == 'nt'):
            print('')
            pipshow_proc = subprocess.Popen(['cmd', '/c', 'pip show browser-use'], shell=True, )
            print('')

        print('playwright install ...')
        if (os.name == 'nt'):
            install_proc1 = subprocess.Popen(['cmd', '/c', 'start /min playwright install'], shell=True, )
        else:
            install_proc1 = subprocess.Popen(['playwright install'])

        print('install complete! ')

    # 準備完了
    #print(qText_ready)
    res = io_text_write(qIO_py2func, qText_ready)

    #print('install ok.')
    sys.exit(0)


