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
if (os.name == 'nt'):
    from io import StringIO
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage

class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "pdf_to_text"
        self.func_ver  = "v0.20240421"
        self.func_auth = "maw8/1eQW13ingbZ1zbQvFxBm1euvDk/1835MJeAgRg="
        self.function  = {
            "name": self.func_name,
            "description": "ＰＤＦファイル内容のテキスト化",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "addin_pdf_test.pdf"
                    },
                },
                "required": ["runMode", "file_path"]
            }
        }

        # 初期設定
        self.runMode = 'assistant'
        self.func_reset()

    def func_reset(self, ):
        self.pdf_enable     = False

        # ＰＤＦ有効化
        if (os.name == 'nt'):
            self.pdf_enable = True

        return self.pdf_enable

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

            text = ''
            try:

                fp = open(file_path, 'rb')

                # 出力する
                outfp = StringIO()

                # PDFファイル内のリソース(テキスト、画像、罫線など)を管理する総元締め的なクラス
                rmgr = PDFResourceManager()

                # PDFファイルのレイアウトパラメータを保持するクラス
                lprms = LAParams()

                # PDFファイル内のテキストを取り出す機能を提供するクラス 
                device = TextConverter(rmgr, outfp, laparams=lprms)

                # PDFファイルを1ページずつ取得。集合(set)として保持するクラス
                iprtr = PDFPageInterpreter(rmgr, device)

                for page in PDFPage.get_pages(fp):
                    iprtr.process_page(page)

                text = outfp.getvalue()

                outfp.close()
                device.close()
                fp.close()

            except Exception as e:
                print(e)
                text = '!'

            # 文書成形
            res_text = self.text_replace(text=text, )

        # 戻り
        dic = {}
        if (res_text is not None):
            if (res_text != ''):
                dic['result']      = 'ok'
                dic['result_text'] = res_text
            else:
                dic['result']      = 'ng'
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
                      + '"file_path" : "addin_pdf_test.pdf"' \
                      + ' }'))


