"""下書き用リポジトリの記事（原本）を、公開用リポジトリへ同期する。

原本 `articles/<下書きslug>.md` を公開用の `articles/<公開slug>.md` として作り直し、
`published` を true にして、記事の画像 `images/<下書きslug>/` を公開側の `images/<公開slug>/` へ移して
参照パスを書き換える（記事の画像ディレクトリは両方とも記事の slug）。

公開側の `articles/<公開slug>.md` と `images/<公開slug>/` は毎回まるごと作り直すので、
公開側で直接編集した内容は消える（公開側は原本の写しとして扱う）。

使い方:
    python -I sync_article.py <下書き側リポジトリ> <公開側リポジトリ> <下書きslug> <公開slug>

NOTE: 改行コードを保つためバイト単位で処理する（Git Bash の sed -i で CR が落ちたことがある）
"""

import re
import shutil
import sys
from pathlib import Path

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
    src_md = src_repo / "articles" / f"{draft_slug}.md"
    dst_md = dst_repo / "articles" / f"{pub_slug}.md"
    src_images = src_repo / "images" / draft_slug
    dst_images = dst_repo / "images" / pub_slug
    if not src_md.is_file():
        print(f"原本が見つからない: {src_md}")
        return 1

    data = src_md.read_bytes()
    data, n = PUBLISHED.subn(b"published: true", data, count=1)
    if n != 1:
        print("frontmatter に `published: false` が無い。原本は非公開のはず")
        return 1
    data = data.replace(b"(/images/" + draft_slug.encode() + b"/", b"(/images/" + pub_slug.encode() + b"/")

    # 他の記事・本の画像ディレクトリを参照していれば、公開側に無いと参照切れになるので先に調べる
    others = sorted({m.decode() for m in re.findall(rb"\(/images/([^/)\s]+)/", data)} - {pub_slug})

    # 公開側を作り直す
    dst_md.parent.mkdir(parents=True, exist_ok=True)
    dst_md.write_bytes(data)
    shutil.rmtree(dst_images, ignore_errors=True)
    if src_images.is_dir():
        shutil.copytree(src_images, dst_images)

    # 書き換え後の参照が公開側に実在するか
    broken = []
    for m in re.finditer(rb"\(/images/([^)\s=]+)", data):
        if not (dst_repo / "images" / m.group(1).decode()).is_file():
            broken.append(f"/images/{m.group(1).decode()}")
    # 原本の画像ディレクトリにあって本文から参照されていない画像（孤児画像）
    used = {m.group(1).decode() for m in re.finditer(rb"\(/images/" + pub_slug.encode() + rb"/([^)\s=]+)", data)}
    orphans = sorted(p.name for p in dst_images.iterdir() if p.name not in used) if dst_images.is_dir() else []

    print(f"同期: articles/{draft_slug}.md -> articles/{pub_slug}.md")
    if src_images.is_dir():
        print(f"  画像: images/{draft_slug} -> images/{pub_slug}（{len(list(dst_images.iterdir()))} 枚）")
    for d in others:
        print(f"  注意: 他のディレクトリの画像を参照している: images/{d}")
    for o in orphans:
        print(f"  孤児画像（本文から参照されていない）: images/{pub_slug}/{o}")
    for b in broken:
        print(f"  参照切れ: {b}")
    return 1 if broken or orphans else 0


if __name__ == "__main__":
    sys.exit(main())
