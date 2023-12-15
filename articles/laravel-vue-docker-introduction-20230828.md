---
title: "Laravel9とVue.jsをDockerで導入してみよう!"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Laravel", "PHP", "Docker", "dockercompose", "Vue"]
published: true # 公開に指定する
---
# はじめに
この記事では「Laravel9とVue.jsをDockerで簡単に構築すること」を目指します。
Dockerを使って少ない労力で環境構築できるようになりたい方のための記事です。
![](/images/laravel-vue-docker-introduction-20230828/2023-08-22-13-10-28.png =500x)
![](/images/laravel-vue-docker-introduction-20230828/2023-08-28-12-35-33.png =500x)

Laravel単体をDokcerで導入することに興味がある方は下記の記事を参照してください。
https://zenn.dev/eguchi244_dev/articles/laravel-and-docker-introduction-20230822

# 前提条件
この記事では以下の知識を持つことを前提にしています。

- HTML&CSS, PHPをある程度は理解している
- Javascriptをある程度は理解している
- Dockerをある程度は理解している
- Linuxコマンドに触れたことがある

これらについては詳細に解説することはありませんのでご承知ください。

# 目的＆内容
Laravel9とVue.jsをDockerで構築して以下の内容を実施することを目的とします。

1. Laravelを導入する
2. Vite から Laravel Mix に戻す
3. Vue.jsと各種ライブラリーを導入する

LaravelではVue.jsを導入しやすく、LaravelとVue.jsの組み合わせは実務のプロジェクトでもよく見受けられるので、ぜひ導入できるようになりましょう。

# 環境構築の目標
環境構築の目標は「Laravel9とVue.jsをDockerで構築する」ことです。
具体的には以下の構成で環境構築をします。

:::message
【環境構築の目標】
- フレームワーク：Laravel Framework 9.x.x (LaravelMix)
- データベース：MYSQL 5.7.36
- DB管理ツール：phpMyAdmin latest
- PHP：PHP 8.0.x
- Nginx：Nginx latest
- Node.js：node 14.18-alpine
- mail：mailhog latest
:::
【ディレクトリ構成】
```js:
Laravel9-Vue-TestPJ（ルートディレクトリ）※ 任意の名前でOK
├── docker-compose.yml
├── docker 
│   ├── php 
│   │   ├── Dockerfile 
│   │   └── php.ini 
│   └── nginx 
│       └── default.conf 
├── phpMyAdmin
└── src 
    └──  LaravelVueProject（Laravelのプロジェクトディレクトリ）※ 任意の名前でOK
```

:::message alert
Laravel Mixについて

特段の事情がない限りは公式が推奨する「Vite」を使うべきでしょう。それでも本記事でLaravel Mixを扱うのは、Viteであればいくらでも情報が見つかるのに対して、Laravel Mixに戻して使うケースの情報が少ないからです。これにより古い構成に対応できるようになるためです。注意点はデプロイサーバーなどがViteにしか対応してないなど環境にされることもあることです。慎重に調査した上で技術選定していきましょう。
:::
:::message alert
Laravel/ui（認証系ライブラリ）について

特段の事情がない限りは公式が推奨する「breeze,jetstream」を使うべきでしょう。それでも本記事で「Laravel/ui」を扱うのは、LaravelMixの時と同様に古い構成にも対応できようになるためです。
:::

# Vue.jsとは
Vue.jsは、アプリケーション開発において、UIを構築するためのJavaScriptフレームワークです。開発者のEvan You氏が提唱したプログレッシブ・フレームワーク（段階的に適用できる構造）という概念のもとで設計されています。

アプリケーションは、リリースされた後も開発が続けられることが一般的です。段階的な仕様変更や新しい機能の追加が繰り返されると、当初採用したフレームワークでは対応が難しくなってくることがあります。そのようなときにVue.jsを採用すれば、既存のアプリケーションへの導入も簡単にでき、要件に合わせた機能を追加していくことでアプリケーションを拡張できます。

より詳しく知りたい方は下記の参考ページを参照してください。
https://www.webstaff.jp/guide/trend/vuejs/#case01

# ①Laravelを導入する
さっそくLaravelを導入していきましょう！下記の手順を実施してください。

1. ルートディレクトリを作成する  

任意のディレクトリに「Laravel9-Vue-TestPJ」を作成します。
```js:Terminal
$ mkdir Laravel9-Vue-TestPJ
~Laravel9-Vue-TestPJ $ cd Laravel9-Vue-TestPJ
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

  mail:
    image: mailhog/mailhog
    container_name: "mailhog"
    # ポートフォワードの指定（ホスト側ポート：コンテナ側ポート）
    ports:
      - 8025:8025

# サービスレベルで名前付きボリュームを命名する
volumes:
  db_data_test:
  db_my.cnf_test:
  db_sql_test:
```
:::message alert
名前付きボリュームを使用する理由

