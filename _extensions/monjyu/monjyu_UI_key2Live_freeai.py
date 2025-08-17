#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------
# COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
# This software is released under the not MIT License.
# Permission from the right holder is required for use.
# https://github.com/ClipnGPT
# Thank you for keeping the rules.
# ------------------------------------------------

import sys
import os
import time
import datetime
import codecs
import glob

import json
import base64
import pyaudio
from playsound3 import playsound
import wave

import threading
import asyncio

from google import genai
from google.genai import types
import speech_recognition as sr

import keyboard

# クリップボード画像処理
from PIL import Image, ImageGrab, ImageTk
import io
import screeninfo
import pyautogui
import cv2
import hashlib

# Monjyu連携
import requests

# グラフ表示
import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')



# インターフェース
qIO_liveAiRun  = 'temp/monjyu_live_ai_run.txt'
qIO_agent2live = 'temp/monjyu_io_agent2live.txt'

# モデル設定 (freeai)
LIVE_MODELS = { "gemini-2.0-flash-exp": "gemini-2.0-flash-exp",
                "gemini-2.0-flash-live-001": "gemini-2.0-flash-live-001",
                "gemini-live-2.5-flash-preview": "gemini-live-2.5-flash-preview",
                "gemini-2.5-flash-exp-native-audio-thinking-dialog": "gemini-2.5-flash-exp-native-audio-thinking-dialog",
                "gemini-2.5-flash-preview-native-audio-dialog": "gemini-2.5-flash-preview-native-audio-dialog", }
LIVE_VOICES = { "Puck": "(2.0) Puck",
                "Charon": "(2.0) Charon", 
                "Kore": "(2.0) Kore Female", 
                "Fenrir": "(2.0) Fenrir", 
                "Aoede": "*** (2.0) Aoede Female", 

                "Leda": "(2.5) Leda Female", 
                "Orus": "(2.5) Orus", 
                "Zephyr": "*** (2.5) Zephyr Female", 

                "Callirrhoe": "Callirrhoe Female", 
                "Autonoe": "Autonoe Female", 
                "Enceladus": "Enceladus", 
                "Lapetus": "Lapetus", 
                "Umbriel": "Umbriel", 
                "Algieba": "Algieba", 
                "Despina": "Despina Female", 
                "Erinome": "Erinome Female", 
                "Algenib": "Algenib", 
                "Rasalgethi": "Rasalgethi", 
                "Laomedeia": "Laomedeia Female", 
                "Achernar": "Achernar Female", 
                "Alnilam": "Alnilam", 
                "Schedar": "Schedar", 
                "Gacrux": "Gacrux Female", 
                "Pulcherrima": "Pulcherrima", 
                "Achird": "Achird", 
                "Zubenelgenubi": "Zubenelgenubi", 
                "Vindemiatrix": "Vindemiatrix Female", 
                "Sadachbia": "Sadachbia", 
                "Sadaltager": "Sadaltager",
                "Sulafat": "Sulafat Female", }

LIVE_MODEL = "gemini-live-2.5-flash-preview"
LIVE_VOICE = "Zephyr"

# 音声ストリーム 設定
INPUT_CHUNK = 2048
INPUT_RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
OUTPUT_CHUNK = 2048
OUTPUT_RATE = 24000

# 定数の定義
CORE_PORT = '8000'
CONNECTION_TIMEOUT = 15
REQUEST_TIMEOUT = 30
ALIVE_BEAT_SEC = 300



def io_text_read(filename=''):
    text = ''
    file1 = filename
    file2 = filename[:-4] + '.@@@'
    try:
        while (os.path.isfile(file2)):
            os.remove(file2)
            time.sleep(0.10)
        if (os.path.isfile(file1)):
            os.rename(file1, file2)
            time.sleep(0.10)
        if (os.path.isfile(file2)):
            r = codecs.open(file2, 'r', 'utf-8-sig')
            for t in r:
                t = t.replace('\r', '')
                text += t
            r.close
            r = None
            time.sleep(0.25)
        while (os.path.isfile(file2)):
            os.remove(file2)
            time.sleep(0.10)
    except:
        pass
    return text

def io_text_write(filename='', text='', ):
    try:
        w = codecs.open(filename, 'w', 'utf-8')
        w.write(text)
        w.close()
        w = None
        return True
    except:
        pass
    return False



