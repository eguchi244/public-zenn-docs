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

# 前提条件
この記事では以下の知識を持つことを前提にしています。

- HTML&CSS, PHPをある程度は理解している
- Dockerをある程度は理解している
- Linuxコマンドに触れたことがある

これらについては詳細に解説することはありませんのでご承知ください。

# 目的＆内容
LaravelをDockerで構築して以下の内容を実施することを目的とします。

1. DockerでLaravel9を導入する
2. テストページを作成する
3. 設定ファイルを作成する
4. 本番環境と開発環境を切り替える
5. 本格的なENV設定をする

このようにLaravelのテストページを表示して **終わり** にしないための記事です。
動かして終わりではなく環境設定が出来てこその「環境構築」です。
これを機に環境設定の基礎と本格的な設定を身につけていきましょう。

# 環境構築の目標
環境構築の目標は「Dockerによる仮想環境で、Laravelを使用できるようにする」ことです。
具体的には以下の構成で環境構築をします。

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

# ①Laravelを導入する
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
root@~LaravelTestProject # chown www-data ./ -R
```

14. ブラウザでLaravelの表示を確認する  

ブラウザに http://localhost/ でアクセスして表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-23-14-14-40.png)

15. コンテナからログアウトする
```js:Terminal
root@~LaravelTestProject # exit
```

これで「**①Laravelを導入する**」は完了です。

とりあえず、**Laravelを起動させて表示を確認する** ことを目的とする場合はこれで終わりです。
まずは、お疲れ様でした。

このまま データーベース と phpMyAdmin の設定を済ませて開発に進みたい方は「**⑤本格的なENV設定**」までスキップしてください。

# ②テストページを作成する
次はテストページを作成してみましょう。目標は Hello world を表示させることです。

## MVCモデルとは
テストページを作成する前に Laravel で採用されている **MVCモデル** を確認しておきましょう。

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

## テストページを作成する
**【目標】hello world を表示させる**
それではテストページを作成してきましょう。下記の手順を実施してください。

0. コンテナにログインする
```js:Terminal
~Laravel9-Docker-TestPJ $ docker-compose exec php bash
root@~/var/www# cd LaravelTestProject
```

1. **ルーティングを設定する**

ルーティングは、どのURLに対してどのコードを実行するかを定義する仕組みです。

[LaravelTestProject\routes\web.php]を下記の通りに編集します。
:::details web.php の記述内容
**routes/web.phpとは**
`routes/web.php` ファイルで、Laravelプロジェクト内のルーティングを定義します。このファイルには、ウェブアプリケーションの異なるページやアクションに対するURLパスと、それに対応する処理を指定します。

具体的には `routes/web.php` ファイルで ルート（Route）を定義します。ルートは、HTTPメソッド（GET、POST、PUT、DELETEなど）とURLパスを指定し、それに対応するコントローラーのアクションやクロージャを関連付けます。例えば、特定のURLにアクセスしたときにどのコントローラーのアクションを実行するかを定義します。


```js:routes/web.php
<?php

use Illuminate\Support\Facades\Route;
/* HelloController クラスの名前空間のインポート文を追加する */
use App\Http\Controllers\HelloController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

/* Laravel welcome Page */
Route::get('/', function () {
    return view('welcome');
});
/* hello world page（ルーティングを追加する） */
Route::get('/hello', [HelloController::class,"index"]);
```
:::message
解説 - use ~\HelloController;

ここでは名前空間でのインポート文を追加しています。これは、この後に作成する コントローラー（`HelloController`）を使いたいので先に関連付けをしているのです。
:::

2. **コントローラーを作成して編集する**

MVCの**Controller（コントローラー）とは** ユーザーの入力に基づいてモデルとビューを制御（橋渡し）する役目を担う部分です。ユーザーが入力した情報に基づいて、モデルへデータを取り出す指示を、ビューにはモデルで取り出したデータを元に画面を表示する指示を出します。

まずはターミナルでコントローラーを作成します。
```js:Terminal
# コントローラーを作成する
root@~LaravelTestProject# php artisan make:controller HelloController
```

次に作成した[LaravelTestProject\app\Htttp\Controllers\HelloController.php]を編集します。
:::details HelloController.php の記述内容
```js:HelloController.php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class HelloController extends Controller
{
    // hello world page（メソッドを追加する）
    public function index()
    {
        // view（hello.blade.php）を呼び出す処理
        return view('hello');
    }
}
```
:::

3. **bladeファイルの作成と編集をする**

ブレード（Blade）とは、Laravelでビュー（View）を作るために用意されたテンプレートエンジン です。

MVCの **View（ビュー）とは** 表示や入出力などのユーザーが実際に見る画面（UI）を担当する部分です。 リクエストデータをControllerに送ったり、Controllerからレスポンスデータを受け取って画面に表示したりします。

まずはターミナルでブレードファイルを作成します。

```js:Terminal
# hello.blade.php を作成する
root@~LaravelTestProject# cd resources/views && touch hello.blade.php
```

次に作成した[resources/views/hello.blade.php]を編集します。
:::details hello.blade.php の記述内容
```js:hello.blade.php
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>My First Page</title>
</head>
<body>
    <h2>Hello World</h2>
