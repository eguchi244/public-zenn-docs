---
title: "MacでPostgreSQLをインストールする"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["SQL", "Database", "PostgreSQL", "macOS"]
published: true # 公開に指定する
---
# はじめに
この記事では **PostgreSQL** をMacでインストールする方法を紹介します。ここでは「インストーラーからインストールする」と「Homebrewからインストールする」を扱います。コマンドに慣れてる人なら圧倒的に Homebrew を使うのが楽です。

# インストーラーからインストールする
下記の手順に沿ってインストールを実施してください。

#### 公式ページにアクセスする
下記から公式ページのダウンロードページにアクセスしてください。
https://www.postgresql.org/download/

#### インストールするPCのOSを選択する（MacOSを選択する）
![](/images/sql-postresql-install-20230620/2023-06-20-18-03-00.png)

#### Download the installer をクリックする
![](/images/sql-postresql-install-20230620/2023-06-20-18-07-46.png)

#### PostgreSQLのバージョンを選択する
![](/images/sql-postresql-install-20230620/2023-06-20-18-10-50.png)

#### DMGファイル（postgresql-15.3-2-osx.dmg）をダブルクリックする
![](/images/sql-postresql-install-20230620/2023-06-20-18-16-27.png =450x)

#### postgresql-15.3-2-osx.app をアプリケーションにドロップする
ドロップしたらダブルクリックして Macのパスワードを打ち込んで先に進んでください。
![](/images/sql-postresql-install-20230620/2023-06-20-18-21-22.png)

#### セットアップ画面で「NEXT」をクリックする
![](/images/sql-postresql-install-20230620/2023-06-20-18-25-57.png =500x)

#### PostgreSQLの保存先を決める
デフォルトのままで「NEXT」をクリックしてください。
![](/images/sql-postresql-install-20230620/2023-06-20-18-28-44.png =500x)

#### PostgreSQLと同時にインストールするコンポーネントを選択する
デフォルトの全て選択された状態で「NEXT」をクリックしてください。
![](/images/sql-postresql-install-20230620/2023-06-20-18-30-51.png =500x)

#### データを保存先を決める
デフォルトのまま「NEXT」をクリックしてください。
![](/images/sql-postresql-install-20230620/2023-06-20-18-32-48.png =500x)

#### スーパーユーザのパスワードを設定する
デフォルトで `postgres` という名前で作成されます。なお、スーパーユーザは、データベース内のアクセス制限をすべて変更することができるユーザーアカウントです。今回はデフォルトの `postgres` のままで設定します。
![](/images/sql-postresql-install-20230620/2023-06-20-18-41-00.png =500x)

#### ポート番号を決める
デフォルトの5432のままで「NEXT」をクリックしてください。
![](/images/sql-postresql-install-20230620/2023-06-20-18-43-41.png  =500x)

#### ロケールを決める
環境に応じて設定してくれるのでデフォルトの［Default locale］のままで「NEXT」をクリックしてください。
![](/images/sql-postresql-install-20230620/2023-06-20-18-45-57.png =500x)

#### 確認画面で「NEXT」をクリックする
![](/images/sql-postresql-install-20230620/2023-06-20-18-47-31.png =500x)

#### インストールを「NEXT」をクリックして開始する
![](/images/sql-postresql-install-20230620/2023-06-20-18-50-11.png =500x)

セットアップが完了したのでFinishを押して終了してください。

Launch Stack Builderのチェックを入れて終了すると追加のツールをインストールできます。（Stack Builderの画面が立ち上がります。）

特別なことが無ければチェックを外してFinishで終了してください。

# Homebrewからインストールする
#### Homebrewを確認してアップデートする
```js:Terminal
$ brew --version
$ brew update
$ brew brew upgrade
$ brew cleanup # 不要な formulae を削除
```

#### インストールできるpostgreSQLを確認する
```js:Terminal
$ brew search postgresql
```

#### PostgreSQlをインストールする
※バージョンを指定する場合は `@` 以降に確認したバージョンを記述する
```js:Terminal
$ brew install postgresql
```

#### バージョンの確認をする
```js:Terminal
$ psql --version
```

#### PostgreSQLを起動する
```js:Terminal
$ brew services start postgresql
Warning: Formula postgresql was renamed to postgresql@14.
==> Successfully started `postgresql@14` (label: homebrew.mxcl.postgresql@14)
```

#### PostgreSQLに接続する
```js:Terminal
# ログイン
$ psql postgres
# パスワード設定（デフォルトで設定）
postgres=#  postgres
# ログアウト
postgres=# \q
```

これにより下記のように設定された状態になります。
| 名称 | 設定値 | 備考 |
| ---- | :---- | :---- |
| ホスト名  | localhost | localhostの場合 |
| ポート番号  | 5432 | デフォルト |
| ロール名（ユーザー名）  | **** | ※スーパーユーザー |
| データベース名  | postgres | デフォルト |

※ スーパーユーザーは、データベース内のアクセス制限をすべて変更することができます

次回からは`psql -h ホスト名 -p ポート番号 -U ロール名 -d データベース名` でも接続をできます。
```js:Terminal
$ psql -h localhost -p 5432 -U **** -d postgres
```