ボリュームのマウント先をホストディレクトリにする書き方をすると環境によっては コンテナ内のユーザーが持っている権限とマウントされたディレクトリの権限が一致せずコンテナが立ち上がらないことがあるからです。
:::
:::message
mailhogについて

mailhogはメールサーバーを構築するライブラリーです。LaravelとVue.jsを構築することには関係ありません。メール機能を実装しない場合は必要ないのでこの部分は削除してください。
:::

3. ルートディレクトリ直下に `¥docker` `¥src` を作成する
```js:Terminal
~Laravel9-Vue-TestPJ $ mkdir docker && mkdir src
```

4. `¥docker` 直下に `¥php` `¥nginx` を作成する
```js:Terminal
~Laravel9-Vue-TestPJ $ cd docker
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
    
    # ファイルアップロードのタイムアウト対策
    fastcgi_connect_timeout 300;
    fastcgi_send_timeout 300;
    fastcgi_read_timeout 300;
    send_timeout 300;
    keepalive_timeout 300;

    root /var/www/LaravelVueProject/public;

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

    # ファイルアップロードのタイムアウト対策
    # FastCGIと接続を確立するためのタイムアウトを設定：300s を指定
    fastcgi_connect_timeout 300;
    # FastCGIに要求を送信するためのタイムアウトを設定：300s を指定
    fastcgi_send_timeout 300;
    # FastCGIからの応答を受信するためのタイムアウトを設定：300s を指定
    fastcgi_read_timeout 300;
    # 要求を送信するためのタイムアウトを設定：300s を指定
    send_timeout 300;
    # タイムアウト時間を設定：300s を指定
    keepalive_timeout 300;

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
今回は「LaravelVueProject」をPJ名にしています。
```js:
root /var/www/<Laravelのプロジェクト名>/public;
```
:::

7. Docker を起動してコンテナを作る
```js:Terminal
~nginx $ cd .. && cd ..
~Laravel9-Vue-TestPJ $ docker-compose up -d
```

8. コンテナにログインする(シェル内でコンテナ操作できるようになります)
```js:Terminal
~Laravel9-Vue-TestPJ $ docker-compose exec php bash
```

9. Laravelをインストールする  

今回は `Composer` を使用してインストールしています。
```js:Terminal
root@~/www# composer create-project "laravel/laravel=9.*" LaravelVueProject
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
root@~/www# cd LaravelVueProject
root@~LaravelVueProject # php artisan --version
Laravel Framework 9.52.15
# Composerのオートロードを再実行しておく
root@~LaravelVueProject # composer dump-autoload
```

12. ブラウザでLaravelの表示を確認する  

ブラウザに http://localhost/ でアクセスして表示されればOKです。
![](/images/laravel-vue-docker-introduction-20230828/2023-09-01-10-50-58.png)

13. 念の為に権限を与える（「12」でエラーが出た場合の対応などのため）
```js:Terminal
# PermissionDeniedエラーの対処方法
root@~LaravelVueProject # chown www-data ./ -R
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

15. ブラウザでLaravelの表示を確認する  

ブラウザに http://localhost/ でアクセスして表示されればOKです。
![](/images/laravel-vue-docker-introduction-20230828/2023-09-01-10-50-58.png)

これで「①Laravelを導入する」は完了です。

# ②Vite から Laravel Mix に戻す

下記の記事を参照して Vite から Laravel Mix に戻してください。
https://zenn.dev/eguchi244_dev/articles/restore-laravel-vite-to-mix-20230829

:::message alert
Webpack(Laravel Mix) と Vite について

Laravel9以降では、フロントエンド(JS,CSS)のビルドツールについて、従来のLaravel Mix から Vite へと置き換わりました。開発要件によって Laravel Mix と Vite を選択することになります。今回は 「Laravel Mix に戻す方法」を採用しますが、基本的にはViteを推奨します。
:::

Vite での環境構築に興味がある方は下記が参考になりますのでご覧ください。
https://reffect.co.jp/laravel/laravel9_vite/

これで「②Vite から Laravel Mix に戻す」は完了です。

# ③Vue.jsと各種ライブラリーを導入する
ここからは Vue.js と 各種ライブラリーを導入していきます。

下記の記事を見ながら作業をすると理解が進むと思います。
https://migisanblog.com/laravel-vue-install/#index_id2

0. コンテナにログインする
```js:Terminal
~Laravel9-Vue-TestPJ $ docker-compose exec php bash
root@~/www# cd LaravelVueProject
# キージェネレートしておく
root@~LaravelVueProject # php artisan key:generate
```

1. laravel/uiのライブラリをインストール（認証系ライブラリ）
```js:Terminal
root@~LaravelVueProject # composer require laravel/ui
```
:::message alert
認証系のライブラリについて