</body>
</html>
```
:::

4. **アクセスして表示を確認する**  

ブラウザに http://localhost/hello でアクセスして「Hello World」が表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-24-13-05-12.png =500x)

5. **コンテナからログアウトする**
```js:Terminal
root@~views#  # exit
```

これで「**②テストページを作成する**」は完了です。

ここから先のセクションについては環境設定の理解を深めるためのものです。
環境設定の理解を深めたいという方はもう一踏ん張りですので頑張っていきましょう。

# ③設定ファイルを作成する
**Laravelでは、アプリ本体は configファイルを経由して .envファイルの情報を読み込みます。**

この理由は、`.env` ファイル の設定情報を直接読み込むのは危険だからです。

直接 `.env` ファイルを読み込んだ方が手っ取り早いように思えますが問題が起きます。例えば、コンフィギュレーションキャッシュ（`config:cache`）というコマンドを使うと `.env` ファイルを読み込めなくなるのは良くあることです。とても危険ですよね。

configファイルを経由していれば 「`.env` ファイルを読み込めなくなる」ようなことは起きません。これが`config` 経由で情報を読み込む理由です。


## .envファイルとconfigファイル
`.env` ファイルと `config` ファイルでは役割が違います。どちらも似たようなものに感じるかもしれませんが実は違うのです。それぞれの違いを見ていきましょう。

### .envファイルとは
`.env` ファイルは環境設定ファイルとも呼ばれます。envは、environment（環境）の省略です。

このファイルには データベースの名前、APIキー、メール送信のための情報 などを追加します。登録された情報は環境によって変える可能性があります。たとえば開発環境でのデータベースと本番環境でのデータベースは変更される場合などです。

### configファイルとは
`config` は、configuration（構造、設定）の省略です。

`config`の内容は環境が変わっても変わりません。つまり、「環境」が変わっても「構造や設定」が維持されるのです。これが`config` 経由で情報を読み込む理由です。
この `config` ファイルはconfigフォルダの中に入っています。


.envファイルとconfigファイルの役割と、なぜこの流れが必要なのかは、下記のサイトで詳しく解説されていますので一読しておいてください。
https://biz.addisteria.com/env_config/

## .env & config の基礎と理解
`.env` & `config` の基礎を理解するには、実際に設定ファイルを書いて動かすのが一番です。

ここでは、エラー画面を「500 | Server Error」に変更することを目標にしていきます。そのために、**.envファイルにあるAPP_DEBUGの値を変えてみる**ことにします。ついでに `config` にも触れてみましょう。

`.env` ファイル内の APP_DEBUG はデフォルトでは true に設定されています。APP_DEBUG はLaravelにアクセスしている時にプログラムの記述ミスやバグがあった場合に原因を究明するために必要となるエラーメッセージの詳細情報を出力してくれます。

.envファイルの基礎を理解するのはとても難しいです。下記のサイトを参照しながら「設定ファイルを作成する」ことをおすすめします。
https://reffect.co.jp/laravel/env-file-basic-understanding/

## 設定ファイルを作成する
**【目標】エラー画面を「500 | Server Error」に変更する**

0. コンテナにログインする
```js:Terminal
~Laravel9-Docker-TestPJ $ docker-compose exec php bash
root@~/var/www# cd LaravelTestProject
```

1. bladeファイルにエラーコードに書き換える
:::details resources/views/hello.blade.php の記述内容
```js:hello.blade.php
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>500 | Server Error</title>
</head>
<body>
    <h1>Laravel ENV FILE</h1>
    {{-- わざとスペルミスしています --}}
    <p>{{ $somethig }}</p>
    
