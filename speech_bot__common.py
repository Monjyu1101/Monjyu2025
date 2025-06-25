#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the MIT License.
# https://github.com/monjyu1101
# Thank you for keeping the rules.
# ------------------------------------------------

# モジュール名
MODULE_NAME = 'bot_comm'

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
import base64

class _bot_common:
    """
    チャットボット共通機能を提供するクラス
    履歴管理やファイル処理などの汎用機能を実装
    """

    def __init__(self):
        """
        bot_commonクラスのコンストラクタ
        各種設定値の初期化を行う
        """
        logger.debug("bot_commonクラスを初期化")
        # シーケンス番号
        self.seq = 0

    def files_check(self, filePath=[], api_type='standard'):
        """
        アップロードされたファイルを処理し、画像ファイルをbase64エンコードする
        各種APIに対応した形式で変換
        Args:
            filePath (list, optional): ファイルパスのリスト
            api_type (str, optional): API種別 ('standard', 'respo', 'groq', etc.)
        Returns:
            tuple: (アップロードファイルリスト, 画像URLリスト)
        """
        upload_files = []
        image_urls = []

        # 添付ファイルの確認と処理
        if (len(filePath) > 0):
            logger.debug(f"files_check() {len(filePath)}個のファイルを処理します")
            try:
                for file_name in filePath:
                    if (os.path.isfile(file_name)):
                        # サイズ制限チェック（API共通）
                        file_size = os.path.getsize(file_name)
                        if (file_size <= 20000000):
                            upload_files.append(file_name)

                            # 画像ファイルの場合、base64エンコードしてURL形式に変換
                            file_ext = os.path.splitext(file_name)[1][1:].lower()
                            if (file_ext in ('jpg', 'jpeg', 'png', 'gif')):
                                base64_text = self._base64_encode(file_name)
                                
                                # API種別による分岐
                                if api_type == 'respo':
                                    # Respo形式
                                    if (file_ext in ('jpg', 'jpeg')):
                                        url = f"data:image/jpeg;base64,{base64_text}"
                                        image_url = {"type": "input_image", 'image_url': url, 'detail': 'high'}
                                        image_urls.append(image_url)
                                    elif (file_ext == 'png'):
                                        url = f"data:image/png;base64,{base64_text}"
                                        image_url = {"type": "input_image", 'image_url': url, 'detail': 'high'}
                                        image_urls.append(image_url)
                                    elif (file_ext == 'gif'):
                                        url = f"data:image/gif;base64,{base64_text}"
                                        image_url = {"type": "input_image", 'image_url': url, 'detail': 'high'}
                                        image_urls.append(image_url)
                                else:
                                    # 標準形式 (OpenAI/ChatGPT/Grok/OpenRT用)
                                    if (file_ext in ('jpg', 'jpeg')):
                                        url = {"url": f"data:image/jpeg;base64,{base64_text}"}
                                        image_url = {'type': 'image_url', 'image_url': url}
                                        image_urls.append(image_url)
                                    elif (file_ext == 'png'):
                                        url = {"url": f"data:image/png;base64,{base64_text}"}
                                        image_url = {'type': 'image_url', 'image_url': url}
                                        image_urls.append(image_url)
                                    elif (file_ext == 'gif'):
                                        url = {"url": f"data:image/gif;base64,{base64_text}"}
                                        image_url = {'type': 'image_url', 'image_url': url}
                                        image_urls.append(image_url)
                        else:
                            logger.warning(f"files_check() ファイルサイズが上限を超えています: {file_name} ({file_size} bytes)")

            except Exception as e:
                logger.error(f"files_check() ファイル処理エラー: {e}")

        return upload_files, image_urls

    def _base64_encode(self, file_path):
        """
        ファイルをBase64エンコードする内部関数
        Args:
            file_path (str): エンコードするファイルのパス
        Returns:
            str: Base64エンコードされた文字列
        """
        with open(file_path, "rb") as input_file:
            logger.debug(f"ファイル '{file_path}' をBase64エンコード")
            return base64.b64encode(input_file.read()).decode('utf-8')

    def select_model(   self, 
                        chat_class, model_select, inpText, upload_files, image_urls,
                        a_nick_name, a_model, a_use_tools,
                        b_nick_name, b_model, b_use_tools,
                        v_nick_name, v_model, v_use_tools,
                        x_nick_name, x_model, x_use_tools):
        """
        モデル選択とテキスト処理のためのサブルーチン
        Returns:
            (処理済みテキスト, 応答モデル名, 応答APIモデル, 使用するツール)
        """
        # 初期値設定
        res_name = None
        res_api = None
        use_tools = None
        
        # モデル選択の補正（アシスタント用）
        assistant_classes = ['assistant', 'コード生成', 'コード実行', '文書検索', '複雑な会話', 'アシスタント']
        if (chat_class in assistant_classes or model_select == 'x') and (x_nick_name != ''):
            res_name = x_nick_name
            res_api = x_model
            use_tools = x_use_tools
        
        # ニックネーム指定によるモデル選択
        nickname_map = {
            a_nick_name: (a_nick_name, a_model, a_use_tools),
            b_nick_name: (b_nick_name, b_model, b_use_tools),
            v_nick_name: (v_nick_name, v_model, v_use_tools),
            x_nick_name: (x_nick_name, x_model, x_use_tools)
        }
        
        # 入力テキストからニックネームを抽出して処理
        for nick, (name, model, tools) in nickname_map.items():
            if nick and inpText.strip().lower().startswith(nick.lower() + ','):
                inpText = inpText.strip()[len(nick)+1:]
                
                # 各モデル特有の条件チェック
                if v_nick_name != '' and nick == v_nick_name:
                    res_name, res_api, use_tools = name, model, tools
                elif x_nick_name != '' and nick == x_nick_name:
                    res_name, res_api, use_tools = name, model, tools
                elif b_nick_name != '' and nick == b_nick_name:
                    res_name, res_api, use_tools = name, model, tools
                elif b_nick_name != '' and (nick == v_nick_name or nick == x_nick_name):
                    res_name, res_api, use_tools = b_nick_name, b_model, b_use_tools
                elif a_nick_name != '':
                    res_name, res_api, use_tools = a_nick_name, a_model, a_use_tools
        
        # 特殊プレフィックスリスト
        special_prefixes = [
            'riki', 'vision', 'assistant', 'openai', 'azure', 
            'chatgpt', 'assist', 'respo', 'gemini', 'freeai',
            'free', 'claude', 'openrouter', 'openrt', 'perplexity',
            'pplx', 'grok', 'groq', 'ollama', 'local'
        ]
        
        # 特殊プレフィックスの処理（カンマまでの部分を比較）
        input_stripped = inpText.strip()
        
        # 入力テキストの最初のカンマの位置を取得
        comma_pos = input_stripped.find(',')
        
        # カンマが見つかった場合、カンマより前の部分を取得して特殊プレフィックスと比較
        if comma_pos > 0:
            prefix_part = input_stripped[:comma_pos].lower()
            
            if prefix_part in special_prefixes:
                # カンマを含めたプレフィックスを削除
                inpText = input_stripped[comma_pos+1:]
                
                # 特定のプレフィックスに対する追加処理
                if prefix_part == 'riki':
                    if x_nick_name != '':
                        res_name, res_api, use_tools = x_nick_name, x_model, x_use_tools
                    elif b_nick_name != '':
                        res_name, res_api, use_tools = b_nick_name, b_model, b_use_tools
                elif prefix_part == 'vision':
                    if v_nick_name != '':
                        res_name, res_api, use_tools = v_nick_name, v_model, v_use_tools
                    elif x_nick_name != '':
                        res_name, res_api, use_tools = x_nick_name, x_model, x_use_tools
                elif prefix_part == 'assistant':
                    if x_nick_name != '':
                        res_name, res_api, use_tools = x_nick_name, x_model, x_use_tools
                    elif b_nick_name != '':
                        res_name, res_api, use_tools = b_nick_name, b_model, b_use_tools
        
        # モデル未設定時の自動選択
        if res_api is None:
            res_name = a_nick_name
            res_api = a_model
            use_tools = a_use_tools
            
            # テキスト長または添付ファイルに基づくモデル選択
            if b_nick_name != '' and (len(upload_files) > 0 or len(inpText) > 1000):
                res_name = b_nick_name
                res_api = b_model
                use_tools = b_use_tools
        
        # 画像処理のためのモデル補正
        if len(image_urls) > 0 and len(image_urls) == len(upload_files):
            if v_nick_name != '':
                res_name = v_nick_name
                res_api = v_model
                use_tools = v_use_tools
        
        return inpText, res_name, res_api, use_tools
    
    def history_add(self, history=[], sysText=None, reqText=None, inpText='こんにちは'):
        """
        会話履歴にメッセージを追加する
        Args:
            history (list, optional): 既存の会話履歴
            sysText (str, optional): システムテキスト
            reqText (str, optional): 要求テキスト
            inpText (str, optional): 入力テキスト
        Returns:
            list: 更新された会話履歴
        """
        res_history = history

        # sysTextの処理 (システムテキスト)
        if (sysText is not None) and (sysText.strip() != ''):
            # 既存履歴のシステムメッセージと異なる場合は履歴をリセット
            if (len(res_history) > 0):
                # 既存の履歴にシステムと新しいものと異なる場合は履歴をクリア
                if (sysText.strip() != res_history[0]['content'].strip()):
                    res_history = []
            # システムテキストを追加
            if (len(res_history) == 0):
                self.seq += 1
                dic = {'seq': self.seq, 'time': time.time(), 'role': 'system', 'name': '', 'content': sysText.strip()}
                res_history.append(dic)
        
        # reqTextの処理 (要求テキスト)
        if (reqText is not None) and (reqText.strip() != ''):
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': reqText.strip()}
            res_history.append(dic)

        # inpTextの処理 (入力テキスト)
        if (inpText.strip() != ''):
            self.seq += 1
            dic = {'seq': self.seq, 'time': time.time(), 'role': 'user', 'name': '', 'content': inpText.rstrip()}
            res_history.append(dic)

        return res_history

    def history_zip1(self, history=[]):
        """
        会話履歴から古いメッセージを削除する（時間ベース）
        15分以上経過したメッセージを削除
        Args:
            history (list, optional): 圧縮する会話履歴
        Returns:
            list: 圧縮された会話履歴
        """
        res_history = history

        if (len(res_history) > 0):
            for h in reversed(range(len(res_history))):
                tm = res_history[h]['time']
                # 15分（900秒）以上前のメッセージは削除対象
                if ((time.time() - tm) > 900):
                    if (h != 0):
                        del res_history[h]
                    else:
                        # インデックス0はシステムメッセージのみ維持
                        if (res_history[0]['role'] != 'system'):
                            del res_history[0]

        return res_history

    def history_zip2(self, history=[], leave_count=4):
        """
        会話履歴から古いメッセージを削除する（カウントベース）
        最新のleave_count件とシステムメッセージを残して削除
        Args:
            history (list, optional): 圧縮する会話履歴
            leave_count (int, optional): 残すメッセージの数
        Returns:
            list: 圧縮された会話履歴
        """
        res_history = history

        if (len(res_history) > 6):
            for h in reversed(range(2, len(res_history) - leave_count)):
                del res_history[h]

        return res_history

    def history2msg_gpt(self, history=[], api_type='standard'):
        """
        履歴をChatgpt API用のメッセージ形式に変換
        Args:
            history (list, optional): 会話履歴            
        Returns:
            list: API用に変換されたメッセージリスト
        """
        res_msg = []
        for h in range(len(history)):
            role = history[h]['role']
            content = history[h]['content']
            name = history[h]['name']

            # function_call以外の通常メッセージを変換
            if (role != 'function_call'):
                if (role not in ['system', 'user', 'assistant']):
                    role = 'user'
                if (name == ''):
                    dic = {'role': role, 'content': content}
                    res_msg.append(dic)
                else:
                    dic = {'role': role, 'name': name, 'content': content}
                    res_msg.append(dic)

        return res_msg

    def history2msg_vision(self, history=[], image_urls=[], api_type='standard'):
        """
        履歴をVision API用のメッセージ形式に変換（画像付き）
        Args:
            history (list, optional): 会話履歴
            image_urls (list, optional): 画像URL情報のリスト
        Returns:
            list: Vision API用に変換されたメッセージリスト
        """
        res_msg = []
        last_h = 0
        
        # 最後の通常メッセージのインデックスを検索
        for h in range(len(history)):
            role = history[h]['role']
            if (role != 'function_call') and (role != 'function'):
                last_h = h 

        # メッセージ変換処理
        for h in range(len(history)):
            role = history[h]['role']
            content = history[h]['content']
            name = history[h]['name']

            # 通常メッセージの処理
            if (role != 'function_call') and (role != 'function'):
                if (role not in ['system', 'user', 'assistant']):
                    role = 'user'
                # 最後のメッセージでない場合は通常変換
                if (h != last_h):
                    if (name == ''):
                        dic = {'role': role, 'content': content}
                        res_msg.append(dic)
                    else:
                        dic = {'role': role, 'name': name, 'content': content}
                        res_msg.append(dic)
                # 最後のメッセージに画像を追加
                else:
                    con = []
                    if api_type == 'respo':
                        con.append({'type': 'input_text', 'text': content})
                    else:
                        con.append({'type': 'text', 'text': content})
                    for image_url in image_urls:
                        con.append(image_url)
                    if (name == ''):
                        dic = {'role': role, 'content': con}
                        res_msg.append(dic)
                    else:
                        dic = {'role': role, 'name': name, 'content': con}
                        res_msg.append(dic)

        return res_msg

    def history2msg_text(self, history=[]):
        """
        履歴をChatgpt API用のメッセージ形式に変換
        Args:
            history (list, optional): 会話履歴            
        Returns:
            list: API用に変換されたメッセージリスト
        """
        # 過去メッセージをテキストとして追加
        msg_text = ''
        if (len(history) > 2):
            msg_text += "''' これは過去の会話履歴です。\n"
            for m in range(0, len(history) - 2):
                role = history[m].get('role','')
                content = history[m].get('content','')
                name = history[m].get('name','')
                if (role != 'system'):
                    # 全てユーザーメッセージにて処理
                    if (name is None) or (name == ''):
                        msg_text += '(' + role + ')' + '\n' + content + '\n'
                    else:
                        if (role == 'function_call'):
                            msg_text += '(function ' + name + ' call)'  + '\n' + content + '\n'
                        else:
                            msg_text += '(function ' + name + ' result) ' + '\n' + content + '\n'
            msg_text += "''' 会話履歴はここまでです。\n"
            msg_text += "\n"
       
        # 最新のユーザーメッセージを追加
        m = len(history) - 1
        msg_text += history[m].get('content', '')

        return msg_text

    def history2msg_perplexity(self, history=[]):
        """
        履歴をChatgpt API用のメッセージ形式に変換
        Args:
            history (list, optional): 会話履歴            
        Returns:
            list: API用に変換されたメッセージリスト
        """
        # 過去メッセージをテキストとして追加
        msg_text = ''
        if (len(history) > 1):
            msg_text += "''' これは過去の会話履歴です。\n"
            for m in range(len(history) - 1):
                role = history[m].get('role','')
                content = history[m].get('content','')
                name = history[m].get('name','')
                # 全てユーザーメッセージにて処理
                if (name is None) or (name == ''):
                    msg_text += '(' + role + ')' + '\n' + content + '\n'
                else:
                    if (role == 'function_call'):
                        msg_text += '(function ' + name + ' call)'  + '\n' + content + '\n'
                    else:
                        msg_text += '(function ' + name + ' result) ' + '\n' + content + '\n'
            msg_text += "''' 会話履歴はここまでです。\n"
            msg_text += "\n"
        
        # 最新のユーザーメッセージを追加
        m = len(history) - 1
        msg_text += history[m].get('content', '')

        # メッセージ配列の作成
        res_msg = []
        dic = {'role': 'user', 'content': msg_text }
        res_msg.append(dic)

        return res_msg

