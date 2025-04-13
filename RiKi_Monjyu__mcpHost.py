#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名定義
MODULE_NAME = 'mcpHost'

# ロガーの設定
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)

import asyncio
import datetime
import json
import os
import time
import threading
import queue
from typing import Any, Dict, List, Optional

# インターフェースのパス設定
qPath_temp   = 'temp/'
qPath_log    = 'temp/_log/'

# MCPクライアントのインポート
import _v7__mcp_host
mcp_client = _v7__mcp_host.mcp_host_class()

# MCP管理クラス
class _mcpHost_class:

    # 初期化
    def __init__(self,  runMode: str = 'debug', qLog_fn: str = '', 
                        main=None, conf=None, data=None, addin=None, botFunc=None):
        logger.debug('初期化開始')
        
        self.runMode = runMode
        
        # ログファイル名の生成
        if qLog_fn == '':
            nowTime = datetime.datetime.now()
            qLog_fn = qPath_log + nowTime.strftime('%Y%m%d.%H%M%S') + '.' + os.path.basename(__file__) + '.log'

        # 設定パラメータの保存
        self.main       = main
        self.conf       = conf
        self.data       = data
        self.addin      = addin
        self.botFunc    = botFunc

        # キュー設定
        self.req_s = queue.Queue()
        self.res_r = queue.Queue()
        
        logger.debug('初期化完了')

    # MCP機能モジュール取得
    def get_mcp_modules(self):
        logger.debug('MCP機能モジュール取得開始')
        
        functions = {}
        for name, value in mcp_client.tools_info.items():
            try:
                function = {
                        "name": name,
                        "description": value.get('description'),
                        "parameters": value.get('inputSchema')
                        }
                server = mcp_client.servers_info[value.get('server')]
                functions[name] = { 'script': 'mcp',
                                    'module': server.get('name'),
                                    'onoff': 'on',
                                    'class': None,
                                    'func_name': name,
                                    'func_ver': '1.0.0',
                                    'func_auth': 'ok',
                                    'function': function,
                                    'func_reset': None,
                                    'func_proc': self.execute}
            except Exception as e:
                logger.error(f'MCP機能モジュール取得エラー: {e}')
            
        logger.debug(f'MCP機能モジュール取得完了: {len(functions)}件')
        return functions

    # MCPツール実行関数
    def execute(self, tool_name: str , request_json: Optional[str] = None):
        logger.info(f'MCPツール実行: {tool_name}')
        
        # 残っているレスポンスを消化
        while not self.res_r.empty():
            res = self.res_r.get()
            logger.debug(f'残存レスポンス: {res}')

        # 実行リクエスト送信
        self.req_s.put({'cmd': 'execute', 'tool_name': tool_name, 'request_json':request_json})

        # 結果待ち（タイムアウト120秒）
        result = None
        chkTime = time.time()
        while (time.time() - chkTime) < 120:
            if not self.res_r.empty():
                result = self.res_r.get()
                break

        if result:
            logger.debug(f'実行結果: {result[:100]}...')
            try:
                dummy = json.loads(result)
                return result
            except:
                logger.warning('JSON解析失敗、メッセージとして返却')
                res_dic = {'message': result}
                return json.dumps(res_dic, ensure_ascii=False)
        else:
            logger.error('実行タイムアウト')
            result = {'error': 'time out!'}
            return json.dumps(result, ensure_ascii=False)

    # MCP実行
    def run(self):
        logger.info('MCP起動')

        # MCPプロセス実行関数
        def mcp_proc(req_s, res_r):
            asyncio.run(main(req_s, res_r))

        # スレッド起動
        mcp_thread = threading.Thread(target=mcp_proc, args=(self.req_s, self.res_r))
        mcp_thread.start()

        # 初期化待機
        time.sleep(5)
        
        # 開始コマンド送信
        self.req_s.put({'cmd': 'start'})
        logger.info('MCP開始コマンド送信')
        time.sleep(5)

# メインループ処理
async def main(req_q, res_q):
    logger.debug('メインループ開始')
    
    while True:
        try:
            if req_q.empty():
                await asyncio.sleep(0.25)
            else:
                req_dic = req_q.get()
                req_cmd = req_dic.get('cmd')
                logger.debug(f'コマンド受信: {req_cmd}')

                if (req_cmd == 'start'):
                    config_path = 'claude_desktop_config.json'
                    reset = True
                    logger.info(f'MCP起動: {config_path}')
                    await mcp_client.start_from_config(config_path=config_path, reset=reset)
                    await asyncio.sleep(2)

                elif (req_cmd == 'terminate'):
                    logger.info('MCP終了処理')
                    result = await mcp_client.terminate()
                    await asyncio.sleep(2)

                elif (req_cmd == 'execute'):
                    tool_name = req_dic.get('tool_name')
                    request_json = req_dic.get('request_json')
                    logger.debug(f'ツール実行: {tool_name}')
                    result = await mcp_client.execute(tool_name=tool_name, request_json=request_json)
                    res_q.put(result)

                else:
                    logger.error(f'予期しないコマンド: {req_dic}')

        except Exception as e:
            logger.error(f'メインループエラー: {e}')


# メイン処理
if __name__ == '__main__':
    print()
    logger.info('プログラム開始')
    
    # インスタンス生成
    runMode = 'debug'
    mcpHost = _mcpHost_class(runMode=runMode, qLog_fn='')

    # MCP実行
    mcpHost.run()

    time.sleep(10)

    # テスト用コード

    logger.info('MCPモジュール一覧取得')
    mcp_modules = mcpHost.get_mcp_modules()
    for mcp_module in mcp_modules:
        print(mcp_module)

    logger.info('MCPツール実行')
    tool_name = "filesystem-list_directory"
    request = {"path": "C:/_共有/_MCP/_sandbox"}
    request_json = json.dumps(request, ensure_ascii=False)
    json_str = mcpHost.execute(tool_name=tool_name, request_json=request_json)

    parsed = json.loads(json_str)
    formatted_json = json.dumps(parsed, indent=4, ensure_ascii=False)
    print(formatted_json)

    # テスト実行待機
    time.sleep(120)
