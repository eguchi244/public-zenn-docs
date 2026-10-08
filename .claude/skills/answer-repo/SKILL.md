---
name: answer-repo
description: 本・記事の章末に置く「答え合わせ用ソースコード」の公開リポジトリを GitHub に作成し、章ごとのブランチに解答コードを置いて push する。「答え合わせ用のリポジトリを作って」「章ブランチを作って」と頼まれたとき、教材リポジトリの解答コードを公開するとき、解答コードの修正を公開リポジトリへ反映するときに使う。中身の確認 → ローカルで章ブランチを積み上げ → gh で公開リポジトリ作成 → push → URL 確認の一連。
---

# 答え合わせ用の公開リポジトリを作る

> このスキルは同じ基準で構成された Zenn リポジトリ間で共通。教材リポジトリの場所はプロファイルの「教材リポジトリ」、既存の答え合わせ用リポジトリの例は同節にある。

教材リポジトリが非公開でも、章末の答え合わせリンクは**読者が開ける公開リポジトリ**に向ける。アプリ（本）ごとに1リポジトリ作り、章ごとにブランチを切る。

## 型（既存の `Laravel9-Tutorial-PJ` に合わせる）

- リポジトリ名: `<題材>-Tutorial-PJ`（例: `JS-Timer-Tutorial-PJ`）
- ブランチ: `Chapter<NN>/<章の見出し>`（例: `Chapter03/シンプルなストップウォッチを作る`）。**その章を終えた時点のプロジェクト全体**を置く。前の章のブランチから派生させて積み上げる
- `main`: 完成版（最終章のブランチと同じ内容）
- コードの無い章（イントロ・設計）にはブランチを作らない
- 章末の定型文:
  ```
  ここまでのソースコードを下記に掲載しておきます。
  確認などにご活用ください。
  https://github.com/<ユーザー>/<リポジトリ>/tree/Chapter<NN>/<章の見出し>
  ```

## 前提

`gh`（GitHub CLI）でログイン済みであること。

```bash
"C:/Program Files/GitHub CLI/gh.exe" auth status      # ✓ Logged in と repo スコープ
```

未ログインなら、ユーザーに PowerShell で次を実行してもらう（ブラウザでの認可が要るので代行できない）。`!` を付けず、パスの前に `&` を付ける。SSH 鍵のアップロードは、既に push できているなら Skip:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" auth login --hostname github.com --git-protocol ssh --web
```

## 1. 公開する中身を確認する

**公開リポジトリは作った瞬間から誰でも見られる。** 作る前に確認する。

- 載せるのは教材の解答コード（教材リポジトリのプロファイルで言う `practice/ans/phaseNN/` や `ans/phaseNN/`）と完成版、読者向け README だけ
- 個人のパス・メモ・認証情報・`.env`・`venv` などが混ざっていないか grep する
  ```bash
  grep -rniE 'C:\\\\|Users|password|token|secret|@gmail' <解答コードのパス>
  ```
- 最終フェーズの解答と完成版の差分を確認する（同じはずのものが食い違っていたらユーザーに確認）
- リポジトリ名・ブランチ名（章の見出し）をユーザーに提示し、確認を取ってから作成する

## 2. ローカルで章ブランチを積み上げる

作業はスクラッチパッドなど、どのリポジトリにも属さないフォルダで行う。

```bash
git init -b main && git config core.autocrlf false
# 読者向け README（本の名前・ブランチ表・動かし方）を書いてコミット
git add README.md && git commit -m "READMEを追加"
git switch -c "Chapter03/<見出し>"   # phase01 の解答をコピーしてコミット
git switch -c "Chapter04/<見出し>"   # phase02 の解答で上書きしてコミット（前章から派生）
# ... 最終章まで
git switch main && git merge --ff-only "Chapter<最終>/<見出し>"
```

コミットメッセージは `入門NN <章の見出し>` の形。README には章とブランチの対応表を置く。

## 3. 公開リポジトリを作って push する

```bash
gh repo create <ユーザー>/<リポジトリ> --public --description "Zennの本「<本の名前>」の答え合わせ用ソースコード"
git remote add origin git@github.com:<ユーザー>/<リポジトリ>.git
git push -u origin --all
```

## 4. URL を確認する

章末に書く URL が開けることを確認する。**日本語のブランチ名は curl にそのまま渡すと 404 になる**（ブラウザは自動でエンコードするので読者は開ける）。確認時はエンコードする:

```bash
python -c "import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))" "<ユーザー>/<リポジトリ>/tree/Chapter03/<見出し>"
curl -s -o /dev/null -w '%{http_code}' "https://github.com/<上の出力>"   # 200
```

## 解答コードを直したとき

教材リポジトリで解答コードを直したら、該当章のブランチ**とそれ以降の章のブランチ・`main`** にも反映する（積み上げ型なので後の章も同じ箇所を含む）。反映後は章末リンクの中身と本文のコードが食い違っていないか確認する。
