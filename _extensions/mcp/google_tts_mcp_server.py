"""
Google TTS MCP サーバー
Model Context Protocol (MCP) を利用したGoogle音声合成サーバーです。
テキストを受け取り、Google TTSで音声合成して再生します。
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'google_tts_mcp_server'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)


import argparse
import asyncio
import json
import sys
import os
import time
import threading
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from gtts import gTTS
from playsound3 import playsound


# 作業ディレクトリ
qPath_work = 'temp/_work/'
qPath_play = 'temp/s6_7play/'


class sub_class:
    """音声再生用のサブクラス"""

    def __init__(self, runMode='assistant'):
        self.runMode = runMode

    def init(self):
        return True

    def play(self, outFile='temp/_work/sound.mp3'):
        """音声ファイルを再生する"""
        if (outFile is None) or (outFile == ''):
            return False
        if (not os.path.isfile(outFile)):
            return False
        try:
            # 再生
            playsound(sound=outFile, block=True)
            return True
        except Exception as e:
            print(e)
        return False


class tts_class:
    """音声合成用のクラス"""
    
    def __init__(self, runMode='assistant'):
        self.runMode = runMode

        # ディレクトリ作成
        if (not os.path.exists(qPath_work)):
            os.makedirs(qPath_work)
        if (not os.path.exists(qPath_play)):
            os.makedirs(qPath_play)

    def google_tts(self, outText='おはよう', outLang='auto', outSpeaker='google', outGender='female', outFile='temp/_work/tts.mp3'):
        """Google TTSを使用して音声合成を行う"""
        outFile = outFile[:-4] + '.mp3'

        # 引数チェック
        text = outText.strip()
        if (text == '') or (text == '!'):
            return False, None

        gender = outGender.lower()

        lang = ''
        if (outLang == 'auto') or (outLang == 'ja') or (outLang == 'ja-JP'):
            lang = 'ja'
        elif (outLang == 'en') or (outLang == 'en-US'):
            lang = 'en'
        elif (outLang == 'ar-AR'):
            lang = 'ar'
        elif (outLang == 'es-ES'):
            lang = 'es'
        elif (outLang == 'de-DE'):
            lang = 'de'
        elif (outLang == 'fr-FR'):
            lang = 'fr'
        elif (outLang == 'it-IT'):
            lang = 'it'
        elif (outLang == 'pt-BR'):
            lang = 'pt'
        elif (outLang == 'ru-RU'):
            lang = 'ru'
        elif (outLang == 'tr-TR'):
            lang = 'tr'
        elif (outLang == 'uk-UK'):
            lang = 'uk'
        elif (outLang == 'zh') or (outLang == 'zh-CN'):
            lang = 'zh'
        elif (outLang == 'kr-KR'):
            lang = 'kr'
        else:
            lang = outLang

        # 音声合成
        try:
            if (outLang == 'auto'):
                tts = gTTS(text=text, lang='ja', slow=False)
            else:
                tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(outFile)
        except Exception as e:
            logger.error(f"音声合成エラー: {e}")
            return False, None

        # 結果確認
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 4096):
                os.remove(outFile)
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 44):
                os.remove(outFile)
            else:
                return outFile, 'google'

        return False, None


class google_tts_mcp_server_class:
    """Google TTS機能を提供するMCPサーバー"""
    
    def __init__(self, name: str = None, transport: str = 'stdio', port: str = None):
        """サーバーインスタンスの初期化"""
        self.name = name if name is not None else MODULE_NAME
        self.transport = transport
        self.port = port
        
        # ログ出力
        logger.info(f"サーバー初期化: name={self.name}, transport={transport}, port={self.port}")
        
        # MCPインスタンス作成
        if transport == 'sse':
            self.mcp = FastMCP(name, host='127.0.0.1', port=int(self.port))
            logger.info(f"SSEモードでサーバーを初期化: port={self.port}")
        else:
            self.mcp = FastMCP(name)
            logger.info("stdioモードでサーバーを初期化")
            
        self.abort_flag = False
        self.error_flag = False
        self.mcp_thread = None
        
        # TTS関連の初期化
        self.tts_proc = tts_class()
        self.sub_proc = sub_class()
        self.tts_seq = 0
        self.last_text = ''
        self.last_speaker = ''
        
        logger.info("サーバーを初期化します...")
        self._setup_tools()
        logger.info("サーバーの初期化が完了しました")
      
    def _create_response(self, result: Dict[str, Any] = None) -> str:
        """JSON形式のレスポンスを作成"""
        try:
            logger.info(f"レスポンスを作成: {result}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"レスポンス作成中にエラー発生: {e}")
            return json.dumps({'error': str(e)}, ensure_ascii=False)

    def _setup_tools(self) -> None:
        """サーバーのツールとリソースを登録"""
        logger.info("ツールとリソースのセットアップを開始")

        # TextToSpeechツール
        @self.mcp.tool()
        async def TextToSpeech(
                speech_text: str = Field(description="合成するテキスト"),
                language: str = Field(description="テキストの言語 (auto, ja, en, 等)", default="auto"),
                gender: str = Field(description="性別 (male, female)", default="female")
            ) -> str:
            """テキストを音声に変換して再生"""
            logger.info(f"TextToSpeechツールが呼び出されました: {speech_text}, 言語: {language}, 性別: {gender}")
            
            # テキスト無しはエラー
            if not speech_text or speech_text.strip() == '':
                return self._create_response({
                    "result": "ng",
                    "error_text": "音声合成エラー。テキストがありません。"
                })
            
            # 連続発声はキャンセル
            speaker = 'google'
            if (speech_text == self.last_text) and (speaker == self.last_speaker):
                return self._create_response({
                    "result": "ng",
                    "error_text": "さきほど再生した内容と同じ内容です。"
                })
            
            # 出力ファイル
            self.tts_seq += 1
            if (self.tts_seq > 9999):
                self.tts_seq = 1
            seq4 = '{:04}'.format(self.tts_seq)
            outFile = qPath_work + 'tts_' + seq4 + '.mp3'
            
            if (os.path.isfile(outFile)):
                try:
                    os.remove(outFile)
                except Exception as e:
                    logger.error(f"ファイル削除エラー: {e}")
            
            # 音声合成
            tts_ok = False
            res, api = self.tts_proc.google_tts(
                outText=speech_text, 
                outLang=language, 
                outGender=gender, 
                outFile=outFile
            )
            
            if res:
                tts_ok = True
                outFile = res
                self.last_text = speech_text
                self.last_speaker = speaker
                logger.info(f"音声合成成功: {outFile} ({api})")
            
            # 音声合成エラー
            if not tts_ok:
                return self._create_response({
                    "result": "ng",
                    "error_text": "音声合成でエラーが発生しました。"
                })
            
            # 音声再生
            play_ok = self.sub_proc.play(outFile=outFile)
            
            # 結果を返す
            if play_ok:
                return self._create_response({
                    "result": "ok",
                    "result_text": "音声合成および再生を実施しました。",
                    "output_path": outFile
                })
            else:
                return self._create_response({
                    "result": "ng",
                    "error_text": "音声ファイルの再生でエラーが発生しました",
                    "output_path": outFile
                })

        # ステータスリソース
        @self.mcp.resource("server://get_status")
        def get_status() -> str:
            """サーバーの状態情報を提供"""
            logger.info("サーバーステータスが要求されました")
            return self._create_response({
                "status": "running",
                "name": self.name,
                "resources": {"tts_engine": "Google TTS"},
                "timestamp": asyncio.get_event_loop().time()
            })

        logger.info("ツールとリソースのセットアップが完了")

    async def run(self) -> None:
        """サーバープロセスを実行"""
        try:
            # 実行用関数
            def run_proc():
                if self.transport == 'sse':
                    logger.info(f"サーバーを実行中: transport={self.transport}, port={self.port}")
                else:
                    logger.info(f"サーバーを実行中: transport={self.transport}")
                try:
                    self.mcp.run(transport=self.transport)
                except Exception as e:
                    logger.error(f"サーバーエラー: {e}")
                    self.error_flag = True
                    
            # スレッド実行
            self.mcp_thread = threading.Thread(target=run_proc, daemon=True)
            self.mcp_thread.start()
            logger.info(f"サーバースレッドを開始しました: thread_id={self.mcp_thread.ident}")
            
            # 終了監視
            while (not self.abort_flag) and (not self.error_flag):
                await asyncio.sleep(0.5)
            
            if self.abort_flag:
                logger.info("中断フラグによりサーバーを終了します")
            elif self.error_flag:
                logger.info("エラーフラグによりサーバーを終了します")
            
            sys.exit(0)
        except Exception as e:
            logger.error(f"サーバー実行中にエラーが発生しました: {e}")
            raise


async def main(**args) -> None:
    """サーバーを初期化して実行"""
    # ポート取得
    port = args.get('port')
    logger.info(f"メイン関数を開始: args={args}")
    
    try:
        # サーバー作成
        if port:
            logger.info(f"SSE transportでサーバーを構成: port={port}")
            tts_server = google_tts_mcp_server_class(transport='sse', port=port)
        else:
            logger.info("標準入出力transportでサーバーを構成: stdio")
            tts_server = google_tts_mcp_server_class(transport='stdio')
        
        # サーバー実行
        logger.info("サーバーを起動します...")
        mcp_task = asyncio.create_task(tts_server.run())
        logger.info("サーバーを起動しました")
        await mcp_task
    except Exception as e:
        logger.critical(f"サーバーを停止しました: {e}")


if __name__ == "__main__":
    # 引数解析
    parser = argparse.ArgumentParser(description='Google TTS MCP サーバー')
    parser.add_argument('--port', type=str, help='使用するポート番号 (SSEモード)')
    args = parser.parse_args()
    logger.info(f"コマンドライン引数: {args}")

    # メイン実行
    logger.info("サーバーの起動プロセスを開始")
    try:
        asyncio.run(main(**vars(args)))
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)