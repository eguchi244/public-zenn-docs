# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリについて

Zenn（zenn.dev）のコンテンツを GitHub 連携で管理する執筆リポジトリ。コードベースではなく Markdown コンテンツが成果物で、ビルドもテストも無い。**`main` への push が Zenn への本番デプロイ**である点が最大の特徴。

構成は次の2記事に準拠している。判断に迷ったらここへ戻る:

- GitHub 連携: https://zenn.dev/eguchi244_dev/articles/github-zenn-linkage-20230501
- 画像管理: https://zenn.dev/eguchi244_dev/articles/github-zenn-img-mgmt-20230511

**このファイルは同じ基準で構成された Zenn リポジトリ間で共通**で、リポジトリごとに違う事実は一切書かない。連携先・公開状態・コンテンツの実状・画像ディレクトリの切り方などは `.claude/zenn-profile.md` にある。**作業を始める前に必ずプロファイルを読む。**

## コマンド

```bash
npm install                      # 初回・node_modules が無いとき
npx zenn preview                 # http://localhost:8000 でプレビュー
npx zenn preview --port 8888     # ポート競合時
npx zenn new:article --slug <slug>
npx zenn new:book --slug <slug>
npx zenn --version
```

プレビューは**表示確認だけでなく設定の検証も兼ねる**。`config.yaml` や frontmatter に不備があると、サーバー起動ログと本の「設定」ページにエラーが出る。変更後は必ず一度起動して確認する。

## デプロイと連携

- Zenn ダッシュボードで連携したリポジトリの**連携ブランチ**（通常は `main`）に push すると自動デプロイされる。連携先はプロファイル参照
- Zenn は**1アカウントで連携できるリポジトリ数に上限がある**。新規リポジトリを作る前に、既存の連携枠が空いているか確認する
- GitHub 連携後は **Zenn の Web エディタから投稿・編集はできない**（画像アップロードのみ可）
- 公開状態は記事の frontmatter / 本の `config.yaml` の `published` で制御する。**`published: true` のコンテンツは push した時点で公開に反映される**。このリポジトリの現在の公開状態はプロファイルの「公開状態」を見る

## ディレクトリ構成

```
articles/   単発記事。<slug>.md
books/      本。<slug>/config.yaml + <番号>.<name>.md
images/     画像。詳細は下記
```

### 本のチャプター

ファイル名は `<番号>.<name>.md`（例 `1.docker-introduction.md`、`13.docker-compose-command.md`）。番号プレフィックスによるファイル名順に並ぶ。

`example.md` のように番号プレフィックスが無いファイルはプレビュー上「除外」と表示され、本には含まれない。

**`config.yaml` に `chapters:` は書かない**（キーごと省く）のが安全。ここは zenn-cli のバージョンで挙動が変わる非互換ポイントで、

- 0.5 系: 空の `chapters:` はエラーになる
- 0.1 系: 空の `chapters:` を `null` として扱い、ファイル名順にフォールバックする

古いリポジトリには空の `chapters:` が残っていることがある。**zenn-cli を上げるときは同時に空の `chapters:` を削除する。** 現状はプロファイルの「config.yaml の現状」を見る。

### config.yaml の書き方

複数行の `summary` は**継続行と閉じクォートを2スペースでインデントする**。インデントを省いた書き方は古い zenn-cli では通ってしまうが、`YAMLException: deficient indentation` を起こすと**本が丸ごと表示されなくなる**。`summary` を編集したら必ず `npx zenn preview` を起動してエラーが出ないことを確認する。

```yaml
title: "本のタイトル"
summary: "
  1段落目。

  2段落目。
  " # 本の紹介文
topics: ["Docker", "WSL2", "初心者"]
published: false
price: 0
toc_depth: 3
```

## 画像

`.vscode/settings.json` の Paste Image 拡張が、貼り付け時に `images/${currentFileNameWithoutExt}/` へ保存し `/images/<ファイル名>/<画像名>.png` の Markdown を挿入する。