今回は`laravel/ui`を採用していますが、`breeze` または `jetstream` を採用することを推奨します。公式が`breeze` または `jetstream` を推奨しているからです。
:::

2. laravel/ui vueのインストール（フロントエンドのベースコード）

vueスカホールドのインストールをします。
```js:Terminal
root@~LaravelVueProject # php artisan ui vue
# phpコンテナからログアウトする
root@~LaravelVueProject # exit
# nodeコンテナにログインする
root@~LaravelVueProject # docker-compose exec node /bin/sh
root@~/www# cd LaravelVueProject
```
:::message
スキャホールドとは

スキャホールド（Scaffold）とは「足場」という意味で、例えばデータベースの基本操作（登録、参照、更新など）に必要な機能の骨組みを自動生成する機能のことをいう。

今回はVue.jsを使うための「足場」を作ったということです。
:::

3. Vue Routerのインストール（ルーティング制御用プラグイン）
```js:Terminal
root@~LaravelVueProject # npm install vue-router@3
```
4. Vue テンプレートのインストール（Vue.jsテンプレートコンパイル用プラグイン）
```js:Terminal
root@~LaravelVueProject # npm install vue-template-compiler --save-dev
```
5. `webpack.mix.js` を編集する

Vue.jsで LaravelMix が動作するように `webpack.mix.js` を編集します。
:::details webpack.mix.js の記述内容
```js:webpack.mix.js
const mix = require('laravel-mix');

/*
 |--------------------------------------------------------------------------
 | Mix Asset Management
 |--------------------------------------------------------------------------
 |
 | Mix provides a clean, fluent API for defining some Webpack build steps
 | for your Laravel applications. By default, we are compiling the CSS
 | file for the application as well as bundling up all the JS files.
 |
 */

mix.js('resources/js/app.js', 'public/js')
    .postCss('resources/css/app.css', 'public/css', [
        //
    ])
    .vue()
    .sass('resources/sass/app.scss', 'public/css');
```
:::

このタイミングで復活したVite絡みのファイルも消しておきましょう。
```js:Terminal
root@~LaravelVueProject # npm remove vite
root@~LaravelVueProject # npm remove laravel-vite-plugin
root@~LaravelVueProject # rm -rf vite.config.js
```

6. Vueコンポーネントを `welcome.blade.php` に取り込む

Vue.jsの動作確認をViewで確認するために下記の編集をしてください。

【CSRFトークンの挿入を追加する】
```js:welcome.blade.php
<meta name="csrf-token" content="{{ csrf_token() }}">
```
Laravelではセキュリティの関連からVue.jsを利用する場合、CSRFトークンを追加することを推奨しています。CRSF対策を一から組み込もうとしたら、かなり大変ですがLaravelでは標準で備わっています。

【Vue.jsのサンプルコンポーネントを取り込む】
```js:welcome.blade.php
<div id="app">
    <example-component></example-component>
</div><!-- #app -->
```
Vueは上記のように #app を目印にしてカスタムタグからVueコンポーネント（今回はExampleComponent.vue）を取り込むことができます。

