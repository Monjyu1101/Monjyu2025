#!/usr/bin/env python3
"""
Simple SQL Server MCP Server (Read-only) - Updated for latest MCP
SQLサーバー用のシンプルなMCPサーバー（読み取り専用）- 最新MCP対応
データベース指定を明確化
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd
import pyodbc
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)
from pydantic import AnyUrl

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLServerMCP:
    def __init__(self):
        # 環境変数から設定を読み込み
        self.server_name = os.getenv('SQL_SERVER_NAME', 'localhost')
        self.default_database = os.getenv('DEFAULT_DATABASE', 'master')
        self.username = os.getenv('SQL_SERVER_USERNAME', 'sa')
        self.password = os.getenv('SQL_SERVER_PASSWORD', '')
        self.excel_json_path = os.getenv('EXCEL_JSON_PATH', './output')
        
        # 出力ディレクトリの作成
        Path(self.excel_json_path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SQL Server MCP initialized")
        logger.info(f"Server: {self.server_name}")
        logger.info(f"Default Database: {self.default_database}")
        logger.info(f"Output Path: {self.excel_json_path}")

    def get_connection_string(self, database: str = None) -> str:
        """SQL Server接続文字列を生成（読み取り専用）"""
        db = database or self.default_database
        
        # ODBC接続文字列（読み取り専用設定）
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server_name};"
            f"DATABASE={db};"
            f"UID={self.username};"
            f"PWD={self.password};"
            "Trusted_Connection=no;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "ApplicationIntent=ReadOnly;"  # 読み取り専用接続
            "Connection Timeout=30;"       # 接続タイムアウト
            "Command Timeout=120;"         # コマンドタイムアウト
        )
        
        return connection_string

    async def execute_query(self, database: str, sql: str) -> Dict[str, Any]:
        """SQLクエリを実行（読み取り専用）"""
        try:
            # データベース名の必須チェック
            if not database or database.strip() == "":
                return {
                    "result": "ng",
                    "error": "データベース名が指定されていません。必須パラメータです。",
                    "json100": [],
                    "excel_path": "",
                    "database_used": "未指定"
                }
            
            # 危険なSQL文をチェック（読み取り専用の確保）
            dangerous_keywords = [
                'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
                'TRUNCATE', 'EXEC', 'EXECUTE', 'MERGE', 'BULK', 'INTO',
                'GRANT', 'REVOKE', 'DENY', 'BACKUP', 'RESTORE'
            ]
            
            sql_upper = sql.upper().strip()
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return {
                        "result": "ng",
                        "error": f"危険なSQL文が検出されました: {keyword}",
                        "json100": [],
                        "excel_path": "",
                        "database_used": database
                    }

            # SELECTまたはWITH文のみ許可
            if not (sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')):
                return {
                    "result": "ng",
                    "error": "SELECT文またはWITH文のみ実行可能です",
                    "json100": [],
                    "excel_path": "",
                    "database_used": database
                }

            # データベース接続（読み取り専用）
            connection_string = self.get_connection_string(database)
            
            with pyodbc.connect(connection_string) as conn:
                # 読み取り専用モードを明示的に設定
                conn.autocommit = True
                
                # カーソル作成
                cursor = conn.cursor()
                
                # 読み取り専用トランザクション分離レベル設定
                cursor.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
                
                # クエリ実行
                cursor.execute(sql)
                
                # 結果取得
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # データフレームに変換
                df = pd.DataFrame([list(row) for row in rows], columns=columns)
                
                # JSONとExcelファイル名生成
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"query_result_{database}_{timestamp}.json"
                excel_filename = f"query_result_{database}_{timestamp}.xlsx"
                
                json_path = os.path.join(self.excel_json_path, json_filename)
                excel_path = os.path.join(self.excel_json_path, excel_filename)
                
                # 最初の100件をJSON用に取得
                json100_data = df.head(100).to_dict('records')
                
                # JSONファイル保存
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "query": sql,
                        "database": database,
                        "timestamp": timestamp,
                        "total_rows": len(df),
                        "data": json100_data
                    }, f, ensure_ascii=False, indent=2, default=str)
                
                # Excelファイル保存
                df.to_excel(excel_path, index=False, engine='openpyxl')
                
                logger.info(f"Query executed successfully on database '{database}'. Rows: {len(df)}")
                
                return {
                    "result": "ok",
                    "total_rows": len(df),
                    "json100": json100_data,
                    "excel_path": excel_path,
                    "json_path": json_path,
                    "database_used": database
                }
                
        except pyodbc.Error as e:
            error_msg = f"SQL Server エラー (データベース: {database}): {str(e)}"
            logger.error(error_msg)
            return {
                "result": "ng",
                "error": error_msg,
                "json100": [],
                "excel_path": "",
                "database_used": database
            }
        except Exception as e:
            error_msg = f"実行エラー (データベース: {database}): {str(e)}"
            logger.error(error_msg)
            return {
                "result": "ng",
                "error": error_msg,
                "json100": [],
                "excel_path": "",
                "database_used": database
            }

# MCPサーバーインスタンス
sql_mcp = SQLServerMCP()
server = Server("sql-server-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """利用可能なツールを返す"""
    return [
        Tool(
            name="query",
            description=f"""SQLサーバーでクエリを実行（読み取り専用）
            
