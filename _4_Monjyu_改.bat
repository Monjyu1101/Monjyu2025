@ECHO OFF
REM ------------------------------------------------
REM COPYRIGHT (C) 2014-2025 Mitsuo KONDOU.
REM This software is released under the MIT License.
REM https://github.com/konsan1101
REM Thank you for keeping the rules.
REM ------------------------------------------------

rem cd ".."

ECHO; ワーク削除
IF EXIST "build"        RD "build"        /s /q
IF EXIST "dist"         RD "dist"         /s /q
IF EXIST "__pycache__"  RD "__pycache__"  /s /q
PAUSE



ECHO;
ECHO -----
ECHO tools
ECHO -----
rem           pip  install --upgrade pip
    python -m pip  install --upgrade pip
    python -m pip  install --upgrade wheel
    python -m pip  install --upgrade setuptools
    python -m pip  install --upgrade pyinstaller

ECHO;
ECHO -------
ECHO etc
ECHO -------
    python -m pip  install --upgrade keyboard
rem python -m pip  install --upgrade mouse 使用禁止
    python -m pip  install --upgrade screeninfo
    python -m pip  install --upgrade pyautogui
    python -m pip  install --upgrade pywin32
    python -m pip  install --upgrade comtypes
    python -m pip  install --upgrade psutil
    python -m pip  install --upgrade rainbow-logging-handler
    python -m pip  install --upgrade pycryptodome
rem python -m pip  install --upgrade pygame
    python -m pip  install --upgrade playsound3
rem python -m pip  install --upgrade pynput 使用禁止!

    python -m pip  install --upgrade numpy
rem python -m pip  install --upgrade numpy==2.0.2
rem python -m pip  install --upgrade numpy==2.2.0
rem python -m pip  install --upgrade opencv-python
rem python -m pip  install --upgrade opencv-contrib-python
rem python -m pip  install --upgrade opencv-python==4.9.0.80
rem python -m pip  install --upgrade opencv-contrib-python==4.9.0.80
    python -m pip  install --upgrade opencv-python==4.10.0.84
    python -m pip  install --upgrade opencv-contrib-python==4.10.0.84

rem python -m pip  install --upgrade pysimplegui
    python -m pip  install --upgrade pillow
    python -m pip  install --upgrade flask
    python -m pip  install --upgrade fastapi
    python -m pip  install --upgrade uvicorn
    python -m pip  install --upgrade chardet
    python -m pip  install --upgrade python-multipart

    python -m pip  install --upgrade httpx
    python -m pip  install --upgrade websockets
    python -m pip  install --upgrade tiktoken
    python -m pip  install --upgrade openai
    python -m pip  install --upgrade anthropic
    python -m pip  install --upgrade google.generativeai
    python -m pip  install --upgrade google.genai
    python -m pip  install --upgrade ollama
    python -m pip  install --upgrade groq

rem    python -m pip  install --upgrade langchain
rem    python -m pip  install --upgrade codeinterpreterapi
rem    python -m pip  install --upgrade jupyter
rem    python -m pip  install --upgrade jupyter-kernel-gateway

    python -m pip  install --upgrade pyperclip
    python -m pip  install --upgrade websocket
    python -m pip  install --upgrade selenium
    python -m pip  install --upgrade webdriver-manager
    python -m pip  install --upgrade bs4
    python -m pip  install --upgrade pdfminer.six
    python -m pip  install --upgrade winocr
    python -m pip  install --upgrade pytesseract
rem python -m pip  install --upgrade wave
rem python -m pip  install --upgrade chardet
rem python -m pip  install --upgrade botocore

    python -m pip  install --upgrade pandas
    python -m pip  install --upgrade openpyxl
    python -m pip  install --upgrade pyodbc
    python -m pip  install --upgrade sqlalchemy
    python -m pip  install --upgrade matplotlib
    python -m pip  install --upgrade seaborn

    python -m pip  install --upgrade gtts
    python -m pip  uninstall -y gtts-token
    python -m pip  install --upgrade gtts-token
rem python -m pip  install --upgrade googletrans
    python -m pip  install --upgrade goslate
    python -m pip  install --upgrade ggtrans

    python -m pip  install --upgrade pyaudio
    python -m pip  install --upgrade speechrecognition



ECHO;
ECHO -------
ECHO compile
ECHO -------

set pyname=RiKi_Monjyu
    echo;
    echo %pyname%.py
       pyinstaller %pyname%.py  -F --log-level ERROR --icon="_icons/%pyname%.ico"

IF EXIST "dist\%pyname%.exe"  ECHO "%pyname%.exe"
    copy "dist\%pyname%.exe"       "%pyname%.exe"
    del  "%pyname%.spec"
    copy "%pyname%.exe"        "C:\RiKi_assistant\%pyname%.exe"
    copy "%pyname%.exe"        "C:\_共有\Worker\%pyname%.exe"
    copy "%pyname%.exe"        "C:\_共有\Monjyu\%pyname%.exe"
    ping  localhost -w 1000 -n 1 >nul
rem del  "%pyname%.exe"



set pyname=RiKi_Monjyu_debug
    echo;
    echo %pyname%.py
       pyinstaller %pyname%.py  -F --log-level ERROR

IF EXIST "dist\%pyname%.exe"  ECHO "%pyname%.exe"
    copy "dist\%pyname%.exe"       "%pyname%.exe"
    del  "%pyname%.spec"
rem copy "%pyname%.exe"        "C:\RiKi_assistant\%pyname%.exe"
rem copy "%pyname%.exe"        "C:\_共有\Worker\%pyname%.exe"
rem copy "%pyname%.exe"        "C:\_共有\Monjyu\%pyname%.exe"
    ping  localhost -w 1000 -n 1 >nul
rem del  "%pyname%.exe"



ECHO;
IF EXIST "build"        RD "build"        /s /q
IF EXIST "dist"         RD "dist"         /s /q
IF EXIST "__pycache__"  RD "__pycache__"  /s /q
rem IF EXIST "temp"                                RD "temp"                                /s /q
rem IF EXIST "_cache"                              RD "_cache"                              /s /q
IF EXIST "C:\RiKi_assistant\temp"              RD "C:\RiKi_assistant\temp"              /s /q
IF EXIST "C:\RiKi_assistant\_cache"            RD "C:\RiKi_assistant\_cache"            /s /q
IF EXIST "C:\_共有\Worker\temp"                RD "C:\_共有\Worker\temp"                /s /q
IF EXIST "C:\_共有\Worker\_cache"              RD "C:\_共有\Worker\_cache"              /s /q
IF EXIST "C:\_共有\Monjyu\temp"                RD "C:\_共有\Monjyu\temp"                /s /q
IF EXIST "C:\_共有\Monjyu\_cache"              RD "C:\_共有\Monjyu\_cache"              /s /q
PAUSE



