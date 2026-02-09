#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

pkg update -y
pkg install -y git cmake clang python wget

if [ ! -d llama.cpp ]; then
  git clone https://github.com/ggerganov/llama.cpp.git
fi

cd llama.cpp
cmake -B build
cmake --build build -j"$(nproc)"

mkdir -p "$HOME/bin"
cp build/bin/llama-cli "$HOME/bin/llama-cli"
chmod +x "$HOME/bin/llama-cli"

echo "Installed llama-cli to $HOME/bin/llama-cli"
echo "Add to PATH if needed: export PATH=$HOME/bin:$PATH"
