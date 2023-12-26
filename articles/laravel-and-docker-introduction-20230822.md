---
title: "Laravel9をDockerで導入してみよう!"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Laravel", "PHP", "Docker", "dockercompose"]
published: true # 公開に指定する
---
# はじめに
この記事では「LaravelをDockerで簡単に構築すること」を目指します。
Dockerを使って少ない労力で環境構築できるようになりたい方のための記事です。
![](/images/laravel-and-docker-introduction-20230822/2023-08-22-13-10-28.png =500x)

## 記事の改訂について
Laravelの環境設定に関する詳細な解説は下記の記事に移転しました。
「LaravelをDockerで簡単に構築すること」の趣旨に反すると判断したからです。
ご理解のほど宜しくお願い致します。
https://zenn.dev/eguchi244_dev/articles/laravel-env-config-setting

# 前提条件
この記事では以下の知識を持つことを前提にしています。

- HTML&CSS, PHPをある程度は理解している
- Linuxコマンドに触れたことがある

これらについては詳細に解説することはありませんのでご承知ください。

# 環境構築の目標
環境構築の目標は「Dockerによる仮想環境で、Laravelを使用できるようにする」ことです。
具体的には以下の構成で環境構築をします。

:::message
【前提条件】
PCに下記がインストールと設定がされていることが前提です。

- Linux/Unix開発環境
    - Windows ： WSL2（Ubuntu）
- Docker, Docker-compose
- composer
- npm
:::

:::message
【環境構築の目標】
- フレームワーク：Laravel Framework 9.x.x(Vite)
- データベース：MYSQL 5.7.36
- DB管理ツール : phpMyAdmin latest
- PHP：PHP 8.0.x
- Nginx：Nginx latest
- Node.js：node 14.18-alpine
:::

:::message
【ディレクトリ構成】
```js:
Laravel9-Docker-TestPJ（ルートディレクトリ）※ 任意の名前でOK
├── docker-compose.yml
├── docker 
│   ├── php 
│   │   ├── Dockerfile 
│   │   └── php.ini 
│   └── nginx 
│       └── default.conf 
├── phpMyAdmin
└── src 
    └──  Laravel9TestProject（Laravelのプロジェクトディレクトリ）※ 任意の名前でOK
```
:::

# Laravelとフレームワーク
### Laravelとは
Laravel（ララベル）とは、PHPのフレームワークです。

手軽で扱いやすく、代表的なPHPフレームワークの1つとして認識されています。PHPフレームワークのSymphony（シンフォニー）を基に開発されたため、これまでのタイプに慣れている方でも比較的扱いやすい仕様となっています。

PHPフレームワークの中では、フレームワークサイズ・学習コストの両面で中間的な立ち位置にあるため、「ちょうど良い」と評されています。

### フレームワークとは
フレームワークとは、アプリケーション開発の際に土台となるソフトウェアのことです。

アプリケーションの枠組み・骨組み・構造部になるため、一般的にはフレームワーク内に必要な機能を追加しながら開発を進めます。Webアプリケーションフレームワークやユーティリティ系フレームワークなど、用途に応じていくつかの種類が存在しています。さらに、高い汎用性・充実した機能性・限定的な機能で軽量など様々なタイプがあります。

### Laravelの特徴
Laravelは下記の11個の特徴を持ったフレームワークです。

1. 世界で最も人気のPHPフレームワーク
2. Symphony（シンフォニー）を土台に作成されている
3. MVCモデルを採用している
4. 機能やプラグインの開発が盛んである
5. 学習コストが中程度で教材が豊富で学習がしやすい
6. Composerでパッケージ管理できる
7. 拡張性と自由度が高い
8. データベースの操作が容易である
9. コマンドツールによって設定や更新が簡単である
10. バリデーションチェックを自動でやってくれる
11. Viewに軽量なテンプレートが使われている

これらの特徴により愛され人気を得ているフレームワークなのです。
より詳しく特徴を知りたい方は下記のサイトをご覧ください。
とても分かりやすく易く参考になります。

https://www.acrovision.jp/career/?p=2776

## MVCモデルとは
Laravel で採用されている **MVCモデル** を確認しておきましょう。

**MVCモデル** とは、プログラムを役割ごとにModel（モデル）・View（ビュー）・Controller（コントローラー）の3つに分けて管理するソフトウェア設計モデルのことです。

**Model（モデル）とは** 
システム内部のビジネスロジックを担当する部分です。

DBとデータをやり取りしたり、データの登録・更新・削除などの処理を行います。

DBから取得したデータや処理の結果はControllerに送ります。