【重要】databaseパラメータは必須です！
- 必ずクエリを実行したいデータベース名を明示的に指定してください
- デフォルト値 '{sql_mcp.default_database}' は参考程度です
- ユーザーが指定したデータベース名を優先して使用してください

【使用例】
- 会計データベースの場合: database="会計システム"
- 顧客データベースの場合: database="顧客管理DB"
- テストデータベースの場合: database="TestDB"

【注意事項】
- SELECT文またはWITH文のみ実行可能
- データ変更を伴う操作（INSERT/UPDATE/DELETE等）は禁止
- 実行結果は最大100件がJSONで返され、全件がExcelファイルに保存されます""",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": f"【必須】データベース名を明示的に指定してください。ユーザーが指定したデータベース名を使用し、デフォルト値（{sql_mcp.default_database}）に頼らないでください。",
                        "minLength": 1
                    },
                    "sql": {
                        "type": "string",
                        "description": "実行するSQL文（SELECT文またはWITH文のみ許可）",
                        "minLength": 1
                    }
                },
                "required": ["database", "sql"],
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """ツール呼び出しを処理"""
    if name == "query":
        database = arguments.get("database", "").strip()
        sql = arguments.get("sql", "").strip()
        
        # データベース名の必須チェック
        if not database:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "result": "ng",
                    "error": "【エラー】databaseパラメータが必須です。データベース名を明示的に指定してください。",
                    "json100": [],
                    "excel_path": "",
                    "database_used": "未指定",
                    "help": "使用例: database='近藤V024ベース改' のように具体的なデータベース名を指定してください"
                }, ensure_ascii=False, indent=2)
            )]
        
        # SQL文の必須チェック  
        if not sql:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "result": "ng",
                    "error": "SQL文が空です",
                    "json100": [],
                    "excel_path": "",
                    "database_used": database
                }, ensure_ascii=False, indent=2)
            )]
        
        # クエリ実行
        result = await sql_mcp.execute_query(database, sql)
        
        # 成功時にも使用したデータベース名を明確に表示
        if result.get("result") == "ok":
            result["message"] = f"データベース '{database}' でクエリを正常に実行しました。"
        
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2, default=str)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=json.dumps({
                "result": "ng",
                "error": f"不明なツール: {name}",
                "json100": [],
                "excel_path": "",
                "database_used": "N/A"
            }, ensure_ascii=False, indent=2)
        )]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """利用可能なリソースを返す"""
    return []

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """リソース読み取り"""
    return ""

async def main():
    """メイン関数"""
    # MCPサーバー実行（最新バージョン対応）
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())


    