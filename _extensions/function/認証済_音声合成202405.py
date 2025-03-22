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

import sys
import os
import time
import datetime
import codecs
import glob

import subprocess
import openai
from gtts import gTTS

import requests
import wave

from playsound3 import playsound

if (os.name == 'nt'):
    import pythoncom
    import win32com.client

import socket
qHOSTNAME = socket.gethostname().lower()

use_openai_list   = ['kondou-latitude', 'kondou-main11', 'kondou-sub64', 'repair-surface7', ]



# インターフェース

qPath_work   = 'temp/_work/'
qPath_play   = 'temp/s6_7play/'

openai_model = 'tts-1'



class sub_class:

    def __init__(self, runMode='assistant', ):
        self.runMode      = runMode

    def init(self, ):
        return True

    def play(self, outFile='temp/_work/sound.mp3', ):
        if (outFile is None) or (outFile == ''):
            return False
        if (not os.path.isfile(outFile)):
            return False
        try:
            # 再生
            playsound(sound=outFile, block=True, )
            return True
        except Exception as e:
            print(e)
        return False



class tts_class:
    def __init__(self, runMode='assistant', ):
        self.runMode  = runMode

        # ディレクトリ作成
        if (not os.path.exists(qPath_work)):
            os.makedirs(qPath_work)
        if (not os.path.exists(qPath_play)):
            os.makedirs(qPath_play)

        # openai チェック
        self.openai_enable = False
        try:
            # APIキーを取得
            self.openai_organization = os.environ.get('OPENAI_ORGANIZATION', '< ? >')
            self.openai_key_id = os.environ.get('OPENAI_API_KEY', '< ? >')
            if (self.openai_organization == '') \
            or (self.openai_organization[:1] == '<') \
            or (self.openai_key_id == '') \
            or (self.openai_key_id[:1] == '<'):
                raise ValueError("Please set your openai organization and key !")

            # APIキーを設定
            openai.organization = self.openai_organization
            openai.api_key      = self.openai_key_id
            self.client = openai.OpenAI(
                organization=self.openai_organization,
                api_key=self.openai_key_id,
            )

            self.openai_enable = True
        except:
            pass

        # VOICEVOX チェック
        self.voicevox_enable = False
        self.voicevox_host   = 'localhost'
        self.voicevox_port   = 50021
        try:
            host = self.voicevox_host
            port = self.voicevox_port
            res = requests.get(
                    f'http://{host}:{port}/version',
                    timeout=(2, 5)
            )
            if (res.status_code == 200):
                self.voicevox_enable  = True
                self.voicevox_version = res.json()
                print('Voicevox ready! (' + self.voicevox_version + ')')
        except:
            pass

    def openai_tts(self, outText='おはよう', outLang='auto', outSpeaker='nova', outGender='female', outFile='temp/_work/tts.mp3', ):
        outFile = outFile[:-4] + '.mp3'

        if (self.openai_enable != True):
            return False, None

        # 引数チェック
        text = outText.strip()
        if (text == '') or (text == '!'):
            return False, None

        voice  = outSpeaker
        if (outSpeaker == 'openai'):
            voice  = 'nova'
        lang   = outLang
        gender = outGender.lower()

        # 音声合成
        if True:
        #try:
            response = self.client.audio.speech.create(
                        input=text, model=openai_model, voice=voice, speed=0.9, timeout=10, )
            #response.stream_to_file(outFile)
            response.write_to_file(outFile)
            time.sleep(0.10)
        #except Exception as e:
        #    print(e)
        #    return False, None

        # 結果確認
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 4096):
                os.remove(outFile)
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 44):
                os.remove(outFile)
            else:
                return outFile, 'openai'

        return False, None

    def google_tts(self, outText='おはよう', outLang='auto', outSpeaker='google', outGender='female', outFile='temp/_work/tts.mp3', ):
        outFile = outFile[:-4] + '.mp3'

        # 引数チェック
        text = outText.strip()
        if (text == '') or (text == '!'):
            return False, None

        gender = outGender.lower()

        lang = ''
        if   (outLang == 'auto') \
        or   (outLang == 'ja') or (outLang == 'ja-JP'):
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
            #time.sleep(0.10)
        except Exception as e:
            print(e)
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

    def winos_tts(self, outText='おはよう', outLang='auto', outSpeaker='winos', outGender='female', outFile='temp/_work/tts.wav'):
        outFile = outFile[:-4] + '.wav'

        if (os.name != 'nt'):
            return False, None

        # 引数チェック
        text = outText.strip()
        if (text == '') or (text == '!'):
            return False, None

        #ja-JP:日本語〇,    en-US:英語〇,
        #ar-AR:アラビア語x, es-ES:スペイン語×, de-DE:ドイツ語×
        #fr-FR:フランス語〇,it-IT:イタリア語×, pt-BR:ポルトガル語×
        #ru-RU:ロシア語×,  tr-TR:トルコ語×,   uk-UK:ウクライナ語×
        #zh-CN:中国語×,    kr-KR:韓国語×

        gender = outGender.lower()

        lang = ''
        if   (outLang == 'auto') \
        or   (outLang == 'ja') or (outLang == 'ja-JP'):
            lang = 'ja-JP'
        elif (outLang == 'en') or (outLang == 'en-US'):
            lang = 'en-US'
        elif (outLang == 'ar'):
            lang = 'ar-AR'
        elif (outLang == 'es'):
            lang = 'es-ES'
        elif (outLang == 'de'):
            lang = 'de-DE'
        elif (outLang == 'fr'):
            lang = 'fr-FR'
        elif (outLang == 'it'):
            lang = 'it-IT'
        elif (outLang == 'pt'):
            lang = 'pt-BR'
        elif (outLang == 'ru'):
            lang = 'ru-RU'
        elif (outLang == 'tr'):
            lang = 'tr-TR'
        elif (outLang == 'uk'):
            lang = 'uk-UK'
        elif (outLang == 'zh') or (outLang == 'zh-CN'):
            lang = 'zh-CN'
        elif (outLang == 'kr'):
            lang = 'kr-KR'
        else:
            lang = outLang

        # 音声合成
        try:

            # MS Windows
            stml  = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
            if (lang == 'ja-JP'):
                stml += '<prosody rate="1.0">'
            stml += '<voice xml:lang="' + lang + '" gender="' + gender + '">'
            stml += text
            stml += '</voice>'
            if (lang == 'ja-JP'):
                stml += '</prosody>'
            stml += '</speak>'

            pythoncom.CoInitialize()

            try:
                engine = win32com.client.Dispatch('SAPI.SpVoice')
                #engine.Speak(stml)

            except Exception as e:
                print(lang, gender, )
                print(e)
                return False, None

            try:
                stream = win32com.client.Dispatch('SAPI.SpFileStream')
                stream.open(outFile, 3, False)
                #for speaker in engine.GetAudioOutputs():
                #    print(speaker.GetDescription())

                engine.AudioOutputStream = stream
                engine.Speak(stml)

                stream.close()
                #time.sleep(0.10)
            except Exception as e:
                print(lang, gender, )
                print(e)
                return False, None

            engine = None
            stream = None

            pythoncom.CoUninitialize()

        except Exception as e:
            print(e)
            return False, None

        # 結果確認
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 4096):
                os.remove(outFile)
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 44):
                os.remove(outFile)
            else:
                return outFile, 'winos'

        return False, None

    def macos_tts(self, outText='おはよう', outLang='auto', outSpeaker='macos', outGender='female', outFile='temp/_work/tts.wav'):
        wrkFile = outFile[:-4] + '.wave'
        outFile = outFile[:-4] + '.wav'

        if (os.path.isfile(wrkFile)):
            try:
                os.remove(wrkFile)
            except Exception as e:
                print(e)

        if (sys.platform != 'darwin'): # MacOS チェック
            return False, None

        # 引数チェック
        text = outText.strip()
        if (text == '') or (text == '!'):
            return False, None

        #ja-JP:日本語,    en-US:英語,
        #ar-SA:アラビア語, es-ES:スペイン語, de-DE:ドイツ語
        #fr-FR:フランス語, it-IT:イタリア語, pt-PT:ポルトガル語
        #ru-RU:ロシア語,  tr-TR:トルコ語,   uk-UK:ウクライナ語×
        #zh-CN:中国語,    ko-KR:韓国語

        gender = outGender.lower()

        voice = ''
        rate  = ''
        if   (outSpeaker.lower() == 'kyoko'):
                voice = 'Kyoko'
                rate  = '200'
        elif (outSpeaker.lower() == 'otoya'):
                voice = 'Otoya'
        elif (outLang == 'auto') \
        or   (outLang == 'ja') or (outLang == 'ja-JP'):
            if (gender != 'male'):
                voice = 'Kyoko'
                #voice = 'O-Ren'
                #voice = ''
                rate  = '200'
            else:
                voice = 'Otoya'
                #voice = 'Hattori'
        elif (outLang == 'en') or (outLang == 'en-US'):
            if (gender != 'male'):
                voice = 'Ava'
            else:
                voice = 'Tom'
        elif (outLang == 'ar'):
            voice = 'Laila'
        elif (outLang == 'es'):
            voice = 'Monica'
        elif (outLang == 'de'):
            voice = 'Anna'
        elif (outLang == 'fr'):
            voice = 'Aurelie'
        elif (outLang == 'it'):
            voice = 'Federica'
        elif (outLang == 'pt'):
            voice = 'Joana'
        elif (outLang == 'ru'):
            voice = 'Milena'
        elif (outLang == 'tr'):
            voice = 'Yelda'
        elif (outLang == 'uk'):
            voice = ''
        elif (outLang == 'zh') or (outLang == 'zh-CN'):
            voice = 'Ting-Ting'
        elif (outLang == 'ko'):
            voice = 'Yuna'

        # 音声合成
        try:
            if (voice != ''):
                if (rate != ''):
                    say = subprocess.Popen(['say', '-v', voice, '"' + outText + '"', '-r', str(rate), '-o', wrkFile, ], )
                else:
                    say = subprocess.Popen(['say', '-v', voice, '"' + outText + '"', '-o', wrkFile, ], )
            else:
                if (rate != ''):
                    say = subprocess.Popen(['say', '"' + outText + '"', '-r', str(rate), '-o', wrkFile, ], )
                else:
                    say = subprocess.Popen(['say', '"' + outText + '"', '-o', wrkFile, ], )

            # 最大10s
            say.wait(timeout=10)
            say.terminate()
            say = None

        except Exception as e:
            print(e)
            return False, None

        # 結果確認
        if (os.path.isfile(wrkFile)):
            os.rename(wrkFile, outFile)
            
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 4096):
                os.remove(outFile)
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 44):
                os.remove(outFile)
            else:
                return outFile, 'macos'

        return False, None

    def voicevox_tts(self, outText='おはよう', outLang='auto', outSpeaker='voicevox', outGender='female', outFile='temp/_work/tts.wav', ):
        outFile = outFile[:-4] + '.wav'

        if (self.voicevox_enable != True):
            return False, None

        # 引数チェック
        text = outText.strip()
        if (text == '') or (text == '!'):
            return False, None

        speaker_id = 20 #もち子
        if (outGender.lower() == 'male') or (outGender.find('男') >= 0):
            speaker_id = 21 #龍星

        if   (outSpeaker.lower() == 'voicevox'):
            pass
        elif (outSpeaker == '四国めたん') or (outSpeaker == 'めたん'):
            speaker_id = 2 #ノーマル
        elif (outSpeaker == 'ずんだもん'):
            speaker_id = 3 #ノーマル
        elif (outSpeaker == '九州そら') or (outSpeaker == 'そら'):
            speaker_id = 16 #ノーマル
        elif (outSpeaker == 'もち子さん') or (outSpeaker == 'もち子'):
            speaker_id = 20
        elif (outSpeaker == '玄野武宏') or (outSpeaker == '武宏'):
            speaker_id = 11
        elif (outSpeaker == '青山龍星') or (outSpeaker == '龍星'):
            speaker_id = 21
        else:
            return False, None

        # 音声合成
        try:
            host = self.voicevox_host
            port = self.voicevox_port

            params = (
                ('text', text),
                ('speaker', speaker_id),
            )

            res1 = requests.post(
                f'http://{host}:{port}/audio_query',
                params=params,
                timeout=(3, 15)
            )

            if (res1.status_code == 200):
                headers = {'Content-Type': 'application/json',}
                res2 = requests.post(
                    f'http://{host}:{port}/synthesis',
                    headers=headers,
                    params=params,
                    data=json.dumps(res1.json()),
                    timeout=(3, 15)
                )

                if (res2.status_code == 200):

                    #wf = wave.open(outFile, 'wb')
                    #wf.setnchannels(1)
                    #wf.setsampwidth(2)
                    #wf.setframerate(24000)
                    #wf.writeframes(res2.content)
                    #wf.close()

                    # 音声ファイルを保存
                    with open(outFile, "wb") as wf:
                        wf.write(res2.content)

        except Exception as e:
            print(e)
            return False, None

        # 結果確認
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 4096):
                os.remove(outFile)
        if (os.path.isfile(outFile)):
            if (os.path.getsize(outFile) <= 44):
                os.remove(outFile)
            else:
                return outFile, 'voicevox'

        return False, None



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "execute_text_to_speech"
        self.func_ver  = "v0.20240518"
        self.func_auth = "tNpDwVT/ekhNji7k5yV2XgWSH6m8ci0aGRbIlTK/w1hMFzR6SE7ISMS8dZ3oY7K3"
        self.function  = {
            "name": self.func_name,
            "description": \
"""
機密保持の必要性から、この機能は指示があった場合のみ実行する。
この機能で、テキストを音声合成するとともに音声再生まで実行される。
別途、音声再生を行う必要はない。
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "speech_text": {
                            "type": "string",
                            "description": "テキスト (例) おはようございます"
                    },
                    "language": {
                            "type": "string",
                            "description": "テキストの言語 auto,ja,en, (例) auto"
                    },
                    "speaker": {
                            "type": "string",
                            "description": \
"""
話者は、'auto', 'openai', 'google', 'winos', 'macos', 'voicevox',
'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmey',
'めたん', 'ずんだもん', 'そら', 'もち子', '武宏', '龍星',
(例) auto
"""
                    },
                    "gender": {
                            "type": "string",
                            "description": "性別 male,female, (例) female"
                    },
                    "immediate": {
                            "type": "string",
                            "description": "即時再生 yes,no, (例) yes"
                    },
                },
                "required": ["runMode", "speech_text"]
            }
        }

        # 初期設定
        self.runMode  = 'assistant'
        self.tts_proc = tts_class(runMode=self.runMode, )
        self.sub_proc = sub_class(runMode=self.runMode, )
        self.func_reset()

        self.tts_seq  = 0

    def func_reset(self, ):
        self.last_text    = ''
        self.last_speaker = ''
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode     = None
        speech_text = None
        language    = None
        speaker     = None
        gender      = 'female'
        immediate   = 'yes'
        if (json_kwargs != None):
            args_dic    = json.loads(json_kwargs)
            runMode     = args_dic.get('runMode')
            speech_text = args_dic.get('speech_text')
            language    = args_dic.get('language')
            speaker     = args_dic.get('speaker')
            gender      = args_dic.get('gender', 'female')
            immediate   = args_dic.get('immediate', 'yes')

        if (runMode is None) or (runMode == ''):
            runMode      = self.runMode
        else:
            self.runMode = runMode

        # 指定
        if (speech_text != None):
            speech_text = speech_text.strip()

        if (language == None):
            language = 'auto'

        if (speaker == None) or (speaker == 'auto'):
            if (sys.platform != 'darwin'): # MacOS チェック
                speaker = 'google'
            else:
                speaker = 'macos'
            if(qHOSTNAME in use_openai_list):
                speaker = 'openai'

        if (gender == None):
            gender = 'female'

        # テキスト無しはエラー！
        if (speech_text == ''):
            dic = {}
            dic['result']     = 'ng'
            dic['error_text'] = '音声合成エラー。テキストがありません。'
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump

        # 連続発声はキャンセル！
        if  (speech_text == self.last_text) \
        and (speaker     == self.last_speaker):
            dic = {}
            dic['result']     = 'ng'
            dic['error_text'] = 'さきほど再生した内容と同じ内容です。'
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump

        # 出力ファイル
        self.tts_seq += 1
        if (self.tts_seq > 9999):
            self.tts_seq = 1
        seq4 = '{:04}'.format(self.tts_seq)
        if (immediate != 'no'):
            outFile = qPath_work + self.func_name + '.' + seq4 + '.mp3'
        else:
            outFile = qPath_play + self.func_name + '.' + seq4 + '.mp3'

        if (os.path.isfile(outFile)):
            try:
                os.remove(outFile)
            except Exception as e:
                print(e)
        if (os.path.isfile(outFile[:-4] + '.wav')):
            try:
                os.remove(outFile[:-4] + '.wav')
            except Exception as e:
                print(e)

        # 初期化
        tts_ok  = False
        play_ok = False

        # 音声合成 (voicevox)
        if (tts_ok == False):
            if (speaker.lower() == 'openai') \
            or (speaker.lower() == 'alloy'  ) or (speaker.lower() == 'echo'   ) \
            or (speaker.lower() == 'fable'  ) or (speaker.lower() == 'onyx'   ) \
            or (speaker.lower() == 'nova'   ) or (speaker.lower() == 'shimmey'):
                res, api = self.tts_proc.openai_tts(outText=speech_text, outLang=language, outSpeaker=speaker, outGender=gender, outFile=outFile, )
                if (res != False):
                    tts_ok  = True
                    outFile = res
                    self.last_text    = speech_text
                    self.last_speaker = speaker

        # 音声合成 (voicevox)
        if (tts_ok == False):
            if (speaker.lower() == 'voicevox') \
            or (speaker == '四国めたん') or (speaker == 'めたん') \
            or (speaker == 'ずんだもん') \
            or (speaker == '九州そら') or (speaker == 'そら') \
            or (speaker == 'もち子さん') or (speaker == 'もち子') \
            or (speaker == '玄野武宏') or (speaker == '武宏') \
            or (speaker == '青山龍星') or (speaker == '龍星'):
                res, api = self.tts_proc.voicevox_tts(outText=speech_text, outLang=language, outSpeaker=speaker, outGender=gender, outFile=outFile, )
                if (res != False):
                    tts_ok  = True
                    outFile = res
                    self.last_text    = speech_text
                    self.last_speaker = speaker

        # 音声合成 (winos)
        if (tts_ok == False):
            if (speaker.lower() == 'winos'):
                res, api = self.tts_proc.winos_tts(outText=speech_text, outLang=language, outSpeaker=speaker, outGender=gender, outFile=outFile, )
                if (res != False):
                    tts_ok  = True
                    outFile = res
                    self.last_text    = speech_text
                    self.last_speaker = speaker

        # 音声合成 (macos)
        if (tts_ok == False):
            if (speaker.lower() == 'macos') \
            or (speaker.lower() == 'kyoko') \
            or (speaker.lower() == 'otoya'):
                res, api = self.tts_proc.macos_tts(outText=speech_text, outLang=language, outSpeaker=speaker, outGender=gender, outFile=outFile, )
                if (res != False):
                    tts_ok  = True
                    outFile = res
                    self.last_text    = speech_text
                    self.last_speaker = speaker

        # 音声合成 (google)
        if (tts_ok == False):
            #if (speaker.lower() == 'google'):
                res, api = self.tts_proc.google_tts(outText=speech_text, outLang=language, outSpeaker=speaker, outGender=gender, outFile=outFile, )
                if (res != False):
                    if (speaker.lower() != 'google'):
                        print('tts : ' + speaker + ' -> google ok')
                    tts_ok  = True
                    outFile = res
                    self.last_text    = speech_text
                    self.last_speaker = speaker
                else:
                    if (speaker.lower() != 'google'):
                        print('tts : ' + speaker + ' -> google ng!')

        # 音声合成エラー
        if (tts_ok == False):
            dic = {}
            dic['result']     = 'ng'
            dic['error_text'] = '音声合成でエラーが発生しました。'
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump

        # 音声再生
        print('tts  :', outFile, '(' + api + ')')

        if (immediate == 'no'):
            dic = {}
            dic['result']      = 'ok'
            dic['result_text'] = '音声合成を実施しました。'
            dic['output_path'] = outFile
            json_dump = json.dumps(dic, ensure_ascii=False, )
            #print('  --> ', json_dump)
            return json_dump

        else:
            print('play :', outFile)
            res = self.sub_proc.play(outFile=outFile, )
            if (res != False):
                play_ok = True

            # 戻り値
            if (play_ok == True):
                dic = {}
                dic['result']      = 'ok'
                dic['result_text'] = '音声合成及び音声ファイルの再生も実施しました。'
                dic['output_path'] = outFile
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print('  --> ', json_dump)
                return json_dump
            else:
                dic = {}
                dic['result']     = 'ng'
                dic['error_text'] = '音声ファイルの再生でエラーが発生しました'
                json_dump = json.dumps(dic, ensure_ascii=False, )
                #print('  --> ', json_dump)
                return json_dump



if __name__ == '__main__':

    ext = _class()
    print(ext.func_proc( '{ "speech_text": "おはようございます", "language": "auto", "speaker": "voicevox", "gender": "female" }' ))
    print(ext.func_proc( '{ "speech_text": "おはようございます", "language": "auto", "speaker": "ずんだもん", "gender": "female" }' ))
    #print(ext.func_proc( '{ "speech_text": "よろしくお願いします", "language": "auto", "speaker": "winos", "gender": "female" }' ))
    #print(ext.func_proc( '{ "speech_text": "ありがとうございます", "language": "auto", "speaker": "macos", "gender": "female" }' ))
    #print(ext.func_proc( '{ "speech_text": "お疲れさまでした", "language": "auto", "speaker": "openai", "gender": "female" }' ))
    print(ext.func_proc( '{ "speech_text": "お疲れさまでした", "language": "auto", "speaker": "google", "gender": "female" }' ))
    #print(ext.func_proc( '{ "speech_text": "お疲れさまでした" }' ))

