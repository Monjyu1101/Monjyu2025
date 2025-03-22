import requests
import json
from playsound3 import playsound

def voicevox_speech(text, speaker=1):
    # 音声合成用のクエリを作成
    query_payload = {"text": text, "speaker": speaker}
    query_response = requests.post("http://localhost:50021/audio_query", params=query_payload)
    
    # 音声合成
    synthesis_payload = {"speaker": speaker}
    synthesis_response = requests.post(
        "http://localhost:50021/synthesis",
        headers={"Content-Type": "application/json"},
        params=synthesis_payload,
        data=json.dumps(query_response.json())
    )
    
    # 音声ファイルを保存
    with open("output.wav", "wb") as f:
        f.write(synthesis_response.content)
    
    # 音声を再生
    playsound(sound="output.wav", block=True, )

# 使用例
voicevox_speech("こんにちは、ずんだもんです")

