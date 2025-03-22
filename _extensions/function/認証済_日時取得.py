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
import datetime

class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "get_current_datetime"
        self.func_ver  = "v0.20230803"
        self.func_auth = "y7KcAt/+SZV0XPCnPbAKxLT4M7gaycOptFGmhoyF0EfM61AzYkebahZpwdI3GmtI"
        self.function  = {
            "name": self.func_name,
            "description": "現在の日付、時刻（時間）を返す",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "現在を表す単語 (例) 今"
                    },
                },
            }
        }

        res = self.func_reset()

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数 無し

        # 処理
        now_dt = datetime.datetime.now()
        date_str = now_dt.strftime('%Y/%m/%d')
        time_str = now_dt.strftime('%H:%M:%S')

        # 戻り
        dic = {}
        dic['date'] = date_str
        dic['time'] = time_str
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump



if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc())
