#!/usr/bin/env bash

set -e

echo "Starting llama-server..."

nohup ~/AI/llama.cpp/build/bin/llama-server \
-m ~/AI/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
-c 2048 \
--host 127.0.0.1 \
--port 8080 \
> ~/AI/server.log 2>&1 &


echo "Waiting for server..."

sleep 5


echo "Starting TermuCoder..."

cd ~/TermuCoderAI

termucoder "$@"