</body>
</html>
```
:::
2. コントローラーを書き換える
:::details [app/Http/Controllers/HelloController.php] の記述内容
このコントローラーからViewの `<p>{{ $somethig }}</p>` に値を渡します。
```js:HelloController.php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class HelloController extends Controller
{
    // hello world page（メソッドを追加する）
    public function index()
    {
        /* view（hello.blade.php）を呼び出す処理 */
        return view('hello',["something"=>"FBK"]);
    }
}
```
:::message
解説

`hello.blade.php`でわざとスペルミスしているので、このコントローラーから値を渡せなくなっています。エラーを出さないようにするには `hello.blade.php` のスペルをコントローラーの `something` と一致するように修正する必要があります。

:::
3. ブラウザでLaravelの表示を確認する

ブラウザに [http://localhost/hello](http://localhost/hello) でエラーが表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-24-18-43-08.png)

4. `.env` ファイルの設定を変更する
```js:.env
APP_DEBUG=false
```
5. 設定変更を反映させるためキャッシュをクリアする
`.env` ファイルは一度ロードされてキャッシュされるとenvヘルパー関数を実行しても値はNULLになり画面にはなにも表示されません。その場合は `php artisan config:clear` を実行してください。
```js:Terminal
root@~LaravelTestProject # php artisan config:clear
```
:::message alert
重要

.env ファイルを書き換えた場合は、`php artisan config:clear` コマンドを実行してください。
:::
6. アクセスして表示を確認する

ブラウザに [http://localhost/hello](http://localhost/hello) でエラーが表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-24-18-51-01.png)
:::message alert
重要 - APP_DEBUGの使い分け

本番環境ではこのように開発中のコードが見えない形でエラーを表示させることが必須です。
この機会にしっかりと覚えておきましょう。

本番環境 → APP_DEBUG=false
開発環境 → APP_DEBUG=true

必要に応じでこのように書き換えましょう。
:::

最後にエラーを出さないようにしてみましょう。
:::details resources/views/hello.blade.php の記述内容
コントローラーの `something` と一致するようにスペルを修正します。
```js:hello.blade.php
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>500 | Server Error</title>
</head>
<body>
    <h1>Laravel ENV FILE</h1>
    {{-- スペルミスを修正する --}}
    <p>{{ $something }}</p>
    
</body>
</html>
```
:::

ブラウザに [http://localhost/hello](http://localhost/hello) で FBK が表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-24-20-51-08.png)

7. env関数を使ってみる（.envの現在の値を確認する）

[resources/views/hello.blade.php] を書き換えてください。
:::details resources/views/hello.blade.php の記述内容
```js:hello.blade.php
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>500 | Server Error</title>
</head>
<body>
    <h1>Laravel ENV FILE</h1>
    <p>{{ env('DB_CONNECTION')}}</p>
</body>
</html>
```
:::
8. アクセスして表示を確認する

ブラウザに [http://localhost/hello](http://localhost/hello) で mysql が表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-24-19-06-44.png)
9. config関数を使ってみる

[resources/views/hello.blade.php] を書き換えてください。
:::details resources/views/hello.blade.php の記述内容
```js:hello.blade.php
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>500 | Server Error</title>
</head>
<body>
    <h1>Laravel ENV FILE</h1>
    <p>{{ config('database.default') }}</p>
</body>
</html>

```
:::
10. アクセスして表示を確認する

ブラウザに [http://localhost/hello](http://localhost/hello) で mysql が表示されればOKです。
![](/images/laravel-and-docker-introduction-20230822/2023-08-24-19-06-44.png)
11. 独自configファイルを作成して編集する

まずは、`config/example.php` を作成します。
```js:Terminal
root@~LaravelTestProject # cd config && touch example.php
```

次に、`config/example.php` を編集します。
:::details config/example.php の記述内容
```js:example.php
<?php