**View（ビュー）とは** 
表示や入出力などのユーザーが実際に見る画面（UI）を担当する部分です。 

リクエストデータをControllerに送ったり、Controllerからレスポンスデータを受け取って画面に表示したりします。

**Controller（コントローラー）とは**
ユーザーの入力に基づいてモデルとビューを制御（橋渡し）する役目を担う部分です。

ユーザーが入力した情報に基づいて、モデルへデータを取り出す指示を、ビューにはモデルで取り出したデータを元に画面を表示する指示を出します。

詳しく知りたい方は下記のサイトが分かり易くておすすめです。
https://system-kaihatu.com/archives/3204

:::message
ModelとViewの違い

Model : データの管理や保存、外部との入出力、内部的な処理を担当する。
View : 利用者に対する画面表示や入力・操作の受け付けなど、外部的な処理を担当する。
:::
:::message
ModelとControllerの違い

Model : データの管理や保存、外部との入出力、内部的な処理を担当する。
Controller : ModelとViewの制御（橋渡し）を担当する。
:::
:::message
ControllerとViewの違い

View : 表示、入出力の処理を担当する。
Controller : ModelとViewの制御（橋渡し）を担当する。
:::

# Laravelを導入する
さっそくLaravelを導入していきましょう！下記の手順を実施してください。

1. ルートディレクトリを作成する  

任意のディレクトリに「Laravel9-Docker-TestPJ」を作成します。
```js:Terminal
$ mkdir Laravel9-Docker-TestPJ
~Laravel9-Docker-TestPJ $ cd Laravel9-Docker-TestPJ
```
2. docker-compose.ymlファイルを作成して編集する

`docker-compose.yml` は Docker Compose を利用するために使用するYMLファイルです。
```js:Terminal
$ touch docker-compose.yml
```
:::details docker-compose.yml の記述内容
```js:docker-compose.yml
version: '3'
services:
  db:
    image: mysql:5.7.36
    container_name: "mysql_test"
    environment:
        MYSQL_ROOT_PASSWORD: root
        MYSQL_DATABASE: mysql_test_db
        MYSQL_USER: admin
        MYSQL_PASSWORD: secret
        TZ: 'Asia/Tokyo'
    # ポートフォワードの指定（ホスト側ポート：コンテナ側ポート）
    ports:
        - 3306:3306
    # コマンドの指定
    command: mysqld --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    # 名前付きボリュームを設定する（名前付きボリューム:コンテナ側ボリュームの場所）
    volumes:
      - db_data_test:/var/lib/mysql
      - db_my.cnf_test:/etc/mysql/conf.d/my.cnf
      - db_sql_test:/docker-entrypoint-initdb.d

  php:
    build: ./docker/php
    container_name: "php-fpm"
    # ボリュームを設定する（ホスト側ディレクトリ:コンテナ側ボリュームの場所）
    volumes:
      - ./src:/var/www

  nginx:
    image: nginx:latest
    container_name: "nginx_test"
    # ポートフォワードの指定（ホスト側ポート：コンテナ側ポート）
    ports:
      - 80:80
    # ボリュームを設定する（ホスト側ディレクトリ:コンテナ側ボリュームの場所）
    volumes:
      - ./src:/var/www
      - ./docker/nginx/default.conf:/etc/nginx/conf.d/default.conf
    # サービスの依存関係を指定（nginxをphpに依存させる）
    depends_on:
      - php

  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    container_name: "phpmyadmin_test"
    environment:
      - PMA_ARBITRARY=1 # サーバ設定：サーバーをローカル以外も指定
      - PMA_HOST=db # ホスト設定：dbを指定
      - PMA_USER=admin # 初期ユーザー設定：adminを指定
      - PMA_PASSWORD=secret # 初期PW設定：secretを指定
    # db（サービス名）とのリンクを設定する
    links:
      - db
    # ポートフォワードの指定（ホスト側ポート：コンテナ側ポート）
    ports:
      - 8080:80
    # ボリュームを設定する（ホスト側ディレクトリ:コンテナ側ボリュームの場所）
    volumes:
      - ./phpmyadmin/sessions:/sessions

  node:
    image: node:14.18-alpine
    container_name: "node14.18-alpine"
    # コンテナ内の標準出力とホストの出力を設定：trueを指定
    tty: true
    # ボリュームを設定する（ホスト側ディレクトリ:コンテナ側ボリュームの場所）
    volumes:
      - ./src:/var/www
    # コンテナ起動後のカレントディレクトリを設定
    working_dir: /var/www

# サービスレベルで名前付きボリュームを命名する
volumes:
  db_data_test:
  db_my.cnf_test:
  db_sql_test:
```