:::details [resources/views/welcome.blade.php] の記述内容
```js:welcome.blade.php
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>Laravel</title>

        <!-- Fonts -->
        <link href="https://fonts.bunny.net/css2?family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">

        <!-- Styles -->
        <style>
            /*! normalize.css v8.0.1 | MIT License | github.com/necolas/normalize.css */html{line-height:1.15;-webkit-text-size-adjust:100%}body{margin:0}a{background-color:transparent}[hidden]{display:none}html{font-family:system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji;line-height:1.5}*,:after,:before{box-sizing:border-box;border:0 solid #e2e8f0}a{color:inherit;text-decoration:inherit}svg,video{display:block;vertical-align:middle}video{max-width:100%;height:auto}.bg-white{--tw-bg-opacity: 1;background-color:rgb(255 255 255 / var(--tw-bg-opacity))}.bg-gray-100{--tw-bg-opacity: 1;background-color:rgb(243 244 246 / var(--tw-bg-opacity))}.border-gray-200{--tw-border-opacity: 1;border-color:rgb(229 231 235 / var(--tw-border-opacity))}.border-t{border-top-width:1px}.flex{display:flex}.grid{display:grid}.hidden{display:none}.items-center{align-items:center}.justify-center{justify-content:center}.font-semibold{font-weight:600}.h-5{height:1.25rem}.h-8{height:2rem}.h-16{height:4rem}.text-sm{font-size:.875rem}.text-lg{font-size:1.125rem}.leading-7{line-height:1.75rem}.mx-auto{margin-left:auto;margin-right:auto}.ml-1{margin-left:.25rem}.mt-2{margin-top:.5rem}.mr-2{margin-right:.5rem}.ml-2{margin-left:.5rem}.mt-4{margin-top:1rem}.ml-4{margin-left:1rem}.mt-8{margin-top:2rem}.ml-12{margin-left:3rem}.-mt-px{margin-top:-1px}.max-w-6xl{max-width:72rem}.min-h-screen{min-height:100vh}.overflow-hidden{overflow:hidden}.p-6{padding:1.5rem}.py-4{padding-top:1rem;padding-bottom:1rem}.px-6{padding-left:1.5rem;padding-right:1.5rem}.pt-8{padding-top:2rem}.fixed{position:fixed}.relative{position:relative}.top-0{top:0}.right-0{right:0}.shadow{--tw-shadow: 0 1px 3px 0 rgb(0 0 0 / .1), 0 1px 2px -1px rgb(0 0 0 / .1);--tw-shadow-colored: 0 1px 3px 0 var(--tw-shadow-color), 0 1px 2px -1px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000),var(--tw-ring-shadow, 0 0 #0000),var(--tw-shadow)}.text-center{text-align:center}.text-gray-200{--tw-text-opacity: 1;color:rgb(229 231 235 / var(--tw-text-opacity))}.text-gray-300{--tw-text-opacity: 1;color:rgb(209 213 219 / var(--tw-text-opacity))}.text-gray-400{--tw-text-opacity: 1;color:rgb(156 163 175 / var(--tw-text-opacity))}.text-gray-500{--tw-text-opacity: 1;color:rgb(107 114 128 / var(--tw-text-opacity))}.text-gray-600{--tw-text-opacity: 1;color:rgb(75 85 99 / var(--tw-text-opacity))}.text-gray-700{--tw-text-opacity: 1;color:rgb(55 65 81 / var(--tw-text-opacity))}.text-gray-900{--tw-text-opacity: 1;color:rgb(17 24 39 / var(--tw-text-opacity))}.underline{text-decoration:underline}.antialiased{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.w-5{width:1.25rem}.w-8{width:2rem}.w-auto{width:auto}.grid-cols-1{grid-template-columns:repeat(1,minmax(0,1fr))}@media (min-width:640px){.sm\:rounded-lg{border-radius:.5rem}.sm\:block{display:block}.sm\:items-center{align-items:center}.sm\:justify-start{justify-content:flex-start}.sm\:justify-between{justify-content:space-between}.sm\:h-20{height:5rem}.sm\:ml-0{margin-left:0}.sm\:px-6{padding-left:1.5rem;padding-right:1.5rem}.sm\:pt-0{padding-top:0}.sm\:text-left{text-align:left}.sm\:text-right{text-align:right}}@media (min-width:768px){.md\:border-t-0{border-top-width:0}.md\:border-l{border-left-width:1px}.md\:grid-cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (min-width:1024px){.lg\:px-8{padding-left:2rem;padding-right:2rem}}@media (prefers-color-scheme:dark){.dark\:bg-gray-800{--tw-bg-opacity: 1;background-color:rgb(31 41 55 / var(--tw-bg-opacity))}.dark\:bg-gray-900{--tw-bg-opacity: 1;background-color:rgb(17 24 39 / var(--tw-bg-opacity))}.dark\:border-gray-700{--tw-border-opacity: 1;border-color:rgb(55 65 81 / var(--tw-border-opacity))}.dark\:text-white{--tw-text-opacity: 1;color:rgb(255 255 255 / var(--tw-text-opacity))}.dark\:text-gray-400{--tw-text-opacity: 1;color:rgb(156 163 175 / var(--tw-text-opacity))}.dark\:text-gray-500{--tw-text-opacity: 1;color:rgb(107 114 128 / var(--tw-text-opacity))}}
        </style>

        <style>
            body {
                font-family: 'Nunito', sans-serif;
            }
        </style>

        <!-- CSRFトークンの挿入を追加する -->
        <meta name="csrf-token" content="{{ csrf_token() }}">
        
        <!-- 下記を追加する -->
        <!-- Styles -->
        <link rel="stylesheet" href="{{ mix('css/app.css') }}">
        <!-- Scripts -->
        <script src="{{ mix('js/app.js') }}" defer></script>
    </head>
    <body class="antialiased">
        <div class="relative flex items-top justify-center min-h-screen bg-gray-100 dark:bg-gray-900 sm:items-center py-4 sm:pt-0">
            @if (Route::has('login'))
                <div class="hidden fixed top-0 right-0 px-6 py-4 sm:block">
                    @auth
                        <a href="{{ url('/home') }}" class="text-sm text-gray-700 dark:text-gray-500 underline">Home</a>
                    @else
                        <a href="{{ route('login') }}" class="text-sm text-gray-700 dark:text-gray-500 underline">Log in</a>

                        @if (Route::has('register'))
                            <a href="{{ route('register') }}" class="ml-4 text-sm text-gray-700 dark:text-gray-500 underline">Register</a>
                        @endif
                    @endauth
                </div>
            @endif

            <div class="max-w-6xl mx-auto sm:px-6 lg:px-8">
                <div class="flex justify-center pt-8 sm:justify-start sm:pt-0">
                    <svg viewBox="0 0 651 192" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-16 w-auto text-gray-700 sm:h-20">
                        <g clip-path="url(#clip0)" fill="#EF3B2D">
                            <path d="M248.032 44.676h-16.466v100.23h47.394v-14.748h-30.928V44.676zM337.091 87.202c-2.101-3.341-5.083-5.965-8.949-7.875-3.865-1.909-7.756-2.864-11.669-2.864-5.062 0-9.69.931-13.89 2.792-4.201 1.861-7.804 4.417-10.811 7.661-3.007 3.246-5.347 6.993-7.016 11.239-1.672 4.249-2.506 8.713-2.506 13.389 0 4.774.834 9.26 2.506 13.459 1.669 4.202 4.009 7.925 7.016 11.169 3.007 3.246 6.609 5.799 10.811 7.66 4.199 1.861 8.828 2.792 13.89 2.792 3.913 0 7.804-.955 11.669-2.863 3.866-1.908 6.849-4.533 8.949-7.875v9.021h15.607V78.182h-15.607v9.02zm-1.431 32.503c-.955 2.578-2.291 4.821-4.009 6.73-1.719 1.91-3.795 3.437-6.229 4.582-2.435 1.146-5.133 1.718-8.091 1.718-2.96 0-5.633-.572-8.019-1.718-2.387-1.146-4.438-2.672-6.156-4.582-1.719-1.909-3.032-4.152-3.938-6.73-.909-2.577-1.36-5.298-1.36-8.161 0-2.864.451-5.585 1.36-8.162.905-2.577 2.219-4.819 3.938-6.729 1.718-1.908 3.77-3.437 6.156-4.582 2.386-1.146 5.059-1.718 8.019-1.718 2.958 0 5.656.572 8.091 1.718 2.434 1.146 4.51 2.674 6.229 4.582 1.718 1.91 3.054 4.152 4.009 6.729.953 2.577 1.432 5.298 1.432 8.162-.001 2.863-.479 5.584-1.432 8.161zM463.954 87.202c-2.101-3.341-5.083-5.965-8.949-7.875-3.865-1.909-7.756-2.864-11.669-2.864-5.062 0-9.69.931-13.89 2.792-4.201 1.861-7.804 4.417-10.811 7.661-3.007 3.246-5.347 6.993-7.016 11.239-1.672 4.249-2.506 8.713-2.506 13.389 0 4.774.834 9.26 2.506 13.459 1.669 4.202 4.009 7.925 7.016 11.169 3.007 3.246 6.609 5.799 10.811 7.66 4.199 1.861 8.828 2.792 13.89 2.792 3.913 0 7.804-.955 11.669-2.863 3.866-1.908 6.849-4.533 8.949-7.875v9.021h15.607V78.182h-15.607v9.02zm-1.432 32.503c-.955 2.578-2.291 4.821-4.009 6.73-1.719 1.91-3.795 3.437-6.229 4.582-2.435 1.146-5.133 1.718-8.091 1.718-2.96 0-5.633-.572-8.019-1.718-2.387-1.146-4.438-2.672-6.156-4.582-1.719-1.909-3.032-4.152-3.938-6.73-.909-2.577-1.36-5.298-1.36-8.161 0-2.864.451-5.585 1.36-8.162.905-2.577 2.219-4.819 3.938-6.729 1.718-1.908 3.77-3.437 6.156-4.582 2.386-1.146 5.059-1.718 8.019-1.718 2.958 0 5.656.572 8.091 1.718 2.434 1.146 4.51 2.674 6.229 4.582 1.718 1.91 3.054 4.152 4.009 6.729.953 2.577 1.432 5.298 1.432 8.162 0 2.863-.479 5.584-1.432 8.161zM650.772 44.676h-15.606v100.23h15.606V44.676zM365.013 144.906h15.607V93.538h26.776V78.182h-42.383v66.724zM542.133 78.182l-19.616 51.096-19.616-51.096h-15.808l25.617 66.724h19.614l25.617-66.724h-15.808zM591.98 76.466c-19.112 0-34.239 15.706-34.239 35.079 0 21.416 14.641 35.079 36.239 35.079 12.088 0 19.806-4.622 29.234-14.688l-10.544-8.158c-.006.008-7.958 10.449-19.832 10.449-13.802 0-19.612-11.127-19.612-16.884h51.777c2.72-22.043-11.772-40.877-33.023-40.877zm-18.713 29.28c.12-1.284 1.917-16.884 18.589-16.884 16.671 0 18.697 15.598 18.813 16.884h-37.402zM184.068 43.892c-.024-.088-.073-.165-.104-.25-.058-.157-.108-.316-.191-.46-.056-.097-.137-.176-.203-.265-.087-.117-.161-.242-.265-.345-.085-.086-.194-.148-.29-.223-.109-.085-.206-.182-.327-.252l-.002-.001-.002-.002-35.648-20.524a2.971 2.971 0 00-2.964 0l-35.647 20.522-.002.002-.002.001c-.121.07-.219.167-.327.252-.096.075-.205.138-.29.223-.103.103-.178.228-.265.345-.066.089-.147.169-.203.265-.083.144-.133.304-.191.46-.031.085-.08.162-.104.25-.067.249-.103.51-.103.776v38.979l-29.706 17.103V24.493a3 3 0 00-.103-.776c-.024-.088-.073-.165-.104-.25-.058-.157-.108-.316-.191-.46-.056-.097-.137-.176-.203-.265-.087-.117-.161-.242-.265-.345-.085-.086-.194-.148-.29-.223-.109-.085-.206-.182-.327-.252l-.002-.001-.002-.002L40.098 1.396a2.971 2.971 0 00-2.964 0L1.487 21.919l-.002.002-.002.001c-.121.07-.219.167-.327.252-.096.075-.205.138-.29.223-.103.103-.178.228-.265.345-.066.089-.147.169-.203.265-.083.144-.133.304-.191.46-.031.085-.08.162-.104.25-.067.249-.103.51-.103.776v122.09c0 1.063.568 2.044 1.489 2.575l71.293 41.045c.156.089.324.143.49.202.078.028.15.074.23.095a2.98 2.98 0 001.524 0c.069-.018.132-.059.2-.083.176-.061.354-.119.519-.214l71.293-41.045a2.971 2.971 0 001.489-2.575v-38.979l34.158-19.666a2.971 2.971 0 001.489-2.575V44.666a3.075 3.075 0 00-.106-.774zM74.255 143.167l-29.648-16.779 31.136-17.926.001-.001 34.164-19.669 29.674 17.084-21.772 12.428-43.555 24.863zm68.329-76.259v33.841l-12.475-7.182-17.231-9.92V49.806l12.475 7.182 17.231 9.92zm2.97-39.335l29.693 17.095-29.693 17.095-29.693-17.095 29.693-17.095zM54.06 114.089l-12.475 7.182V46.733l17.231-9.92 12.475-7.182v74.537l-17.231 9.921zM38.614 7.398l29.693 17.095-29.693 17.095L8.921 24.493 38.614 7.398zM5.938 29.632l12.475 7.182 17.231 9.92v79.676l.001.005-.001.006c0 .114.032.221.045.333.017.146.021.294.059.434l.002.007c.032.117.094.222.14.334.051.124.088.255.156.371a.036.036 0 00.004.009c.061.105.149.191.222.288.081.105.149.22.244.314l.008.01c.084.083.19.142.284.215.106.083.202.178.32.247l.013.005.011.008 34.139 19.321v34.175L5.939 144.867V29.632h-.001zm136.646 115.235l-65.352 37.625V148.31l48.399-27.628 16.953-9.677v33.862zm35.646-61.22l-29.706 17.102V66.908l17.231-9.92 12.475-7.182v33.841z"/>
                        </g>
                    </svg>
                </div>

                <div class="mt-8 bg-white dark:bg-gray-800 overflow-hidden shadow sm:rounded-lg">
                    <div class="grid grid-cols-1 md:grid-cols-2">
                        <div class="p-6">
                            <div class="flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-gray-500"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>
                                <div class="ml-4 text-lg leading-7 font-semibold"><a href="https://laravel.com/docs" class="underline text-gray-900 dark:text-white">Documentation</a></div>
                            </div>

                            <div class="ml-12">
                                <div class="mt-2 text-gray-600 dark:text-gray-400 text-sm">
                                    Laravel has wonderful, thorough documentation covering every aspect of the framework. Whether you are new to the framework or have previous experience with Laravel, we recommend reading all of the documentation from beginning to end.
                                </div>
                            </div>
                        </div>

                        <div class="p-6 border-t border-gray-200 dark:border-gray-700 md:border-t-0 md:border-l">
                            <div class="flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-gray-500"><path stroke-linecap="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" /></svg>
                                <div class="ml-4 text-lg leading-7 font-semibold"><a href="https://laracasts.com" class="underline text-gray-900 dark:text-white">Laracasts</a></div>
                            </div>

                            <div class="ml-12">
                                <div class="mt-2 text-gray-600 dark:text-gray-400 text-sm">
                                    Laracasts offers thousands of video tutorials on Laravel, PHP, and JavaScript development. Check them out, see for yourself, and massively level up your development skills in the process.
                                </div>
                            </div>
                        </div>

                        <div class="p-6 border-t border-gray-200 dark:border-gray-700">
                            <div class="flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-gray-500"><path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" /></svg>
                                <div class="ml-4 text-lg leading-7 font-semibold"><a href="https://laravel-news.com/" class="underline text-gray-900 dark:text-white">Laravel News</a></div>
                            </div>

                            <div class="ml-12">
                                <div class="mt-2 text-gray-600 dark:text-gray-400 text-sm">
                                    Laravel News is a community driven portal and newsletter aggregating all of the latest and most important news in the Laravel ecosystem, including new package releases and tutorials.
                                </div>
                            </div>
                        </div>

                        <div class="p-6 border-t border-gray-200 dark:border-gray-700 md:border-l">
                            <div class="flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-gray-500"><path stroke-linecap="round" stroke-linejoin="round" d="M6.115 5.19l.319 1.913A6 6 0 008.11 10.36L9.75 12l-.387.775c-.217.433-.132.956.21 1.298l1.348 1.348c.21.21.329.497.329.795v1.089c0 .426.24.815.622 1.006l.153.076c.433.217.956.132 1.298-.21l.723-.723a8.7 8.7 0 002.288-4.042 1.087 1.087 0 00-.358-1.099l-1.33-1.108c-.251-.21-.582-.299-.905-.245l-1.17.195a1.125 1.125 0 01-.98-.314l-.295-.295a1.125 1.125 0 010-1.591l.13-.132a1.125 1.125 0 011.3-.21l.603.302a.809.809 0 001.086-1.086L14.25 7.5l1.256-.837a4.5 4.5 0 001.528-1.732l.146-.292M6.115 5.19A9 9 0 1017.18 4.64M6.115 5.19A8.965 8.965 0 0112 3c1.929 0 3.716.607 5.18 1.64" /></svg>
                                <div class="ml-4 text-lg leading-7 font-semibold text-gray-900 dark:text-white">Vibrant Ecosystem</div>
                            </div>

                            <div class="ml-12">
                                <div class="mt-2 text-gray-600 dark:text-gray-400 text-sm">
                                    Laravel's robust library of first-party tools and libraries, such as <a href="https://forge.laravel.com" class="underline">Forge</a>, <a href="https://vapor.laravel.com" class="underline">Vapor</a>, <a href="https://nova.laravel.com" class="underline">Nova</a>, and <a href="https://envoyer.io" class="underline">Envoyer</a> help you take your projects to the next level. Pair them with powerful open source libraries like <a href="https://laravel.com/docs/billing" class="underline">Cashier</a>, <a href="https://laravel.com/docs/dusk" class="underline">Dusk</a>, <a href="https://laravel.com/docs/broadcasting" class="underline">Echo</a>, <a href="https://laravel.com/docs/horizon" class="underline">Horizon</a>, <a href="https://laravel.com/docs/sanctum" class="underline">Sanctum</a>, <a href="https://laravel.com/docs/telescope" class="underline">Telescope</a>, and more.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex justify-center mt-4 sm:items-center sm:justify-between">
                    <div class="text-center text-sm text-gray-500 sm:text-left">
                        <div class="flex items-center">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="-mt-px w-5 h-5 text-gray-400">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" />
                            </svg>

                            <a href="https://laravel.bigcartel.com" class="ml-1 underline">
                                Shop
                            </a>

                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="ml-4 -mt-px w-5 h-5 text-gray-400">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                            </svg>

                            <a href="https://github.com/sponsors/taylorotwell" class="ml-1 underline">
                                Sponsor
                            </a>
                        </div>
                    </div>

                    <div class="ml-4 text-center text-sm text-gray-500 sm:text-right sm:ml-0">
                        Laravel v{{ Illuminate\Foundation\Application::VERSION }} (PHP v{{ PHP_VERSION }})
                    </div>
                </div>

                <!-- Vue.jsのサンプルコンポーネント（ExampleComponent.vue）を取り込む -->
                <div id="app">
                    <example-component></example-component>
                </div><!-- #app -->

            </div>
        </div>
    </body>
</html>
```
:::

