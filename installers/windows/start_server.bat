@echo off
cd /d %~dp0\..\..
AI\llama-server.exe -m models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf -c 4096 --host 127.0.0.1 --port 8080