:::

3. ルートディレクトリ直下に `¥docker` `¥src` を作成する
```js:Terminal
~Laravel9-Docker-TestPJ $ mkdir docker && mkdir src
```

4. `¥docker` 直下に `¥php` `¥nginx` を作成する
```js:Terminal
~Laravel9-Docker-TestPJ $ cd docker
~docker$ mkdir php && mkdir nginx
```

5. `¥php` 直下に `Dockerfile` `php.ini` を作成して編集する
```js:Terminal
~docker $ cd php
~php $ touch Dockerfile && touch php.ini
```
:::details Dockerfile の記述内容
**Dockerfileとは**
Dockerfileは、Dockerコンテナをビルドするための指示を含むテキストファイルです。

Dockerfileを使用することで、特定の環境でアプリケーションを実行するために必要な手順を自動化することができます。

Dockerfileは、コンテナ内にどのようなファイルや設定を配置するか、どのベースイメージを使用するか、どのコマンドを実行するかなど、コンテナの構築に関する情報を提供します。

```js:Dockerfile
# Dockerimage の指定
FROM php:8.0-fpm
COPY php.ini /usr/local/etc/php/

# Package & Library install
RUN apt-get update \
    && apt-get install -y zlib1g-dev mariadb-client vim libzip-dev \
    && docker-php-ext-install zip pdo_mysql

# Composer install
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
RUN php composer-setup.php
RUN php -r "unlink('composer-setup.php');"
RUN mv composer.phar /usr/local/bin/composer

ENV COMPOSER_ALLOW_SUPERUSER 1
ENV COMPOSER_HOME /composer
ENV PATH $PATH:/composer/vendor/bin

# WorkDir Path setting
WORKDIR /var/www

# Laravel Package install
RUN composer global require "laravel/installer"
```
:::

:::details php.ini の記述内容
**php.iniとは**
php.ini は、PHPの設定ファイルであり、PHPの動作や機能をカスタマイズするための設定を含むファイルです。PHPの挙動を細かく制御するためには php.ini ファイルを使用します。

```js:php.ini
; 日付設定
[Date]
date.timezone = "Asia/Tokyo"
; 文字＆言語設定
[mbstring]
mbstring.internal_encoding = "UTF-8"
mbstring.language = "Japanese"
```
:::

6. `¥nginx` 直下に `default.conf` を作成して編集する
```js:Terminal
~php $ cd ..
~docker $ cd nginx && touch default.conf
```
:::details default.conf の記述内容
```js:default.conf
server {
    listen 80;
    index index.php index.html;
    root /var/www/LaravelTestProject/public;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            fastcgi_param PATH_INFO $fastcgi_path_info;
    }
}
```
:::details default.conf の解説
default.conf は、Nginx（エンジンエックス）ウェブサーバーソフトウェアの設定ファイルの1つです。Nginxは、さまざまなウェブサーバー関連の機能を提供するためのソフトウェアです。
```js:default.conf
server {
    # nginx側のポート番号を指定（ymlのnginxのコンテナ側ポートと同じにする）
    listen 80;

    # indexファイルのファイル名と形式を指定（index.php, index.htmlを指定）
    index index.php index.html;

    # サーバー側のルートPathを指定（ymlのphpのvolumesのtopPage位置と同じにする）
    root /var/www/LaravelTestProject/public;

    # locationディレクティブ：HTTPリクエストパスに応じたコンテキストを定義する
    # ここではlocationディレクティブのマッチングを行います
    location / {
        # try_files：左から指定した順番で URL の確認および転送を行う指示を出せる項目
        # ( 1 ) $url → URL のパスにファイルがあるか 
        # ( 2 ) $uri/ → ( 1 ) が存在しなかった場合に、URL のパスにディレクトリがあるか 
        # ( 3 ) /index.php … → ( 1 ) ( 2 ) 共に存在しなかった場合、指定したロケーションに行く
        try_files $uri $uri/ /index.php?$query_string;
    }

    # locationディレクティブ： 「.php 」拡張子のファイルを指定された際に実行した結果に応じたコンテキストをで定義する
    # fastcgi_passの 'php'部分 は、docker-compose.ymlの phpサービス名 と同じにすること（'php-fpm'などの場合も多い）
    # それ以外は下記のデフォルトのままでOKです
    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            fastcgi_param PATH_INFO $fastcgi_path_info;
    }
}
```
:::message alert
サーバー側のルートPathを指定

この部分をLaravelのプロジェクト名に書き替えないとエラーになります。
あらかじめLaravelのプロジェクト名は決めておきましょう。
今回は「LaravelTestProject」をPJ名にしています。
```js:
root /var/www/<Laravelのプロジェクト名>/public;
```
:::


