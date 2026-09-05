# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリについて

Zenn（zenn.dev）のコンテンツを GitHub 連携で管理する執筆リポジトリ。コードベースではなく Markdown コンテンツが成果物で、ビルドもテストも無い。**`main` への push が Zenn への本番デプロイ**である点が最大の特徴。

構成は作者自身の解説記事に準拠している。判断に迷ったらこの2本を参照する:

- GitHub 連携: https://zenn.dev/eguchi244_dev/articles/github-zenn-linkage-20230501
- 画像管理: https://zenn.dev/eguchi244_dev/articles/github-zenn-img-mgmt-20230511

## コマンド

```bash
npm install                      # 初回・node_modules が無いとき
npx zenn preview                 # http://localhost:8000 でプレビュー
npx zenn preview --port 8888     # ポート競合時
npx zenn new:article --slug <slug>
npx zenn new:book --slug <slug>
npx zenn --version               # 現在 0.1.156
```

プレビューは**表示確認だけでなく設定の検証も兼ねる**。`config.yaml` や frontmatter に不備があると、サーバー起動ログと本の「設定」ページにエラーが出る。変更後は必ず一度起動して確認する。

## デプロイと公開状態

- Zenn ダッシュボードで `eguchi244/public-zenn-docs` の **`main` ブランチ**が連携済み。push すると自動デプロイされる
- **このリポジトリのコンテンツは記事12本・本1冊すべて `published: true`。つまり `main` への push は即座に公開内容へ反映される。** 下書きのつもりの変更を main に入れない
- Zenn は1アカウントで連携できるリポジトリ数に上限がある。このアカウントは `public-zenn-docs` と `private-zenn-docs` を運用しており、新規リポジトリの追加連携はできない前提で考える
- GitHub 連携後は **Zenn の Web エディタから投稿・編集はできない**（画像アップロードのみ可）
- 公開状態は frontmatter / `config.yaml` の `published` で制御する

## ディレクトリ構成

```
articles/   単発記事 12本
books/      本 1冊（laravel-tutorial-books）
images/     画像 214件 / 11ディレクトリ。詳細は下記
```

### 記事

`articles/<slug>.md`。すべて `published: true`。

| ファイル | タイトル |
|---|---|
| `github-zenn-linkage-20230501.md` | ZennとGithubを連携する方法 |
| `github-zenn-img-mgmt-20230511.md` | Github連携でZennの画像管理をする方法 |
| `google-analytics-zenn-linkage-20230501.md` | ZennにGoogleAnalyticsを導入する |
| `vscode-regexp-search-20230513.md` | VScodeの正規表現での検索方法 |
| `review-knowledge-20230516.md` | レビューの心得 |
| `question-knowledge-20230517.md` | ITエンジニアの質問の心得 |
| `sql-postresql-install-20230620.md` | MacでPostgreSQLをインストールする |
| `laravel-and-docker-introduction-20230822.md` | Laravel9をDockerで導入してみよう! |
| `laravel-vue-docker-introduction-20230828.md` | Laravel9とVue.jsをDockerで導入してみよう! |
| `restore-laravel-vite-to-mix-20230829.md` | LaravelのViteをLaravel Mixに戻す方法 |
| `laravel-react-docker-introduction-20230831.md` | Laravel9とReactをDockerで導入してみよう! |
| `laravel-env-config-setting.md` | LaravelのENVとConfigの違いを理解する |

### 本のチャプター

`books/laravel-tutorial-books/`（Laravel入門 - Laravelを使ってみよう!）に `config.yaml` + `cover.jpg` + 全18章。

ファイル名は `<番号>.<name>.md`（`1.laravel-introduction.md` 〜 `18.laravel-todo-app-reference-article.md`）。**`config.yaml` の `chapters:` は空のまま**で、番号プレフィックスによるファイル名順が使われる（zenn-cli は空の `chapters:` を `null` として扱い、ファイル名順にフォールバックする）。

番号プレフィックスが無い `.md` を置くとプレビュー上「除外」と表示され、本には含まれない。

### config.yaml

現在の内容:

