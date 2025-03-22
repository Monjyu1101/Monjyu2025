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

import requests
import urllib

class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "get_location_weather"
        self.func_ver  = "v0.20230803"
        self.func_auth = "i2MVvNm3ixND6JZNpMRJvoMNfrK3xYw9hWCdjTt8MSn6KO1Wt+STCZiAOT06QcoI"
        self.function  = {
            "name": self.func_name,
            "description": "指定した場所の天気、気温、風速を返す",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                            "type": "string",
                            "description": "天気を知りたい場所の県や市の名前 (例) 兵庫県三木市"
                    },
                },
                "required": ["location"]
            }
        }

        res = self.func_reset()

    def func_reset(self, ):
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        location = None
        if (json_kwargs != None):
            args_dic = json.loads(json_kwargs)
            location = args_dic.get('location')

        # 戻り値
        latitude    = None
        longitude   = None
        weather     = '不明'
        temperature = '不明'
        windspeed   = '不明'

        # 場所から緯度経度取得
        makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
        s_quote = urllib.parse.quote(location)
        response = requests.get(makeUrl + s_quote, timeout=(2,10), )
        if (response.status_code == 200):

            if (location == '兵庫県三木市'):
                latitude  =  34.797016
                longitude = 134.930450

            try:
                latitude  = response.json()[0]["geometry"]["coordinates"][1]
                longitude = response.json()[0]["geometry"]["coordinates"][0]
            except Exception as e:
                print(response.content)
                print(e)

        if (latitude == None) or (longitude == None):
            dic = {}
            dic['weather'] = weather
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump

        # 緯度経度から天気取得
        else:
            #print(latitude,longitude)

            base_url = "https://api.open-meteo.com/v1/forecast"
            parameters = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true"
            }
            response = requests.get(base_url, params=parameters, timeout=(2,10),)
            if (response.status_code == 200):

                try:
                    data = response.json()
                    #print(data['current_weather'])

                    # 気温、風速
                    temperature = data['current_weather']['temperature']
                    windspeed   = data['current_weather']['windspeed']

                    # WMO 気象解釈コード (WW)
                    cd = data["current_weather"]['weathercode']
                    if   (cd == 0): weather='晴天, 雲の発達が観測されない、または観測できない'
                    elif (cd == 1): weather='晴れ, 雲は一般的に溶けるか、発達が鈍くなっています'
                    elif (cd == 2): weather='晴れ時々曇り'
                    elif (cd == 3): weather='曇り'

                    elif (cd ==10): weather='靄'

                    elif (cd ==25): weather='にわか雨'
                    elif (cd ==26): weather='にわか雨、にわか雪'
                    elif (cd ==27): weather='あられ、にわか雨'
                    elif (cd ==28): weather='霧または氷霧'
                    elif (cd ==29): weather='雷雨'

                    elif (cd ==30): weather='砂嵐 - 前の 1 時間に減少しました'
                    elif (cd ==31): weather='砂嵐 - 前の 1 時間に目立った変化なし'
                    elif (cd ==32): weather='砂嵐 - 直前の 1 時間に始まった、または増加した'
                    elif (cd ==33): weather='激しい砂嵐 - 過去 1 時間で減少しました'
                    elif (cd ==34): weather='激しい砂嵐 - 前の 1 時間に目立った変化なし'
                    elif (cd ==35): weather='激しい砂嵐 - 直前の 1 時間に始まった、または増加した'

                    elif (cd ==36): weather='吹雪 - 全体的に低いところ（目の高さより下）で、わずかまたは中程度の吹雪'
                    elif (cd ==37): weather='吹雪 - 重い吹き雪は全体的に低いところ（目の高さより下）'
                    elif (cd ==38): weather='吹雪 - 全体的に高いところ（目の高さより上）で、わずかまたは中程度の吹雪'
                    elif (cd ==39): weather='吹雪 - 大雪が全体的に高いところ（目の高さよりも高い）に吹雪'

                    elif (cd ==41): weather='斑点状の霧または氷霧'
                    elif (cd ==42): weather='霧または氷霧、前の 1 時間で見える空が薄くなった'
                    elif (cd ==43): weather='霧または氷霧、目に見えない空が前の 1 時間で薄くなった'
                    elif (cd ==44): weather='霧または氷霧、空は見える 前の 1 時間に目立った変化なし'
                    elif (cd ==45): weather='霧または氷霧、空は見えない 前の 1 時間に目立った変化なし'
                    elif (cd ==46): weather='濃い霧または氷霧、空が見え始めたか、前の 1 時間で濃くなった'
                    elif (cd ==47): weather='濃い霧または氷霧、空が見えなくなった、または前の 1 時間で空が濃くなった'
                    elif (cd ==48): weather='霧、霧氷の堆積、空が見える'
                    elif (cd ==49): weather='濃い霧、霧氷の堆積、空は見えない'

                    elif (cd ==50): weather='霧雨、氷点下ではない、観測時断続的にわずかに降る'
                    elif (cd ==51): weather='霧雨、氷点下なし、観測時微雨継続'
                    elif (cd ==52): weather='霧雨、氷点下ではない、観測時断続中程度'
                    elif (cd ==53): weather='霧雨、氷点下なし、観測時中程度が継続'
                    elif (cd ==54): weather='激しい霧雨、氷点下ではない、観測時断続的に激しい（濃密）'
                    elif (cd ==55): weather='激しい霧雨、氷点下ではない、観測時は継続的に激しい（うねり）'
                    elif (cd ==56): weather='霧雨、氷点下、わずかに降る'
                    elif (cd ==57): weather='激しい霧雨、凍結、中程度または激しい（デンス）'
                    elif (cd ==58): weather='霧雨、小雨'
                    elif (cd ==59): weather='激しい霧雨と雨、中程度または激しい'

                    elif (cd ==60): weather='小雨、氷点下ではないが観測時は断続的に小雨'
                    elif (cd ==61): weather='雨、氷点下ではないが観測時は微雨が続いている'
                    elif (cd ==62): weather='雨、氷点下ではない、観測時は断続的中程度'
                    elif (cd ==63): weather='雨、氷点下ではないが観測時は穏やかな状態が続いている'
                    elif (cd ==64): weather='激しい雨、氷点下ではない、観測時は断続的に激しい雨'
                    elif (cd ==65): weather='激しい雨、氷点下ではないが観測時は激しい雨が続いている'
                    elif (cd ==66): weather='凍てつく雨、氷点下、小雨'
                    elif (cd ==67): weather='激しい雨、氷点下、中程度または激しい雨'
                    elif (cd ==68): weather='雨、または小雨と雪、わずかに'
                    elif (cd ==69): weather='激しい雨、霧雨、雪、中程度または激しい'

                    elif (cd ==70): weather='小雪、断続的に降る雪片は観察時にわずかに発生'
                    elif (cd ==71): weather='小雪、観測時に微量の雪片が継続的に降る'
                    elif (cd ==72): weather='雪、観測時の断続的な雪片の降下は中程度'
                    elif (cd ==73): weather='雪、観測時は雪片の継続的な降下は中程度'
                    elif (cd ==74): weather='大雪、観測時に大量の雪片が断続的に降る'
                    elif (cd ==75): weather='大雪、観測時には大量の雪片が降り続いている'
                    elif (cd ==76): weather='小雪、アイスプリズム（霧ありまたは霧なし）'
                    elif (cd ==77): weather='小雪、雪の粒子（霧の有無）'
                    elif (cd ==78): weather='小雪、孤立した星のような雪の結晶 (霧の有無にかかわらず)'
                    elif (cd ==79): weather='雪、氷ペレット'

                    elif (cd ==80): weather='にわか雨、わずかに'
                    elif (cd ==81): weather='激しいにわか雨、中程度または激しい'
                    elif (cd ==82): weather='激しいにわか雨、激しい雨'
                    elif (cd ==83): weather='にわか雨、雨と雪が混じった、わずかなにわか雨'
                    elif (cd ==84): weather='激しいにわか雨、雨と雪が混じった、中程度または激しいにわか雨'
                    elif (cd ==85): weather='にわか雪、わずかに'
                    elif (cd ==86): weather='激しいにわか雪、中程度または激しい'
                    elif (cd ==87): weather='雪粒または氷粒のシャワー、雨の有無にかかわらず、または雨と雪の混合 - わずか'
                    elif (cd ==88): weather='激しい雪粒または氷粒のシャワー、雨の有無にかかわらず、または雨と雪の混合 - 中程度または激しい'
                    elif (cd ==89): weather='雹のにわか雨、雨の有無、または雨と雪が混じる、雷を伴わない - わずか'

                    elif (cd ==90): weather='激しい雹のにわか雨、雨の有無にかかわらず、または雨と雪が混じる、雷を伴わない - 中程度または激しい'
                    elif (cd ==91): weather='小雨、観測時には小雨が降っていましたが、前の1時間は雷雨'
                    elif (cd ==92): weather='激しい雨、観測時に中程度または激しい雨 - 前の1時間に雷雨'
                    elif (cd ==93): weather='小雪、観測時はわずかな雪、または雨と雪の混じり、またはひょう - 前の1時間に雷雨'
                    elif (cd ==94): weather='大雪、中程度の雪または大雪、または雨と雪の混合またはひょう - 前の1時間に雷雨が発生'
                    elif (cd ==95): weather='雷雨、軽度または中程度、雹なし、ただし観測時に雨および/または雪 - 観測時に雷雨'
                    elif (cd ==96): weather='雷雨、軽度または中程度、雹を伴う - 観測時に雷雨'
                    elif (cd ==97): weather='激しい雷雨、激しい、雹はありませんが、観測時に雨または雪、あるいはその両方 - 観測時に雷雨'
                    elif (cd ==98): weather='砂嵐または砂嵐を伴う雷雨 - 観測時に雷雨'
                    elif (cd ==99): weather='激しい雷雨、激しい、雹を伴う - 観測時雷雨'
                    else:           weather='国際天気通報コード=' + str(cd) + 'です'
        
                except Exception as e:
                    print(response.content)
                    print(e)

        # 戻り
        dic = {}
        dic['weather'] = weather
        dic['temperature'] = str(temperature)
        dic['windspeed'] = str(windspeed)
        dic['latitude'] = str(latitude)
        dic['longitude'] = str(longitude)
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc( '{ "location": "兵庫県三木市" }' ))
