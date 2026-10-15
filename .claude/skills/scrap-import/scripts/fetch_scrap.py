"""公開済みの Zenn スクラップを取得し、Markdown と画像に戻して下書き用リポジトリへ取り込む。

スクラップは GitHub 連携の対象外で、API（`https://zenn.dev/api/scraps/<id>`）も HTML（`body_html`）しか
返さない。この HTML を Zenn の Markdown 記法（`:::message`・`:::details`・`言語:ファイル名` のコードブロック・
リンクカード）に戻し、画像は Zenn のサーバーからダウンロードしてリポジトリの画像ディレクトリに置く。

使い方:
    python -I fetch_scrap.py <スクラップのURLかid> <下書き用リポジトリ> <出力先md> <画像ディレクトリ名>

    出力先md      : 下書き用リポジトリからの相対パス（例: articles/<公開slug>-draft.md）。frontmatter は付けない
    画像ディレクトリ名: images/ の下に作るディレクトリ（記事なら記事の slug）。既にあって中身があれば中止する

出力:
    - 出力先md: 先頭に元スクラップの情報を HTML コメントで残し、コメント（返信も）を投稿順に並べる
    - images/<画像ディレクトリ名>/: 画像。ファイル名は規約の `YYYY-MM-DD-HH-MM-SS.<拡張子>`。撮影日時は
      分からないので、そのコメントの投稿時刻から1秒ずつずらして掲載順に付ける
    - 標準出力: 画像の対応表（番号・ファイル名・元URL・直前の見出し・直前の本文）。置き換え対象を決めるのに使う

変換できない要素は捨てずに警告し、中のテキストは残す。1枚でも画像の取得に失敗したら終了コード1。

NOTE: 改行は LF で書き出す（Zenn の Markdown として読めればよく、元の改行コードは存在しない）
"""

import datetime
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

API = "https://zenn.dev/api/scraps/{}"
UA = {"User-Agent": "Mozilla/5.0 (fetch_scrap.py)"}
VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr"}
EXT_BY_TYPE = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/gif": "gif"}
LANG_BY_EXT = {
    "py": "python", "js": "js", "ts": "ts", "jsx": "jsx", "tsx": "tsx", "php": "php", "rb": "ruby",
    "sh": "bash", "ps1": "powershell", "bat": "bat", "json": "json", "yml": "yaml", "yaml": "yaml",
    "html": "html", "css": "css", "sql": "sql", "md": "markdown", "java": "java", "go": "go",
}
LANG_BY_NAME = {"cmd": "shell", "bash": "bash", "shell": "shell", "terminal": "shell", "powershell": "powershell"}


class Node:
    def __init__(self, tag: str, attrs: dict[str, str] | None = None, parent: "Node | None" = None):
        self.tag = tag
        self.attrs = attrs or {}
        self.parent = parent
        self.children: list["Node | str"] = []

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def hidden(self) -> bool:
        return "display:none" in self.attrs.get("style", "").replace(" ", "")

    def text(self) -> str:
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)

    def find_all(self, pred) -> list["Node"]:
        found = []
        for c in self.children:
            if isinstance(c, Node):
                if pred(c):
                    found.append(c)
                found.extend(c.find_all(pred))
        return found


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: v or "" for k, v in attrs}, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


