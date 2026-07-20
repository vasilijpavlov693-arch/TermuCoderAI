#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "=== TermuCoder AI Termux Installer ==="

pkg update -y

pkg install -y \
git \
python \
clang \
cmake \
make \
wget

echo "[1/5] Installing Python packages..."

pip install --upgrade pip

pip install -r requirements.txt

pip install -e .


echo "[2/5] Preparing directories..."

mkdir -p ~/AI/models


echo "[3/5] Downloading model..."

MODEL=~/AI/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf

if [ ! -f "$MODEL" ]; then

wget \
-O "$MODEL" \
https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf

else

echo "Model already exists"

fi


echo "[4/5] Installing llama.cpp..."

if [ ! -d ~/AI/llama.cpp ]; then

git clone https://github.com/ggerganov/llama.cpp ~/AI/llama.cpp

fi


cd ~/AI/llama.cpp

cmake -B build

cmake --build build -j$(nproc)


echo "[5/5] Done"

echo ""
echo "Run: termucoder ask \"hello\""
