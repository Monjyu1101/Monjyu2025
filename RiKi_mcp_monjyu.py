#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'mcp_monjyu'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)


import argparse
import asyncio
import json
import sys
import threading
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import time
import requests


# 定数の定義
CORE_PORT = '8000'
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30



class _monjyu_class:
    def __init__(self, runMode='chat' ):
        self.runMode   = runMode

        # ポート設定等
        self.local_endpoint0 = f'http://localhost:{ int(CORE_PORT) + 0 }'

    def get_ready(self):
        # ファイル添付
        try:
            response = requests.get(
                self.local_endpoint0 + '/get_ready_count',
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                results = response.json()
                isReady = results.get('ready_count',0)
                isBusy = results.get('busy_count',0)
                if isReady > 0:
                    return True
                else:
                    return False
            else:
                logger.error(f"Monjyu_Request : Error response (/get_input_list) : {response.status_code}")
        except Exception as e:
            logger.error(f"Monjyu_Request : Error communicating (/get_input_list) : {e}")
        return False

    def request(self, req_mode='chat', user_id='admin', sysText='', reqText='', inpText='', ):
        res_port = ''

        # ファイル添付
        file_names = []
        try:
            response = requests.get(
                self.local_endpoint0 + '/get_input_list',
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                results = response.json()
                for f in results['files']:
                    #fx = f.split(' ')
                    #if (fx[3] == 'checked'):
                    #    file_names.append(fx[0])
                    file_name = f.get('file_name','')
                    checked   = f.get('checked','')
                    if checked == 'yes':
                        file_names.append(file_name)
            else:
                logger.error(f"Monjyu_Request : Error response (/get_input_list) : {response.status_code}")
        except Exception as e:
            logger.error(f"Monjyu_Request : Error communicating (/get_input_list) : {e}")

        # AI要求送信
        try:
            res_port = ''
            if (req_mode in ['clip', 'voice']):
                res_port = CORE_PORT
            response = requests.post(
                self.local_endpoint0 + '/post_req',
                json={'user_id': user_id, 'from_port': CORE_PORT, 'to_port': res_port,
                    'req_mode': req_mode,
                    'system_text': sysText, 'request_text': reqText, 'input_text': inpText,
                    'file_names': file_names, 'result_savepath': '', 'result_schema': '', },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code == 200:
                if (res_port == ''):
                    res_port = str(response.json()['port'])
            else:
                logger.error(f"Monjyu_Request : Error response (/post_req) : {response.status_code}")
        except Exception as e:
            logger.error(f"Monjyu_Request : Error communicating (/post_req) : {e}")

        # AI結果受信
        res_text = ''
        if res_port != '':
            try:

                # AIメンバー応答待機
                timeout = time.time() + 120
                while time.time() < timeout:

                    response = requests.get(
                        self.local_endpoint0 + '/get_sessions_port?user_id=' + user_id + '&from_port=' + CORE_PORT,
                        timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
                    )
                    if response.status_code == 200:
                        results = response.json()
                        key_val = f"{ user_id }:{ CORE_PORT }:{ res_port }"
                        if key_val in results:
                            if results[key_val]["out_time"] is not None:
                                res_text = str(results[key_val]["out_data"])
                                break
                        else:
                            time.sleep(1.00)
                    else:
                        logger.error(f"Monjyu_Request : Error response (/get_sessions_port) : {response.status_code} - {response.text}")

            except Exception as e:
                logger.error(f"'Monjyu_Request : Error communicating (/get_sessions_port) : {e}")

        return res_text


class mcp_server_class:
    """Monjyuを実行するMCPサーバー"""
    
    def __init__(self, name: str = None, transport: str = 'stdio', port: str = None):
        """サーバーインスタンスの初期化"""
        self.name = name if name is not None else MODULE_NAME
        self.transport = transport
        self.port = port if port is not None else '5000'

        self.monjyu = _monjyu_class()

        # ログ出力
        logger.info(f"サーバー初期化: name={self.name}, transport={transport}, port={self.port}")
        
        # MCPインスタンス作成
        if transport == 'sse':
            self.mcp = FastMCP(name, host='127.0.0.1', port=int(self.port))
            logger.info(f"SSEモードでMCPサーバーを初期化: port={self.port}")
        else:
            self.mcp = FastMCP(name)
            logger.info("stdioモードでMCPサーバーを初期化")
            
        self.abort_flag = False
        self.error_flag = False
        self.mcp_thread = None
        
        logger.info("MCPサーバーを初期化します...")
        self._setup_tools()
        logger.info("MCPサーバーの初期化が完了しました")
      
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

        @self.mcp.tool()
        async def request(
                request_text: str = Field(description="外部AIMonjyuへ依頼するテキスト")
            ) -> str:
            logger.info("Monjyu MCP サーバーが呼び出されました")

            isReady = self.monjyu.get_ready()
            if (isReady == False):
                logger.error(f"サービス停止中です")
                return self._create_response({"error": "サービス停止中です"})

            req_mode = "chat"
            user_id = "admin"
            sysText = "あなたは美しい日本語を話す賢いアシスタントです。"
            reqText = request_text
            inpText = ""
            resText = self.monjyu.request(req_mode=req_mode, user_id=user_id, sysText=sysText, reqText=reqText, inpText=inpText,)
            return self._create_response({"result": "ok", "result_text": resText})

        logger.info("ツールとリソースのセットアップが完了")

    async def run(self) -> None:
        """サーバープロセスを実行"""
        try:
            # 実行用関数
            def run_proc():
                if self.transport == 'sse':
                    logger.info(f"MCPサーバーを実行中: transport={self.transport}, port={self.port}")
                else:
                    logger.info(f"MCPサーバーを実行中: transport={self.transport}")
                try:
                    self.mcp.run(transport=self.transport)
                except Exception as e:
                    logger.error(f"MCPサーバーエラー: {e}")
                    self.error_flag = True
                    
            # スレッド実行
            self.mcp_thread = threading.Thread(target=run_proc, daemon=True)
            self.mcp_thread.start()
            logger.info(f"MCPサーバースレッドを開始しました: thread_id={self.mcp_thread.ident}")
            
            # 終了監視
            while (not self.abort_flag) and (not self.error_flag):
                await asyncio.sleep(0.5)
            
            if self.abort_flag:
                logger.info("中断フラグによりMCPサーバーを終了します")
            elif self.error_flag:
                logger.info("エラーフラグによりMCPサーバーを終了します")
            
            sys.exit(0)
        except Exception as e:
            logger.error(f"MCPサーバー実行中にエラーが発生しました: {e}")
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
        logger.info("MCPサーバーを起動します...")
        mcp_task = asyncio.create_task(mcp_server.run())
        logger.info("MCPサーバーを起動しました")
        await mcp_task
    except Exception as e:
        logger.critical(f"MCPサーバーを停止しました: {e}")


if __name__ == "__main__":
    # 引数解析
    parser = argparse.ArgumentParser(description='MCP サーバー')
    parser.add_argument('--port', type=str, help='使用するポート番号 (SSEモード)')
    args = parser.parse_args()
    logger.info(f"コマンドライン引数: {args}")

    # メイン実行
    logger.info("MCPサーバーの起動プロセスを開始")
    try:
        asyncio.run(main(**vars(args)))
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
