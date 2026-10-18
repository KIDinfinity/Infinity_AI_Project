#!/usr/bin/env python3
"""② 谱面识别（路线 B：本地视觉 LLM 兜底，无需 Java/Audiveris）

原理：把预处理长图喂给视觉模型，让它输出该行的小节/音符/时值 JSON。
精度不如 Audiveris，仅作兜底。

依赖：Ollama 已拉取视觉模型（如 qwen2.5vl），或任意 OpenAI 兼容视觉端点。
用法（Ollama）：
    ollama pull qwen2.5vl
    uv run --with requests python 02_omr_vision.py --src <preprocessed.png>
"""
import argparse
import base64
import json
import os

import requests

# 脚本位置：tools/music/omr/，work 在 tools/music/work/
MUSIC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(MUSIC_DIR, "work")

# 配置：二选一
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5vl"
OPENAI_COMPAT_URL = os.environ.get("VL_BASE_URL", "")  # 可选，如 http://localhost:8000/v1
OPENAI_COMPAT_KEY = os.environ.get("VL_API_KEY", "")

PROMPT = (
    "你是乐谱识别专家。这张图是一行钢琴五线谱（可能含高音谱和低音谱两个声部）。"
    "请只输出 JSON，不要任何解释，格式："
    '{"measures":[{"index":1,"right_hand":[{"pitch":"C5","duration":0.5}],"left_hand":[]}]}'
    "其中 pitch 用音名+八度（如 C4 中央C），duration 用四分音符=1 的倍数。"
    "无法辨认的地方用空数组，不要编造。"
)


def query_ollama(img_b64):
    r = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": PROMPT, "images": [img_b64]}],
        "stream": False,
    }, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]


def query_openai_compat(img_b64):
    r = requests.post(f"{OPENAI_COMPAT_URL}/chat/completions", headers={
        "Authorization": f"Bearer {OPENAI_COMPAT_KEY}",
    }, json={
        "model": os.environ.get("VL_MODEL", "qwen2.5-vl"),
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
        ]}],
    }, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(WORK, "preprocessed.png"))
    ap.add_argument("--ollama", action="store_true",
                    help="强制使用 Ollama（默认优先 OpenAI 兼容端点）")
    args = ap.parse_args()

    if not os.path.exists(args.src):
        raise SystemExit(f"未找到 {args.src}，先运行 01_preprocess.py")
    if not OPENAI_COMPAT_URL and not args.ollama:
        print("⚠️ 未设置 VL_BASE_URL，默认改用 Ollama（若未启动请先 ollama serve）")

    with open(args.src, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    if OPENAI_COMPAT_URL and not args.ollama:
        raw = query_openai_compat(img_b64)
    else:
        raw = query_ollama(img_b64)

    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(raw)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("⚠️ 本脚本只输出识别 JSON，尚未合成 MusicXML（多行切分需外部循环）。")
    print("建议：用 PlayScore2/Audiveris 生成 MusicXML 后直接走 score/ 目录脚本。")


if __name__ == "__main__":
    main()
