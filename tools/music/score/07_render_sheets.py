#!/usr/bin/env python3
"""⑦ 批量渲染每日谱子为 PDF + PNG（MuseScore CLI）。

通用工具：遍历目标 plan 下所有 dayNN_*/sheet/sheet.musicxml，用 mscore 渲染。
用法：
    python3 07_render_sheets.py --plan-root <plan 目录> [--dpi 150] [--only pdf|png]

前置：brew install --cask musescore（提供 mscore 命令）
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

PLAN_ROOT_DEFAULT = "/Users/infinity/Documents/a_future/plan/plan_piano"


def find_mscore():
    p = shutil.which("mscore")
    if p:
        return p
    # macOS 上 mscore 可能没进 PATH，直接找 app 内二进制
    for cand in [
        "/Applications/MuseScore 4.app/Contents/MacOS/mscore",
        "/Applications/MuseScore 4.app/Contents/MacOS/mscore3",
        "/Applications/MuseScore 4.app/Contents/MacOS/MuseScore 4",
    ]:
        if os.path.exists(cand):
            return cand
    return None


def render_one(mscore, musicxml, out_pdf, out_png, dpi, only):
    if only in ("pdf", "both"):
        subprocess.run([mscore, "-o", out_pdf, musicxml],
                       check=False, capture_output=True)
    if only in ("png", "both"):
        # 输出必须带 .png 后缀；多页时 mscore 生成 out-1.png, out-2.png ...
        subprocess.run([mscore, "-o", out_png + ".png", musicxml, "-r", str(dpi)],
                       check=False, capture_output=True)
        # 单页时把 out-1.png 重命名为 out.png
        p1 = f"{out_png}-1.png"
        if os.path.exists(p1) and not os.path.exists(f"{out_png}-2.png"):
            os.rename(p1, f"{out_png}.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-root", default=PLAN_ROOT_DEFAULT)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--only", default="both", choices=["pdf", "png", "both"])
    args = ap.parse_args()

    mscore = find_mscore()
    if not mscore:
        print("❌ 未找到 mscore。请先 brew install --cask musescore")
        sys.exit(1)
    print(f"使用 mscore: {mscore}")

    musicxmls = sorted(glob.glob(os.path.join(args.plan_root, "**/sheet/sheet.musicxml"), recursive=True))
    if not musicxmls:
        print(f"❌ 未找到任何 sheet.musicxml（--plan-root={args.plan_root}）")
        sys.exit(1)
    print(f"共 {len(musicxmls)} 个谱子待渲染（dpi={args.dpi}, only={args.only}）")

    ok = 0
    for mx in musicxmls:
        d = os.path.dirname(mx)
        out_pdf = os.path.join(d, "sheet.pdf")
        out_png = os.path.join(d, "sheet")
        render_one(mscore, mx, out_pdf, out_png, args.dpi, args.only)
        ok += 1
        if ok % 10 == 0 or ok == len(musicxmls):
            print(f"  进度 {ok}/{len(musicxmls)}")

    print(f"✅ 完成 {ok} 个谱子渲染")


if __name__ == "__main__":
    main()
