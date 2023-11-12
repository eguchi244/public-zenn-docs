---
title: "LaravelのViteをLaravel Mixに戻す方法"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Laravel", "Vite", "LaravelMix"]
published: true # 公開に指定する
---
# はじめに
Laravel9以降のバージョンでは、フロントエンド(JS,CSS)のビルドツールが、従来のLaravel MixからViteへと置き換わりました。

この記事は、LaravelのViteをLaravel Mixに戻したいという方のためのものです。

この記事は下記のサイトを参考にして作成されています。
https://biz.addisteria.com/remove_vite/

なお、Vue.jsなどを使用している場合は追加の設定が必要な点にご留意ください。

もしも、Viteを使用して Vue.js などを使用する場合は下記の記事が参考になります。
ご興味のある方はこちらも選択するのもありだと思います。
https://reffect.co.jp/laravel/laravel9_vite/
https://reffect.co.jp/laravel/laravel9_vite_react/

# Laravelを導入する
下記の記事を参考にしてLaravelのプロジェクトを導入してください。
https://zenn.dev/eguchi244_dev/articles/laravel-and-docker-introduction-20230822

Dockerを使いたくない場合は下記の Laravel Sail などが簡単でおすすめです。
【Windows】
https://chigusa-web.com/blog/laravel-sail/
【Mac】
https://chigusa-web.com/blog/laravel-sail-mac/

これで「Laravelを導入する」は完了です。

# LaravelからViteを削除する
ここでは「LaravelからViteを削除する」方法を紹介します。

0. コンテナにログインする
```js:Terminal
# nodeコンテナにログインする
root@~# docker-compose exec node /bin/sh
# プロジェクトディレクトリに移動する
root@~# cd <プロジェクトディレクトリ名>
```
1. Nodeモジュールのインストールしておく
```js:Terminal
# npm(jsモジュール)をインストールする
root@~# npm install
```

2. Vite削除コマンドを実行する
```js:Terminal
root@~# npm remove vite
root@~# npm remove laravel-vite-plugin
```

3. Vite設定ファイル（vite.config.js）を削除する
```js:Terminal
root@~# rm -rf vite.config.js
```

4. テンプレートファイルのリンクを無効にする

テンプレートファイルを作成してる場合は下記の部分を無効または削除します。
```js:[resources/views/layouts/app.balde.php]
@vite([‘resources/css/app.css’, ‘resources/js/app.js’])
```
```js:[resources/views/layouts/guest.blade.php]
@vite([‘resources/css/app.css’, ‘resources/js/app.js’])
```

5. `package.json` を修正する
:::details package.jsonの記述内容
```js:package.json
{
    "private": true,
    "scripts": {
        /* 削除する */
        // "dev": "vite",
        // "build": "vite build"
    },
    "devDependencies": {
        "axios": "^1.1.2",
        "laravel-vite-plugin": "^0.7.2",
        "lodash": "^4.17.19",
        "postcss": "^8.1.14",
        /* 削除する */
        // "vite": "^4.0.0"
    }
}
```
:::

6. jsファイルを修正する

`resources/js/app.js` を下記のように修正します。
```js:app.js の修正部分
// import './bootstrap';
require('./bootstrap');
```
:::details [resources/js/app.js]の記述内容
```js:[resources/js/app.js]
// import './bootstrap';
require('./bootstrap');
```
:::

`resources/views/js/bootstrap.js` を下記のように修正します。
```js:bootstrap.js の修正部分
// import _ from 'lodash';
window._ = require('lodash');
 
// import axios from 'axios';
window.axios = require('axios');
 
window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
```
:::details [resources/js/bootstrap.js]の記述内容
```js:[esources/js/bootstrap.js]
// import _ from 'lodash';
window._ = require('lodash');

/**
 * We'll load the axios HTTP library which allows us to easily issue requests
 * to our Laravel back-end. This library automatically handles sending the
 * CSRF token as a header based on the value of the "XSRF" token cookie.
 */

// import axios from 'axios';
window.axios = require('axios');
window.axios = axios;

window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

/**
 * Echo exposes an expressive API for subscribing to channels and listening
 * for events that are broadcast by Laravel. Echo and event broadcasting
 * allows your team to easily build robust real-time web applications.
 */

// import Echo from 'laravel-echo';

// import Pusher from 'pusher-js';
// window.Pusher = Pusher;

// window.Echo = new Echo({
//     broadcaster: 'pusher',
//     key: import.meta.env.VITE_PUSHER_APP_KEY,
//     cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER ?? 'mt1',
//     wsHost: import.meta.env.VITE_PUSHER_HOST ? import.meta.env.VITE_PUSHER_HOST : `ws-${import.meta.env.VITE_PUSHER_APP_CLUSTER}.pusher.com`,
//     wsPort: import.meta.env.VITE_PUSHER_PORT ?? 80,
//     wssPort: import.meta.env.VITE_PUSHER_PORT ?? 443,
//     forceTLS: (import.meta.env.VITE_PUSHER_SCHEME ?? 'https') === 'https',
//     enabledTransports: ['ws', 'wss'],
// });
```
:::

