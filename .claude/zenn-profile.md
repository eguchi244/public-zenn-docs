# public-zenn-docs のプロファイル

`CLAUDE.md` から読み込まれる、このリポジトリ固有の事実。共通基準は `CLAUDE.md`、コミット手順は `.claude/skills/commit-flow/SKILL.md` にある。

このファイル以外の設定ファイルは他の Zenn リポジトリと同一。**固有の事実はここだけに書く。**

## 連携先

`eguchi244/public-zenn-docs` の **`main` ブランチ**が Zenn ダッシュボードで連携済み。

同じアカウントで `private-zenn-docs` も連携しており、**連携枠は上限に達している**。新規リポジトリの追加連携はできない前提で考える。

## 公開状態

**記事12本・本1冊すべて `published: true`。つまり `main` への push は即座に公開内容へ反映される。**

- 下書きのつもりの変更を `main` に入れない
- マージ前に `npx zenn preview` で最終確認する

## コンテンツ

- `articles/` に単発記事12本（`<slug>.md`）
- `books/laravel-tutorial-books/`（Laravel入門 - Laravelを使ってみよう!）に `config.yaml` + `cover.jpg` + 全18章。ファイル名は `1.laravel-introduction.md` 〜 `18.laravel-todo-app-reference-article.md`

一覧が必要なときは `ls articles books/*/` で見る。

## 画像ディレクトリの方針

**記事と本でルールが違う。**

- 記事: `images/<記事の slug>/`
- 本: **`images/laravel-tutorial-books/` に全18章分の画像をまとめて入れている。章ごとには分けていない**

Paste Image は章のファイル名（`images/5.laravel-todo-app-create-folder/`）へ保存しようとするので、**本のチャプターに画像を貼ったら `images/laravel-tutorial-books/` へ移動し、参照パスを書き換える。** そのまま放置すると既存の構成と分裂する。

参照例: `![](/images/sql-postresql-install-20230620/2023-06-20-15-03-17.png)`

本の1章が `images/laravel-and-docker-introduction-20230822/`（記事側のディレクトリ）を参照している箇所がある。画像の使い回しで参照は解決するので壊れてはいない。**ディレクトリを整理するときだけ意識する。**

## config.yaml の現状

- **`chapters:` が値なしで残っている。** zenn-cli 0.1 系は `null` 扱いでファイル名順にフォールバックするため現状は動いている。**zenn-cli を上げるときはこの行を削除する**（0.5 系はエラーにする）
- zenn-cli は `^0.1.156`
- 複数行 `summary` の継続行が**インデント無し**で書かれている。現行 CLI では通るが `YAMLException: deficient indentation` を起こしやすい箇所。`summary` を編集したら必ず `npx zenn preview` を起動してエラーが出ないことを確認する。ここが壊れると本が丸ごと表示されなくなる

## slug の例外

以下は命名ルールから外れているが**既に公開済みで、slug を変えると URL が変わるため変更しない**。

| slug | 外れている点 |
|---|---|
| `laravel-env-config-setting` | 記事だが末尾に年月日が無い |
| `laravel-tutorial-books` | 本だがユーザー名サフィックスが無い |

ルールは新規作成にのみ適用する。

## コミット履歴の慣習

```
[LaravelのENVとConfigの違いを理解する]を投稿
[Laravel9をDockerで導入してみよう]を修正
[Laravelを使ってみよう]表紙を修正
[Laravelを使ってみよう][入門11 - ToDoアプリの認証機能を作るPart1]を修正
各記事を修正
ClaudeCodeの設定を導入
```

- 本のチャプター単位の修正は `[本の名前][チャプターの見出し]を修正` と**角括弧を2つ重ねる**
- 複数の記事にまたがる修正は `各記事を修正` / `各ページを修正`
- 設定変更や CLI 更新は角括弧なしの日本語件名
- 履歴の前半には角括弧なしで記事名を書いた古い書式（`MacでPostgreSQLをインストールするを投稿`）も残っているが、**新しく書くものは角括弧付きに揃える**
- **ブランチ運用は導入済み**（`feature/xxxをマージ` のマージコミットが履歴にある）。ただし履歴の大半は `main` 直コミットなので、古いコミットに feature ブランチの痕跡が無くても誤りではない