- 画像ファイル名は `YYYY-MM-DD-HH-MM-SS.png`（スクリーンショットの日時）
- 参照は絶対パス `![](/images/<ディレクトリ>/2023-05-19-15-03-17.png)`
- 幅指定は Zenn 独自記法 `![](/images/.../x.png =600x)`
- **画像を Git LFS で管理しない**（Zenn 連携が正しく動かない）
- **ディレクトリ名は参照側と完全一致させる（大文字小文字も）。** 開発環境は Windows で大文字小文字を区別しないが、Zenn のデプロイ先は区別する。ローカルで表示できてもデプロイ後に画像が出ない事故につながる

### ディレクトリの切り方

記事に貼る場合、Paste Image の保存先は記事の slug と一致するのでそのままでよい。

**本のチャプターに貼る場合は注意する。** Paste Image は章のファイル名のディレクトリ（`images/2.docker-summary/`）に保存するが、本の画像を**章ごとに分けるか本の slug 単位に集約するかはリポジトリごとに方針が違う**。集約する方針のリポジトリでは、貼った後に画像を移動して参照パスを書き換える。どちらの方針かはプロファイルの「画像ディレクトリの方針」を見る。

記事や本を削除するときは、対応する `images/<name>/` も一緒に消す。消し漏れると孤児画像として残り続ける。

## slug の付け方

**他ユーザーと重複した slug はデプロイに失敗する。** 新規作成時のルール:

- 記事は末尾に年月日を付ける（`github-zenn-linkage-20230501`）
- 本はユーザー名を付ける（`docker-introduction-<ユーザー名>`）

**このルールは新規作成にのみ適用する。** 公開済みコンテンツの slug を変えると URL が変わるため、ルールに合っていなくても変更しない。既存の例外はプロファイルの「slug の例外」にある。

## コミットとブランチ

`.claude/skills/commit-flow/SKILL.md` に手順がある。要点:

- `main` に直接コミットせず feature ブランチを切り、`--no-ff` でマージする
- コミット件名は `[<対象記事・本の名前>]を<投稿|修正|削除>`。記事に紐づかない変更（CLI 更新、設定変更など）は角括弧なしの自由な日本語件名
- `git status` の未追跡ファイルは `git add -A` せず中身を見て仕分ける

## コミットしないもの

`.gitignore` 済み: `node_modules`、`.DS_Store`、`.claude/settings.local.json`（個人設定）、`plan/`（`plansDirectory` 設定によりリポジトリ内に生成されるプランファイル）、`.claude/instruction_log.md` と `.claude/instruction_log.error.txt`（下記フックの出力）。

`.mcp.json`、`.claude/settings.json`、`.claude/skills/`、`.claude/hooks/`、`.claude/zenn-profile.md` は共有資産としてコミットする。

## フック

`.claude/settings.json` の `SessionEnd` が `.claude/hooks/save_instruction_log.ps1` を呼び、そのセッションでユーザーが出した指示を `.claude/instruction_log.md` へ追記する。**スクリプトは共有資産、出力ログは各自の手元に残すもの**なので、前者だけをコミットする。

フックの登録内容を変えたら、**新しいセッションを開始しないと反映されない**（起動時にスナップショットされる）。`/hooks` で現在の登録を確認できる。

## 他の Zenn リポジトリへ適用する

この設定一式は他の Zenn リポジトリへそのまま持ち込める。手順は `.claude/skills/zenn-repo-setup/SKILL.md`（共通ファイルのコピー → リポジトリ調査 → プロファイル生成）。

**共通ファイル（このファイル・`.claude/skills/`・`.claude/hooks/`・`.claude/settings.json`・`.mcp.json`・`.vscode/settings.json`・`.gitignore`）にリポジトリ固有の事実を書き足さない。** 固有の事実が出てきたらプロファイル側へ書く。

## このリポジトリ固有の情報

@.claude/zenn-profile.md
