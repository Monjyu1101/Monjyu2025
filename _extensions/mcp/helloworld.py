"""
ハローワールド MCP サーバー
Model Context Protocol (MCP) を利用した簡単なサーバーです。
基本的な挨拶メッセージとエコー機能を提供します。
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
MODULE_NAME = 'helloworld'

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
import threading
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field


class mcp_server_class:
    """メッセージ機能を提供するMCPサーバー"""
    
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
        self.message_header = 'Hello World!'
        self.mcp_thread = None
        
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

        # HelloWorldツール
        @self.mcp.tool()
        async def HelloWorld() -> str:
            """現在のメッセージヘッダーを返す"""
            logger.info("HelloWorldツールが呼び出されました")
            return self._create_response({"result": "ok", "message": self.message_header})

        # Echoツール
        @self.mcp.tool()
        async def Echo(
                message_text: str = Field(description="エコーするメッセージテキスト")
            ) -> str:
            """メッセージをヘッダー付きでエコー"""
            logger.info(f"Echoツールが呼び出されました: {message_text}")
            return self._create_response({"result": "ok", "message": f"{self.message_header}, {message_text}"})
        
        # ヘッダー設定ツール
        @self.mcp.tool()
        async def SetMessageHeader(
                header_text: str = Field(description="設定するヘッダーテキスト")
            ) -> str:
            """メッセージヘッダーを変更"""
            logger.info(f"メッセージヘッダーを変更: '{self.message_header}' -> '{header_text}'")
            self.message_header = header_text
            return self._create_response({"result": "ok", "message_header": self.message_header})

        # ステータスリソース
        @self.mcp.resource("server://get_status")
        def get_status() -> str:
            """サーバーの状態情報を提供"""
            logger.info("サーバーステータスが要求されました")
            return self._create_response({
                "status": "running",
                "name": self.name,
                "resources": {"message_header": self.message_header},
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
            mcp_server = mcp_server_class(transport='sse', port=port)
        else:
            logger.info("標準入出力transportでサーバーを構成: stdio")
            mcp_server = mcp_server_class(transport='stdio')
        
        # サーバー実行
        logger.info("サーバーを起動します...")
        mcp_task = asyncio.create_task(mcp_server.run())
        logger.info("サーバーを起動しました")
        await mcp_task
    except Exception as e:
        logger.critical(f"サーバーを停止しました: {e}")


if __name__ == "__main__":
    # 引数解析
    parser = argparse.ArgumentParser(description='MCP サーバー')
    parser.add_argument('--port', type=str, help='使用するポート番号 (SSEモード)')
    args = parser.parse_args()
    logger.info(f"コマンドライン引数: {args}")

    # メイン実行
    logger.info("サーバーの起動プロセスを開始")
    try:
        asyncio.run(main(**vars(args)))
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
