#!/usr/bin/env bash

set -e

echo "=== TermuCoder AI Linux Installer ==="


sudo apt update

sudo apt install -y \
git \
python3 \
python3-pip \
cmake \
build-essential \
wget


python3 -m pip install -r requirements.txt
python3 -m pip install .


mkdir -p ~/AI/models


MODEL=~/AI/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf


if [ ! -f "$MODEL" ]; then

wget \
-O "$MODEL" \
https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf

fi


if [ ! -d ~/AI/llama.cpp ]; then

git clone https://github.com/ggml-org/llama.cpp ~/AI/llama.cpp

fi


cd ~/AI/llama.cpp

cmake -B build
cmake --build build -j$(nproc)


echo "Done!"
echo ""
echo "Run: termucoder ask \"hello\""
