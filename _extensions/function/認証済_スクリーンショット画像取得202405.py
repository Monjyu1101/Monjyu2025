#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

import sys
import os
import time
import datetime
import codecs
import glob

import json

from playsound3 import playsound

import screeninfo
import pyautogui
from PIL import ImageGrab

import numpy as np
import cv2

if (os.name == 'nt'):
    import ctypes
    from ctypes import wintypes
    #import win32con



# インターフェース

qPath_output   = 'temp/output/'

qPath_work     = 'temp/_work/'
qPath_pictures = 'temp/_work/'
qPath_videos   = 'temp/_work/'
if (os.name == 'nt'):
    qUSERNAME = os.environ["USERNAME"]
    qPath_pictures = 'C:/Users/' + qUSERNAME + '/Pictures/RiKi/'
    qPath_videos   = 'C:/Users/' + qUSERNAME + '/Videos/RiKi/'
else:
    qUSERNAME = os.environ["USER"]



class scrnShot_class:
    def __init__(self, runMode='assistant', ):
        self.runMode      = runMode
        
        # ディレクトリ作成
        if (not os.path.isdir(qPath_output)):
            os.makedirs(qPath_output)
        if (not os.path.isdir(qPath_work)):
            os.makedirs(qPath_work)
        if (not os.path.isdir(qPath_pictures)):
            os.makedirs(qPath_pictures)
        if (not os.path.isdir(qPath_videos)):
            os.makedirs(qPath_videos)

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

    def screen_shot(self, screen_number='auto', ):

        workfile = qPath_work + 'screenShot.png'
        cv_img   = None

        # メイン画面 のみ
        if (len(screeninfo.get_monitors()) == 0):
            pyautogui.screenshot(workfile)
            cv_image = cv2.imread(workfile)
            cv_img   = cv_image.copy()
            if (os.path.isfile(workfile)):
                os.remove(workfile)

        # 全画面
        elif (str(screen_number) == 'all'):
            try:
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )
                cv_img   = cv_image.copy()
            except:
                time.sleep(0.50)
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )
                cv_img   = cv_image.copy()

        # マルチ画面 切り出し
        else:
            try:
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )
            except:
                time.sleep(0.50)
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )

            # スクリーン指定確認
            if (str(screen_number).isdigit()):
                if (int(screen_number) < 0) \
                or (int(screen_number) >= len(screeninfo.get_monitors())):
                    screen_number = 'auto'

            # 全スクリーンの配置
            min_left     = 0
            min_top      = 0
            max_right    = 0
            max_buttom   = 0
            for s in screeninfo.get_monitors():
                if (s.x < min_left):
                    min_left = s.x
                if (s.y  < min_top):
                    min_top = s.y
                if ((s.x+s.width) > max_right):
                    max_right = (s.x+s.width)
                if ((s.y+s.height) > max_buttom):
                    max_buttom = (s.y+s.height)

            # マウス配置
            (mouse_x,mouse_y) = pyautogui.position()

            # 画像切り出し
            screen = -1
            for s in screeninfo.get_monitors():
                screen += 1

                # 処理スクリーン？
                flag = False
                if (str(screen_number).isdigit()):
                    if (int(screen_number) == screen):
                        flag = True
                else:
                    if  (mouse_x >= s.x) and (mouse_x <= (s.x+s.width)) \
                    and (mouse_y >= s.y) and (mouse_y <= (s.y+s.height)):
                        flag = True

                # 切り出し
                if (flag == True):
                    left = s.x - min_left
                    top  = s.y - min_top

                    cv_img = np.zeros((s.height, s.width, 3), np.uint8)
                    cv_img[ 0:s.height, 0:s.width ] = cv_image[ top:top+s.height, left:left+s.width ]

        # 戻り値
        return cv_img

    def pil2cv(self, pil_image=None):
        try:
            cv2_image = np.array(pil_image, dtype=np.uint8)
            if (cv2_image.ndim == 2):  # モノクロ
                pass
            elif (cv2_image.shape[2] == 3):  # カラー
                cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)
            elif (cv2_image.shape[2] == 4):  # 透過
                cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGBA2BGRA)
            return cv2_image
        except:
            pass
        return None

    def findWindow(self, winTitle='Display', ):
        if (os.name != 'nt'):
            return False
        parent_handle = ctypes.windll.user32.FindWindowW(0, winTitle)
        if (parent_handle == 0):
            return False
        else:
            return parent_handle

    def setForegroundWindow(self, winTitle='Display', ):
        if (os.name != 'nt'):
            return False
        parent_handle = self.findWindow(winTitle)
        if (parent_handle == False):
            return False
        else:
            ctypes.windll.user32.SetForegroundWindow(parent_handle)
            return True



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "get_screen_shot_image"
        self.func_ver  = "v0.20240518"
        self.func_auth = "ZFAWzm18nZue2xv3G0iL9WlZ8JURmY02coUaaj20R2cVss1D6Fl0sViyOPJyFVwF"
        self.function  = {
            "name": self.func_name,
            "description": \
"""
機密保持の必要性から、この機能は指示があった場合のみ実行する。
この機能で、スクリーンショット画像が取得できる。
オプションでスクリーン番号の指定が可能で、指定があった場合はそのスクリーンの画像を取得する。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "screen_number": {
                        "type": "string",
                        "description": "スクリーン番号 auto,all,0,1,2... 例）auto"
                    },
                },
                "required": ["runMode"]
            }
        }

        # 初期設定
        self.runMode  = 'assistant'
        self.sub_proc = scrnShot_class(runMode=self.runMode, )
        self.func_reset()

        self.file_seq = 0

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode       = None
        screen_number = None
        if (json_kwargs is not None):
            args_dic      = json.loads(json_kwargs)
            runMode       = args_dic.get('runMode')
            screen_number = str( args_dic.get('screen_number') )

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # スクリーン番号
        if (screen_number is None):
            screen_number = 'auto'

        # スクリーンショット
        cv_img   = self.sub_proc.screen_shot(screen_number=screen_number)
        filename = None

        # 画像保存
        if (cv_img is not None):

            # カウンタ
            self.file_seq += 1
            if (self.file_seq > 9999):
                self.file_seq = 1

            # ファイル名
            winTitle   = 'screenShot'
            nowTime    = datetime.datetime.now()
            yyyymmdd   = nowTime.strftime('%Y%m%d')
            stamp      = nowTime.strftime('%Y%m%d.%H%M%S')
            seq        = '{:04}'.format(self.file_seq)
            filename   = qPath_output + stamp + '.' + seq + '.' + winTitle + '.png'

            # 確認表示
            try:
                cv_height, cv_width = cv_img.shape[:2]
                cv_img2 = cv2.resize(cv_img, (int(cv_width/3), int(cv_height/3)))
                cv2.rectangle(cv_img2, (0, 0), (int(cv_width/3), int(cv_height/3)), (0, 0, 255), thickness=10, )
                # 表示
                cv2.imshow(winTitle, cv_img2)
                cv2.waitKey(1)
                self.sub_proc.setForegroundWindow(winTitle=winTitle, )
            except Exception as e:
                print(e)

            try:
                chkTime = time.time()

                # シャッター音
                self.sub_proc.play('_sounds/_sound_shutter.mp3')

                # 画像保存
                cv2.imwrite(filename, cv_img)
                if (not os.path.isdir(qPath_pictures + yyyymmdd + '/')):
                    os.makedirs(qPath_pictures + yyyymmdd + '/')
                filename2 = filename.replace(qPath_output, qPath_pictures + yyyymmdd + '/')
                cv2.imwrite(filename2, cv_img)

                # ２秒待機
                while ((time.time() - chkTime) < 2):
                    time.sleep(0.10)
            except Exception as e:
                print(e)

            # 確認消去
            try:
                cv2.destroyWindow(winTitle)
                cv2.waitKey(1)
            except Exception as e:
                print(e)

        # 戻り
        dic = {}
        if (filename is not None):
            dic['result'] = 'ok'
            dic['image_path'] = filename
        else:
            dic['result'] = 'ng'
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ ' \
                      + '"screen_number" : "auto"' \
                      + ' }'))


