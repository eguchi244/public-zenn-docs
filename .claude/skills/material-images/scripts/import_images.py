"""教材リポジトリ（submodule）の画像を、記事・本の画像ディレクトリへ Zenn の命名規約で取り込む。

ファイル名は `YYYY-MM-DD-HH-MM-SS.png`（CLAUDE.md の「画像」）。教材の画像には撮影日時が無いので、
教材リポジトリでその画像がコミットされた日時を使う。同じコミットに入った画像は日時が重なるため、
**渡した順に1秒ずつずらす**（本文に載せる順に渡すと、ファイル名の順と掲載順が揃う）。

使い方:
    python -I import_images.py <Zennリポジトリ> <submoduleのパス> <画像ディレクトリ名> <教材内の画像>[@幅]... [--width 650]

    画像ディレクトリ名: 下書き用リポジトリの方針に従う（例: 本の章なら章ファイル名 `3.js-timer-stopwatch`）
    @幅: その画像だけ幅を変える（例: `img/phase03_mobile.png@300`）。省略時は --width（既定 650）

    **1つのディレクトリの画像は1回の実行でまとめて渡す。** 連番は実行ごとに 0 から始まるので、
    分けて実行すると同じ日時の名前が重なる（中身が違えば上書きせずに失敗する）

出力: 取り込んだ画像ごとに、本文へ貼る Markdown（`![](/images/<ディレクトリ>/<日時>.png =<幅>x)`）

NOTE: 同じ名前のファイルが既にあって中身も同じなら何もしない（撮り直していなければ再実行しても増えない）。
      中身が違う場合は上書きせず失敗する（撮り直した画像は、古い画像を消してから取り込み直す）
"""

import datetime
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path


def commit_time(submodule: Path, rel: str) -> datetime.datetime:
    """画像が教材リポジトリに最後にコミットされた日時（ローカル時刻）を返す

    Args:
        submodule : submodule のパス
        rel       : submodule 内の画像の相対パス

    Returns:
        コミット日時（タイムゾーン付き、ローカル時刻に変換済み）
    """
    out = subprocess.run(
        ["git", "-C", str(submodule), "log", "-1", "--format=%ct", "--", rel],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if not out:
        raise SystemExit(f"教材リポジトリにコミットされていない: {rel}")
    return datetime.datetime.fromtimestamp(int(out)).astimezone()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    width = 650
    if "--width" in args:
        i = args.index("--width")
        width = int(args[i + 1])
        del args[i:i + 2]
    if len(args) < 4:
        print(__doc__)
        return 2
    repo, submodule, image_dir, sources = Path(args[0]), Path(args[1]), args[2], args[3:]
    if not submodule.is_absolute():
        submodule = repo / submodule

    dst_dir = repo / "images" / image_dir
    dst_dir.mkdir(parents=True, exist_ok=True)
    for seq, spec in enumerate(sources):
        rel, _, w = spec.partition("@")
        img_width = int(w) if w else width
        src = submodule / rel
        if not src.is_file():
            print(f"教材に画像が無い: {src}")
            return 1
        stamp = (commit_time(submodule, rel) + datetime.timedelta(seconds=seq)).strftime("%Y-%m-%d-%H-%M-%S")
        dst = dst_dir / f"{stamp}{src.suffix}"
        if dst.exists() and not filecmp.cmp(src, dst, shallow=False):
            print(f"同じ名前で中身が違う画像がある（上書きしない）: {dst}")
            return 1
        shutil.copyfile(src, dst)
        print(f"{rel}\t![](/images/{image_dir}/{dst.name} ={img_width}x)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
