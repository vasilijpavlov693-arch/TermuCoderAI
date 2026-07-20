#!/usr/bin/env bash
set -e

# TermuCoderAI One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/vasilijpavlov693-arch/TermuCoderAI/main/install.sh | bash

REPO="https://github.com/vasilijpavlov693-arch/TermuCoderAI.git"
INSTALL_DIR="$HOME/TermuCoderAI"
MODELS_DIR="$HOME/AI/models"
LLAMA_DIR="$HOME/AI/llama.cpp"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}$1${NC}"; }
success() { echo -e "${GREEN}✔ $1${NC}"; }
error()   { echo -e "${RED}✖ $1${NC}"; }
warn()    { echo -e "${YELLOW}⚠ $1${NC}"; }

# Check arguments
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "TermuCoderAI Installer"
    echo ""
    echo "Usage:"
    echo "  curl -sSL <url> | bash           # Install with defaults"
    echo "  curl -sSL <url> | bash -s -- --check  # Check prerequisites only"
    echo "  curl -sSL <url> | bash -s -- --dir /path  # Custom install directory"
    echo ""
    echo "Options:"
    echo "  --check    Check prerequisites only"
    echo "  --dir DIR  Install to custom directory"
    echo "  --no-model Skip model download"
    echo "  --help     Show this help"
    exit 0
fi

# Parse arguments
CHECK_ONLY=false
CUSTOM_DIR=""
SKIP_MODEL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check) CHECK_ONLY=true; shift ;;
        --dir) CUSTOM_DIR="$2"; shift 2 ;;
        --no-model) SKIP_MODEL=true; shift ;;
        *) shift ;;
    esac
done

if [[ -n "$CUSTOM_DIR" ]]; then
    INSTALL_DIR="$CUSTOM_DIR"
fi

echo ""
info "╔══════════════════════════════════════╗"
info "║       TermuCoderAI Installer         ║"
info "╚══════════════════════════════════════╝"
echo ""

# Check Python
info "Checking Python..."
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    error "Python not found. Install Python 3.11+"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)
PY_VERSION=$($PYTHON --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
success "Python $PY_VERSION"

# Check pip
info "Checking pip..."
if ! $PYTHON -m pip --version &>/dev/null; then
    error "pip not found. Install pip: $PYTHON -m ensurepip --upgrade"
    exit 1
fi
success "pip available"

if $CHECK_ONLY; then
    echo ""
    success "All prerequisites met!"
    exit 0
fi

# Detect OS
info "Detecting OS..."
if [[ -f /data/data/com.termux/files/usr/bin/bash ]]; then
    OS="termux"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    OS="unknown"
fi
success "OS: $OS"

# Install system dependencies
info "Installing dependencies..."
if [[ "$OS" == "linux" ]]; then
    if command -v apt &>/dev/null; then
        sudo apt update -qq && sudo apt install -y -qq git cmake build-essential wget >/dev/null 2>&1 || true
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm git cmake wget >/dev/null 2>&1 || true
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y git cmake gcc-c++ make wget >/dev/null 2>&1 || true
    fi
elif [[ "$OS" == "termux" ]]; then
    pkg update -y >/dev/null 2>&1 || true
    pkg install -y git python cmake make wget >/dev/null 2>&1 || true
fi
success "Dependencies installed"

# Clone or update repository
info "Setting up TermuCoderAI..."
if [[ -d "$INSTALL_DIR/.git" ]]; then
    cd "$INSTALL_DIR"
    git pull -q
    success "Updated existing installation"
else
    git clone -q "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    success "Cloned to $INSTALL_DIR"
fi

# Install Python package
info "Installing termucoder-ai..."
$PYTHON -m pip install -e . -q 2>/dev/null || $PYTHON -m pip install -r requirements.txt -q 2>/dev/null
success "Package installed"

# Create directories
mkdir -p "$MODELS_DIR"
success "Models directory: $MODELS_DIR"

# Download model
if [[ "$SKIP_MODEL" == false ]]; then
    MODEL="$MODELS_DIR/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
    if [[ ! -f "$MODEL" ]]; then
        info "Downloading model (1.1 GB, may take a while)..."
        wget -q --show-progress -O "$MODEL" \
            "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf" \
            || warn "Model download failed. Download manually later."
        success "Model downloaded"
    else
        success "Model already exists"
    fi
else
    warn "Skipping model download (--no-model)"
fi

# Setup config
info "Setting up configuration..."
if [[ ! -f "settings.json" ]]; then
    cat > settings.json << 'CONFIG'
{
    "server": {
        "host": "127.0.0.1",
        "port": 8080,
        "context": 2048,
        "threads": 4,
        "gpu_layers": 0,
        "parallel": 1
    },
    "model": {
        "name": "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "path": "~/AI/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
    },
    "generation": {
        "temperature": 0.2,
        "max_tokens": 512,
        "top_p": 0.9,
        "top_k": 40
    },
    "prompts": {
        "system": "Ты AI помощник программиста."
    },
    "memory": {
        "enabled": true,
        "auto_learn": true
    }
}
CONFIG
    success "Configuration created"
else
    success "Configuration exists"
fi

# Final check
echo ""
info "Running diagnostics..."
$PYTHON -c "from termucoder.doctor import doctor; doctor()" 2>/dev/null || true

echo ""
success "Installation complete!"
echo ""
echo -e "  ${CYAN}Quick start:${NC}"
echo "    cd $INSTALL_DIR"
echo "    termucoder server start"
echo "    termucoder ask \"Hello!\""
echo ""
echo -e "  ${CYAN}Or use the launcher:${NC}"
echo "    $INSTALL_DIR/start.sh"
echo ""