7. Docker を起動してコンテナを作る
```js:Terminal
~nginx $ cd .. && cd ..
~Laravel9-Docker-TestPJ $ docker-compose up -d
```

8. コンテナにログインする(シェル内でコンテナ操作できるようになります)
```js:Terminal
~Laravel9-Docker-TestPJ $ docker-compose exec php bash
```

9. Laravelをインストールする  

今回は `Composer` を使用してインストールしています。
```js:Terminal
root@~/www# composer create-project "laravel/laravel=9.*" LaravelTestProject
```
:::message
それぞれのLaravelのインストール方法
【最新版】
```js:Terminal
root@~/www# laravel new <Laravelのプロジェクト名>
```
【バージョン指定】
```js:Terminal
root@~/www# composer create-project "laravel/laravel=9.*" <Laravelのプロジェクト名>
```
:::

10. Composerのオートロード設定を変更する

Laravel9以降はモデルのディレクトリ構成がVersion8未満と異なっています。
下記のようにオートロード設定を追加してください。
```js:composer.json
"autoload": {
    "psr-4": {
        "App\\": "app/",
        "App\\Models\\": "app/Models/",
        [中略]
    }
},
```

11. インストールの確認をする
```js:Terminal
root@~/www# cd LaravelTestProject
root@~LaravelTestProject # php artisan --version
Laravel Framework 9.52.15
# Composerのオートロードを再実行しておく
root@~LaravelTestProject # composer dump-autoload
```

12. ブラウザでLaravelの表示を確認する  

ブラウザに http://localhost/ でアクセスして表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-23-14-14-40.png)

13. 念の為に権限を与える（「12」でエラーが出た場合の対応などのため）
```js:Terminal
# PermissionDeniedエラーの対処方法
root@~LaravelTestProject # chown ./www-data/storage -R
```

14. `.env` と `.env.example` の環境設定をする

ここで `docker-compose` に合わせて `.env` の設定を書き換えておきます。

`.env.example` のDBの設定を下記のように書き換えてください。
```js: .env.example（書き換え箇所）
DB_CONNECTION=db
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=mysql_test_db
DB_USERNAME=admin
DB_PASSWORD=secret
```

次に `.env.example` を `.env` にコピーします。
```js:Terminal
# .env.example を .env にコピー
root@~LaravelReactProject # cp .env.example .env
# キージェネレートする
root@~LaravelReactProject # php artisan key:generate
```

:::details  .env.example の全体コード
```js:
APP_NAME=Laravel
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://localhost

LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=db
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=mysql_test_db
DB_USERNAME=admin
DB_PASSWORD=secret

BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120

MEMCACHED_HOST=127.0.0.1

REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379

MAIL_MAILER=smtp
MAIL_HOST=mailpit
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS="hello@example.com"
MAIL_FROM_NAME="${APP_NAME}"

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=
AWS_USE_PATH_STYLE_ENDPOINT=false

PUSHER_APP_ID=
PUSHER_APP_KEY=
PUSHER_APP_SECRET=
PUSHER_HOST=
PUSHER_PORT=443
PUSHER_SCHEME=https
PUSHER_APP_CLUSTER=mt1

VITE_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
VITE_PUSHER_HOST="${PUSHER_HOST}"
VITE_PUSHER_PORT="${PUSHER_PORT}"
VITE_PUSHER_SCHEME="${PUSHER_SCHEME}"
VITE_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"
```
:::

:::message alert
超重要

最後に `.env` と `.env.example` について触れておきます。

Laravelでは、非常に重要な `.env` ファイルは Githib などで共有できないようになっています。これは  `.env` がシステムの根幹に関わる環境設定ファイルだからです。そのため `.gitignore` で `.env` が除外指定されています。そして除外されているべきものでもあります。

しかし、環境設定ファイルを雛形なしに作るのは大変です。そこで登場するのが `.env.example` です。`.env.example` ならば除外されることはありません。例えば、プライベートリポジトリなどセキュリティの高い状態で `.env.example（環境情報の値も記述されているもの）` 共有して差し替えていくのが開発現場でのセオリーです。

もっとセキュリティを高める場合は `.env.example` は雛形に徹して 環境情報の値を安全に共有して書き換えていくことになります。
:::

15. ブラウザで表示を確認する  

【Laravelのウェルカムページ】
ブラウザに http://localhost/ でアクセスして表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-23-14-14-40.png)