class Converter:
    """body_html を Zenn の Markdown に戻す。画像は images に (src, 直前の見出し, 直前の本文) を積む"""

    def __init__(self):
        self.images: list[dict] = []
        self.warnings: list[str] = []
        self.heading = ""
        self.last_text = ""

    # --- ブロック -------------------------------------------------------------
    def blocks(self, node: Node) -> str:
        parts = [self.block(c) for c in node.children]
        return "\n\n".join(p for p in parts if p.strip())

    def block(self, n: "Node | str") -> str:
        if isinstance(n, str):
            return self.clean(n)
        if n.hidden():
            return ""
        tag, cls = n.tag, n.classes
        if re.fullmatch(r"h[1-6]", tag):
            title = self.clean(self.inline_children(n))
            self.heading = title
            return "#" * int(tag[1]) + " " + title
        if tag == "p":
            return self.paragraph(n)
        if tag in ("ul", "ol"):
            return self.list_(n, 0)
        if tag == "div" and "code-block-container" in cls:
            return self.code_block(n)
        if tag == "pre":
            return self.code_block(n)
        if tag == "aside" and "msg" in cls:
            content = n.find_all(lambda x: "msg-content" in x.classes)
            body = self.blocks(content[0] if content else n)
            kind = "message alert" if "alert" in cls else "message"
            return self.fence(kind, body)
        if tag == "details":
            summary = next((c for c in n.children if isinstance(c, Node) and c.tag == "summary"), None)
            title = self.clean(self.inline_children(summary)) if summary else ""
            content = n.find_all(lambda x: "details-content" in x.classes)
            body = self.blocks(content[0]) if content else ""
            return self.fence(f"details {title}", body)
        if tag == "blockquote":
            return "\n".join("> " + line if line else ">" for line in self.blocks(n).split("\n"))
        if tag == "hr":
            return "---"
        if tag == "table":
            return self.table(n)
        if tag == "div":
            return self.blocks(n)
        if tag == "span" and "embed-block" in cls:
            return self.embed(n)
        # インライン要素がブロックの位置に来た場合
        if tag in ("a", "strong", "em", "code", "img", "span", "b", "i", "del", "s", "br"):
            return self.paragraph(n, wrap=False)
        self.warn(tag, n)
        return self.blocks(n)

    def paragraph(self, n: Node, wrap: bool = True) -> str:
        body = self.inline_children(n) if wrap else self.inline(n)
        lines = [line.strip(" \t") for line in body.split("\n")]
        out = "\n".join(lines)
        return re.sub(r"\n{3,}", "\n\n", out).strip("\n")

    def list_(self, n: Node, depth: int) -> str:
        lines = []
        num = 1
        for li in n.children:
            if not isinstance(li, Node) or li.tag != "li":
                continue
            inline_parts, nested = [], []
            for c in li.children:
                if isinstance(c, Node) and c.tag in ("ul", "ol"):
                    nested.append(self.list_(c, depth + 1))
                elif isinstance(c, Node) and c.tag == "p":
                    inline_parts.append(self.inline_children(c))
                else:
                    inline_parts.append(c if isinstance(c, str) else self.inline(c))
            text = self.clean("".join(inline_parts)).replace("\n", " ")
            mark = f"{num}." if n.tag == "ol" else "-"
            num += 1
            lines.append("  " * depth + f"{mark} {text}")
            lines.extend(nested)
        return "\n".join(lines)

    def code_block(self, n: Node) -> str:
        names = n.find_all(lambda x: "code-block-filename" in x.classes)
        filename = self.clean(names[0].text()) if names else ""
        pres = [n] if n.tag == "pre" else n.find_all(lambda x: x.tag == "pre")
        if not pres:
            self.warn("code-block（pre なし）", n)
            return ""
        pre = pres[0]
        lines = pre.find_all(lambda x: "line" in x.classes)
        code = "\n".join(l.text() for l in lines) if lines else pre.text()
        code = code.rstrip("\n")
        lang = ""
        for c in pre.find_all(lambda x: x.tag == "code") + [pre]:
            m = re.search(r"language-([\w+-]+)", c.attrs.get("class", ""))
            if m:
                lang = m.group(1)
                break
        if not lang and filename:
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            lang = LANG_BY_EXT.get(ext) or LANG_BY_NAME.get(filename.lower(), "")
        info = f"{lang}:{filename}" if filename else lang
        ticks = "```"
        while ticks in code:
            ticks += "`"
        self.last_text = filename or self.last_text
        return f"{ticks}{info}\n{code}\n{ticks}"

    def table(self, n: Node) -> str:
        rows = []
        for tr in n.find_all(lambda x: x.tag == "tr"):
            cells = [self.clean(self.inline_children(c)).replace("\n", "<br>").replace("|", "\\|")
                     for c in tr.children if isinstance(c, Node) and c.tag in ("th", "td")]
            rows.append("| " + " | ".join(cells) + " |")
        if not rows:
            return ""
        cols = rows[0].count(" | ") + 1
        rows.insert(1, "|" + "---|" * cols)
        return "\n".join(rows)

    def embed(self, n: Node) -> str:
        frames = n.find_all(lambda x: x.tag == "iframe")
        if frames and frames[0].attrs.get("data-content"):
            return urllib.parse.unquote(frames[0].attrs["data-content"])
        self.warn("embed（data-content なし）", n)
        return frames[0].attrs.get("src", "") if frames else self.blocks(n)

    @staticmethod
    def fence(kind: str, body: str) -> str:
        inner = max((len(m) for m in re.findall(r"^(:{3,})", body, re.MULTILINE)), default=2)
        colons = ":" * max(3, inner + 1)
        return f"{colons}{kind}\n{body}\n{colons}"

    # --- インライン -----------------------------------------------------------
    def inline_children(self, n: Node | None) -> str:
        if n is None:
            return ""
        return "".join(self.inline(c) for c in n.children)

    def inline(self, n: "Node | str") -> str:
        if isinstance(n, str):
            # ソース上の改行は <br> の直後などにあるだけ。改行は <br> から作るので捨てる
            text = n.replace("\n", "")
            if text.strip():
                self.last_text = text.strip()
            return text
        if n.hidden():
            return ""
        tag, cls = n.tag, n.classes
        if tag == "br":
            return "\n"
        if tag == "img":
            return self.image(n)
        if tag == "span" and "embed-block" in cls:
            return "\n\n" + self.embed(n) + "\n\n"
        inner = self.inline_children(n)
        if tag == "a":
            if "header-anchor-link" in cls or not inner.strip():
                return inner
            href = n.attrs.get("href", "")
            return href if inner == href else f"[{inner}]({href})"
        if tag in ("strong", "b"):
            return f"**{inner}**"
        if tag in ("em", "i"):
            return f"*{inner}*"
        if tag in ("del", "s"):
            return f"~~{inner}~~"
        if tag == "code":
            return f"`{n.text()}`"
        if tag in ("span", "sup", "sub", "small", "mark", "u"):
            if tag != "span":
                self.warn(tag, n)
            return inner
        if tag in ("p", "div"):
            return "\n\n" + inner + "\n\n"
        self.warn(tag, n)
        return inner

    def image(self, n: Node) -> str:
        idx = len(self.images)
        self.images.append({
            "src": n.attrs.get("src", ""),
            "alt": n.attrs.get("alt", ""),
            "width": n.attrs.get("width", ""),
            "heading": self.heading,
            "text": self.last_text,
        })
        return f"\x00IMG{idx}\x00"

    # --- 補助 -----------------------------------------------------------------
    @staticmethod
    def clean(s: str) -> str:
        return s.strip(" \t\n")

    def warn(self, what: str, n: Node) -> None:
        self.warnings.append(f"{what}: {n.text()[:40]!r}")


