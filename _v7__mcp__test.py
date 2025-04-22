"""
MCP テスト
MCPクライアントを使用したサーバー起動とコマンド実行のテストスクリプト
"""
import argparse
import asyncio
import json
import sys
import _v7__mcp_host
import logging

# モジュール名定義
MODULE_NAME = 'mcp_test'

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-16s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(MODULE_NAME)

# MCPホストのインスタンス化
mcp_host = _v7__mcp_host.mcp_host_class()


async def main():
    """異なる起動方法でMCPサーバーの動作をテストします"""
    logger.info("MCPホストを起動します")

    # モジュール起動テスト（無効状態）
    if True:
        print()
        logger.info("serverをモジュール起動します")
        module_path = './_v7__mcp_server.py'
        parms = ['--port', '5001']
        env = {}
        
        # モジュールとして起動
        start_success = await mcp_host.start_module(module_path, parms, env)
        if start_success:
            logger.info("モジュールとしてサーバーを起動しました")
        else:
            logger.error("モジュールとしてサーバーを起動できませんでした")
            return

        # 初期化待機
        logger.info("5秒間待機します...")
        await asyncio.sleep(5)
        
        # HelloWorldツールのテスト
        result = await mcp_host.execute("_v7__mcp_server-HelloWorld")
        if result:
            logger.info(f"HelloWorld実行結果: {result}")
            print(f'----------\n{result}\n----------')
        
        # 操作間の待機
        logger.info("5秒間待機します...")
        await asyncio.sleep(5)

        # サーバー停止
        logger.info("全てのMCPサーバーの停止処理を開始します")
        await mcp_host.terminate()

        # 終了待機
        logger.info("10秒間待機します...")
        await asyncio.sleep(10)

    # スクリプト起動テスト
    if True:
        print()
        logger.info("serverをスクリプト起動します")
        module_path = './_v7__mcp_server.py'
        parms = []
        env = {}
        
        # スクリプトとして起動
        start_success = await mcp_host.start_script(module_path, parms, env)
        logger.info(f"スクリプト起動結果: {start_success}")

        # 初期化待機
        logger.info("5秒間待機します...")
        await asyncio.sleep(5)

        # Echoツールのテスト
        request = {"message_text": "こんにちは世界"}
        request_json = json.dumps(request, ensure_ascii=False)
        result = await mcp_host.execute("_v7__mcp_server-Echo", request_json=request_json)
        if result:
            logger.info(f"Echo実行結果: {result}")
            print(f'----------\n{result}\n----------')

        # サーバー停止
        logger.info("全てのMCPサーバーの停止処理を開始します")
        await mcp_host.terminate()

        # 終了待機
        logger.info("10秒間待機します...")
        await asyncio.sleep(10)

    # 設定ファイルからの起動テスト
    if True:
        print()
        logger.info("config.jsonで起動します")
        config_path = '_config/claude_desktop_config.json'
        
        # 設定ファイルから起動
        start_success = await mcp_host.start_from_config(config_path)
        logger.info(f"JSON設定ファイルからの起動結果: {start_success}")

        # 初期化待機
        logger.info("5秒間待機します...")
        await asyncio.sleep(5)

        # ファイルシステムツールのテスト
        request = {"path": "C:/_共有/_sandbox"}
        request_json = json.dumps(request, ensure_ascii=False)
        result = await mcp_host.execute("filesystem-list_directory", request_json=request_json)
        if result:
            logger.info(f"list_directory実行結果の長さ: {len(result) if result else 0}")
            print(f'----------\n{result}\n----------')

        # サーバー停止
        logger.info("全てのMCPサーバーの停止処理を開始します")
        await mcp_host.terminate()

        # 終了待機
        logger.info("10秒間待機します...")
        await asyncio.sleep(10)

    logger.info("MCPクライアントを正常に終了します")


if __name__ == "__main__":
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='MCP クライアントランチャー')
    args = parser.parse_args()
    logger.info("コマンドライン引数を解析しました")

    # メイン処理の実行
    logger.info("MCPクライアントの起動プロセスを開始")
    try:
        asyncio.run(main(**vars(args)))
    except KeyboardInterrupt:
        logger.info("ユーザーによる中断を検出しました")
        sys.exit(0)
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        sys.exit(1)