class _key2Action:

    def __init__(self, runMode='assistant', ):
        self.runMode = runMode

        # APIキーを取得
        self.freeai_key_id = os.environ.get('FREEAI_API_KEY', '< ? >')

        # live実行状況クリア
        dummy = io_text_read(qIO_liveAiRun)

        # liveAPI クラス
        self.liveAPI = _live_api_freeai(api_key=self.freeai_key_id, )

        # liveAPI 監視
        self.liveAPI_rerun = 0
        self.liveAPI_task = threading.Thread(target=self.liveAPI_check, daemon=True)
        self.liveAPI_task.start()

        # キーボード監視 開始
        self.last_key_time = 0
        self.kb_handler_id = None
        self.start_kb_listener()

    # liveAPI監視
    def liveAPI_check(self):
        while True:
            if (self.liveAPI_rerun > 0):
                if self.liveAPI.session is None:
                    if (self.liveAPI_rerun != 1):
                        time.sleep(2.00)
                    self.liveAPI.start()
                    chkTime = time.time()
                    while ((time.time() - chkTime) < 10) and (self.liveAPI.session is None):
                        time.sleep(1.00)
                    self.liveAPI_rerun += 1
            time.sleep(1.00)
            if (self.liveAPI.error_flag == True):
                self.liveAPI_rerun = 0

    # キーボード監視 開始
    def start_kb_listener(self, runMode='assistant',):
        self.shift_l_down = False
        self.shift_r_down = False
        self.last_ctrl_l_time  = 0
        self.last_ctrl_l_count = 0

        # イベントハンドラの登録
        self.last_key_time      = 0
        self.debounce_interval  = 0.05  # 50ミリ秒のデバウンス時間
        self.kb_handler_id = keyboard.hook(self._keyboard_event_handler)

    # イベントハンドラ
    def _keyboard_event_handler(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            # デバウンス期間中は処理をスキップ 
            now_time = time.time()
            if (now_time - self.last_key_time < self.debounce_interval):
                return
            self.last_key_time = now_time
            self.on_press(event)
        elif event.event_type == keyboard.KEY_UP:
            self.on_release(event)

    # キーボード監視 終了
    def stop_kb_listener(self):
        try:
            if (self.kb_handler_id is not None):
                keyboard.unhook(self.kb_handler_id)
                self.kb_handler_id = None
        except Exception as e:
            print(e)

    # キーボードイベント
    def on_press(self, event):
        if (event.name in ["left shift", "shift"]):
            self.shift_l_down = True
        elif (event.name == "right shift"):
            self.shift_r_down = True
        elif (event.name in ["left ctrl", "ctrl"]) \
        and (self.shift_l_down == False) \
        and (self.shift_r_down == False):
            pass
        else:
            self.last_ctrl_l_time  = 0
            self.last_ctrl_l_count = 0

    def on_release(self, event):

        if (event.name in ["left shift", "shift"]):
            self.shift_l_down = False
        elif (event.name == "right shift"):
            self.shift_r_down = False

        # --------------------
        # ctrl_l キー
        # --------------------
        elif (event.name in ["left ctrl", "ctrl"]) \
        and (self.shift_l_down == False) \
        and (self.shift_r_down == False):
            press_time = time.time()
            if ((press_time - self.last_ctrl_l_time) > 1):
                self.last_ctrl_l_time  = press_time
                self.last_ctrl_l_count = 1
            else:
                self.last_ctrl_l_count += 1
                if (self.last_ctrl_l_count < 3):
                    self.last_ctrl_l_time = press_time
                else:
                    self.last_ctrl_l_time  = 0
                    self.last_ctrl_l_count = 0
                    #print("Press ctrl_l x 3 !")

                    # キー操作監視 停止
                    self.stop_kb_listener()

                    # live API クラス
                    if self.liveAPI.session is None:
                        dummy = io_text_write(qIO_liveAiRun, 'run')
                        dummy = io_text_read(qIO_agent2live)
                        #self.liveAPI.start()
                        self.liveAPI.break_flag = False
                        self.liveAPI.error_flag = False
                        self.liveAPI_rerun = 1
                    else:
                        dummy = io_text_read(qIO_liveAiRun)
                        self.liveAPI_rerun = 0
                        self.liveAPI.stop()

                    # キー操作監視 再開
                    self.start_kb_listener()

        # --------------------
        # end キー
        # --------------------
        elif (event.name == "end"):
            self.last_ctrl_l_time  = 0
            self.last_ctrl_l_count = 0

            # キー操作監視 停止
            self.stop_kb_listener()

            # live API クラス
            self.liveAPI_rerun = 0
            if self.liveAPI.session is not None:
                self.liveAPI.stop()

            # キー操作監視 再開
            self.start_kb_listener()

        # --------------------
        # shift + print_screen キー
        # --------------------
        elif (event.name == "print screen") and (self.shift_l_down == True) \
        or   (event.name == "print screen") and (self.shift_r_down == True):
            # live API クラス
            if self.liveAPI.session is not None:
                if (self.liveAPI.image_input_number is None):
                    self.liveAPI.image_input_number = 0
                else:
                    self.liveAPI.image_input_number += 1

        else:
            self.last_ctrl_l_time  = 0
            self.last_ctrl_l_count = 0



class _live_api_freeai:
    def __init__(self, api_key, ):

        # 実行パラメータ
        self.live_models = LIVE_MODELS
        self.live_voices = LIVE_VOICES
        self.live_model = LIVE_MODEL
        self.live_voice = LIVE_VOICE
        self.live_voice_level = 2500
        sec60 = int( (INPUT_RATE/INPUT_CHUNK) * 60) # 60sec
        self.voice_base = [0 for _ in range(sec60)]

        # イメージ送信タイミング
        self.shot_interval_sec = 2      # 送信間隔
        self.clip_interval_sec = 30     # クリップボード送信後のアイドル秒数
        self.shot_last_time = time.time() - self.shot_interval_sec
        self.clip_last_time = time.time() - self.clip_interval_sec

        # API情報
        self.client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1alpha'})

        # 設定
        self.image_send_queue = None
        self.audio_send_queue = None
        self.audio_receive_queue = None
        self.graph_input_queue = None
        self.graph_output_queue = None
        self.break_flag = False
        self.error_flag = False
        self.last_send_time = time.time()
        self.session = None
        self.monjyu_once_flag = False
        self.monjyu_enable = False
        self.monjyu_funcinfo = ''
        self.image_input_number = None

        # バッファ
        self.audio_last_time = time.time()
        self.audio_input_time = None
        self.audio_input_buffer = []
        self.audio_output_time = None
        self.audio_output_buffer = []

        # タスクグループ設定
        self.tg = None

        # イメージショット設定
        self.imageShot = _imageShot_class()

        # main,data,addin,botFunc,mcpHost,
        self.main    = None
        self.data    = None
        self.addin   = None
        self.botFunc = None
        self.mcpHost = None
        self.function_modules = {}

        # monjyu
        self.monjyu = _monjyu_class(runMode='assistant', )

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

    async def input_audio(self):
        vad_count = int( (INPUT_RATE/INPUT_CHUNK) * 2) # 2sec
        input_stream = None
        try:

            # ストリーム設定
            audio_stream = pyaudio.PyAudio()
            #mic_info = audio_stream.get_default_input_device_info()
            input_stream = await asyncio.to_thread(
                audio_stream.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=INPUT_RATE,
                input=True,
                #input_device_index=mic_info["index"],
                frames_per_buffer=INPUT_CHUNK,
            )

            # マイク入力
            last_zero_count = 0
            while (self.session is not None) and (not self.break_flag):
                audio_data = await asyncio.to_thread(input_stream.read, INPUT_CHUNK)
                if audio_data is not None:
                    input_data = np.abs(np.frombuffer(audio_data, dtype=np.int16))
                    data_max = np.max(input_data)
                    del self.voice_base[0]
                    self.voice_base.append(data_max)
                    base_avg = np.average(self.voice_base)
                    if data_max > (base_avg + self.live_voice_level):
                        await self.audio_send_queue.put(audio_data)
                        await self.graph_input_queue.put(audio_data)
                        self.audio_last_time = time.time()
                        if (self.audio_input_time == None):
                            self.audio_input_time = datetime.datetime.now()
                        self.audio_input_buffer.append(audio_data)
                        last_zero_count = 0
                    else:
                        if (time.time() - self.audio_last_time) > ALIVE_BEAT_SEC \
                        or last_zero_count <= vad_count:
                            await self.audio_send_queue.put(audio_data)
                            self.audio_last_time = time.time()
                            if len(self.audio_input_buffer) > 0:
                                if last_zero_count <= 5:
                                    self.audio_input_buffer.append(audio_data)
                                if (last_zero_count == vad_count):
                                    #print('  audio_input_buffer =', len(self.audio_input_buffer))
                                    try:
                                        #self.monjyu.live_audio_input(time_stamp=self.audio_input_time, audio_buffer=self.audio_input_buffer.copy())
                                        input_thread = threading.Thread(
                                            target=self.monjyu.live_audio_input,args=(self.audio_input_time, self.audio_input_buffer.copy()),
                                            daemon=True
                                        )
                                        input_thread.start()
                                    except Exception as e:
                                        print(e)
                                    self.audio_input_time = None
                                    self.audio_input_buffer = []
                            last_zero_count += 1
                        await self.graph_input_queue.put(bytes(INPUT_CHUNK * 2))
                else:
                    await asyncio.sleep(0.01)

        except Exception as e:
            print(f"input_audio: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
            # ストリーム解放
            if input_stream:
                await asyncio.to_thread(input_stream.stop_stream)
                await asyncio.to_thread(input_stream.close)
                await asyncio.to_thread(audio_stream.terminate)
        return True

    async def send_audio(self):
        try:

            # 音声送信
            while (self.session is not None) and (not self.break_flag):
                audio_data = await self.audio_send_queue.get()
                if audio_data is not None:
                    await self.session.send(input={"mime_type": "audio/pcm", "data": audio_data})
                    self.last_send_time = time.time()
                else:
                    await asyncio.sleep(0.01)

        except Exception as e:
            print(f"send_audio: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
        return True

    async def clip_image(self):
        last_image_hash = None
        new_image = ImageGrab.grabclipboard()
        if isinstance(new_image, Image.Image):
            last_image_hash = hashlib.sha256(new_image.tobytes()).hexdigest()
        try:

            # イメージ確認
            while (self.session is not None) and (not self.break_flag):
                try:
                    new_image = ImageGrab.grabclipboard()
                    if isinstance(new_image, Image.Image):
                        image_hash = hashlib.sha256(new_image.tobytes()).hexdigest()
                        if (last_image_hash is None) or (image_hash != last_image_hash):  # 変更確認
                            last_image_hash = image_hash
                            print(" Live(freeai) : [IMAGE] Detected ")

                            # jpeg変換
                            jpeg_io = io.BytesIO()
                            rgb = new_image.convert("RGB")
                            rgb.thumbnail([1024, 1024])
                            rgb.save(jpeg_io, format="jpeg")
                            jpeg_io.seek(0)
                            jpeg_bytes = jpeg_io.read()

                            self.clip_last_time = time.time()
                            await self.image_send_queue.put(jpeg_bytes)
                except:
                    pass
                await asyncio.sleep(0.50)

        except Exception as e:
            print(f"clip_image: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
        return True

    async def input_image(self):
        last_image_hash = None
        try:

            # イメージ確認
            while (self.session is not None) and (not self.break_flag):
                if (self.image_input_number is not None):
                    if self.image_send_queue.empty():

                        if  ((time.time() - self.clip_last_time) > self.clip_interval_sec) \
                        and ((time.time() - self.shot_last_time) > self.shot_interval_sec):

                            try:
                                if (self.image_input_number == 0):
                                    new_image = self.imageShot.screen_shot(screen_number='auto')
                                else:
                                    new_image = self.imageShot.cv2capture(dev=str(self.image_input_number - 1))
                                    if (new_image is None):
                                        self.image_input_number = None
                                        self.visualizer.update_image(None)

                                if new_image is not None:
                                    image_hash = hashlib.sha256(new_image.tobytes()).hexdigest()
                                    if (last_image_hash is None) or (image_hash != last_image_hash):  # 変更確認
                                        last_image_hash = image_hash
                                        #print(" Live(freeai) : [IMAGE] Detected ")

                                        pil_image = self.imageShot.cv2pil(new_image)

                                        # jpeg変換
                                        jpeg_io = io.BytesIO()
                                        rgb = pil_image.convert("RGB")
                                        rgb.thumbnail([1024, 1024])
                                        rgb.save(jpeg_io, format="jpeg")
                                        jpeg_io.seek(0)
                                        jpeg_bytes = jpeg_io.read()

                                        self.shot_last_time = time.time()
                                        await self.image_send_queue.put(jpeg_bytes)
                            except:
                                pass
                await asyncio.sleep(0.25)

        except Exception as e:
            print(f"input_image: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
        return True

    async def send_image(self):
        try:

            # イメージ送信
            while (self.session is not None) and (not self.break_flag):
                jpeg_bytes = await self.image_send_queue.get()
                if jpeg_bytes is not None:
                    print(" Live(freeai) : [IMAGE] Sending... ")
                    await self.session.send(input={"mime_type": "image/jpeg", "data": base64.b64encode(jpeg_bytes).decode()})
                    self.visualizer.update_image(jpeg_bytes)
                    self.last_send_time = time.time()
                else:
                    await asyncio.sleep(0.01)

        except Exception as e:
            print(f"send_image: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
        return True

    async def play_audio(self):
        output_stream = None
        try:

            # ストリーム設定
            audio_stream = pyaudio.PyAudio()
            output_stream = await asyncio.to_thread(
                audio_stream.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=OUTPUT_RATE,
                output=True,
            )

            # 音声再生
            while (self.session is not None) and (not self.break_flag):
                audio_data = await self.audio_receive_queue.get()
                if audio_data is not None:
                    await asyncio.to_thread(output_stream.write, audio_data)
                    await self.graph_output_queue.put(audio_data)
                else:
                    await asyncio.sleep(0.01)

        except Exception as e:
            print(f"play_audio: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
            # ストリーム解放
            if output_stream:
                await asyncio.to_thread(output_stream.stop_stream)
                await asyncio.to_thread(output_stream.close)
                await asyncio.to_thread(audio_stream.terminate)
        return True

    async def agent_result(self, ):
        try:
            # Live実行確認
            while (self.session is not None) and (not self.break_flag):
                text = io_text_read(qIO_agent2live)
                if (text != ''):
                    #request_text = "''' AIエージェントからの実行報告\n"
                    #request_text += text.rstrip() + "\n"
                    #request_text += "'''\n"
                    await self.send_request_async(request_text=text,)
                await asyncio.sleep(0.25)
        except Exception as e:
            print(f"agent_result: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
        return True

    def send_request(self, request_text='',):
        return asyncio.run(self.send_request_async(request_text))

    async def send_request_async(self, request_text='',):
        try:
            if (request_text is not None) and (request_text != ''):
                print(f" User(text): { request_text }")
                if (self.session is not None) and (not self.break_flag):

                    # テキスト送信
                    await self.session.send(input=request_text or ".", end_of_turn=True)
                    self.last_send_time = time.time()

                    try:
                        reqText = request_text
                        inpText = ''
                        #self.monjyu.post_input_log(reqText=reqText, inpText=inpText)
                        thread = threading.Thread(
                            target=self.monjyu.post_input_log,args=(reqText, inpText),
                            daemon=True
                        )
                        thread.start()
                    except Exception as e:
                        print(e)

        except Exception as e:
            print(f"send_request: {e}")
            self.error_flag = True
            return False
        return True

    async def receive_proc(self):
        try:
            while (self.session is not None) and (not self.break_flag):

                async for response in self.session.receive():
                    server_content = response.server_content
                    tool_call = response.tool_call
                    go_away = response.go_away

                    # server_content
                    if server_content is not None:
                        #print('response.server_content ')
                        #res = await self._server_content(server_content)
                        asyncio.create_task( self._server_content(server_content) )
                        #if res == False:
                        #    break

                    # tool_call
                    if tool_call is not None:
                        #print('response.tool_call ')
                        #res = await self._tool_call(tool_call)
                        asyncio.create_task( self._tool_call(tool_call) )
                        #if res == False:
                        #    break

                    # 例外レスポンス
                    if  server_content is None \
                    and tool_call is None:

                        if go_away is not None:
                            print(f" Live(freeai) : [GO_AWAY] { go_away }")
                            self.error_flag = False  # 自動復帰のためエラー解除にしておく
                            break
                        else:
                            print('response ???')
                            print(response)

        except Exception as e:
            if ("received 1011" in str(e)):
                print(f" Live(freeai) : [DISCONNECT] ")
            else:
                print(f"receive_proc: {e}")
                self.error_flag = True
        finally:
            self.break_flag = True
        return True

    async def _server_content(self, server_content):
        try:
            model_turn = server_content.model_turn
            turn_complete = server_content.turn_complete
            interrupted = server_content.interrupted
            generation_complete = server_content.generation_complete

            # model_turn
            if model_turn is not None:
                parts = model_turn.parts
                for part in parts:
                    if part.text is not None:
                        print(part.text, end="")
                    elif part.inline_data is not None:
                        audio_data = part.inline_data.data
                        await self.audio_receive_queue.put(audio_data)
                        if (self.audio_output_time == None):
                            self.audio_output_time = datetime.datetime.now()
                        self.audio_output_buffer.append(audio_data)
                    elif part.executable_code is not None:
                        executable_code = part.executable_code.code
                        #print(executable_code)
                    elif part.code_execution_result is not None:
                        output = part.code_execution_result.output
                        #print(output)
                    else:
                        # 例外レスポンス parts
                        print('server_content.model_turn.parts [ ??? ]')
                        print(part)

            # turn_complete = True
            if turn_complete:
                #print('server_content.turn_complete = True ')
                if len(self.audio_output_buffer) > 0:
                    #print('  audio_output_buffer =', len(self.audio_output_buffer))
                    try:
                        #self.monjyu.live_audio_output(
                        # time_stamp=self.audio_output_time,
                        # audio_buffer=self.audio_output_buffer.copy()
                        # out_model=self.live_model)
                        output_thread = threading.Thread(
                            target=self.monjyu.live_audio_output,args=(self.audio_output_time, self.audio_output_buffer.copy(), self.live_model),
                            daemon=True
                        )
                        output_thread.start()
                    except Exception as e:
                        print(e)
                    self.audio_output_time = None
                    self.audio_output_buffer = []
                #while not self.audio_receive_queue.empty():
                #    await self.audio_receive_queue.get()

            # 例外レスポンス server_content
            if  model_turn is None \
            and not turn_complete:

                # interrupted = True
                if interrupted:
                    print(' server_content.interrupted !')
                    while not self.audio_receive_queue.empty():
                        await self.audio_receive_queue.get()
                    #if not self.graph_output_queue.empty():
                    #    self.graph_output_queue.queue.clear()
                    self.audio_output_time = None
                    self.audio_output_buffer = []

                # generation_complete = True
                elif generation_complete:
                    print(' server_content.generation_complete !')

                else:
                    print(' server_content.??? ')
                    print(server_content)

        except Exception as e:
            print(f"_server_content: {e}")
            self.error_flag = True
            return False
        return True

    async def _tool_call(self, tool_call):
        try:
            print()
            for fc in tool_call.function_calls:
                #print(fc)

                f_id = fc.id
                f_name = fc.name
                f_kwargs = json.dumps(fc.args, ensure_ascii=False, )
                #print(f_id, f_name)
                #print(f_kwargs)
                hit = False

                if len(self.function_modules) > 0:
                    for module_dic in self.function_modules.values():
                        if (f_name == module_dic['func_name']):

                            hit = True
                            print(f" Live(freeai) :   function_call '{ module_dic['script'] }' ({ f_name })")
                            print(f" Live(freeai) :   → { f_kwargs }")

                            # function 実行
                            try:
                                ext_func_proc = module_dic['func_proc']
                                if (module_dic['script'] != 'mcp'):
                                    res_json = ext_func_proc(f_kwargs)
                                else:
                                    res_json = ext_func_proc(f_name, f_kwargs)
                            except Exception as e:
                                print(e)
                                # エラーメッセージ
                                dic = {}
                                dic['error'] = e 
                                res_json = json.dumps(dic, ensure_ascii=False, )

                            # tool_result
                            #print(f" Live(freeai) :   → { res_json }")
                            #print()

                            # 通常返信
                            tool_response = types.LiveClientToolResponse(
                                function_responses=[types.FunctionResponse(
                                    name=f_name,
                                    id=f_id,
                                    response=json.loads(res_json),
                                )]
                            )
                            await self.session.send(input=tool_response)

                if hit == False:
                            # Not Found 返信
                            tool_response = types.LiveClientToolResponse(
                                function_responses=[types.FunctionResponse(
                                    name=f_name,
                                    id=f_id,
                                    response={'result':'error'},
                                )]
                            )
                            await self.session.send(input=tool_response)

        except Exception as e:
            print(f"_tool_call: {e}")
            self.error_flag = True
            return False
        return True

    def start(self):
        return asyncio.run( self.start_async() )

    async def start_async(self):
        self.break_flag = False
        self.error_flag = False
        self.last_send_time = time.time()
        self.image_input_number = None
        # UI設定
        if self.data is not None:
            live_model = self.data.live_setting['freeai'].get('live_model', '')
            live_voice = self.data.live_setting['freeai'].get('live_voice', '')
            shot_interval_sec = self.data.live_setting['freeai'].get('shot_interval_sec', str(self.shot_interval_sec))
            clip_interval_sec = self.data.live_setting['freeai'].get('clip_interval_sec', str(self.clip_interval_sec))
            if live_model != '':
                self.live_model = live_model
            if live_voice != '':
                self.live_voice = live_voice
            if (shot_interval_sec != ''):
                self.shot_interval_sec = int(shot_interval_sec)
            if (clip_interval_sec != ''):
                self.clip_interval_sec = int(clip_interval_sec)
        print(f" Live(freeai) : [START] ({ self.live_model }) ")

        # function_modules 設定
        self.function_modules = {}
        if (self.botFunc is not None):
            self.function_modules = self.botFunc.function_modules
        # mcp tools 設定
        if (self.mcpHost is not None):
            mcp_modules = self.mcpHost.get_mcp_modules()
            for key, mcp_module in mcp_modules.items():
                self.function_modules[key] = mcp_module

        # Monjyu 確認
        if (self.monjyu_once_flag == False):
            self.monjyu_once_flag = True
            self.monjyu_enable = False
            self.monjyu_funcinfo = ''
            # 有効確認
            if len(self.function_modules) > 0:
                module_dic = self.function_modules.get('execute_monjyu_request', None)
                if (module_dic is not None):

                    # Monjyu function 実行
                    self.monjyu_enable = True
                    print(f" Live(freeai) : [INIT] (execute_monjyu_request) ")
                    # 受付音
                    self.play(outFile='_sounds/_sound_accept.mp3')
                    # function 実行
                    dic = {}
                    dic['runMode'] = 'chat' #ここは'chat'で内部的に問い合わせる
                    dic['userId'] = 'live'
                    dic['reqText'] = '利用できるFunctions(Tools)と機能内容を要約して報告してください'
                    f_kwargs = json.dumps(dic, ensure_ascii=False, )
                    try:
                        ext_func_proc = module_dic['func_proc']
                        res_json = ext_func_proc( f_kwargs )
                        res_dic = json.loads(res_json)
                        res_text = res_dic.get('result_text','')
                        res_text = res_text.replace('`', '"')
                        #print(res_text)
                        self.monjyu_funcinfo = res_text
                    except Exception as e:
                        print(e)

        # 初期化
        self.image_send_queue = asyncio.Queue()
        self.audio_send_queue = asyncio.Queue()
        self.audio_receive_queue = asyncio.Queue()
        self.graph_input_queue = asyncio.Queue()
        self.graph_output_queue = asyncio.Queue()
        # バッファ
        self.audio_input_time = None
        self.audio_input_buffer = []
        self.audio_output_time = None
        self.audio_output_buffer = []
        # スレッド処理
        def main_thread():
            try:
                # visualizer開始
                self.visualizer = _visualizer_class()
                self.visualizer.api_instance = self  # 自身への参照を追加
                asyncio.run(self._main())
                # visualizer停止
                self.visualizer.root.quit()
                self.visualizer.root.destroy()
            except Exception as e:
                #print(f"main_thread: {e}")
                pass
            finally:
                self.break_flag = True
                print(f" Live(freeai) : [END] ")
        # 起動
        self.main_task = threading.Thread(target=main_thread, daemon=True)
        self.main_task.start()
        return True

    def stop(self):
        return asyncio.run( self.stop_async() )

    async def stop_async(self):
        print(" Live(freeai) : [STOP] ")
        # 停止
        self.break_flag = True
        try:
            if self.tg is not None:
                for t in self.tg._tasks:
                    t.cancel()
        except:
            pass
        self.tg = None
        self.main_task.join()
        return True

    async def _main(self):
        try:
            # 起動
            if (self.session is None):

                # voice 設定
                live_voice = self.live_voice
                print(f" Live(freeai) : [VOICE] { live_voice } ")

                instructions = \
"""
あなたは美しい日本語を話す賢いアシスタントです。
あなたはLiveAPI(RealtimeAPI)で実行中のアシスタントです。
あなたの名前は「力/RiKi(りき)」です。
複数人で会話をしていますので、会話の流れを把握するようにして、口出しは最小限にお願いします。
あなたへの指示でない場合、相槌も必要ありません。できるだけ静かにお願いします。
"""
                # Monjyu 有効
                if (self.monjyu_enable == True):
                    print(" Live(freeai) : [READY] 外部AI Monjyu(もんじゅ:execute_monjyu_request) ")
                    instructions += \
"""
外部AI Monjyu(もんじゅ:execute_monjyu_request) が利用可能です。
利用指示があった場合、Monjyu(もんじゅ) をRunMode='voice'で呼び出すことで、適切なFunctions(Tools)を間接的に利用して、その結果を報告してください。
"""
                    if (self.monjyu_funcinfo != ''):
                        instructions += '\n【外部AI Monjyu(もんじゅ:execute_monjyu_request) 経由で利用可能なFunctions(Tools)の情報】\n'
                        instructions += self.monjyu_funcinfo

                # ツール設定 通常はexecute_monjyu_requestのみ有効として処理
                tools = []
                tools.append({"google_search": {}, })

                if (self.live_model.lower().find('thinking') < 0):
                    tools.append({"code_execution": {}, })

                    function_declarations = []
                    if len(self.function_modules) > 0:
                        for module_name, module_dic in self.function_modules.items():
                            set_flag = 'ng'
                            if (self.monjyu_enable == True):
                                #if (module_dic['func_name'] == 'execute_monjyu_request') \
                                #or (module_dic['script'] == 'mcp'):
                                if (module_dic['func_name'] == 'execute_monjyu_request'):
                                    set_flag = 'ok'
                            else:
                                    set_flag = 'ok'

                            if (set_flag == 'ok'):
                                func_dic = module_dic['function']
                                not_support = False
                                properties = func_dic['parameters'].get('properties', {})
                                for field in properties:
                                    if properties[field]['type'] in ['array', 'boolean']:
                                        not_support = True
                                if not_support == False:
                                    function_declarations.append(func_dic)
                                    #print(func_dic)

                    if (len(function_declarations) > 0):
                        tools.append({"function_declarations": function_declarations})
            
                # config 設定
                speech_config = types.LiveConnectConfig(
                            response_modalities=["AUDIO"],
                            speech_config=types.SpeechConfig(
                                language_code="ja-JP",
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self.live_voice)
                                )
                            ),
                        )
                config =    {   "generation_config": speech_config,
                                "system_instruction": types.Content(
                                    parts=  [ types.Part(
                                                text=instructions
                                            )]
                                    ),
                                "tools": tools,
                            }

                # Live 実行
                #session = await self.client.aio.live.connect(model=self.live_model, config=config)
                #tg = asyncio.TaskGroup()
                async with (
                    self.client.aio.live.connect(model=self.live_model, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    # 開始音
                    self.play(outFile='_sounds/_sound_up.mp3')

                    self.session = session
                    self.tg = tg

                    def cleanup(task):
                        self.break_flag = True
                        try:
                            if self.tg is not None:
                                for t in self.tg._tasks:
                                    t.cancel()
                        except:
                            pass
                        self.tg = None

                    # タスクの作成
                    self.tg.create_task(self.clip_image())
                    self.tg.create_task(self.input_image())
                    self.tg.create_task(self.send_image())
                    self.tg.create_task(self.input_audio())
                    self.tg.create_task(self.send_audio())
                    self.tg.create_task(self.play_audio())
                    self.tg.create_task(self.agent_result())
                    self.tg.create_task(self.receive_proc())
                    self.tg.create_task(self.visualizer_update())

                    for t in self.tg._tasks:
                        t.add_done_callback(cleanup)

                    # 待機
                    print(" Live(freeai) : [INFO] Shift+PrtScrn to start/stop screen capture. ")
                    print(" Live(freeai) : [RUN]  Waiting... ")
                    while (not self.break_flag):
                        await asyncio.sleep(0.10)

        except Exception as e:
            print(f"_main: {e}")
            self.error_flag = True
        finally:
            self.break_flag = True
            self.session = None

        # 終了音
        self.play(outFile='_sounds/_sound_down.mp3')
        return True

    async def visualizer_update(self):
        self.inp_flag = False
        self.inp_zero = True
        self.out_flag = False
        self.out_zero = True
        try:

            # グラフ更新
            while (self.session is not None) and (not self.break_flag):

                if not self.graph_input_queue.empty():
                    input_data = await self.graph_input_queue.get()
                    self.visualizer.update_value(input_chunk=input_data)
                    self.inp_flag = True
                    self.inp_zero = False
                else:
                    self.visualizer.update_value(input_chunk=bytes(INPUT_CHUNK * 2))
                    if (self.inp_zero == False):
                        self.inp_flag = True
                        self.inp_zero = True

                if not self.graph_output_queue.empty():
                    output_data = await self.graph_output_queue.get()
                    self.visualizer.update_value(output_chunk=output_data)
                    self.out_flag = True
                    self.out_zero = False
                else:
                    self.visualizer.update_value(output_chunk=bytes(OUTPUT_CHUNK * 2))
                    if (self.out_zero == False):
                        self.out_flag = True
                        self.out_zero = True

                if (self.inp_flag == True) or (self.out_flag == True):
                    self.visualizer.update_graph()
                await asyncio.sleep(0.01)

        except Exception as e:
            print(f"visualizer_update: {e}")
            #self.error_flag = True
        finally:
            self.break_flag = True
        return True



class _imageShot_class:
    def __init__(self):
        pass

    def screen_shot(self, screen_number='auto', ):
        cv_img   = None

        # 全画面
        if (str(screen_number) == 'all'):
            try:
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )
                cv_img   = cv_image.copy()
            except:
                time.sleep(0.50)
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )
                cv_img   = cv_image.copy()

        # マルチ画面 切り出し
        else:
            try:
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )
            except:
                time.sleep(0.50)
                pil_img  = ImageGrab.grab(all_screens=True,)
                cv_image = self.pil2cv(pil_image=pil_img, )

            # スクリーン指定確認
            if (str(screen_number).isdigit()):
                if (int(screen_number) < 0) \
                or (int(screen_number) >= len(screeninfo.get_monitors())):
                    screen_number = 'auto'

            # 全スクリーンの配置
            min_left     = 0
            min_top      = 0
            max_right    = 0
            max_buttom   = 0
            for s in screeninfo.get_monitors():
                if (s.x < min_left):
                    min_left = s.x
                if (s.y  < min_top):
                    min_top = s.y
                if ((s.x+s.width) > max_right):
                    max_right = (s.x+s.width)
                if ((s.y+s.height) > max_buttom):
                    max_buttom = (s.y+s.height)

            # マウス配置
            (mouse_x,mouse_y) = pyautogui.position()

            # 画像切り出し
            screen = -1
            for s in screeninfo.get_monitors():
                screen += 1

                # 処理スクリーン？
                flag = False
                if (str(screen_number).isdigit()):
                    if (int(screen_number) == screen):
                        flag = True
                else:
                    if  (mouse_x >= s.x) and (mouse_x <= (s.x+s.width)) \
                    and (mouse_y >= s.y) and (mouse_y <= (s.y+s.height)):
                        flag = True

                # 切り出し
                if (flag == True):
                    left = s.x - min_left
                    top  = s.y - min_top

                    cv_img = np.zeros((s.height, s.width, 3), np.uint8)
                    cv_img[ 0:s.height, 0:s.width ] = cv_image[ top:top+s.height, left:left+s.width ]

        # 戻り値
        return cv_img

    def cv2capture(self, dev='0', ):
        image   = None

        # オープン
        try:
            if (os.name != 'nt'):
                cv2video = cv2.VideoCapture(int(dev))
            else:
                cv2video = cv2.VideoCapture(int(dev), cv2.CAP_DSHOW)
        except:
            return image

        # 取り込み
        try:
            ret, image = cv2video.read()
        except Exception as e:
            ret = False
            image = None

        # クローズ
        finally:
            cv2video.release()

        return image

    def pil2cv(self, pil_image=None):
        try:
            cv2_image = np.array(pil_image, dtype=np.uint8)
            if (cv2_image.ndim == 2):  # モノクロ
                pass
            elif (cv2_image.shape[2] == 3):  # カラー
                cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)
            elif (cv2_image.shape[2] == 4):  # 透過
                cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGBA2BGRA)
            return cv2_image
        except:
            pass
        return None

    def cv2pil(self, cv2_image=None):
        try:
            wrk_image = cv2_image.copy()
            if (wrk_image.ndim == 2):  # モノクロ
                pass
            elif (wrk_image.shape[2] == 3):  # カラー
                wrk_image = cv2.cvtColor(wrk_image, cv2.COLOR_BGR2RGB)
            elif (wrk_image.shape[2] == 4):  # 透過
                wrk_image = cv2.cvtColor(wrk_image, cv2.COLOR_BGRA2RGBA)
            pil_image = Image.fromarray(wrk_image)
            return pil_image
        except:
            pass
        return None



class _visualizer_class:

    def __init__(self):
        # 左側モニター
        monitor = screeninfo.get_monitors()[0] #left monitor
        left, top = monitor.x + monitor.width - 512 - 50, monitor.y + monitor.height - 256 - 90
        # tk
        self.root = tk.Tk()
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)
        self.root.geometry(f"512x256+{ left }+{ top }")
        self.root.title("Visualizer (freeai)")
        
        # ウィンドウクローズイベントのハンドラを追加
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
                
        # グラフ用のフレーム作成
        self.frame = ttk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky="nsew")

        # 画像用のキャンバス無効
        self.img_canvas = None

        # グラフの初期化を直接実行
        self.initialize_plot()
        
    def initialize_plot(self):
        # Matplotlibのfigure作成（サイズを512x256に修正）
        self.fig, self.ax = plt.subplots(1, 1, figsize=(5.12,2.56))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # グラフの初期設定
        self.ax.set_title('Audio Level')

        # 背景を黒に設定
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')

        # グリッド線と軸の色を設定
        self.ax.grid(True, color='gray')
        self.ax.tick_params(colors='white',axis='y') # y軸のみ表示
        for spine in self.ax.spines.values():
            spine.set_color('white')
        
        # タイトルの色を白に
        self.ax.set_title('Audio Level', color='white')
        
        # 入力を赤、出力を青の棒グラフに設定
        self.line1, = self.ax.plot([], [], 'r', drawstyle='steps-pre', label='Input')  # 赤色
        self.line2, = self.ax.plot([], [], 'b', drawstyle='steps-pre', label='Output')  # 青色
        
        # Y軸の範囲設定（絶対値を100分率表示）
        self.ax.set_ylim(0, 100)
        
        # X軸の表示を消す
        self.ax.set_xticks([])
        
        # Y軸のラベルを追加
        self.ax.set_ylabel('Level (%)', color='white')
        
        # 凡例を表示
        self.ax.legend(loc='upper right', facecolor='black', labelcolor='white')
        
        # データバッファ
        self.input_data = []
        self.output_data = []

    def on_closing(self):
        pyautogui.keyDown('end')
        pyautogui.keyUp('end')
        if hasattr(self, 'api_instance'):
            self.api_instance.break_flag = True
            
    def update_value(self, input_chunk=None, output_chunk=None):
        # 入力波形
        if input_chunk is not None:
            # 絶対値に変換
            input_data = np.abs( np.frombuffer(input_chunk, dtype=np.int16) )
            # 最初のINPUT_CHUNKバイトを有効に
            if (len(input_data) > INPUT_CHUNK):
                 input_data = input_data[:INPUT_CHUNK]
            # バイト数がINPUT_CHUNK未満の場合
            elif (len(input_data) < INPUT_CHUNK):
                input_data = np.pad(input_data, (0, (INPUT_CHUNK - len(input_data))), 'constant')
            # 最大値に対する100分率に変換
            max_val = np.max(input_data)
            if max_val > 0:  # ゼロ除算を防ぐ
                input_data = (input_data / max_val) * 100
            self.input_data = input_data
            self.line1.set_data(range(len(input_data)), input_data)
            self.ax.set_xlim(0, len(input_data))

        # 出力波形
        if output_chunk is not None:
            # 絶対値に変換
            output_data = np.abs( np.frombuffer(output_chunk, dtype=np.int16) )
            # 最初のOUTPUT_CHUNKバイトを有効に
            if (len(output_data) > OUTPUT_CHUNK):
                 output_data = output_data[:OUTPUT_CHUNK]
            # バイト数がOUTPUT_CHUNK未満の場合
            elif (len(output_data) < OUTPUT_CHUNK):
                output_data = np.pad(output_data, (0, (OUTPUT_CHUNK - len(output_data))), 'constant')
            # 最大値に対する100分率に変換
            max_val = np.max(output_data)
            if max_val > 0:  # ゼロ除算を防ぐ
                output_data = (output_data / max_val) * 100
            self.output_data = output_data
            self.line2.set_data(range(len(output_data)), output_data)
            self.ax.set_xlim(0, len(output_data))

    def update_image(self, jpeg_bytes):
        if (jpeg_bytes is None):
            if self.img_canvas is not None:
                try:
                    # キャンバスの内容をクリアして削除
                    self.img_canvas.delete("all")
                    self.img_canvas.place_forget()
                    self.img_canvas = None
                except Exception as e:
                    print(f"update image: {e}")
            return True

        try:
            # JPEGバイト列からPIL Imageを作成
            image = Image.open(io.BytesIO(jpeg_bytes))

            # 画像用のキャンバス作成
            if self.img_canvas is None:
                self.img_canvas = tk.Canvas(self.root, bg="black")
                self.img_canvas.place(relx=1.0, rely=1.0, anchor="se")
                self.canvas.draw()
                self.root.update()

            # ウィンドウサイズを更新
            max_width = int(self.root.winfo_width() / 2)
            max_height = int(self.root.winfo_height() / 2)
            
            # ウィンドウサイズが取得できた場合のみリサイズ
            if max_width > 0 and max_height > 0:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS) # 必要に応じてImage.LANCZOSに変更
            
            # PIL ImageからPhotoImageを作成
            self.img_photo = ImageTk.PhotoImage(image)
            
            # キャンバスに画像を追加
            self.img_canvas.config(width=image.width, height=image.height)
            
            # 画像を右下に配置
            self.img_canvas.create_image(0, 0, image=self.img_photo, anchor="nw")
            
        except Exception as e:
            print(f"updating image: {e}")
        return True

    def update_graph(self):
        try:
            self.canvas.draw()
            self.root.update()
        except:
            pass