def scrap_id(arg: str) -> str:
    m = re.search(r"scraps/([0-9a-f]+)", arg)
    return m.group(1) if m else arg


def fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read(), res.headers.get_content_type()


def walk_comments(comments: list[dict], depth: int = 0):
    for c in comments:
        yield c, depth
        yield from walk_comments(c.get("children") or [], depth + 1)


def main() -> int:
    # NOTE: Windows のコンソールは既定で cp932 のため、日本語の出力が化けないよう固定する
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    sid = scrap_id(sys.argv[1])
    repo, out_rel, image_dir = Path(sys.argv[2]), sys.argv[3], sys.argv[4]
    out_md = repo / out_rel
    img_root = repo / "images" / image_dir
    if out_md.exists():
        print(f"出力先が既にある。上書きしないので消してから実行する: {out_md}")
        return 1
    if img_root.is_dir() and any(img_root.iterdir()):
        print(f"画像ディレクトリが空でない。上書きしないので中身を確認して消してから実行する: {img_root}")
        return 1

    data, _ = fetch(API.format(sid))
    scrap = json.loads(data)["scrap"]
    user = scrap["user"]["username"]
    topics = ", ".join(t.get("display_name") or t["name"] for t in scrap.get("topics", []))

    sections = []
    images: list[dict] = []
    warnings: list[str] = []
    for comment, depth in walk_comments(scrap["comments"]):
        root = TreeBuilder()
        root.feed(comment["body_html"])
        conv = Converter()
        body = conv.blocks(root.root)
        start = datetime.datetime.fromisoformat(comment["created_at"])
        for i, img in enumerate(conv.images):
            img["time"] = start + datetime.timedelta(seconds=i)
            img["placeholder"] = f"\x00IMG{i}\x00"
        # 1つのスクラップでプレースホルダーが重ならないよう、コメントごとに置き換えてから積む
        for img in conv.images:
            img["no"] = len(images) + 1
            token = f"\x00IMGN{img['no']}\x00"
            body = body.replace(img["placeholder"], token)
            img["placeholder"] = token
            images.append(img)
        warnings.extend(conv.warnings)
        label = "コメント" if depth == 0 else "返信"
        sections.append(f"<!-- {label}: {comment['created_at']} -->\n\n{body}")

    header = (
        "<!--\n"
        f"元スクラップ: https://zenn.dev/{user}/scraps/{scrap['slug']}\n"
        f"タイトル: {scrap['title']}\n"
        f"topics: {topics}\n"
        f"取得日: {datetime.date.today().isoformat()}\n"
        "-->"
    )
    md = header + "\n\n" + "\n\n".join(sections) + "\n"

    # 画像をダウンロードして参照を書き換える
    failed = []
    img_root.mkdir(parents=True, exist_ok=True)
    print("| 番号 | ファイル名 | 元URL | 直前の見出し | 直前の本文 |")
    print("|---|---|---|---|---|")
    for img in images:
        src = img["src"]
        try:
            blob, ctype = fetch(src)
        except Exception as e:  # noqa: BLE001 - 失敗は一覧にして最後に終了コードで返す
            failed.append(f"{img['no']}: {src} ({e})")
            continue
        ext = EXT_BY_TYPE.get(ctype) or Path(urllib.parse.urlparse(src).path).suffix.lstrip(".") or "png"
        name = img["time"].strftime("%Y-%m-%d-%H-%M-%S") + "." + ext
        (img_root / name).write_bytes(blob)
        width = f" ={img['width']}x" if img["width"] else ""
        md = md.replace(img["placeholder"], f"![{img['alt']}](/images/{image_dir}/{name}{width})")
        print(f"| {img['no']} | {name} | {src} | {img['heading']} | {img['text'][:30]} |")

    # 取得に失敗した画像は元の URL のまま残す
    for img in images:
        md = md.replace(img["placeholder"], f"![{img['alt']}]({img['src']})")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_bytes(md.encode("utf-8"))
    print(f"\n出力: {out_rel}（コメント {len(sections)} 件・画像 {len(images) - len(failed)}/{len(images)} 枚）")
    for w in warnings:
        print(f"  警告（未対応の要素）: {w}")
    for f in failed:
        print(f"  画像の取得に失敗: {f}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
