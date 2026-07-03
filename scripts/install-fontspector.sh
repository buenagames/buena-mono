#!/usr/bin/env bash
# Download the fontspector prebuilt binary into venv/bin (no Rust/cargo needed),
# so `make test` / `make package` can run GF QA anywhere without a Rust toolchain.
set -euo pipefail
cd "$(dirname "$0")/.."

DEST="venv/bin/fontspector"
if [ -x "$DEST" ]; then
  echo "fontspector already present ($DEST — $("$DEST" --version 2>/dev/null))"
  exit 0
fi

VER="fontspector-v1.7.2"
os=$(uname -s); arch=$(uname -m)
case "$os" in
  Darwin) case "$arch" in arm64|aarch64) triple=aarch64-apple-darwin;; *) triple=x86_64-apple-darwin;; esac;;
  Linux)  triple=x86_64-unknown-linux-gnu;;
  *) echo "unsupported OS for auto-install: $os (install fontspector manually)" >&2; exit 1;;
esac

url="https://github.com/fonttools/fontspector/releases/download/${VER}/${VER}-${triple}.tar.gz"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
echo "downloading fontspector ($triple)..."
curl -fsSL "$url" -o "$tmp/fs.tar.gz"
tar xzf "$tmp/fs.tar.gz" -C "$tmp"
bin=$(find "$tmp" -name fontspector -type f | head -1)
[ -n "$bin" ] || { echo "fontspector binary not found in archive" >&2; exit 1; }
mkdir -p venv/bin
cp "$bin" "$DEST"; chmod +x "$DEST"
echo "installed fontspector -> $DEST ($("$DEST" --version 2>/dev/null))"