class _monjyu_class:
    def __init__(self, runMode='assistant' ):
        self.runMode = runMode

        # フォルダ
        self.path = 'temp/live_work/'
        if (not os.path.isdir(self.path)):
            os.makedirs(self.path)

        # ポート設定等
        self.core_port2 = str(int(CORE_PORT) + 2)
        self.core_port3 = str(int(CORE_PORT) + 3)
        self.local_endpoint2 = f'http://localhost:{ self.core_port2 }'
        self.local_endpoint3 = f'http://localhost:{ self.core_port3 }'
        self.user_id = 'admin'

        # 履歴送信用
        self.last_reqText = ''
        self.last_inpText = ''
        self.last_outText = ''
        self.last_outData = ''

    def live_audio_input(self, time_stamp=None, audio_buffer=[], ):
        if (len(audio_buffer) == 0):
            return False
        if (time_stamp is None):
            time_stamp = datetime.datetime.now()
        filename = self.path + time_stamp.strftime('%Y%m%d.%H%M%S') + '.live.input.wav'

        try:
            waveFile = wave.open(filename, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(2) #16bit
            waveFile.setframerate(INPUT_RATE)
            waveFile.writeframes(b''.join(audio_buffer))
            waveFile.close()
        except Exception as e:
            print(f"live_audio_input: {e}")
            return False

        try:
            recognize_text = ''
            srr  = sr.Recognizer()
            audiodata  = sr.AudioData(b''.join(audio_buffer), INPUT_RATE, 2)
            recognize_text = srr.recognize_google(audiodata, language='ja')
        except Exception as e:
            #print(f"live_audio_input: {e}")
            recognize_text = ''
        
        if (recognize_text.strip() == ''):
            try:
                os.remove(filename)
            except:
                pass
            return False
        
        recognize_text = recognize_text.strip()
        print(f" Live(freeai) : (user) { recognize_text } ")
        return self.post_input_log(reqText=recognize_text, inpText='')

    def live_audio_output(self, time_stamp=None, audio_buffer=[], out_model=None, ):
        if (len(audio_buffer) == 0):
            return False
        if (time_stamp is None):
            time_stamp = datetime.datetime.now()
        filename = self.path + time_stamp.strftime('%Y%m%d.%H%M%S') + '.live.output.wav'

        try:
            waveFile = wave.open(filename, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(2) #16bit
            waveFile.setframerate(OUTPUT_RATE)
            waveFile.writeframes(b''.join(audio_buffer))
            waveFile.close()
        except Exception as e:
            print(f"live_audio_output: {e}")
            return False

        try:
            recognize_text = ''
            srr  = sr.Recognizer()
            audiodata  = sr.AudioData(b''.join(audio_buffer), OUTPUT_RATE, 2)
            recognize_text = srr.recognize_google(audiodata, language='ja')
        except Exception as e:
            #print(f"live_audio_input: {e}")
            return False
        
        if (recognize_text.strip() == ''):
            return False
        
        # 入力音声変換待機 最大3秒+1秒
        chkTime = time.time()
        while (self.last_reqText == '') and ((time.time() - chkTime) < 3):
            time.sleep(0.25)
        time.sleep(1.00)

        recognize_text = recognize_text.strip()
        print(f" Live(freeai) : { recognize_text } ")
        if (out_model is not None):
            outText = f"[Live] ({ out_model })\n" + recognize_text
        else:
            outText = f"[Live]\n" + recognize_text
        res = self.post_output_log(outText=outText, outData=outText)
        if (res != True):
            return False
        else:
            return self.post_histories()

    def post_input_log(self, reqText='', inpText=''):
        self.last_reqText = reqText
        self.last_inpText = inpText
        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint2 + '/post_input_log',
                json={'user_id': self.user_id, 
                      'request_text': reqText,
                      'input_text': inpText, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                print('error', f"Error response ({ self.core_port2 }/post_input_log) : {response.status_code} - {response.text}")
        except Exception as e:
            print('error', f"Error communicating ({ self.core_port2 }/post_input_log) : {e}")
            return False
        return True

    def post_output_log(self, outText='', outData=''):
        self.last_outText = outText
        self.last_outData = outData
        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint3 + '/post_output_log',
                json={'user_id': self.user_id, 
                      'output_text': outText,
                      'output_data': outData, },
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                print('error', f"Error response ({ self.core_port3 }/post_output_log) : {response.status_code} - {response.text}")
        except Exception as e:
            print('error', f"Error communicating ({ self.core_port3 }/post_output_log) : {e}")
            return False
        return True

    def post_histories(self):
        # AI要求送信
        try:
            response = requests.post(
                self.local_endpoint3 + '/post_histories',
                json={'user_id': self.user_id, 'from_port': "live", 'to_port': "live",
                      'req_mode': "live",
                      'system_text': "", 'request_text': self.last_reqText, 'input_text': self.last_inpText,
                      'result_savepath': "", 'result_schema': "",
                      'output_text': self.last_outText, 'output_data': self.last_outData,
                      'output_path': "", 'output_files': [],
                      'status': "READY"},
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT)
            )
            if response.status_code != 200:
                print('error', f"Error response ({ self.core_port3 }/post_histories) : {response.status_code} - {response.text}")
        except Exception as e:
            print('error', f"Error communicating ({ self.core_port3 }/post_histories) : {e}")
            self.last_reqText = ''
            self.last_inpText = ''
            self.last_outText = ''
            self.last_outData = ''
            return False

        self.last_reqText = ''
        self.last_inpText = ''
        self.last_outText = ''
        self.last_outData = ''
        return True



class _class:

    def __init__(self, ):
        self.version   = "v0"
        self.func_name = "extension_UI_key2Live_freeai"
        self.func_ver  = "v0.20241215"
        self.func_auth = "h0MmuBSfyHFVSPQ+uqVSZLedZDYu9tr2O6EXUhHJ+hwDwrMGiDGqDTlC4v4DSj2G"
        self.function  = {
            "name": self.func_name,
            "description": "拡張ＵＩ_キー(ctrl-l)連打で、LiveAPI(RealTimeAPI)でfreeaiとの会話を起動または停止する。",
            "parameters": {
                "type": "object",
                "properties": {
                    "runMode": {
                        "type": "string",
                        "description": "実行モード 例) assistant"
                    },
                    "reqText": {
                        "type": "string",
                        "description": "要求文字列 例) おはようございます"
                    },
                },
                "required": ["runMode"]
            }
        }

        # 設定
        self.runMode = 'assistant'

        # キーボード監視 開始
        self.sub_proc = _key2Action(runMode=self.runMode, )

        # 初期化
        self.func_reset()

    def func_reset(self, main=None, data=None, addin=None, botFunc=None, mcpHost=None, ):
        if (main is not None):
            self.sub_proc.liveAPI.main = main
        if (data is not None):
            self.sub_proc.liveAPI.data = data
        if (addin is not None):
            self.sub_proc.liveAPI.addin = addin
        if (botFunc is not None):
            self.sub_proc.liveAPI.botFunc = botFunc
        if (mcpHost is not None):
            self.sub_proc.liveAPI.mcpHost = mcpHost
        return True

    def func_proc(self, json_kwargs=None, ):
        #print(json_kwargs)

        # 引数
        runMode = None
        reqText = None
        if (json_kwargs is not None):
            args_dic = json.loads(json_kwargs)
            runMode = args_dic.get('runMode')
            reqText = args_dic.get('reqText')

        if (runMode is None) or (runMode == ''):
            runMode = self.runMode
        else:
            self.runMode = runMode

        # 処理
        if (reqText != ''):
            if self.sub_proc.liveAPI.session is None:
                self.sub_proc.liveAPI.start()
                time.sleep(5.00)
            self.sub_proc.liveAPI.send_request(request_text=reqText, )

        # 戻り
        dic = {}
        dic['result'] = "ok"
        json_dump = json.dumps(dic, ensure_ascii=False, )
        #print('  --> ', json_dump)
        return json_dump

if __name__ == '__main__':

    ext = _class()
    api_key = ext.sub_proc.freeai_key_id

    #liveAPI = _live_api_freeai(api_key, )
    #liveAPI.start()
    #time.sleep(5)
    #liveAPI.send_request(request_text='日本語で話してください')
    #time.sleep(30)
    #liveAPI.stop()
    #time.sleep(5)
    #liveAPI.start()
    #time.sleep(10)
    #liveAPI.stop()


    #ext = _class()
    print(ext.func_proc('{ "runMode" : "assistant", "reqText" : "" }'))

    time.sleep(2)

    print(ext.func_proc('{ "runMode" : "assistant", "reqText" : "おはようございます" }'))

    time.sleep(180)