return [
    // テスト用のconfigファイルのkey設定をする
    'key' => env('EXAMPLE_APP_KEY', 'EX_APP_KEY'),
];
```
:::

次に、`.env` ファイルを編集します。
:::details .env の記述内容
.env の末尾に `EXAMPLE_APP_KEY` を追加してください。
```js:.env
EXAMPLE_APP_KEY = 123456789ABCDEF
```
:::

次に、[resources/views/hello.blade.php] を書き換えてください。
:::details resources/views/hello.blade.php の記述内容
```js:hello.blade.php
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>500 | Server Error</title>
</head>
<body>
    <h1>Laravel ENV FILE</h1>
    <p>{{ env('EXAMPLE_APP_KEY')}}</p>
    <p>{{ config('example.key')}}</p>
</body>
</html>
```
:::
12. アクセスして表示を確認する

ブラウザに [http://localhost/hello](http://localhost/hello) で 123456789ABCDEF が表示されればOKです。  
無事に `.env` と `config` の設定が反映されていることが分かります。
![](/images/laravel-and-docker-introduction-20230822/2023-08-24-19-33-38.png)

13. 開発中なので`.env` ファイルの設定を戻す
```js:.env
APP_DEBUG=true
```

14. コンテナからログアウトする
```js:Terminal
root@~LaravelTestProject # exit
```

これで「**③設定ファイルを作成する**」は完了です。

ここまでの学習で`.env` と `config` について理解が深まったのではないでしょうか。
次回からは、本番環境と開発環境を切り替えを学んでいきます。

# ④本番環境と開発環境

0. コンテナにログインする
```js:Terminal
~Laravel9-Docker-TestPJ $ docker-compose exec php bash
root@~/var/www# cd LaravelTestProject
```

1. 現在の設定値を確認する
```js:Terminal
root@~LaravelTestProject # php artisan env
[中略]
    # local（開発）環境であることが分かります
   INFO  The application environment is [local].  
```
2. 本番環境に切り替える

まずは `.env` の下記の部分を書き換えてください。
```js:.env
APP_ENV=production
```
:::message 
それぞれのアプリケーション環境設定

`APP_ENV` には以下の3つの環境を設定することが一般的です。
- 開発環境（ローカル） → local
- 開発環境 → development
- 本番環境 → production
:::

次に、[resources/views/hello.blade.php] を書き換えます。
:::details resources/views/hello.blade.php の記述内容
```js:hello.blade.php
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>500 | Server Error</title>
</head>
<body>
    <h1>Laravel ENV FILE</h1>

    <?php

        if (App::environment('local')) {
            // 環境が local(開発）の場合
            echo "開発環境（ローカル）です";
        }elseif(App::environment('development')) {
            // 環境が development(開発）の場合
            echo "開発環境です";
        }elseif(App::environment('production')) {
            // 環境が production(本番）の場合
            echo "本番環境です";
        }else{
            // その他の環境
            echo "その他の環境です";
        }

    ?>
