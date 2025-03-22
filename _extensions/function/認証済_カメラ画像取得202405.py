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



class cam_class:
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

    def cv2capture(self, dev='0', retry_max=2, retry_wait=1.00, ):

        retry_max   = retry_max
        retry_count = 0
        check       = False
        while (check == False) and (retry_count <= retry_max):
            # キャプチャー
            image = self.cv2capture_sub(dev, )
            if (image is not None):
                check = True
            # リトライ
            if (check == False):
                time.sleep(retry_wait)
                retry_count += 1

        if (check == True):
            return image
        else:
            return None

    def cv2capture_sub(self, dev='0', ):
        image   = None

        # オープン
        res = self.cv2open(dev=dev, )

        # 取り込み
        if  (res == True):
            image = self.cv2read()

        # クローズ
        self.cv2close()

        return image

    def cv2open(self, dev='0', ):

        # クローズ
        self.cv2close()

        # オープン
        try:
            if (not str(dev).isdigit()):
                self.cv2video = cv2.VideoCapture(dev)
            else:
                if (os.name != 'nt'):
                    self.cv2video = cv2.VideoCapture(int(dev))
                else:
                    self.cv2video = cv2.VideoCapture(int(dev), cv2.CAP_DSHOW)
        except Exception as e:
            self.cv2video  = None
            self.cv2device = None
            return False

        self.cv2device = dev
        return True

    def cv2read(self, ):
        frame = None

        # 取り込み
        if (self.cv2video is not None):
            try:
                ret, frame = self.cv2video.read()
            except Exception as e:
                ret = False
                frame = None

        return frame

    def cv2close(self, ):

        # クローズ
        try:
            self.cv2video.release()
        except Exception as e:
            pass

        self.cv2video  = None
        self.cv2device = None
        return True

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
        self.func_name = "get_camera_image"
        self.func_ver  = "v0.20240518"
        self.func_auth = "VVgwbx7lLdVV+Fd35+T9MKIGuzg70oQ8f3SAIV8iaNc="
        self.function  = {
            "name": self.func_name,
            "description": \
"""
機密保持の必要性から、この機能は指示があった場合のみ実行する。
この機能で、カメラ画像が取得できる。
オプションでカメラのデバイス番号の指定が可能で、指定があった場合はそのデバイス番号のカメラ画像を取得する。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "device_number": {
                        "type": "string",
                        "description": "デバイス番号 auto,0,1,2... 例）auto"
                    },
                },
                "required": ["runMode"]
            }
        }

        # 初期設定
        self.runMode  = 'assistant'
        self.sub_proc = cam_class(runMode=self.runMode, )
        self.func_reset()

        self.file_seq = 0

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode       = None
        device_number = None
        if (json_kwargs is not None):
            args_dic      = json.loads(json_kwargs)
            runMode       = args_dic.get('runMode')
            device_number = str( args_dic.get('device_number') )

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # デバイス番号
        if (device_number is None):
            device_number = '0'
        if (not str(device_number).isdigit()):
            device_number = '0'

        # カメラ画像取得
        cv_img = self.sub_proc.cv2capture(dev=device_number, )
        filename = None

        # 画像保存
        if (cv_img is not None):

            # カウンタ
            self.file_seq += 1
            if (self.file_seq > 9999):
                self.file_seq = 1

            # ファイル名
            winTitle   = 'camShot'
            nowTime    = datetime.datetime.now()
            yyyymmdd   = nowTime.strftime('%Y%m%d')
            stamp      = nowTime.strftime('%Y%m%d.%H%M%S')
            seq        = '{:04}'.format(self.file_seq)
            filename   = qPath_output + stamp + '.' + seq + '.' + winTitle + '.jpg'

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
                      + '"device_number" : "auto"' \
                      + ' }'))


