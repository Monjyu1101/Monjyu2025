#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'llm'

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
import codecs
import random

from typing import Dict, List, Tuple

# freeai チャットボット
import speech_bot_chatgpt
import speech_bot_chatgpt_key as chatgpt_key
import speech_bot_respo
import speech_bot_respo_key as respo_key
import speech_bot_gemini
import speech_bot_gemini_key as gemini_key
import speech_bot_freeai
import speech_bot_freeai_key as freeai_key
import speech_bot_claude
import speech_bot_claude_key as claude_key
import speech_bot_openrt
import speech_bot_openrt_key as openrt_key
import speech_bot_perplexity
import speech_bot_perplexity_key as perplexity_key
import speech_bot_grok
import speech_bot_grok_key as grok_key
import speech_bot_groq
import speech_bot_groq_key as groq_key
import speech_bot_ollama
import speech_bot_ollama_key as ollama_key


# インターフェース
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'
qPath_input  = 'temp/input/'
qPath_output = 'temp/output/'


class llm_class:
    """
    チャットボットクラス
    """
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '',
                        main=None, conf=None, data=None, addin=None, botFunc=None, mcpHost=None,
                        coreAPI=None, ):
        """
        コンストラクタ
        Args:
            runMode (str, optional): 実行モード。
            qLog_fn (str, optional): ログファイル名。
        """
        self.runMode = runMode

        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'
        
        # ログの初期化
        #qLog.init(mode='logger', filename=qLog_fn)
        logger.debug("init")

        # 設定
        self.main       = main
        self.conf       = conf
        self.data       = data
        self.addin      = addin
        self.coreAPI     = coreAPI
        self.botFunc    = botFunc
        self.mcpHost    = mcpHost

        # bot 定義
        self.history            = []
        self.chatgpt_enable     = None
        self.respo_enable       = None
        self.gemini_enable      = None
        self.freeai_enable      = None
        self.claude_enable      = None
        self.openrt_enable      = None
        self.perplexity_enable  = None
        self.grok_enable        = None
        self.groq_enable        = None
        self.ollama_enable      = None

        # CANCEL要求
        self.bot_cancel_request = False

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

        hit = True
        while (hit == True):
            if (text.find('\n\n')>0):
                hit = True
                text = text.replace('\n  \n', '\n')
                text = text.replace('\n \n', '\n')
                text = text.replace('\n\n', '\n')
            else:
                hit = False

        return text.strip()

    def chatgpt_auth(self):
        """
        chatgpt 認証
        """

        # chatgpt 定義
        self.chatgptAPI = speech_bot_chatgpt._chatgptAPI()
        self.chatgptAPI.init(stream_queue=None)
        chatgptKEY = chatgpt_key._conf_class()
        chatgptKEY.init(runMode=self.runMode)

        # chatgpt 認証情報
        api_type      	= chatgptKEY.api_type
        organization  	= chatgptKEY.openai_organization
        openai_key_id 	= chatgptKEY.openai_key_id
        endpoint      	= chatgptKEY.azure_endpoint
        version       	= chatgptKEY.azure_version
        azure_key_id  	= chatgptKEY.azure_key_id
        if (self.conf is not None):
            if (self.conf.openai_api_type not in ['', 'auto']):
                api_type = self.conf.openai_api_type
            if (self.conf.openai_organization[:1] not in ['', '<']):
                organization = self.conf.openai_organization
            if (self.conf.openai_key_id[:1] not in ['', '<']):
                openai_key_id = self.conf.openai_key_id
            if (self.conf.azure_endpoint[:1] not in ['', '<']):
                endpoint = self.conf.azure_endpoint
            if (self.conf.azure_version not in ['', 'yyyy-mm-dd']):
                version = self.conf.azure_version
            if (self.conf.azure_key_id[:1] not in ['', '<']):
                azure_key_id = self.conf.azure_key_id

        # chatgpt 認証実行
        res = self.chatgptAPI.authenticate('chatgpt',
                            api_type,
                            chatgptKEY.default_gpt, chatgptKEY.default_class,
                            chatgptKEY.auto_continue,
                            chatgptKEY.max_step, chatgptKEY.max_session,
                            chatgptKEY.max_wait_sec,

                            organization, openai_key_id,
                            endpoint, version, azure_key_id,

                            chatgptKEY.a_nick_name, chatgptKEY.a_model, chatgptKEY.a_token,
                            chatgptKEY.a_use_tools,
                            chatgptKEY.b_nick_name, chatgptKEY.b_model, chatgptKEY.b_token,
                            chatgptKEY.b_use_tools,
                            chatgptKEY.v_nick_name, chatgptKEY.v_model, chatgptKEY.v_token,
                            chatgptKEY.v_use_tools,
                            chatgptKEY.x_nick_name, chatgptKEY.x_model, chatgptKEY.x_token,
                            chatgptKEY.x_use_tools,
                            )

        if res == True:
            self.chatgpt_enable = True
            #logger.info('chatgpt authenticate OK!')
        else:
            self.chatgpt_enable = False
            logger.error('chatgpt authenticate NG!')

        return self.chatgpt_enable

    def respo_auth(self):
        """
        respo 認証
        """

        # respo 定義
        self.respoAPI = speech_bot_respo._respoAPI()
        self.respoAPI.init(stream_queue=None)
        respoKEY = respo_key._conf_class()
        respoKEY.init(runMode=self.runMode)

        # respo 認証情報
        api_type      	= respoKEY.api_type
        organization  	= respoKEY.openai_organization
        openai_key_id 	= respoKEY.openai_key_id
        endpoint      	= respoKEY.azure_endpoint
        version       	= respoKEY.azure_version
        azure_key_id  	= respoKEY.azure_key_id
        if (self.conf is not None):
            if (self.conf.openai_api_type not in ['', 'auto']):
                api_type = self.conf.openai_api_type
            if (self.conf.openai_organization[:1] not in ['', '<']):
                organization = self.conf.openai_organization
            if (self.conf.openai_key_id[:1] not in ['', '<']):
                openai_key_id = self.conf.openai_key_id
            if (self.conf.azure_endpoint[:1] not in ['', '<']):
                endpoint = self.conf.azure_endpoint
            if (self.conf.azure_version not in ['', 'yyyy-mm-dd']):
                version = self.conf.azure_version
            if (self.conf.azure_key_id[:1] not in ['', '<']):
                azure_key_id = self.conf.azure_key_id

        # respo 認証実行
        res = self.respoAPI.authenticate('respo',
                            api_type,
                            respoKEY.default_gpt, respoKEY.default_class,
                            respoKEY.auto_continue,
                            respoKEY.max_step, respoKEY.max_session,
                            respoKEY.max_wait_sec,

                            organization, openai_key_id,
                            endpoint, version, azure_key_id,

                            respoKEY.a_nick_name, respoKEY.a_model, respoKEY.a_token,
                            respoKEY.a_use_tools,
                            respoKEY.b_nick_name, respoKEY.b_model, respoKEY.b_token,
                            respoKEY.b_use_tools,
                            respoKEY.v_nick_name, respoKEY.v_model, respoKEY.v_token,
                            respoKEY.v_use_tools,
                            respoKEY.x_nick_name, respoKEY.x_model, respoKEY.x_token,
                            respoKEY.x_use_tools,
                            )

        if res == True:
            self.respo_enable = True
            #logger.info('respo authenticate OK!')
        else:
            self.respo_enable = False
            logger.error('respo authenticate NG!')

        return self.respo_enable

    def gemini_auth(self):
        """
        gemini 認証
        """

        # gemini 定義
        self.geminiAPI = speech_bot_gemini._geminiAPI()
        self.geminiAPI.init(stream_queue=None)
        geminiKEY = gemini_key._conf_class()
        geminiKEY.init(runMode=self.runMode)

        # gemini 認証情報
        key_id = geminiKEY.gemini_key_id
        if (self.conf is not None):
            if (self.conf.gemini_key_id[:1] not in ['', '<']):
                key_id = self.conf.gemini_key_id

        # gemini 認証実行
        res = self.geminiAPI.authenticate('google',
                            geminiKEY.api_type,
                            geminiKEY.default_gpt, geminiKEY.default_class,
                            geminiKEY.auto_continue,
                            geminiKEY.max_step, geminiKEY.max_session,
                            geminiKEY.max_wait_sec,

                            key_id,

                            geminiKEY.a_nick_name, geminiKEY.a_model, geminiKEY.a_token,
                            geminiKEY.a_use_tools,
                            geminiKEY.b_nick_name, geminiKEY.b_model, geminiKEY.b_token,
                            geminiKEY.b_use_tools,
                            geminiKEY.v_nick_name, geminiKEY.v_model, geminiKEY.v_token,
                            geminiKEY.v_use_tools,
                            geminiKEY.x_nick_name, geminiKEY.x_model, geminiKEY.x_token,
                            geminiKEY.x_use_tools,
                            )

        if res == True:
            self.gemini_enable = True
            #logger.info('google (Gemini) authenticate OK!')
        else:
            self.gemini_enable = False
            logger.error('google (Gemini) authenticate NG!')

        return self.gemini_enable

    def freeai_auth(self):
        """
        freeai 認証
        """

        # freeai 定義
        self.freeaiAPI = speech_bot_freeai._freeaiAPI()
        self.freeaiAPI.init(stream_queue=None)
        freeaiKEY = freeai_key._conf_class()
        freeaiKEY.init(runMode=self.runMode)

        # freeai 認証情報
        key_id = freeaiKEY.freeai_key_id
        if (self.conf is not None):
            if (self.conf.freeai_key_id[:1] not in ['', '<']):
                key_id = self.conf.freeai_key_id

        # freeai 認証実行
        res = self.freeaiAPI.authenticate('google',
                            freeaiKEY.api_type,
                            freeaiKEY.default_gpt, freeaiKEY.default_class,
                            freeaiKEY.auto_continue,
                            freeaiKEY.max_step, freeaiKEY.max_session,
                            freeaiKEY.max_wait_sec,

                            key_id,

                            freeaiKEY.a_nick_name, freeaiKEY.a_model, freeaiKEY.a_token,
                            freeaiKEY.a_use_tools,
                            freeaiKEY.b_nick_name, freeaiKEY.b_model, freeaiKEY.b_token,
                            freeaiKEY.b_use_tools,
                            freeaiKEY.v_nick_name, freeaiKEY.v_model, freeaiKEY.v_token,
                            freeaiKEY.v_use_tools,
                            freeaiKEY.x_nick_name, freeaiKEY.x_model, freeaiKEY.x_token,
                            freeaiKEY.x_use_tools,
                            )

        if res == True:
            self.freeai_enable = True
            #logger.info('google (FreeAI) authenticate OK!')
        else:
            self.freeai_enable = False
            logger.error('google (FreeAI) authenticate NG!')

        return self.freeai_enable

    def claude_auth(self):
        """
        claude 認証
        """

        # claude 定義
        self.claudeAPI = speech_bot_claude._claudeAPI()
        self.claudeAPI.init(stream_queue=None)
        claudeKEY = claude_key._conf_class()
        claudeKEY.init(runMode=self.runMode)

        # claude 認証情報
        key_id = claudeKEY.claude_key_id
        if (self.conf is not None):
            if (self.conf.claude_key_id[:1] not in ['', '<']):
                key_id = self.conf.claude_key_id

        # claude 認証実行
        res = self.claudeAPI.authenticate('anthropic',
                            claudeKEY.api_type,
                            claudeKEY.default_gpt, claudeKEY.default_class,
                            claudeKEY.auto_continue,
                            claudeKEY.max_step, claudeKEY.max_session,
                            claudeKEY.max_wait_sec,

                            key_id,

                            claudeKEY.a_nick_name, claudeKEY.a_model, claudeKEY.a_token,
                            claudeKEY.a_use_tools,
                            claudeKEY.b_nick_name, claudeKEY.b_model, claudeKEY.b_token,
                            claudeKEY.b_use_tools,
                            claudeKEY.v_nick_name, claudeKEY.v_model, claudeKEY.v_token,
                            claudeKEY.v_use_tools,
                            claudeKEY.x_nick_name, claudeKEY.x_model, claudeKEY.x_token,
                            claudeKEY.x_use_tools,
                            )

        if res == True:
            self.claude_enable = True
            #logger.info('anthropic (Claude) authenticate OK!')
        else:
            self.claude_enable = False
            logger.error('anthropic (Claude) authenticate NG!')

        return self.claude_enable

    def openrt_auth(self):
        """
        openrt 認証
        """

        # openrt 定義
        self.openrtAPI = speech_bot_openrt._openrtAPI()
        self.openrtAPI.init(stream_queue=None)
        openrtKEY = openrt_key._conf_class()
        openrtKEY.init(runMode=self.runMode)

        # openrt 認証情報
        key_id = openrtKEY.openrt_key_id
        if (self.conf is not None):
            if (self.conf.openrt_key_id[:1] not in ['', '<']):
                key_id = self.conf.openrt_key_id

        # openrt 認証実行
        res = self.openrtAPI.authenticate('openrouter',
                            openrtKEY.api_type,
                            openrtKEY.default_gpt, openrtKEY.default_class,
                            openrtKEY.auto_continue,
                            openrtKEY.max_step, openrtKEY.max_session,
                            openrtKEY.max_wait_sec,

                            key_id,

                            openrtKEY.a_nick_name, openrtKEY.a_model, openrtKEY.a_token,
                            openrtKEY.a_use_tools,
                            openrtKEY.b_nick_name, openrtKEY.b_model, openrtKEY.b_token,
                            openrtKEY.b_use_tools,
                            openrtKEY.v_nick_name, openrtKEY.v_model, openrtKEY.v_token,
                            openrtKEY.v_use_tools,
                            openrtKEY.x_nick_name, openrtKEY.x_model, openrtKEY.x_token,
                            openrtKEY.x_use_tools,
                            )

        if res == True:
            self.openrt_enable = True
            #logger.info('openRouter authenticate OK!')
        else:
            self.openrt_enable = False
            logger.error('openRouter authenticate NG!')

        return self.openrt_enable

    def perplexity_auth(self):
        """
        perplexity 認証
        """

        # perplexity 定義
        self.perplexityAPI = speech_bot_perplexity._perplexityAPI()
        self.perplexityAPI.init(stream_queue=None)
        perplexityKEY = perplexity_key._conf_class()
        perplexityKEY.init(runMode=self.runMode)

        # perplexity 認証情報
        key_id = perplexityKEY.perplexity_key_id
        if (self.conf is not None):
            if (self.conf.perplexity_key_id[:1] not in ['', '<']):
                key_id = self.conf.perplexity_key_id

        # perplexity 認証実行
        res = self.perplexityAPI.authenticate('perplexity',
                            perplexityKEY.api_type,
                            perplexityKEY.default_gpt, perplexityKEY.default_class,
                            perplexityKEY.auto_continue,
                            perplexityKEY.max_step, perplexityKEY.max_session,
                            perplexityKEY.max_wait_sec,

                            key_id,

                            perplexityKEY.a_nick_name, perplexityKEY.a_model, perplexityKEY.a_token,
                            perplexityKEY.a_use_tools,
                            perplexityKEY.b_nick_name, perplexityKEY.b_model, perplexityKEY.b_token,
                            perplexityKEY.b_use_tools,
                            perplexityKEY.v_nick_name, perplexityKEY.v_model, perplexityKEY.v_token,
                            perplexityKEY.v_use_tools,
                            perplexityKEY.x_nick_name, perplexityKEY.x_model, perplexityKEY.x_token,
                            perplexityKEY.x_use_tools,
                            )

        if res == True:
            self.perplexity_enable = True
            #logger.info('perplexity authenticate OK!')
        else:
            self.perplexity_enable = False
            logger.error('perplexity authenticate NG!')

        return self.perplexity_enable

    def grok_auth(self):
        """
        grok 認証
        """

        # grok 定義
        self.grokAPI = speech_bot_grok._grokAPI()
        self.grokAPI.init(stream_queue=None)
        grokKEY = grok_key._conf_class()
        grokKEY.init(runMode=self.runMode)

        # grok 認証情報
        key_id   = grokKEY.grok_key_id
        if (self.conf is not None):
            if (self.conf.grok_key_id[:1] not in ['', '<']):
                key_id = self.conf.grok_key_id

        # grok 認証実行
        res = self.grokAPI.authenticate('grok',
                            grokKEY.api_type,
                            grokKEY.default_gpt, grokKEY.default_class,
                            grokKEY.auto_continue,
                            grokKEY.max_step, grokKEY.max_session,
                            grokKEY.max_wait_sec,

                            key_id,

                            grokKEY.a_nick_name, grokKEY.a_model, grokKEY.a_token,
                            grokKEY.a_use_tools,
                            grokKEY.b_nick_name, grokKEY.b_model, grokKEY.b_token,
                            grokKEY.b_use_tools,
                            grokKEY.v_nick_name, grokKEY.v_model, grokKEY.v_token,
                            grokKEY.v_use_tools,
                            grokKEY.x_nick_name, grokKEY.x_model, grokKEY.x_token,
                            grokKEY.x_use_tools,
                            )

        if res == True:
            self.grok_enable = True
            #logger.info('grok authenticate OK!')
        else:
            self.grok_enable = False
            logger.error('grok authenticate NG!')

        return self.grok_enable

    def groq_auth(self):
        """
        groq 認証
        """

        # groq 定義
        self.groqAPI = speech_bot_groq._groqAPI()
        self.groqAPI.init(stream_queue=None)
        groqKEY = groq_key._conf_class()
        groqKEY.init(runMode=self.runMode)

        # groq 認証情報
        key_id = groqKEY.groq_key_id
        if (self.conf is not None):
            if (self.conf.groq_key_id[:1] not in ['', '<']):
                key_id = self.conf.groq_key_id

        # groq 認証実行
        res = self.groqAPI.authenticate('groq',
                            groqKEY.api_type,
                            groqKEY.default_gpt, groqKEY.default_class,
                            groqKEY.auto_continue,
                            groqKEY.max_step, groqKEY.max_session,
                            groqKEY.max_wait_sec,

                            key_id,

                            groqKEY.a_nick_name, groqKEY.a_model, groqKEY.a_token,
                            groqKEY.a_use_tools,
                            groqKEY.b_nick_name, groqKEY.b_model, groqKEY.b_token,
                            groqKEY.b_use_tools,
                            groqKEY.v_nick_name, groqKEY.v_model, groqKEY.v_token,
                            groqKEY.v_use_tools,
                            groqKEY.x_nick_name, groqKEY.x_model, groqKEY.x_token,
                            groqKEY.x_use_tools,
                            )

        if res == True:
            self.groq_enable = True
            #logger.info('groq authenticate OK!')
        else:
            self.groq_enable = False
            logger.error('groq authenticate NG!')

        return self.groq_enable

    def ollama_auth(self):
        """
        ollama 認証
        """

        # ollama 定義
        self.ollamaAPI = speech_bot_ollama._ollamaAPI()
        self.ollamaAPI.init(stream_queue=None)
        ollamaKEY = ollama_key._conf_class()
        ollamaKEY.init(runMode=self.runMode)

        # ollama 認証情報
        server = ollamaKEY.ollama_server
        port = ollamaKEY.ollama_port
        if (self.conf is not None):
            if (self.conf.ollama_server not in['', 'auto']):
                server = self.conf.ollama_server
            if (self.conf.ollama_port not in['', 'auto']):
                port = self.conf.ollama_port

        # ollama 認証実行
        res = self.ollamaAPI.authenticate('ollama',
                            ollamaKEY.api_type,
                            ollamaKEY.default_gpt, ollamaKEY.default_class,
                            ollamaKEY.auto_continue,
                            ollamaKEY.max_step, ollamaKEY.max_session,
                            ollamaKEY.max_wait_sec,

                            server, port,

                            ollamaKEY.a_nick_name, ollamaKEY.a_model, ollamaKEY.a_token,
                            ollamaKEY.a_use_tools,
                            ollamaKEY.b_nick_name, ollamaKEY.b_model, ollamaKEY.b_token,
                            ollamaKEY.b_use_tools,
                            ollamaKEY.v_nick_name, ollamaKEY.v_model, ollamaKEY.v_token,
                            ollamaKEY.v_use_tools,
                            ollamaKEY.x_nick_name, ollamaKEY.x_model, ollamaKEY.x_token,
                            ollamaKEY.x_use_tools,
                            )

        if res == True:
            self.ollama_enable = True
            #logger.info('ollama authenticate OK!')
        else:
            self.ollama_enable = False
            logger.error('ollama authenticate NG!')

        return self.ollama_enable

    def chatBot(self,   req_mode='chat', engine='freeai',
                        chat_class='auto', model_select='auto', session_id='debug', 
                        history=[], function_modules={},
                        sysText='', reqText='', inpText='',
                        filePath=[], jsonSchema=None, inpLang='ja', outLang='ja'):

        # DEBUG
        if reqText:
            logger.debug("subbot.chatBot:reqText")
            logger.debug(reqText)
        if inpText:
            logger.debug("subbot.chatBot:inpText")
            logger.debug(inpText)

        # 認証実行

        if (self.chatgpt_enable is None):
            self.chatgpt_auth()
        if (self.respo_enable is None):
            self.respo_auth()
        if (self.gemini_enable is None):
            self.gemini_auth()
        if (self.freeai_enable is None):
            self.freeai_auth()
        if (self.claude_enable is None):
            self.claude_auth()
        if (self.openrt_enable is None):
            self.openrt_auth()
        if (self.perplexity_enable is None):
            self.perplexity_auth()
        if (self.grok_enable is None):
            self.grok_auth()
        if (self.groq_enable is None):
            self.groq_auth()
        if (self.ollama_enable is None):
            self.ollama_auth()

        #logger.info('chatBot start')
        print()

        # pass 1
        req_hit = reqText.find(',', 1, 20)
        inp_hit = inpText.find(',', 1, 20)
        if (engine != '') or (req_hit >= 1) or (inp_hit >= 1):
            res_text, res_data, res_path, res_files, res_engine, res_name, res_api, history = \
                self.chatBot_sub(   req_mode=req_mode, engine=engine,
                                    chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                    history=history, function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText,
                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
        else:
            res_text        = ''
            res_data        = ''
            res_path        = ''
            res_files       = []
            res_engine      = ''
            res_name        = None
            res_api         = None

        # pass 2 (エンジン指定なし?,エラー? 自動再試行)
        if ((res_text == '') or (res_text == '!')):
            engine2 = ''
            if   (self.freeai_enable == True):
                engine2 = '[freeai]'
            elif (self.openrt_enable == True):
                engine2 = '[openrt]'
            elif (self.gemini_enable == True):
                engine2 = '[gemini]'
            elif (self.chatgpt_enable == True):
                engine2 = '[chatgpt]'
            elif (self.ollama_enable == True):
                engine2 = '[ollama]'

            if (engine2 != ''):
                # pass 2
                res_text, res_data, res_path, res_files, res_engine, res_name, res_api, history = \
                self.chatBot_sub(   req_mode=req_mode, engine=engine2,
                                    chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                    history=history, function_modules=function_modules,
                                    sysText=sysText, reqText=reqText, inpText=inpText,
                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )

        if (res_text != '') and (res_text != '!'):
            #logger.info('chatBot complite!')
            print()
        else:
            #logger.info('chatBot error!')
            print('!')
            print()
        return res_text, res_data, res_path, res_files, res_engine, res_name, res_api, history

    def chatBot_sub(self,   req_mode='chat', engine='freeai',
                        chat_class='auto', model_select='auto', session_id='debug', 
                        history=[], function_modules={},
                        sysText='', reqText='', inpText='',
                        filePath=[], jsonSchema=None, inpLang='ja', outLang='ja'):

        # cancel
        self.bot_cancel_request = False
        
        # 戻り値
        res_text        = ''
        res_data        = ''
        res_path        = ''
        res_files       = []
        res_engine      = ''
        res_name        = None
        res_api         = None
        res_history     = history

        # chatBot 実行

        engine_text = ''

        # # schema 指定
        # if (jsonSchema is not None) and (jsonSchema != ''):
        #     if (engine == ''):
        #         if (self.openai_enable == True):
        #             engine = '[openai]'

        # chatgpt
        if  ((res_text == '') or (res_text == '!')) \
        and (self.chatgpt_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("chatgpt, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[chatgpt]'):
                engine_text = self.chatgptAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name1 = 'chatgpt'
                model_nick_name2 = 'riki'
                a_nick_name = self.chatgptAPI.a_nick_name.lower()
                b_nick_name = self.chatgptAPI.b_nick_name.lower()
                v_nick_name = self.chatgptAPI.v_nick_name.lower()
                x_nick_name = self.chatgptAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        reqText = reqText[len(model_nick_name1)+1:].strip()
                    elif (req_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        reqText = reqText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        inpText = inpText[len(model_nick_name1)+1:].strip()
                    elif (inp_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        inpText = inpText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### ChatGPT ###')

                    if (self.coreAPI is not None):
                        self.chatgptAPI.set_models( max_wait_sec=self.coreAPI.subbot.llm.chatgptAPI.max_wait_sec,
                                                    a_model=self.coreAPI.subbot.llm.chatgptAPI.a_model,
                                                    a_use_tools=self.coreAPI.subbot.llm.chatgptAPI.a_use_tools,
                                                    b_model=self.coreAPI.subbot.llm.chatgptAPI.b_model,
                                                    b_use_tools=self.coreAPI.subbot.llm.chatgptAPI.b_use_tools,
                                                    v_model=self.coreAPI.subbot.llm.chatgptAPI.v_model,
                                                    v_use_tools=self.coreAPI.subbot.llm.chatgptAPI.v_use_tools,
                                                    x_model=self.coreAPI.subbot.llm.chatgptAPI.x_model,
                                                    x_use_tools=self.coreAPI.subbot.llm.chatgptAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.chatgptAPI.chatBot(    chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                    history=history, function_modules=function_modules,
                                                    sysText=sysText, reqText=reqText, inpText=inpText2,
                                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'ChatGPT'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # respo
        if  ((res_text == '') or (res_text == '!')) \
        and (self.respo_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("respo, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[respo]'):
                engine_text = self.respoAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name1 = 'respo'
                model_nick_name2 = 'vision'
                a_nick_name = self.respoAPI.a_nick_name.lower()
                b_nick_name = self.respoAPI.b_nick_name.lower()
                v_nick_name = self.respoAPI.v_nick_name.lower()
                x_nick_name = self.respoAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        reqText = reqText[len(model_nick_name1)+1:].strip()
                    elif (req_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        reqText = reqText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        inpText = inpText[len(model_nick_name1)+1:].strip()
                    elif (inp_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        inpText = inpText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### Respo ###')

                    if (self.coreAPI is not None):
                        self.respoAPI.set_models(   max_wait_sec=self.coreAPI.subbot.llm.respoAPI.max_wait_sec,
                                                    a_model=self.coreAPI.subbot.llm.respoAPI.a_model,
                                                    a_use_tools=self.coreAPI.subbot.llm.respoAPI.a_use_tools,
                                                    b_model=self.coreAPI.subbot.llm.respoAPI.b_model,
                                                    b_use_tools=self.coreAPI.subbot.llm.respoAPI.b_use_tools,
                                                    v_model=self.coreAPI.subbot.llm.respoAPI.v_model,
                                                    v_use_tools=self.coreAPI.subbot.llm.respoAPI.v_use_tools,
                                                    x_model=self.coreAPI.subbot.llm.respoAPI.x_model,
                                                    x_use_tools=self.coreAPI.subbot.llm.respoAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.respoAPI.chatBot(      chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                    history=history, function_modules=function_modules,
                                                    sysText=sysText, reqText=reqText, inpText=inpText2,
                                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'Respo'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # gemini
        if  ((res_text == '') or (res_text == '!')) \
        and (self.gemini_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("gemini, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[gemini]'):
                engine_text = self.geminiAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name = 'gemini'
                a_nick_name = self.geminiAPI.a_nick_name.lower()
                b_nick_name = self.geminiAPI.b_nick_name.lower()
                v_nick_name = self.geminiAPI.v_nick_name.lower()
                x_nick_name = self.geminiAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        reqText = reqText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        inpText = inpText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### Gemini ###')

                    if (self.coreAPI is not None):
                        self.geminiAPI.set_models(  max_wait_sec=self.coreAPI.subbot.llm.geminiAPI.max_wait_sec,
                                                    a_model=self.coreAPI.subbot.llm.geminiAPI.a_model,
                                                    a_use_tools=self.coreAPI.subbot.llm.geminiAPI.a_use_tools,
                                                    b_model=self.coreAPI.subbot.llm.geminiAPI.b_model,
                                                    b_use_tools=self.coreAPI.subbot.llm.geminiAPI.b_use_tools,
                                                    v_model=self.coreAPI.subbot.llm.geminiAPI.v_model,
                                                    v_use_tools=self.coreAPI.subbot.llm.geminiAPI.v_use_tools,
                                                    x_model=self.coreAPI.subbot.llm.geminiAPI.x_model,
                                                    x_use_tools=self.coreAPI.subbot.llm.geminiAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.geminiAPI.chatBot(     chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                    history=history, function_modules=function_modules,
                                                    sysText=sysText, reqText=reqText, inpText=inpText2,
                                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'Gemini'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # freeai
        # 最後の砦処理！

        # claude
        if  ((res_text == '') or (res_text == '!')) \
        and (self.claude_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("claude, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[claude]'):
                engine_text = self.claudeAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name = 'claude'
                a_nick_name = self.claudeAPI.a_nick_name.lower()
                b_nick_name = self.claudeAPI.b_nick_name.lower()
                v_nick_name = self.claudeAPI.v_nick_name.lower()
                x_nick_name = self.claudeAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        reqText = reqText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        inpText = inpText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### Claude ###')

                    if (self.coreAPI is not None):
                        self.claudeAPI.set_models(  max_wait_sec=self.coreAPI.subbot.llm.claudeAPI.max_wait_sec,
                                                    a_model=self.coreAPI.subbot.llm.claudeAPI.a_model,
                                                    a_use_tools=self.coreAPI.subbot.llm.claudeAPI.a_use_tools,
                                                    b_model=self.coreAPI.subbot.llm.claudeAPI.b_model,
                                                    b_use_tools=self.coreAPI.subbot.llm.claudeAPI.b_use_tools,
                                                    v_model=self.coreAPI.subbot.llm.claudeAPI.v_model,
                                                    v_use_tools=self.coreAPI.subbot.llm.claudeAPI.v_use_tools,
                                                    x_model=self.coreAPI.subbot.llm.claudeAPI.x_model,
                                                    x_use_tools=self.coreAPI.subbot.llm.claudeAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.claudeAPI.chatBot(     chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                    history=history, function_modules=function_modules,
                                                    sysText=sysText, reqText=reqText, inpText=inpText2,
                                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'Claude'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # openrt
        if  ((res_text == '') or (res_text == '!')) \
        and (self.openrt_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("openrt, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[openrt]'):
                engine_text = self.openrtAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name = 'openrt'
                a_nick_name = self.openrtAPI.a_nick_name.lower()
                b_nick_name = self.openrtAPI.b_nick_name.lower()
                v_nick_name = self.openrtAPI.v_nick_name.lower()
                x_nick_name = self.openrtAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        reqText = reqText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        inpText = inpText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### OpenRouter ###')

                    if (self.coreAPI is not None):
                        self.openrtAPI.set_models(  max_wait_sec=self.coreAPI.subbot.llm.openrtAPI.max_wait_sec,
                                                    a_model=self.coreAPI.subbot.llm.openrtAPI.a_model,
                                                    a_use_tools=self.coreAPI.subbot.llm.openrtAPI.a_use_tools,
                                                    b_model=self.coreAPI.subbot.llm.openrtAPI.b_model,
                                                    b_use_tools=self.coreAPI.subbot.llm.openrtAPI.b_use_tools,
                                                    v_model=self.coreAPI.subbot.llm.openrtAPI.v_model,
                                                    v_use_tools=self.coreAPI.subbot.llm.openrtAPI.v_use_tools,
                                                    x_model=self.coreAPI.subbot.llm.openrtAPI.x_model,
                                                    x_use_tools=self.coreAPI.subbot.llm.openrtAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.openrtAPI.chatBot(     chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                    history=history, function_modules=function_modules,
                                                    sysText=sysText, reqText=reqText, inpText=inpText2,
                                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'OpenRouter'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # perplexity
        if  ((res_text == '') or (res_text == '!')) \
        and (self.perplexity_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("perplexity, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[perplexity]'):
                engine_text = self.perplexityAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name1 = 'perplexity'
                model_nick_name2 = 'pplx'
                a_nick_name = self.perplexityAPI.a_nick_name.lower()
                b_nick_name = self.perplexityAPI.b_nick_name.lower()
                v_nick_name = self.perplexityAPI.v_nick_name.lower()
                x_nick_name = self.perplexityAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        reqText = reqText[len(model_nick_name1)+1:].strip()
                    elif (req_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        reqText = reqText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        inpText = inpText[len(model_nick_name1)+1:].strip()
                    elif (inp_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        inpText = inpText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### Perplexity ###')

                    if (self.coreAPI is not None):
                        self.perplexityAPI.set_models(  max_wait_sec=self.coreAPI.subbot.llm.perplexityAPI.max_wait_sec,
                                                        a_model=self.coreAPI.subbot.llm.perplexityAPI.a_model,
                                                        a_use_tools=self.coreAPI.subbot.llm.perplexityAPI.a_use_tools,
                                                        b_model=self.coreAPI.subbot.llm.perplexityAPI.b_model,
                                                        b_use_tools=self.coreAPI.subbot.llm.perplexityAPI.b_use_tools,
                                                        v_model=self.coreAPI.subbot.llm.perplexityAPI.v_model,
                                                        v_use_tools=self.coreAPI.subbot.llm.perplexityAPI.v_use_tools,
                                                        x_model=self.coreAPI.subbot.llm.perplexityAPI.x_model,
                                                        x_use_tools=self.coreAPI.subbot.llm.perplexityAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.perplexityAPI.chatBot(     chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                        history=history, function_modules=function_modules,
                                                        sysText=sysText, reqText=reqText, inpText=inpText2,
                                                        filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )                    
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'Perplexity'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # grok
        if  ((res_text == '') or (res_text == '!')) \
        and (self.grok_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("grok, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[grok]'):
                engine_text = self.grokAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name = 'grok'
                a_nick_name = self.grokAPI.a_nick_name.lower()
                b_nick_name = self.grokAPI.b_nick_name.lower()
                v_nick_name = self.grokAPI.v_nick_name.lower()
                x_nick_name = self.grokAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        reqText = reqText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        inpText = inpText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### Grok ###')

                    if (self.coreAPI is not None):
                        self.grokAPI.set_models(max_wait_sec=self.coreAPI.subbot.llm.grokAPI.max_wait_sec,
                                                a_model=self.coreAPI.subbot.llm.grokAPI.a_model,
                                                a_use_tools=self.coreAPI.subbot.llm.grokAPI.a_use_tools,
                                                b_model=self.coreAPI.subbot.llm.grokAPI.b_model,
                                                b_use_tools=self.coreAPI.subbot.llm.grokAPI.b_use_tools,
                                                v_model=self.coreAPI.subbot.llm.grokAPI.v_model,
                                                v_use_tools=self.coreAPI.subbot.llm.grokAPI.v_use_tools,
                                                x_model=self.coreAPI.subbot.llm.grokAPI.x_model,
                                                x_use_tools=self.coreAPI.subbot.llm.grokAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.grokAPI.chatBot(   chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                history=history, function_modules=function_modules,
                                                sysText=sysText, reqText=reqText, inpText=inpText2,
                                                filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'Grok'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # groq
        if  ((res_text == '') or (res_text == '!')) \
        and (self.groq_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("groq, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[groq]'):
                engine_text = self.groqAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name = 'groq'
                a_nick_name = self.groqAPI.a_nick_name.lower()
                b_nick_name = self.groqAPI.b_nick_name.lower()
                v_nick_name = self.groqAPI.v_nick_name.lower()
                x_nick_name = self.groqAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        reqText = reqText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        inpText = inpText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### Groq ###')

                    if (self.coreAPI is not None):
                        self.groqAPI.set_models(max_wait_sec=self.coreAPI.subbot.llm.groqAPI.max_wait_sec,
                                                a_model=self.coreAPI.subbot.llm.groqAPI.a_model,
                                                a_use_tools=self.coreAPI.subbot.llm.groqAPI.a_use_tools,
                                                b_model=self.coreAPI.subbot.llm.groqAPI.b_model,
                                                b_use_tools=self.coreAPI.subbot.llm.groqAPI.b_use_tools,
                                                v_model=self.coreAPI.subbot.llm.groqAPI.v_model,
                                                v_use_tools=self.coreAPI.subbot.llm.groqAPI.v_use_tools,
                                                x_model=self.coreAPI.subbot.llm.groqAPI.x_model,
                                                x_use_tools=self.coreAPI.subbot.llm.groqAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.groqAPI.chatBot(   chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                history=history, function_modules=function_modules,
                                                sysText=sysText, reqText=reqText, inpText=inpText2,
                                                filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'Groq'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # ollama
        if  ((res_text == '') or (res_text == '!')) \
        and (self.ollama_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("ollama, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[ollama]'):
                engine_text = self.ollamaAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name1 = 'local'
                model_nick_name2 = 'ollama'
                a_nick_name = self.ollamaAPI.a_nick_name.lower()
                b_nick_name = self.ollamaAPI.b_nick_name.lower()
                v_nick_name = self.ollamaAPI.v_nick_name.lower()
                x_nick_name = self.ollamaAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (engine_text == '') and (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        reqText = reqText[len(model_nick_name1)+1:].strip()
                    elif (req_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        reqText = reqText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                if (engine_text == '') and (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        inpText = inpText[len(model_nick_name1)+1:].strip()
                    elif (inp_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        inpText = inpText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                try:
                    logger.info('### Ollama ###')

                    if (self.coreAPI is not None):
                        self.ollamaAPI.set_models(  max_wait_sec=self.coreAPI.subbot.llm.ollamaAPI.max_wait_sec,
                                                    a_model=self.coreAPI.subbot.llm.ollamaAPI.a_model,
                                                    a_use_tools=self.coreAPI.subbot.llm.ollamaAPI.a_use_tools,
                                                    b_model=self.coreAPI.subbot.llm.ollamaAPI.b_model,
                                                    b_use_tools=self.coreAPI.subbot.llm.ollamaAPI.b_use_tools,
                                                    v_model=self.coreAPI.subbot.llm.ollamaAPI.v_model,
                                                    v_use_tools=self.coreAPI.subbot.llm.ollamaAPI.v_use_tools,
                                                    x_model=self.coreAPI.subbot.llm.ollamaAPI.x_model,
                                                    x_use_tools=self.coreAPI.subbot.llm.ollamaAPI.x_use_tools, )

                    res_text, res_path, res_files, res_name, res_api, res_history = \
                        self.ollamaAPI.chatBot(     chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                    history=history, function_modules=function_modules,
                                                    sysText=sysText, reqText=reqText, inpText=inpText2,
                                                    filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                    if ((res_text != '') and (res_text != '!')):
                        res_engine = 'Ollama'
                        res_data = res_text
                except Exception as e:
                    logger.error(f"Error: {e}")

        # freeai
        if  ((res_text == '') or (res_text == '!')) \
        and (self.freeai_enable == True):

            # DEBUG
            if (engine == '') and (reqText.find(',') < 1) and (inpText.find(',') < 1):
                logger.debug("freeai, reqText and inpText not nick_name !!!")

            engine_text = ''
            if (engine == '[freeai]'):
                engine_text = self.freeaiAPI.b_nick_name.lower() + ',\n'
            else:
                model_nick_name1 = 'free'
                model_nick_name2 = 'freeai'
                a_nick_name = self.freeaiAPI.a_nick_name.lower()
                b_nick_name = self.freeaiAPI.b_nick_name.lower()
                v_nick_name = self.freeaiAPI.v_nick_name.lower()
                x_nick_name = self.freeaiAPI.x_nick_name.lower()
                if (engine != ''):
                    if   ((len(a_nick_name) != 0) and (engine.lower() == a_nick_name)):
                        engine_text = a_nick_name + ',\n'
                    elif ((len(b_nick_name) != 0) and (engine.lower() == b_nick_name)):
                        engine_text = b_nick_name + ',\n'
                    elif ((len(v_nick_name) != 0) and (engine.lower() == v_nick_name)):
                        engine_text = v_nick_name + ',\n'
                    elif ((len(x_nick_name) != 0) and (engine.lower() == x_nick_name)):
                        engine_text = x_nick_name + ',\n'
                if (reqText.find(',') >= 1):
                    req_nick_name = reqText[:reqText.find(',')].lower()
                    if   (req_nick_name == model_nick_name):
                        engine_text = model_nick_name + ',\n'
                        reqText = reqText[len(model_nick_name)+1:].strip()
                    elif (len(a_nick_name) != 0) and (req_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        reqText = reqText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (req_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        reqText = reqText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (req_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        reqText = reqText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (req_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        reqText = reqText[len(x_nick_name)+1:].strip()
                elif (inpText.find(',') >= 1):
                    inp_nick_name = inpText[:inpText.find(',')].lower()
                    if   (inp_nick_name == model_nick_name1):
                        engine_text = model_nick_name1 + ',\n'
                        inpText = inpText[len(model_nick_name1)+1:].strip()
                    elif (inp_nick_name == model_nick_name2):
                        engine_text = model_nick_name2 + ',\n'
                        inpText = inpText[len(model_nick_name2)+1:].strip()
                    elif (len(a_nick_name) != 0) and (inp_nick_name == a_nick_name):
                        engine_text = a_nick_name + ',\n'
                        inpText = inpText[len(a_nick_name)+1:].strip()
                    elif (len(b_nick_name) != 0) and (inp_nick_name == b_nick_name):
                        engine_text = b_nick_name + ',\n'
                        inpText = inpText[len(b_nick_name)+1:].strip()
                    elif (len(v_nick_name) != 0) and (inp_nick_name == v_nick_name):
                        engine_text = v_nick_name + ',\n'
                        inpText = inpText[len(v_nick_name)+1:].strip()
                    elif (len(x_nick_name) != 0) and (inp_nick_name == x_nick_name):
                        engine_text = x_nick_name + ',\n'
                        inpText = inpText[len(x_nick_name)+1:].strip()

            #if (engine_text == ''):
            #    #engine_text = self.freeaiAPI.b_nick_name.lower() + ',\n'
            #    if (req_mode == 'session'):
            #        engine_text = a_nick_name + ',\n'
            #    else:
            #        engine_text = b_nick_name + ',\n'

            if (engine_text != ''):
                inpText2 = engine_text + inpText
                engine_text = ''

                n_max = 1
                if (engine == '[freeai]'):
                    n_max = 2
                n = 0
                while ((res_text == '') or (res_text == '!')) and (n < n_max) and (self.bot_cancel_request != True):
                    n += 1

                    try:
                        if (n == 1):
                            logger.info('### FreeAI ###')

                            if (self.coreAPI is not None):
                                self.freeaiAPI.set_models(  max_wait_sec=self.coreAPI.subbot.llm.freeaiAPI.max_wait_sec,
                                                            a_model=self.coreAPI.subbot.llm.freeaiAPI.a_model,
                                                            a_use_tools=self.coreAPI.subbot.llm.freeaiAPI.a_use_tools,
                                                            b_model=self.coreAPI.subbot.llm.freeaiAPI.b_model,
                                                            b_use_tools=self.coreAPI.subbot.llm.freeaiAPI.b_use_tools,
                                                            v_model=self.coreAPI.subbot.llm.freeaiAPI.v_model,
                                                            v_use_tools=self.coreAPI.subbot.llm.freeaiAPI.v_use_tools,
                                                            x_model=self.coreAPI.subbot.llm.freeaiAPI.x_model,
                                                            x_use_tools=self.coreAPI.subbot.llm.freeaiAPI.x_use_tools, )

                        else:
                            logger.warning(f"freeai retry = { n }/{ n_max },")

                        res_text, res_path, res_files, res_name, res_api, res_history = \
                                self.freeaiAPI.chatBot(     chat_class=chat_class, model_select=model_select, session_id=session_id, 
                                                            history=history, function_modules=function_modules,
                                                            sysText=sysText, reqText=reqText, inpText=inpText2,
                                                            filePath=filePath, jsonSchema=jsonSchema, inpLang=inpLang, outLang=outLang, )
                        if ((res_text != '') and (res_text != '!')):
                            res_engine = 'FreeAI'
                            res_data = res_text
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        if (n >= n_max):
                            break

                        # n*20 + 40～60秒待機
                        wait_sec = n*20 + random.uniform(40, 60)
                        logger.warning(f"freeai retry waitting { float(wait_sec) :.1f}s ...")
                        chkTime = time.time()
                        while ((time.time() - chkTime) < wait_sec):
                            time.sleep(0.25)

                            # キャンセル確認
                            if (self.bot_cancel_request == True):
                                break

        if (res_text == '') or (res_text == '!'):
            res_text = '!'
            res_data = '!'
        else:
            data_hit = False
            wrk_data = '\n' + res_data
            think_data = ''

            # <think>以外の結果抽出
            st = wrk_data.find('\n<think>')
            if (st >= 0):
                en = wrk_data.find('\n</think>', st+8)
                if (en > st):
                    think_data = wrk_data[st+8:en]
                    res_data = wrk_data[1:st] + wrk_data[en+9:]
                    wrk_data = wrk_data[:st]  + wrk_data[en+9:]
                    if (wrk_data[:1] != '\n'):
                        wrk_data = '\n' + wrk_data

            # res_data中の検索、think中の検索
            for l in [1, 2]:

                # ２回転目
                if (l == 2):
                    if (data_hit == True):
                        break
                    if (think_data == ''):
                        break
                    else:
                        wrk_data = '\n' + think_data

                # ３連文字による結果抽出
                if (data_hit == False):
                    st = wrk_data.find('\n```')
                    while (st >= 0):
                        en = wrk_data.find('\n```', st+8)
                        if (en > st):
                            res_data = wrk_data[st+1:en+4]
                            data_hit = True
                            wrk_data = wrk_data[en+4:]
                            if (wrk_data[:1] != '\n'):
                                wrk_data = '\n' + wrk_data
                            st = wrk_data.find('\n```')
                        else:
                            st = -1

                # <html>による結果抽出
                if (data_hit == False):
                    st = wrk_data.find('\n<html')
                    while (st >= 0):
                        en = wrk_data.find('\n</html>')
                        if (en > st):
                            tmp_data  = "```html\n"
                            tmp_data += "<!DOCTYPE html>\n"
                            tmp_data += wrk_data[st+1:en+8] + "\n"
                            tmp_data += "```\n"
                            res_data = tmp_data
                            data_hit = True
                            wrk_data = wrk_data[en+8:]
                            if (wrk_data[:1] != '\n'):
                                wrk_data = '\n' + wrk_data
                            st = wrk_data.find('\n<html')
                        else:
                            st = -1

            # 以外
            if (data_hit == False):
                res_data = self.text_replace(text=res_data, )
                if (res_data.strip() == ''):
                    res_data = '!'

        if (res_path is None):
            res_path = ''

        # ソースは、ファイル出力も行う
        if (res_text != '') and (res_text != '!'):
            if (res_path == '') and (len(res_files) == 0):
                if (res_data[:3] == res_data.rstrip()[-3:]):
                    first_n = res_data.find('\n')
                    if (first_n >= 1):

                        # ファイル名
                        file_name = res_data[3:first_n].strip()
                        if   (file_name.lower() == ''):
                            file_name = 'source.txt'
                        elif (file_name.lower() == 'html'):
                            file_name = 'index.html'
                        elif (file_name.lower() == 'python'):
                            file_name = 'main.py'

                        # データ
                        file_data = res_data.rstrip()[first_n+1:-3]

                        # 書き込み
                        try:
                            w = codecs.open(qPath_output + file_name, 'w', 'utf-8')
                            w.write(file_data)
                            w.close()
                            w = None
                            res_path = qPath_output + file_name
                            res_files.append(res_path)
                        except:
                            pass

        # DEBUG
        if res_text not in ['', '!']:
            logger.debug("subbot.chatBot:res_text")
            logger.debug(res_text)

        return res_text, res_data, res_path, res_files, res_engine, res_name, res_api, res_history


if __name__ == '__main__':

    llm = llm_class(runMode='debug')

    input_text = 'おはよう'
    res_text, _, _, _, _, _, _, _ = llm.chatBot(req_mode='chat', engine='freeai',
                                                chat_class='auto', model_select='auto', session_id='debug', 
                                                history=[], function_modules={},
                                                sysText='', reqText='', inpText=input_text,
                                                filePath=[], jsonSchema=None, inpLang='ja', outLang='ja')

    print(res_text)