</body>
</html>
```
:::

3. アクセスして表示を確認する

ブラウザに [http://localhost/hello](http://localhost/hello) で 本番環境です が表示されればOKです。  
その他にも`.env` の `APP_ENV` の値を 色々（`local`, `development`, `production`）と変えてみましょう。
![](/images/laravel-and-docker-introduction-20230822/2023-08-25-12-04-27.png)
![](/images/laravel-and-docker-introduction-20230822/2023-08-25-12-12-31.png)
![](/images/laravel-and-docker-introduction-20230822/2023-08-25-12-12-57.png)

4. `.env` の設定を元に戻す
```js:.env
APP_ENV=local
```

5. コンテナからログアウトする
```js:Terminal
root@~LaravelTestProject # exit
```

これで「**④本番環境と開発環境**」は完了です。

ここまでの学習で 本番環境と開発環境の切り替え について理解が深まったのではないでしょうか。
次回からは、Laravelのための本格的なENV設定を学んでいきます。

# ⑤本格的なENV設定をする
Laravelは、フルスタックフレームワークです。フロントエンドもバックエンドも網羅したタイプのフレームワークです。今まで何も設定していなくても動いていたのはデフォルトの設定の範囲で問題のない機能の実装でしかなかったからです。

実際のところ、このセクションで行う内容も初期設定で動いてしまいます。しかし、それでは Dokcerファイル に合わせた設定に触れずに終わってしまいます。

例えば、Laravel側でテーブル定義をしてテーブルを作成する機能をマイグレーションと呼びます。この機能を使うには適切に `.env` を設定しておかないといけません。そのためにも「Dockerに合わせたENV設定」をしっかりと身につけておきたいところです。

ここでは理解を深めるためにも 「Dockerに合わせたENV設定」 を学んでいきます。

## 本格的なENV設定をする
**【目標】hello world を表示させる, phpMyAdminに接続する**
さっそく本格的なENV設定をしていきましょう。

今までの作業では直接 `.env` に記述してきましたが、ここからは `.env.example`に記述していきます。その理由は巻末の「超重要」のトピックをご覧ください。

この作業では `phpMyAdmin` は必須なので念のために再ビルドを実行しておきます。
特にGithubでコード管理してる方などは `phpMyAdmin` はリモートブランチに `push` されないので陥りがちです。
```js:Terminal
# Dockerで再ビルドする
~Laravel9-Docker-TestPJ $ docker-compose up -d
```

0. コンテナにログインする
```js:Terminal
~Laravel9-Docker-TestPJ $ docker-compose exec php bash
root@~/var/www# cd LaravelTestProject
```

1. `.env` を `.env.example` にコピーする
```js:Terminal
root@~LaravelTestProject # cp .env .env.example
```


2. `.env.example` の設定を書き換える

URL設定を `localhost` に変更する
```js:.env.example
APP_URL=http://localhost
```
DBの設定を変更する（DB_HOSTは localhost だと接続されない時がある）
```js:.env.example
# 値は docker-compose.ymlファイルと同じにする
DB_CONNECTION=mysql
DB_HOST=db
DB_PORT=3306
DB_DATABASE=mysql_test_db
DB_USERNAME=admin
DB_PASSWORD=secret
```
「④本番環境と開発環境」を実施している人は 不要な設定とファイルを削除する（後始末する）
```js:.env.example
EXAMPLE_APP_KEY = 123456789ABCDEF
```

3. `.env.example` を `.env` にコピーする

理由は後述しますが `.env.example` に記述して `.env` に反映させるのは開発のセオリーです。
```js:Terminal
root@~LaravelTestProject # cp .env.example .env
# キージェネレートする
root@~LaravelTestProject # php artisan key:generate
```

:::details .env.example の全体コード
```js:.env.example
APP_NAME=Laravel
APP_ENV=local
APP_KEY=base64:uDselircjsSAkOadnmIwVxEsTnkjQKjncsDmbLgA05s=
APP_DEBUG=true
APP_URL=http://localhost

LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=mysql
DB_HOST=db
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

4. configフォルダの不要な example.php を削除する
```js:Terminal
root@~LaravelTestProject # cd config && rm example.php
```

5. アクセスして表示を確認する

ブラウザに [http://localhost/hello](http://localhost/hello) で 開発環境（ローカル）です が表示されればOKです。
Dcokerファイルに合わせたENV設定は問題ないことが確認できました。
![](/images/laravel-and-docker-introduction-20230822/2023-08-25-12-12-57.png)

ブラウザに [http://localhost:8080/](http://localhost:8080/) で phpMyAdmin が表示されればOKです。 
phpMyAdmin が表示されているなら MySQL（DB）も phpMyAdmin 問題なく稼働しています。
![](/images/laravel-and-docker-introduction-20230822/2023-08-25-14-46-29.png)

6. コンテナからログアウトする
```js:Terminal
root@~config # exit
```

### .env.example について
:::message alert
超重要

最後に `.env` と `.env.example` について触れておきます。

Laravelでは、非常に重要な `.env` ファイルは Githib などで共有できないようになっています。これは  `.env` がシステムの根幹に関わる環境設定ファイルだからです。そのため `.gitignore` で `.env` が除外指定されています。そして除外されているべきものでもあります。

しかし、環境設定ファイルを雛形なしに作るのは大変です。そこで登場するのが `.env.example` です。`.env.example` ならば除外されることはありません。例えば、プライベートリポジトリなどセキュリティの高い状態で `.env.example（環境情報の値も記述されているもの）` 共有して差し替えていくのが開発現場でのセオリーです。

もっとセキュリティを高める場合は `.env.example` は雛形に徹して 環境情報の値を安全に共有して書き換えていくことになります。
:::

これで「**⑤本格的なENV設定をする**」は完了です。

ここまでの学習で Dockerを使ったENV設定 や データーベースを使うためのENV設定の方法を理解できたと思います。

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
