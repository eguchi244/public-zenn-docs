---
name: commit-flow
description: 変更をコミットして main へマージする。「コミット・プッシュ・マージして」「ブランチ削除して」と頼まれたとき、または一区切りついた変更をリポジトリへ反映するときに使う。feature ブランチ作成 → 日本語コミット → push → --no-ff マージ → push → ブランチ削除の一連。
---

# コミット〜マージの手順

**main に直接コミットしない。** 必ず feature ブランチを切る。

> このリポジトリの既存履歴は `main` 直コミットで、マージコミットは存在しない。ブランチ運用はこのスキルから導入する方針。過去のコミットに feature ブランチの痕跡が無くても誤りではない。

## 1. 着手前に状態を確認する

```bash
git status --short
git branch -vv
git diff --stat
```

差分の中身を読んで、**何をした変更なのかを自分で説明できる状態にしてからコミットする**。`git status` に出ている未追跡ファイルは、必ず中身を確認して仕分ける（後述）。

## 2. feature ブランチを作る

```bash
git switch -c feature/<内容>
```

## 3. 論理的なまとまりごとにコミットする

1つの変更に複数のテーマが混ざっている場合はコミットを分ける。ただし**同じファイルの同じ箇所に絡み合っている場合は無理に分けない**（部分ステージングは事故のもと）。

コミットメッセージは**日本語**。書式:

```
[<対象記事・本の名前>]を<投稿|修正|削除>

<なぜそうしたか。背景と判断>

- <変更点>
- <変更点>

検証: <実際に確認したこと。やっていないことは書かない>

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: <セッションURL>
```

- 件名は既存履歴の書式に揃える。プレフィックスは付けない

  ```
  [LaravelのENVとConfigの違いを理解する]を投稿
  [Laravel9をDockerで導入してみよう]を修正
  [Laravelを使ってみよう]表紙を修正
  [Laravelを使ってみよう][入門11 - ToDoアプリの認証機能を作るPart1]を修正
  ```

- 本のチャプター単位の修正は `[本の名前][チャプターの見出し]を修正` と角括弧を2つ重ねる書き方が履歴にある
- 複数の記事にまたがる修正は `各記事を修正` / `各ページを修正` が使われている
- 記事・本に紐づかない変更（CLI 更新、設定変更など）は角括弧なしの自由な日本語件名でよい（例: `ZennCLIをアップデート`）
- 履歴の前半には角括弧なしで記事名を書いた古い書式（`MacでPostgreSQLをインストールするを投稿`）も残っているが、**新しく書くものは角括弧付きに揃える**
- **検証欄には実際に実行したことだけを書く。** 「`npx zenn preview` で表示を確認」と書くなら本当に起動して見ていること

## 4. プッシュしてマージする

> **`main` への push は Zenn への本番デプロイ。** このリポジトリの記事12本・本1冊はすべて `published: true` なので、マージした内容はそのまま公開ページに反映される。マージ前に `npx zenn preview` で最終確認する。

```bash
git push -u origin feature/<内容>
git switch main
git merge --no-ff feature/<内容> -m "feature/<内容>をマージ"
git push origin main
```

マージメッセージは `feature/xxxをマージ` の形に固定。

## 5. ブランチを削除する

**削除は依頼されてから行う。** 頼まれていなければ 4 で止めて、一言添えて確認する。

```bash
git branch -d feature/<内容>
git push origin --delete feature/<内容>
git remote prune origin
```

## 6. 最終確認

```bash
git branch -a && git status --short && git log --oneline -3
```

---

## 未追跡ファイルの仕分け

`git status` の `??` は機械的に `git add -A` せず、中身を見て判断する。このリポジトリで実際に出るもの:

| 種類 | 対処 |
|---|---|
| `.claude/settings.local.json`（個人設定） | コミットしない。`.gitignore` 済み |
| `plan/`（プランファイル） | コミットしない。`.gitignore` 済み |
| `.mcp.json`、`.claude/settings.json`、`.claude/skills/` | 共有資産としてコミットする |
| `images/` 配下の貼り付け画像 | 記事から参照されていればコミット。孤児画像はユーザーに確認する |

**本のチャプターに画像を貼った場合は要注意。** Paste Image は `images/<チャプターのファイル名>/` に保存するが、この本の画像は `images/laravel-tutorial-books/` に集約されている。コミット前に移動と参照パスの書き換えを済ませる（`CLAUDE.md` の「画像」節を参照）。

## 注意点

- 改行コードだけの差分（`git status` は `M` だが `git diff` が空）は、ステージしても内容が変わらない。無理に含めなくてよい
- ファイル名を変えた場合は `git add -A` すれば Git がリネームとして認識する
