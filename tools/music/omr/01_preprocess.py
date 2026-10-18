#!/usr/bin/env python3
"""① 谱面预处理：把多张谱子图片拼成一页长图，放大、灰度、二值化增强。

通用工具：任何乐器的谱子图片都能用。
用法：
    uv run --with Pillow --with numpy python 01_preprocess.py \
        --src-dir <图片目录> --out <输出长图.png>
"""
import argparse
import os

from PIL import Image, ImageEnhance


def main():
    ap = argparse.ArgumentParser(description="拼接+增强谱子图片为一张长图")
    ap.add_argument("--src-dir", required=True, help="谱子图片所在目录")
    ap.add_argument("--out", required=True, help="输出长图路径，如 .../work/preprocessed.png")
    ap.add_argument("--scale", type=int, default=2, help="放大倍数（OMR 识别率更高），默认 2")
    args = ap.parse_args()

    exts = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
    files = sorted(f for f in os.listdir(args.src_dir)
                   if f.lower().endswith(exts))
    if not files:
        raise SystemExit(f"未找到图片：{args.src_dir}")

    imgs = []
    for f in files:
        im = Image.open(os.path.join(args.src_dir, f)).convert("L")  # 灰度
        w, h = im.size
        im = im.resize((w * args.scale, h * args.scale), Image.LANCZOS)
        im = ImageEnhance.Contrast(im).enhance(1.6)
        im = im.point(lambda p: 255 if p > 140 else 0)  # 简单二值化
        imgs.append(im)
        print(f"  加载 {f}: {im.size[0]}x{im.size[1]}")

    total_h = sum(im.height for im in imgs)
    max_w = max(im.width for im in imgs)
    canvas = Image.new("L", (max_w, total_h), 255)
    y = 0
    for im in imgs:
        canvas.paste(im, (0, y))
        y += im.height

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    canvas.save(args.out)
    print(f"✅ 已生成 {args.out}  ({max_w}x{total_h})")


if __name__ == "__main__":
    main()