【phpMyAdminのTOPページ】
ブラウザに [http://localhost:8080/](http://localhost:8080/) で アクセスして表示されればOKです。 
phpMyAdmin が表示されているなら MySQL（DB）も phpMyAdmin 問題なく稼働しています。
![](/images/laravel-and-docker-introduction-20230822/2023-08-25-14-46-29.png)

16. コンテナからログアウトする
```js:Terminal
root@~LaravelTestProject # exit
```

これで「**Laravelを導入する**」は完了です。

実際にLaravelを使ってアプリを作成してみたい方のためのWEB書籍も執筆しています。
ご興味のある方は下記を実施みてください。
https://zenn.dev/eguchi244_dev/books/laravel-tutorial-books

# 後始末をする
今回で使ったDockerコンテナなど学習用のものは普段は必要ないので消してしまいましょう。
Dockerを使っているので必要になったら、またビルド（構築）すれば良いだけです。
どんなコードを書いていたかを確認したいのであれば本記事を確認すれば済みます。

1. サービスに関連するコンテナ, イメージ, ボリュームを全て削除する
```js:Terminal
~Laravel9-Docker-TestPJ $ docker-compose down -v --rmi all
```
:::message alert
解説 - docker-compose down -v --rmi all

このコマンドではサービスに関連する下記の内容を削除してくれます。

- docker-compose down → コンテナ（とネットワーク）の削除
- -vオプション → ボリュームの削除
- --rmi all → イメージの削除

個別に消したい場合には下記のようにします。
```js:Terminal
# コンテナ（とネットワーク）削除
~Laravel9-Docker-TestPJ $ docker-compose down
# コンテナとボリュームの削除
~Laravel9-Docker-TestPJ $ docker-compose down -v
# コンテナとイメージの削除
~Laravel9-Docker-TestPJ $ docker-compose down --rmi all
```

サービスに関連するものだけを削除するのでこの後に紹介するコマンドより安全です。
:::

:::details サービスに限定しないで一括で消す場合
```js:Terminal
# コンテナを停止する
~Laravel9-Docker-TestPJ $ docker-compose stop
# コンテナの一括削除
~Laravel9-Docker-TestPJ $ docker rm $(docker ps -aq)
# ネットワークの一括削除
~Laravel9-Docker-TestPJ $ docker network prune
# イメージの一括削除
~Laravel9-Docker-TestPJ $ docker rmi $(docker images -q)
# ボリュームの削除
~Laravel9-Docker-TestPJ $ docker volume prune
```
但し、このコマンドはサービスに限定せずに全ての現在実行中および停止中の全ての コンテナ, ネットワーク, イメージ, ボリューム を一括削除します。そのため、実行する際には慎重に行なってください。例えば、何が起きても困らない自分の学習用PC端末などですべて消したい場合で使用します。
:::

:::details 個別に消したい場合
```js:Terminal
# コンテナを停止する
~Laravel9-Docker-TestPJ $ docker-compose stop

# コンテナを確認する
~Laravel9-Docker-TestPJ $ docker ps -a
# 特定のコンテナの削除
~Laravel9-Docker-TestPJ $ docker rm コンテナID (CONTAINER ID)

# ネットワークを確認する
~Laravel9-Docker-TestPJ $ docker network ls
# 特定のネットワークの削除
~Laravel9-Docker-TestPJ $ docker network rm (NETWORK NAME)

# イメージを確認する
~Laravel9-Docker-TestPJ $ docker images
# 特定のイメージの削除
~Laravel9-Docker-TestPJ $ docker rmi イメージID (IMAGE ID)

# ボリュームを確認する
~Laravel9-Docker-TestPJ $ docker images
docker volume ls
# 特定のボリュームの削除
~Laravel9-Docker-TestPJ $ docker volume rm (VOLUME NAME)
```
:::

2. 任意でホストPCの今回で使用したフォルダとファイルを消す

ここでの操作ついては個々人の判断にお任せします。
本記事をみれば良いと思ってる人はフォルダとファイルも消してしまいましょう。
```js:Terminal
# 親ディレクトリに移動
~Laravel9-Docker-TestPJ $ cd ..
~親ディレクトリ名 $ rm -rf Laravel9-Docker-TestPJ
```
これで「**後始末をする**」は完了です。

# まとめ
これで全ての作業が完了しました。お疲れ様でした。
ここまでの作業で「DockerでLaravelを導入する方法」を概ね理解できたのではないでしょうか。

環境構築は手間が掛かるものですが Docker を使えば コマンドを何度か実行すれば環境構築できるようになります。本当にしたい作業に集中するためにも手早く済ませたいものですよね。

本記事がその一助になればと思っております。