```yaml
title: "Laravel入門 - Laravelを使ってみよう!"
summary: "
...本文...
" # 本の紹介文
topics: ["PHP", "Laravel", "Docker", "初心者"]
published: true
price: 0
toc_depth: 3
chapters:
```

複数行 `summary` の継続行は現状インデント無しで、zenn-cli 0.1.156 では問題なくパースされる。ただし YAML の複数行クォート文字列はインデントの扱いで `YAMLException: deficient indentation` を起こしやすい箇所なので、**`summary` を編集したら必ず `npx zenn preview` を起動してエラーが出ないことを確認する**。ここが壊れると本が丸ごと表示されなくなる。

## 画像

`.vscode/settings.json` の Paste Image 拡張が、貼り付け時に `images/${currentFileNameWithoutExt}/` へ保存し `/images/<ファイル名>/<画像名>.png` の Markdown を挿入する。

- 参照は絶対パス `![](/images/sql-postresql-install-20230620/2023-06-20-15-03-17.png)`
- 幅指定は Zenn 独自記法 `![](/images/.../x.png =600x)`
- **画像を Git LFS で管理しない**（Zenn 連携が正しく動かない）
- **ディレクトリ名は参照側と完全一致させる（大文字小文字も）。** 開発環境は Windows で大文字小文字を区別しないが、Zenn のデプロイ先は区別する。ローカルで表示できてもデプロイ後に画像が出ない事故につながる

### ディレクトリの実際の切り方

**記事は slug 単位、本は本の slug 単位**で、記事側と本側でルールが違う。

- 記事: `images/<記事の slug>/`（10ディレクトリ）
- 本: `images/laravel-tutorial-books/` に**全18章の画像137件がまとめて入っている**。チャプターごとには分けていない

Paste Image はチャプターのファイル名（`images/5.laravel-todo-app-create-folder/`）へ保存しようとするので、**本のチャプターに画像を貼ったら `images/laravel-tutorial-books/` へ移動し、参照パスを書き換える**。そのまま放置すると既存の構成と分裂する。

### 現状の把握

- 参照が解決しない画像パスはコードサンプル内の例示（`/images/blog-slug-name/...`、`${currentFileNameWithoutExt}` など解説記事の中身）だけで、**実際に壊れているリンクは無い**
- どこからも参照されていない画像が3件ある:
  - `images/github-zenn-img-mgmt-20230511/img-2023-05-11-13.50.41.png`
  - `images/laravel-env-config-setting/2023-08-22-13-45-45.png`
  - `images/laravel-env-config-setting/2023-08-24-19-12-39.png`
- 本の1章が `images/laravel-and-docker-introduction-20230822/`（記事側のディレクトリ）を参照している箇所が1件ある。画像の使い回しで、参照は解決するので壊れてはいない

記事や本を削除するときは、対応する `images/<name>/` も一緒に消す。

## slug の付け方

**他ユーザーと重複した slug はデプロイに失敗する。** 新規作成時のルール:

- 記事は末尾に年月日を付ける（`github-zenn-linkage-20230501`）
- 本はユーザー名を付ける（`laravel-tutorial-eguchi244` のように）

ただし**既存の公開済みコンテンツには例外がある**。`laravel-env-config-setting`（日付なし）と `laravel-tutorial-books`（ユーザー名なし）は既に公開済みで、slug を変えると URL が変わるため**変更しない**。ルールは新規作成にのみ適用する。

## コミットとブランチ

`.claude/skills/commit-flow/SKILL.md` に手順がある。要点:

- `main` に直接コミットせず feature ブランチを切り、`--no-ff` でマージする
- コミット件名は `[<対象記事・本の名前>]を<投稿|修正|削除>`。記事に紐づかない変更（CLI 更新、設定変更など）は角括弧なしの自由な日本語件名
- `git status` の未追跡ファイルは `git add -A` せず中身を見て仕分ける

## コミットしないもの

`.gitignore` 済み: `node_modules`、`.DS_Store`、`.claude/settings.local.json`（個人設定）、`plan/`（`plansDirectory` 設定によりリポジトリ内に生成されるプランファイル）。

`.mcp.json` と `.claude/skills/` は共有資産としてコミットする。
