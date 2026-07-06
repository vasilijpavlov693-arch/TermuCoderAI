@echo off
chcp 65001 > nul

echo ==========================
echo TermuCoder AI Installer
echo Windows
echo ==========================

where python >nul 2>nul

if %errorlevel% neq 0 (
    echo Python не найден
    echo Установи Python 3.11+
    pause
    exit /b
)


echo Installing dependencies...

python -m pip install --upgrade pip
pip install -r requirements.txt


if not exist models mkdir models
if not exist AI mkdir AI


echo Download llama.cpp...


if not exist AI\llama.cpp.exe (

curl -L ^
-o AI\llama.cpp.zip ^
https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b5480-bin-win-cuda-cu12.4-x64.zip


powershell -Command "Expand-Archive AI\llama.cpp.zip AI"

)


echo Download Qwen model...


if not exist models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf (

curl -L ^
-o models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf ^
https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf

)


echo Creating launcher...


(
echo @echo off
echo cd /d %%~dp0\..\..
echo AI\llama-server.exe ^
-m models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf ^
-c 4096 ^
--host 127.0.0.1 ^
--port 8080
)>start_server.bat


(
echo @echo off
echo cd /d %%~dp0\..\..
echo python -m termucoder %%*
)>start.bat


echo.
echo DONE!
echo.
echo First run:
echo start_server.bat
echo.
echo Then:
echo start.bat code "write quicksort"
echo.

pause