7. `.env` と `.env.example` を修正する

`.env.example` のVite用の設定を削除し、Laravel Mix用の設定を追加します。

```js:.env.example（削除）
VITE_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
VITE_PUSHER_HOST="${PUSHER_HOST}"
VITE_PUSHER_PORT="${PUSHER_PORT}"
VITE_PUSHER_SCHEME="${PUSHER_SCHEME}"
VITE_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"
```

```js:.env.example（追加）
MIX_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
MIX_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"
```

:::details .envの全体コード
Dockerを使ってない方はこちらからコピーするのを避けてください。
```js:.env
APP_NAME=Laravel
APP_ENV=local
APP_KEY=base64:7wMLRSDs8r6avMME1LXmjg+dc1SCBrcwtORGBM1N4PY=
APP_DEBUG=true
APP_URL=http://localhost

LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=mysql
DB_HOST=db
DB_PORT=3306
DB_DATABASE=LaravelProject_test_db
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

MIX_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
MIX_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"
```
:::

次に `.env.example` を `.env` にコピーします。
```js:Terminal
root@~ # exit
root@~ # docker-compose exec php bash
root@~ # cd <プロジェクトディレクトリ>
# .env.example を .env にコピー
root@~ # cp .env.example .env
# キージェネレートする
root@~ # php artisan key:generate
root@~ # exit
```

これで「LaravelからViteを削除する」は完了です。

# LaravelにLaravel Mixを導入する
次に LaravelMix を導入していきます。

1. LaravelMixをインストールする
```js:Terminal
# nodeコンテナにログインする
root@~# docker-compose exec node /bin/sh
root@~# cd <プロジェクトディレクトリ>
root@~# npm install --save-dev laravel-mix
```
2. `webpack.mix.js` を作成する

まずは、`webpack.mix.js` を作成します。
```js:Terminal
root@~# touch webpack.mix.js
```

次に、`webpack.mix.js` を編集します。
:::details webpack.mix.jsの記述内容
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
    ]);
```
:::

3. MixでビルドしたJSやCSSをBladeファイルで読み込めるように追加する
```js:Bladeファイル（resources/views/welcome.blade.phpなど）
{{-- 下記を追加する --}}
<!-- Styles -->
<link rel="stylesheet" href="{{ mix('css/app.css') }}">
<!-- Scripts -->
<script src="{{ mix('js/app.js') }}" defer></script>
```
4. `package.json` を修正する

package.jsonの "script" に下記を追加する。
```js:package.json に追加
"dev": "npm run development",
"development": "mix",
"watch": "mix watch",
"watch-poll": "mix watch -- --watch-options-poll=1000",
"hot": "mix watch --hot",
"prod": "npm run production",
"production": "mix --production"
```
:::details package.json の記述内容
```js:package.json
{
    "private": true,
    "scripts": {
        // スクリプト部分に追加する
        "dev": "npm run development",
        "development": "mix",
        "watch": "mix watch",
        "watch-poll": "mix watch -- --watch-options-poll=1000",
        "hot": "mix watch --hot",
        "prod": "npm run production",
        "production": "mix --production"
    },
    "devDependencies": {
        "axios": "^1.1.2",
        "laravel-vite-plugin": "^0.7.2",
        "lodash": "^4.17.19",
        "postcss": "^8.1.14"
    }
}
```
:::

5. jsファイルを修正する

「LaravelからViteを削除する」の「jsファイルを修正する」と同じなので省略します。

6. `.env` と `.env.example` を修正する

「LaravelからViteを削除する」の「.envを修正する」と同じなので省略します。

7. npm(jsモジュール)を実行する
```js:Terminal
root@~# npm update && npm run dev
```
![](/images/restore-laravel-vite-to-mix-20230829/2023-08-30-13-17-45.png)

上記のように「successfully」になっていれば成功です。

これで「LaravelにLaravel Mixを導入する」は完了です。

# まとめ
LaravelのViteをLaravel Mixに戻す方法を紹介させていただきました。
世の中の開発現場の全てが Vite を使っている訳ではありません。
そういう時に Laravel Mix に戻して開発を開始する機会もあるかもしれません。
もちろん、推奨されるものではありませんが事情に左右されることはあります。
そんな時の皆様の一助となれればと思っております。