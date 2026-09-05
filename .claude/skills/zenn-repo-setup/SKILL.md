---
name: zenn-repo-setup
description: 新しい Zenn リポジトリに、この基準の Claude Code 設定一式を適用する。「別の Zenn リポジトリにも同じ設定を入れて」「zenn-profile を作り直して」と頼まれたとき、またはコンテンツ構成が大きく変わってプロファイルを更新するときに使う。共通ファイルのコピー → リポジトリ調査 → .claude/zenn-profile.md 生成の一連。
---

# Zenn リポジトリへのセットアップ

対象は [GitHub 連携](https://zenn.dev/eguchi244_dev/articles/github-zenn-linkage-20230501) / [画像管理](https://zenn.dev/eguchi244_dev/articles/github-zenn-img-mgmt-20230511) の基準で構成された Zenn リポジトリ。

設定は2層に分かれている。**この分離を崩さないことがこのスキルの目的**:

| 層 | ファイル | 性質 |
|---|---|---|
| 共通 | `CLAUDE.md`、`.claude/skills/`、`.claude/hooks/`、`.claude/settings.json`、`.mcp.json`、`.vscode/settings.json`、`.gitignore` | 全リポジトリで**バイト単位で同一**。そのままコピーする |
| 固有 | `.claude/zenn-profile.md` | このリポジトリだけの事実。調査して生成する |

**共通ファイルにリポジトリ固有の事実（記事名、件数、公開状態、バージョン）を書き足さない。** それをやると汎用性が失われる。固有の事実はすべてプロファイル側に書く。

## 1. 共通ファイルをコピーする

既存の Zenn リポジトリをコピー元にする。

```bash
SRC=<コピー元リポジトリのパス>
DST=<セットアップ先のパス>

mkdir -p "$DST/.claude" "$DST/.vscode"
cp "$SRC/CLAUDE.md"               "$DST/CLAUDE.md"
cp "$SRC/.claude/settings.json"   "$DST/.claude/settings.json"
cp -r "$SRC/.claude/skills"       "$DST/.claude/"
cp -r "$SRC/.claude/hooks"        "$DST/.claude/"
cp "$SRC/.mcp.json"               "$DST/.mcp.json"
cp "$SRC/.vscode/settings.json"   "$DST/.vscode/settings.json"
cp "$SRC/.gitignore"              "$DST/.gitignore"
```

`.gitignore` が既にある場合は上書きせず、`node_modules` / `.DS_Store` / `.claude/settings.local.json` / `plan/` / `.claude/instruction_log.md` / `.claude/instruction_log.error.txt` の6項目が揃っているか確認して足りない分だけ追記する。

`.claude/settings.local.json`（`plansDirectory`、`enabledMcpjsonServers`）は個人設定なのでコピーしない。必要なら各自で作る。

## 2. リポジトリを調査する

**推測で書かない。** 以下を実際に実行して、出力から事実を拾う。

```bash
git remote -v                                   # 連携先リポジトリ
git branch --show-current                       # 連携ブランチ
grep -h '^published' articles/*.md              # 記事の公開状態
grep -h '^published' books/*/config.yaml        # 本の公開状態
ls articles books images                        # コンテンツ棚卸し
grep -n 'chapters:' books/*/config.yaml         # 空の chapters: が残っていないか
grep zenn-cli package.json                      # zenn-cli のバージョン
git log --oneline -20                           # コミット件名の慣習
git log --merges --oneline | head -3            # ブランチ運用が入っているか
```

画像ディレクトリの方針は `ls images` の結果を記事 slug・本 slug・章ファイル名と突き合わせて判定する:

- ディレクトリ名が記事の slug と一致 → 記事 slug 単位
- ディレクトリ名が本の slug と一致し、その中に複数章分の画像がある → **本の slug 単位に集約**
- ディレクトリ名が `2.docker-summary` のように章ファイル名と一致 → 章ファイル名単位

孤児画像や参照ズレを確認するときは、`images/` 配下のディレクトリ名が `.md` から参照されているかを grep で突き合わせる。ただし**個別のファイル名や件数はプロファイルに書かない**（すぐ古くなる）。方針として意識すべき事実だけ書く。

## 3. `.claude/zenn-profile.md` を生成する

見出し構成は固定。**調査で確認した事実だけを書く。** 確認していないことは書かない。

```markdown
# <リポジトリ名> のプロファイル

`CLAUDE.md` から読み込まれる、このリポジトリ固有の事実。共通基準は `CLAUDE.md`、コミット手順は `.claude/skills/commit-flow/SKILL.md` にある。

## 連携先
## 公開状態
## コンテンツ
## 画像ディレクトリの方針
## config.yaml の現状
## slug の例外
## コミット履歴の慣習
```

各節に書くこと:

- **連携先** — Zenn と連携している GitHub リポジトリと連携ブランチ
- **公開状態** — `published: true` / `false` の内訳。**push が即公開に反映されるかどうか**を明記する。ここが最も事故に直結する
- **コンテンツ** — 記事・本のおおまかな構成（本の slug と章数など）。記事の全一覧表は作らない
- **画像ディレクトリの方針** — 記事側・本側それぞれの切り方。集約している場合は「貼った後に移動が必要」と明記
- **config.yaml の現状** — `chapters:` の有無、zenn-cli のバージョン、複数行 `summary` の書き方の実状
- **slug の例外** — 命名ルールから外れているが公開済みで変更できない slug。無ければ「無し」
- **コミット履歴の慣習** — 実際の件名の実例を3〜5個。ブランチ運用が入っているかどうか

## 4. 動作を確認する

```bash
npm install
npx zenn preview     # エラーが出ないこと。確認したら停止する
```

`CLAUDE.md` 末尾の `@.claude/zenn-profile.md` が解決しているかは、Claude Code を起動して `/context` にプロファイル内の固有語が含まれるかで確認できる。

## 5. コミットする

`commit-flow` スキルに従う。件名は `ClaudeCodeの設定を導入` のような角括弧なしの日本語で構わない。
