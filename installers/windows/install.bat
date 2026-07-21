@echo off

echo ==========================
echo TermuCoder AI Installer
echo Windows
echo ==========================

where python >nul 2>nul

if %errorlevel% neq 0 (
    echo Python not found
    echo Install Python 3.11+
    pause
    exit /b
)

cd /d %~dp0\..\..

echo Installing dependencies...

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install .

if not exist models mkdir models
if not exist AI mkdir AI

echo Download llama.cpp...

if not exist AI\llama-server.exe (

powershell -Command "$r = Invoke-RestMethod 'https://api.github.com/repos/ggml-org/llama.cpp/releases/latest'; $a = $r.assets | Where-Object { $_.name -match 'win-cuda-12' -and $_.name -match '^llama-' -and $_.name -notmatch 'cudart' } | Select-Object -First 1; Write-Host 'Downloading:' $a.name; Invoke-WebRequest -Uri $a.browser_download_url -OutFile 'AI\llama.cpp.zip'"

powershell -Command "Expand-Archive -Path AI\llama.cpp.zip -DestinationPath AI -Force"

del AI\llama.cpp.zip

)

echo Download Qwen model...

if not exist models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf (

curl -L -o models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf ^
https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf

)

echo Creating launcher...

>start_server.bat (
echo @echo off
echo cd /d %%~dp0\..\..
echo AI\llama-server.exe -m models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf -c 4096 --host 127.0.0.1 --port 8080
)

>start.bat (
echo @echo off
echo cd /d %%~dp0\..\..
echo python -m termucoder %%*
)

echo.
echo DONE!
echo.
echo First run: start_server.bat
echo Then: start.bat ask "write quicksort"
echo.

pause
