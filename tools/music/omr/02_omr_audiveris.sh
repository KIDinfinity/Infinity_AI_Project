#!/usr/bin/env bash
# ② 谱面识别（路线 A：Audiveris，离线开源，最准）
# 前置：Java 17 + Audiveris 5.x
#
# 安装（macOS）：
#   brew install --cask temurin@17
#   # 下载 audiveris dist 到 ~/audiveris 并解压，例如 Audiveris-5.3.1.zip
#   export AUDIVERIS_HOME=~/audiveris/Audiveris-5.3.1
#   export PATH="$AUDIVERIS_HOME/bin:$PATH"
set -euo pipefail

# 脚本位置：tools/music/omr/，work 在 tools/music/work/
MUSIC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$MUSIC_DIR/work"
SRC="${1:-$WORK/preprocessed.png}"
OUT="$WORK/full.mxl"

if ! command -v audiveris >/dev/null 2>&1; then
  echo "❌ 未找到 audiveris。请先安装 Java 17 + Audiveris（见脚本头部注释）"
  exit 1
fi

if [ ! -f "$SRC" ]; then
  echo "❌ 未找到 $SRC，先运行 01_preprocess.py"
  exit 1
fi

mkdir -p "$WORK"
echo "→ 运行 Audiveris OMR ..."
audiveris -batch -export -output "$WORK" "$SRC"

BASE="$(basename "$SRC" .png)"
if [ -f "$WORK/$BASE.mxl" ]; then
  mv "$WORK/$BASE.mxl" "$OUT"
elif [ -f "$WORK/$BASE.xml" ]; then
  mv "$WORK/$BASE.xml" "${OUT%.mxl}.xml"
  echo "→ 得到 MusicXML（.xml），请确认下游脚本读取路径"
else
  echo "⚠️ 未找到 Audiveris 输出，请在 Audiveris GUI 中打开 $SRC 手动识别并导出 MusicXML 到 $OUT"
  exit 1
fi

echo "✅ OMR 完成 → $OUT"
