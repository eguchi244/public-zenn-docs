"""本の表紙（cover.jpg）を作る。

黒地にアクセント色の線を引き、タイトル・サブタイトル・アイコンを並べたレイアウト。
Zenn 推奨の 500x700 で出力する。

使い方:
    python -I make_cover.py <出力先 cover.jpg> --title "JavaScript入門" \
        --subtitle "Vanilla JSで" --subtitle "タイマーアプリを作ってみよう！" \
        --accent "#F7DF1E" [--icon a.png --icon b.png] [--font <ttf/ttc>]

- --subtitle は1行ずつ指定する（2行まで推奨）
- --icon は透過 PNG を推奨。0〜2個。指定した順に左から並べる
- 4倍の解像度で描いてから縮小し、線と文字のギザギザを抑える
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 500, 700
K = 4  # 描画時の倍率
FONT_CANDIDATES = [
    "C:/Windows/Fonts/NotoSansJP-VF.ttf",
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def s(v: float) -> int:
    return int(v * K)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(path, s(size))
    try:
        f.set_variation_by_axes([400])  # 可変フォントなら Regular に固定
    except Exception:
        pass
    return f


def find_font(arg: str | None) -> str | None:
    for p in [arg] if arg else FONT_CANDIDATES:
        if p and Path(p).is_file():
            return p
    return None


def fit(d: ImageDraw.ImageDraw, text: str, path: str, size: int, max_w: int):
    """max_w に収まるまでフォントを縮める"""
    while size > 10:
        f = load_font(path, size)
        if d.textlength(text, font=f) <= s(max_w):
            return f
        size -= 1
    return load_font(path, size)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", action="append", default=[])
    ap.add_argument("--accent", default="#FF2D20")
    ap.add_argument("--icon", action="append", default=[])
    ap.add_argument("--font")
    a = ap.parse_args()

    font_path = find_font(a.font)
    if not font_path:
        print("日本語フォントが見つからない。--font で指定する")
        return 1
    if len(a.icon) > 2:
        print("--icon は2個まで")
        return 1

    accent = a.accent
    img = Image.new("RGB", (s(W), s(H)), (0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = s(3)

    # 線（右の縦線・下の横線2本・右下の縦線）
    d.rectangle([s(436), 0, s(436) + lw, s(H)], fill=accent)
    d.rectangle([0, s(424), s(W), s(424) + lw], fill=accent)
    d.rectangle([0, s(496), s(W), s(496) + lw], fill=accent)
    d.rectangle([s(348), s(424), s(348) + lw, s(H)], fill=accent)

    # 文字は縦線の左側（x=0〜436）の中央に置く
    cx, area = 220, 380

    def ctext(y: int, text: str, f) -> None:
        w = d.textlength(text, font=f)
        d.text((s(cx) - w / 2, s(y)), text, font=f, fill="white")

    ctext(58, a.title, fit(d, a.title, font_path, 44, area))
    d.rectangle([s(55), s(132), s(384), s(132) + lw], fill=accent)
    for i, line in enumerate(a.subtitle[:2]):
        ctext(155 + i * 40, line, fit(d, line, font_path, 23, area))

    # アイコン（y=250〜360 の帯に、1個なら中央・2個なら左右に並べる）
    box = 110
    centers = {0: [], 1: [cx], 2: [cx - 85, cx + 85]}[len(a.icon)]
    for path, icx in zip(a.icon, centers):
        ic = Image.open(path).convert("RGBA")
        r = s(box) / max(ic.size)  # 小さい画像も枠いっぱいまで拡大する
        ic = ic.resize((round(ic.width * r), round(ic.height * r)), Image.LANCZOS)
        img.paste(ic, (s(icx) - ic.width // 2, s(305) - ic.height // 2), ic)

    out = img.resize((W, H), Image.LANCZOS)
    out.save(a.out, "JPEG", quality=92, dpi=(300, 300))
    print(f"表紙を作成: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
