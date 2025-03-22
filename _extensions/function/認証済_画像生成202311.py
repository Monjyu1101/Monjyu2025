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
import datetime
import time
import codecs

import openai
from io import BytesIO
import requests
from PIL import Image

import numpy as np
import cv2

qPath_output = 'temp/output/'

model_generate = 'dall-e-3'
#model_edit     = 'dall-e-2'

class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "execute_ganerate_image_from_english_prompt"
        self.func_ver  = "v0.20231112"
        self.func_auth = "t2a8hlcccMq1buueq8cuSXk7Ykx4WkChrF8GpgKz40a773tZC36OY2ksOt9SxI2GRdNwNddKArN0+7Ne5BUakQ=="
        self.function  = {
            "name": self.func_name,
            "description": \
"""
英語で書かれたプロンプトをもとに画像生成'generate'を行う。
画像のサイズは３種類から指定できる。正方形は'1024x1024',横長は'1024x1792',スマホ用などで使う縦長は'1792x1024'
画像の品質は２種類から指定できる。標準品質は'standard',高品質は'hd',指定なき場合は標準品質
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "english_prompt": {
                            "type": "string",
                            "description": "英語で書かれたプロンプト (例) cute cat"
                    },
                    "image_size": {
                            "type": "string",
                            "description": "画像のサイズ。正方形は'1024x1024',横長は'1024x1792',縦長は'1792x1024' (例) 1024x1024"
                    },
                    "image_quality": {
                            "type": "string",
                            "description": "画像の品質。標準品質は'standard',高品質は'hd',指定なき場合は標準品質 (例) standard"
                    },
                },
                "required": ["english_prompt"]
            }
        }

        res = self.func_reset()

    def func_reset(self, ):
        self.last_time  = time.time()
        self.last_path  = None
        self.last_image = None

        # APIキーを取得
        self.openai_organization = os.environ.get('OPENAI_ORGANIZATION', '< ? >')
        self.openai_key_id = os.environ.get('OPENAI_API_KEY', '< ? >')
        if (self.openai_organization == '') \
        or (self.openai_organization[:1] == '<') \
        or (self.openai_key_id == '') \
        or (self.openai_key_id[:1] == '<'):
            raise ValueError("Please set your openai organization and key !")

        # APIキーを設定
        openai.organization = self.openai_organization
        openai.api_key      = self.openai_key_id
        self.client = openai.OpenAI(
            organization=self.openai_organization,
            api_key=self.openai_key_id,
        )

        # 出力フォルダ用意
        if (not os.path.isdir(qPath_output)):
            os.makedirs(qPath_output)
        return True

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

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        english_prompt = None
        image_size     = None
        image_quality  = None
        if (json_kwargs != None):
            args_dic = json.loads(json_kwargs)
            english_prompt = args_dic.get('english_prompt')
            image_size     = args_dic.get('image_size')
            image_quality  = args_dic.get('image_quality')
        if (image_size    == None):
            image_size    = '1024x1024'
        if (image_quality == None):
            image_quality = 'standard'

        try:

            if ((time.time() - self.last_time) > 300):
                self.last_path  = None
                self.last_image = None

            # 画像生成
            #if (generate_or_edit == 'genarate'):
            if True:

                # DALL-Eによる画像生成
                response = self.client.images.generate(
                    model=model_generate,
                    prompt=english_prompt,
                    size=image_size,
                    quality=image_quality,
                    n=1,
                    response_format="url"
                )

                # 画像変換
                image_path = response.data[0].url
                get_data   = requests.get(url=image_path, timeout=10, )
                pil_image  = Image.open(BytesIO(get_data.content))
                cv2_img    = self.pil2cv(pil_image=pil_image)
                self.last_time  = time.time()
                self.last_path  = image_path
                self.last_image = cv2_img.copy()

                # 画像保存
                nowTime  = datetime.datetime.now()
                output_path = qPath_output + nowTime.strftime('%Y%m%d.%H%M%S') + '.image.png'
                try:
                    cv2.imwrite(filename=output_path, img=cv2_img, )
                    image_path = output_path
                except:
                    pass

                # 戻り
                dic = {}
                dic['result'] = '画像生成できました'
                dic['image_path'] = image_path
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print('  --> ', json_dump)
                return json_dump

            # 画像編集
            #if (generate_or_edit == 'edit'):
            if True:

                # リサイズ
                if   (image_size.lower() == '256x256'):
                    cv2_img = cv2.resize(self.last_image, (256, 256))
                elif (image_size.lower() == '512x512'):
                    cv2_img = cv2.resize(self.last_image, (512, 512))
                elif (image_size.lower() == '1024x1024'):
                    cv2_img = cv2.resize(self.last_image, (1024, 1024))
                else:
                    cv2_img = self.last_image.copy()

                cv2_rgba  = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2RGBA)
                cv2_rgba[:, :, 3] = 0
                png_image = cv2.imencode('.png', cv2_rgba, )[1]

                # DALL-Eによる画像編集
                response = self.client.images.generate(
                    model=model_edit,
                    image=png_image,
                    prompt=english_prompt,
                    size=image_size,
                    quality=image_quality,
                    n=1,
                    response_format="url"
                )

                # 画像変換
                image_path = response.data[0].url
                get_data   = requests.get(url=image_path, timeout=10, )
                pil_image  = Image.open(BytesIO(get_data.content))
                cv2_img    = self.pil2cv(pil_image=pil_image)
                self.last_time  = time.time()
                self.last_path  = image_path
                self.last_image = cv2_img.copy()

                # 戻り
                dic = {}
                dic['result'] = '画像編集できました'
                dic['image_path'] = image_path
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print('  --> ', json_dump)
                return json_dump

        except Exception as e:
            print(e)

        # 戻り
        dic = {}
        dic['result'] = '画像生成でエラーが発生しました'
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc( '{ "english_prompt": "cute cat", "image_size": "1024x1024", "image_quality": "hd" }' ))
