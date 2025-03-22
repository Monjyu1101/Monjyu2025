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

# OCR
import pytesseract
if (os.name == 'nt'):
    import winocr

from PIL import Image

class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "image_to_text"
        self.func_ver  = "v0.20240421"
        self.func_auth = "Ugn1S2LQIHGRuewaCI3+VSYmEK5gET5h16q+C3ptbpo="
        self.function  = {
            "name": self.func_name,
            "description": "イメージファイルのテキスト化(OCR)",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "addin_ocr_test.jpg"
                    },
                },
                "required": ["runMode", "file_path"]
            }
        }

        # 初期設定
        self.runMode = 'assistant'
        self.tesseract_enable  = True
        if (os.name == 'nt'):
            self.winocr_enable = True
        else:
            self.winocr_enable = False
        self.func_reset()

    def func_reset(self, ):
        if (self.tesseract_enable == True) or (self.winocr_enable == True):
            self.ocr_enable = True
        else:
            self.ocr_enable = False
        return self.ocr_enable

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode   = None
        file_path = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode   = args_dic.get('runMode')
            file_path = args_dic.get('file_path')

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # 処理
        res_okng = 'ng'
        res_text = None

        if (file_path is None) or (not os.path.isfile(file_path)):
            pass

        else:
            image = Image.open(file_path)

            text = ''

            if (text == '') and (self.tesseract_enable == True):
                try:
                    text = pytesseract.image_to_string(image, lang='jpn', config='--psm 6', timeout=30, )
                    text = text.strip()
                    #print('tesseract-OCR\n', text)
                except Exception as e:
                    print(e)
                    self.tesseract_enable = False

            if (text == '') and (self.winocr_enable == True):
                try:
                    res = winocr.recognize_pil_sync(image, 'ja')
                    text = ''
                    for line in res['lines']:
                        text += line['text'] + '\n'
                    #print('win-OCR\n', text)
                except Exception as e:
                    print(e)
                    self.winocr_enable = False

            if (text == ''):
                if (self.tesseract_enable == True) or (self.winocr_enable == True):
                    self.ocr_enable = True
                else:
                    self.ocr_enable = False

            else:

                # 文書成形
                res_text = self.text_replace(text=text, )

        # 戻り
        dic = {}
        if (res_text is not None) and (res_text != ''):
            dic['result']      = 'ok'
            dic['result_text'] = res_text
        else:
            dic['result']      = 'ng'
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump



    def text_replace(self, text=''):
        if "```" not in text:
            return self.text_replace_sub(text)
        else:
            # ```が2か所以上含まれている場合の処理
            first_triple_quote_index = text.find("```")
            last_triple_quote_index = text.rfind("```")
            if first_triple_quote_index == last_triple_quote_index:
                return self.text_replace_sub(text)
            # textの先頭から最初の```までをtext_replace_subで成形
            text_before_first_triple_quote = text[:first_triple_quote_index]
            formatted_before = self.text_replace_sub(text_before_first_triple_quote)
            formatted_before = formatted_before.strip() + '\n'
            # 最初の```から最後の```の直前までを文字列として抽出
            code_block = text[first_triple_quote_index : last_triple_quote_index]
            code_block = code_block.strip() + '\n'
            # 最後の```以降の部分をtext_replace_subで成形
            text_after_last_triple_quote = text[last_triple_quote_index:]
            formatted_after = self.text_replace_sub(text_after_last_triple_quote)
            formatted_after = formatted_after.strip() + '\n'
            # 結果を結合して戻り値とする
            return (formatted_before + code_block + formatted_after).strip()

    def text_replace_sub(self, text='', ):
        if (text.strip() == ''):
            return ''

        text = text.replace('\r', '')

        text = text.replace('。', '。\n')
        text = text.replace('?', '?\n')
        text = text.replace('？', '?\n')
        text = text.replace('!', '!\n')
        text = text.replace('！', '!\n')
        text = text.replace('。\n」','。」')
        text = text.replace('。\n"' ,'。"')
        text = text.replace("。\n'" ,"。'")
        text = text.replace('?\n」','?」')
        text = text.replace('?\n"' ,'?"')
        text = text.replace("?\n'" ,"?'")
        text = text.replace('!\n」','!」')
        text = text.replace('!\n"' ,'!"')
        text = text.replace("!\n'" ,"!'")
        text = text.replace("!\n=" ,"!=")
        text = text.replace("!\n--" ,"!--")

        text = text.replace('\n \n ' ,'\n')
        text = text.replace('\n \n' ,'\n')

        hit = True
        while (hit == True):
            if (text.find('\n\n')>0):
                hit = True
                text = text.replace('\n\n', '\n')
            else:
                hit = False

        return text.strip()



if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc('{ "runMode" : "assistant" }'))

    print(ext.func_proc('{ ' \
                      + '"file_path" : "addin_ocr_test.jpg"' \
                      + ' }'))


