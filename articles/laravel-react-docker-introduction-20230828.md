---
title: "Laravel9とVue.jsをDockerで導入してみよう!"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Laravel", "PHP", "Docker", "dockercompose", "Vue"]
published: false # 公開に指定する
---
# はじめに
この記事では「Laravel9とVue.jsをDockerで簡単に構築すること」を目指します。
Dockerを使って少ない労力で環境構築できるようになりたい方のための記事です。
![](/images/laravel-and-docker-introduction-20230822/2023-08-22-13-10-28.png =500x)
![](/images/laravel-react-docker-introduction-20230828/2023-08-28-12-35-33.png =500x)

Laravel単体をDokcerで導入することに興味がある方は下記の記事を参照してください。
https://zenn.dev/eguchi244_dev/articles/laravel-and-docker-introduction-20230822

# 前提条件
この記事では以下の知識を持つことを前提にしています。

- HTML&CSS, PHPをある程度は理解している
- Javascriptをある程度は理解している
- Dockerをある程度は理解している
- Laravelをある程度は理解している
- Linuxコマンドに触れたことがある

これらについては詳細に解説することはありませんのでご承知ください。

# 目的＆内容
Laravel9とVue.jsをDockerで構築して以下の内容を実施することを目的とします。

1. DockerでLaravel9を導入する
2. テストページを作成する
3. ENV設定をする

LaravelではVue.jsを導入しやすく、LaravelとVue.jsの組み合わせは実務のプロジェクトでもよく見受けられるので、ぜひ導入できるようになりましょう。

# 環境構築の目標
環境構築の目標は「Laravel9とVue.jsをDockerで構築する」ことです。
具体的には以下の構成で環境構築をします。

:::message
【環境構築の目標】
- フレームワーク：Laravel Framework 9.x.x
- データベース：MYSQL 5.7.36
- DB管理ツール：phpMyAdmin latest
- PHP：PHP 8.0.x
- Nginx：Nginx latest
- Node.js：node 14.18-alpine
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
touch docker-compose.yml
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

10. インストールの確認をする
```js:Terminal
root@~/www# cd LaravelVueProject
root@~LaravelVueProject # php artisan --version
Laravel Framework 9.52.15
```

11. ブラウザでLaravelの表示を確認する  

ブラウザに http://localhost/ でアクセスして表示されればOKです。

12. 念の為に権限を与える（「11」でエラーが出た場合の対応などのため）
```js:Terminal
# PermissionDeniedエラーの対処方法
root@~LaravelVueProject # chown www-data ./ -R
```

13. ブラウザでLaravelの表示を確認する  

ブラウザに http://localhost/ でアクセスして表示されればOKです。

# Vite から Laravel Mix に戻す

下記の記事を参照して Vite から Laravel Mix に戻してください。
https://zenn.dev/eguchi244_dev/articles/restore-laravel-vite-to-mix-20230829

:::message alert
Webpack(Laravel Mix) と vite について

Laravel9以降では、フロントエンド(JS,CSS)のビルドツールについて、従来のLaravel Mix から Vite へと置き換わりました。開発要件によって Laravel Mix と Vite を選択することになります。今回は 「Laravel Mix に戻す方法」を採用します。 Vite での環境構築に興味がある方は下記が参考になりますのでご覧ください。

[Laravel9のVite環境でVue.js 3を利用する方法](https://reffect.co.jp/laravel/laravel9_vite/)
:::





# Veu.jsと各種ライブラリーを導入する
ここからは Vue.js と 各種ライブラリーを導入していきます。

1. laravel/uiのインストール（認証系のライブラリ）
```js:Terminal
root@~LaravelVueProject # composer require laravel/ui
```
2. laravel/ui vueのインストール（フロントエンドのベースコード）
```js:Terminal
root@~LaravelVueProject # php artisan ui vue
```
3. npmのインストール（Node.jsのパッケージ管理システム）
```js:Terminal
# phpコンテナからログアウトする
root@~LaravelVueProject # exit
# nodeコンテナにログインする
~Laravel9-Vue-TestPJ $ docker-compose exec node /bin/sh
root@~/www#  cd LaravelVueProject
root@~LaravelVueProject # npm install
```
4. Vue Routerのインストール（ルーティング制御用プラグイン）
```js:Terminal
root@~LaravelVueProject # npm install vue-router@3
```
5. ビルドの実行をする
    1. フロントエンドのビルドを実行します
    ```js:Terminal
    root@~LaravelVueProject # npm update && npm run dev
    ```
    ※この段階では、npm ERR! が発生します（ケース4）参考：[npm ERR! の対処法](https://qiita.com/wafuwafu13/items/2fe43414aa6e1899f494)
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
    6. ブラウザで表示されるか確認する
    
6. a
7. a
8. a
9. a
10. a
```js:Terminal
root@~LaravelVueProject # 
```