if __name__ == '__main__':
    """
    テスト用コード
    """
    logger.setLevel(logging.INFO)
    logger.info("【テスト開始】")

    # bot_commonクラスのインスタンス化
    bot_common = _bot_common()
    
    # 基本的な機能テスト
    history = []
    
    # history_add テスト
    logger.info("history_add テスト")
    history = bot_common.history_add(history=history, sysText="こんにちは、システムです。", inpText="ユーザーからの入力です。")
    print(f"履歴数: {len(history)}")
    for item in history:
        print(f"  {item['role']}: {item['content']}")
    
    # history_zip1 テスト (時間経過をシミュレートするため、時間を操作)
    logger.info("history_zip1 テスト")
    # 古い時間のエントリを手動で追加
    old_time = time.time() - 1000  # 16分以上前
    bot_common.seq += 1
    old_entry = {'seq': bot_common.seq, 'time': old_time, 'role': 'user', 'name': '', 'content': "これは古いメッセージです"}
    history.append(old_entry)
    
    print(f"圧縮前の履歴数: {len(history)}")
    history = bot_common.history_zip1(history=history)
    print(f"圧縮後の履歴数: {len(history)}")
    for item in history:
        print(f"  {item['role']}: {item['content']}")
    
    logger.info("【テスト終了】")
