"""下書き用リポジトリの本（原本）を、公開用リポジトリへ同期する。

原本 `books/<下書きslug>/` を公開用の `books/<公開slug>/` として作り直し、
`published` を true にして、本が参照する画像を公開側の方針
`images/<公開slug>/<元のディレクトリ名>/` へ移して参照パスを書き換える。

公開側の `books/<公開slug>/` と `images/<公開slug>/` は毎回まるごと作り直すので、
公開側で直接編集した内容は消える（公開側は原本の写しとして扱う）。

使い方:
    python -I sync_book.py <下書き側リポジトリ> <公開側リポジトリ> <下書きslug> <公開slug>

NOTE: 改行コードを保つためバイト単位で処理する（Git Bash の sed -i で CR が落ちたことがある）
"""

import re
import shutil
import sys
from pathlib import Path

IMAGE_REF = re.compile(rb"\(/images/([^/)\s]+)/")
PUBLISHED = re.compile(rb"^published:\s*false", re.MULTILINE)


def main() -> int:
    # NOTE: Windows のコンソールは既定で cp932 のため、日本語の出力が化けないよう固定する
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    src_repo, dst_repo = Path(sys.argv[1]), Path(sys.argv[2])
    draft_slug, pub_slug = sys.argv[3], sys.argv[4]

    if draft_slug == pub_slug:
        print("下書きslug と公開slug が同じ。両リポジトリが Zenn 連携していると衝突するため中止する")
        return 1
    src_book = src_repo / "books" / draft_slug
    dst_book = dst_repo / "books" / pub_slug
    dst_images = dst_repo / "images" / pub_slug
    if not (src_book / "config.yaml").is_file():
        print(f"原本が見つからない: {src_book}")
        return 1

    # 公開側を作り直す
    shutil.rmtree(dst_book, ignore_errors=True)
    shutil.rmtree(dst_images, ignore_errors=True)
    dst_book.mkdir(parents=True)

    image_dirs: set[str] = set()
    for src in sorted(src_book.iterdir()):
        if not src.is_file():
            continue
        data = src.read_bytes()
        if src.name == "config.yaml":
            data, n = PUBLISHED.subn(b"published: true", data)
            if n != 1:
                print("config.yaml に `published: false` が1行も無い。原本は非公開のはず")
                return 1
        elif src.suffix == ".md":
            image_dirs.update(m.decode() for m in IMAGE_REF.findall(data))
            data = IMAGE_REF.sub(
                lambda m: b"(/images/" + pub_slug.encode() + b"/" + m.group(1) + b"/", data
            )
        (dst_book / src.name).write_bytes(data)

    # 参照されている画像ディレクトリだけを公開側へ移す
    missing = []
    for d in sorted(image_dirs):
        src_dir = src_repo / "images" / d
        if not src_dir.is_dir():
            missing.append(d)
            continue
        shutil.copytree(src_dir, dst_images / d)

    # 書き換え後の参照が公開側に実在するか
    broken = []
    for md in dst_book.glob("*.md"):
        for m in re.finditer(rb"\(/images/([^)\s=]+)", md.read_bytes()):
            if not (dst_repo / "images" / m.group(1).decode()).is_file():
                broken.append(f"{md.name}: /images/{m.group(1).decode()}")

    print(f"同期: books/{draft_slug} -> books/{pub_slug}")
    for d in sorted(image_dirs):
        print(f"  画像: images/{d} -> images/{pub_slug}/{d}")
    if missing or broken:
        for d in missing:
            print(f"  原本側に画像ディレクトリが無い: images/{d}")
        for b in broken:
            print(f"  参照切れ: {b}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
