---
name: source-material
description: 別リポジトリにある教材（要件定義・設計・チュートリアルなど）を Git submodule で参照して記事・本を書く。「<教材>を記事にして」「教材を元に書いて」と頼まれたとき、教材の変更を記事に反映するとき、submodule の参照を更新するときに使う。最新化 → 教材を読む → 記事を書く → 記事と参照の更新を一緒にコミットの一連。
---

# 教材リポジトリを参照して書く

> このスキルは同じ基準で構成された Zenn リポジトリ間で共通。**どの教材リポジトリをどのパスに submodule として置いているか**は `.claude/zenn-profile.md` の「教材リポジトリ」にある。まずそこを読む。「無し」なら、このスキルは使わない。

教材リポジトリはファイルとしては取り込まず、submodule（「どのリポジトリの、どのコミットか」だけを記録する参照）で持つ。こうすると、**どの版の教材から書いたかがコミットごとに自動で残り**、教材のコード本体もこのリポジトリに溜まらない。

## 1. 教材を最新にする

`commit-flow` どおり feature ブランチを切ってから行う（参照の更新もコミット対象になるため）。

```bash
git submodule update --init --remote <submodule のパス>
git -C <submodule のパス> log --oneline -1      # 今回読む教材の版
git status --short                              # 参照が進んでいれば ` M <submodule のパス>` が出る
```

- submodule が見るのは**教材リポジトリの GitHub 上の追跡ブランチ**。教材を手元で編集中なら、先に教材リポジトリ側で commit・push してもらう（未 push の編集は見えない）。編集中の内容を記事に使いたいと言われたら、push が先だと伝える
- 同じ教材の作業用クローンが別の場所にあっても、**記事の材料は submodule 側だけを読む**（版の記録とずれないように）

### 教材リポジトリの Claude Code 設定を展開しない（初回だけ）

教材リポジトリが自分の `CLAUDE.md`・`.claude/`（スキル・フック）・`.mcp.json` を持っていると、submodule 内のファイルを読んだときにそれらも読み込まれ、同名のスキル（`commit-flow` など）が二重に見えて、どちらの規約に従うべきかが曖昧になる。**記事の材料に要るのは教材だけ**なので、sparse-checkout でこれらを作業ツリーに展開しない。

```bash
MSYS_NO_PATHCONV=1 git -C <submodule のパス> sparse-checkout set --no-cone '/*' '!/.claude/' '!/CLAUDE.md' '!/.mcp.json'
git -C <submodule のパス> sparse-checkout list    # 4行が上のとおり出ること
ls -a <submodule のパス>                           # .claude・CLAUDE.md・.mcp.json が無いこと
```

- **Git Bash では `MSYS_NO_PATHCONV=1` が必須。** 付けないと `!/.claude/` が `!C:/Program Files/Git/.claude/` に変換され、除外が効かない（`sparse-checkout list` で気づける）。PowerShell から実行する場合は不要
- 設定はローカルだけでリポジトリに記録されない。**clone し直したり submodule を初期化し直したりしたら再設定する**（`ls -a` で `CLAUDE.md` が見えたら未設定）
- `git submodule update --remote` で教材を進めても設定は維持される
- 参照しているコミット（gitlink）は変わらないので、このリポジトリ側にコミットすべき差分は出ない

### 公開中の記事・本の元になった教材が変わったとき

前回どの版から書いたかは、原本の最終コミットの本文（`教材: <リポジトリ>@<短縮ハッシュ>`）か、そのときの submodule の参照で分かる。最新化したあと、その版からの差分を見て、記事・本のどこに影響するかを洗い出す。

```bash
git log -1 --format=%B -- books/<下書きslug>/        # 前回の「教材:」行を確認
git -C <submodule のパス> diff --stat <前回の版>..HEAD -- <教材内のパス>
git -C <submodule のパス> diff <前回の版>..HEAD -- <教材内のパス>
```

解答コードが変わっていれば答え合わせ用リポジトリも更新が要る（`answer-repo` スキル）。公開側への反映は `draft-to-publish` スキルの「公開後の修正」。

## 2. 教材を読んで書く

- submodule の中のファイルは**読むだけ**。編集・コミットしない（教材の修正は教材リポジトリ側で行う）
- 教材の相対リンク・画像パス・「このプロジェクト直下の〜」のような手元前提の書き方は、読者が教材リポジトリを持っていない前提で書き換える
- 画像は教材から `images/` 配下へコピーして使う（submodule 内を参照しない。Zenn のデプロイ対象外のため）

## 3. コミットする

`commit-flow` に従い、**記事と参照の更新（` M <submodule のパス>`）を同じコミットに入れる。** 本文に元にした教材の版を1行書く:

```
教材: <教材リポジトリ名>@<短縮ハッシュ>（<教材内のパス>）
```

記事を変えずに参照だけ進めたい場合は、件名を `教材参照を<短縮ハッシュ>に更新` としてコミットしてよい。

## 注意点

- **教材リポジトリは非公開でもよいが、記事から教材リポジトリへリンクしない**（読者は開けない）。答え合わせ用のコードは公開リポジトリを別に用意してリンクする
- 公開用リポジトリへの複製（`draft-to-publish`）では submodule を持ち込まない。複製対象は `articles/`・`books/`・`images/` だけ
- clone し直した環境では `git submodule update --init` するまで submodule の中は空。空でも壊れてはいない