7. フロントエンドビルド（JS,CSS）を実行する
    1. npm(jsモジュール)を再インストールして実行する

    各種loaderをインストールするために npm をビルドします。
    ```js:Terminal
    root@~LaravelVueProject # npm install && npm run dev
    ```
    ※この段階では、npm ERR! が発生します（ケース4）参考：[npm ERR! の対処法](https://qiita.com/wafuwafu13/items/2fe43414aa6e1899f494)
    依存関係などを解消するために下記の手順を実施してください。

    2. インストールされたJSモジュールを全部消す
    ```js:Terminal
    root@~LaravelVueProject # rm -rf node_modules
    ```
    3. インストールされたJSモジュールのバージョン情報を消す
    ```js:Terminal
    root@~LaravelVueProject # rm -rf package-lock.json
    ```
    4. npmのキャッシュをクリアする
    ```js:Terminal
    root@~LaravelVueProject # npm cache clear --force
    ```
    5. npm(jsモジュール)を再インストールして実行する
    ```js:Terminal
    root@~LaravelVueProject # npm install && npm run dev
    ```
    ![](/images/laravel-vue-docker-introduction-20230828/2023-08-31-14-46-48.png)

9. ブラウザで表示されるか確認する

ブラウザに [http://localhost/](http://localhost/) で Vueコンポーネント が表示されればOKです。

![](/images/laravel-vue-docker-introduction-20230828/2023-08-31-15-03-06.png)

10. LaravelMixビルドのコンパイルを対象外にする

Laravel Mixのビルド処理によりコンパイルされるjs、cssを除外対象にしています。
これをしないとコンパイルのたびにGitなどに書き換えが検出されて煩わしくなります。

```js:[src/LaravelVueProject/.gitignore]の末尾に追加
/public/js
/public/css
```

これで「③Vue.jsと各種ライブラリーを導入する」は完了です。

# 後始末をする
今回で使ったDockerコンテナなど学習用のものは普段は必要ないので消してしまいましょう。
Dockerを使っているので必要になったら、またビルド（構築）すれば良いだけです。
どんなコードを書いていたかを確認したいのであれば本記事を確認すれば済みます。

1. サービスに関連するコンテナ, イメージ, ボリュームを全て削除する
```js:Terminal
~Laravel9-Vue-TestPJ $ docker-compose down -v --rmi all
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
~Laravel9-Vue-TestPJ $ docker-compose down
# コンテナとボリュームの削除
~Laravel9-Vue-TestPJ $ docker-compose down -v
# コンテナとイメージの削除
~Laravel9-Vue-TestPJ $ docker-compose down --rmi all
```

サービスに関連するものだけを削除するのでこの後に紹介するコマンドより安全です。
:::

:::details サービスに限定しないで一括で消す場合
```js:Terminal
# コンテナを停止する
~Laravel9-Vue-TestPJ $ docker-compose stop
# コンテナの一括削除
~Laravel9-Vue-TestPJ $ docker rm $(docker ps -aq)
# ネットワークの一括削除
~Laravel9-Vue-TestPJ $ docker network prune
# イメージの一括削除
~Laravel9-Vue-TestPJ $ docker rmi $(docker images -q)
# ボリュームの削除
~Laravel9-Vue-TestPJ $ docker volume prune
```
但し、このコマンドはサービスに限定せずに全ての現在実行中および停止中の全ての コンテナ, ネットワーク, イメージ, ボリューム を一括削除します。そのため、実行する際には慎重に行なってください。例えば、何が起きても困らない自分の学習用PC端末などですべて消したい場合で使用します。
:::

:::details 個別に消したい場合
```js:Terminal
# コンテナを停止する
~Laravel9-Vue-TestPJ $ docker-compose stop

# コンテナを確認する
~Laravel9-Vue-TestPJ $ docker ps -a
# 特定のコンテナの削除
~Laravel9-Vue-TestPJ $ docker rm コンテナID (CONTAINER ID)

# ネットワークを確認する
~Laravel9-Vue-TestPJ $ docker network ls
# 特定のネットワークの削除
~Laravel9-Vue-TestPJ $ docker network rm (NETWORK NAME)

# イメージを確認する
~Laravel9-Vue-TestPJ $ docker images
# 特定のイメージの削除
~Laravel9-Vue-TestPJ $ docker rmi イメージID (IMAGE ID)

# ボリュームを確認する
~Laravel9-Vue-TestPJ $ docker images
docker volume ls
# 特定のボリュームの削除
~Laravel9-Vue-TestPJ $ docker volume rm (VOLUME NAME)
```
:::

2. 任意でホストPCの今回で使用したフォルダとファイルを消す

ここでの操作ついては個々人の判断にお任せします。
本記事をみれば良いと思ってる人はフォルダとファイルも消してしまいましょう。
```js:Terminal
# 親ディレクトリに移動
~Laravel9-Vue-TestPJ $ cd ..
~親ディレクトリ名 $ rm -rf Laravel9-Vue-TestPJ
```
これで「**後始末をする**」は完了です。


# まとめ
これで全ての作業が完了しました。お疲れ様でした。
ここまでの作業で「Laravel9とVue.jsをDockerで導入する方法」を概ね理解できたのではないでしょうか。

環境構築は手間が掛かるものですが Docker を使えば コマンドを何度か実行すれば環境構築できるようになります。本当にしたい作業に集中するためにも手早く済ませたいものですよね。

本記事がその一助になればと思っております。