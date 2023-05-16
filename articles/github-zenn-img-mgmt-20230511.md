---
title: "Github連携でZennの画像管理をする方法"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Zenn", "Github", "VSCode"]
published: true # 公開に指定する
---
# はじめに
Github連携でZennの画像管理をする方法をご紹介します。スクリーンショット画像に焦点を当てて、Github連携の場合の画像管理を紹介されている記事がありますが、Github連携での画像管理方法を、それぞれの方法で論点整理されたものが欲しいので執筆することにしました。

# 目的
Github連携でZennの画像管理を出来るようにすることです。
具体的には下記の「内容」に記載された3点を習得することを目的とします。

# 内容
Github連携でZennの画像管理をする論点は下記の3点です。

1. Zennの「画像をアップロード」を使用する方法
2. GitHubリポジトリ連携で画像をアップロードする方法
3. スクリーンショット画像を便利に画像管理する方法

さっそく、はじめてみましょう。

# Zennの「画像をアップロード」を使用する方法
Zennの管理画面から、「画像をアップロード」で画像を使用することもできます。デメリットは画像がZennのサーバーに保存されるので、Zennがサービス終了すると画像も消滅してしまうことです。Githubで本や記事をバックアップしていても、この方法だと画像はバックアップされません。それでも「GitHubリポジトリ連携で画像をアップロードする方法」よりは簡単ですので、その方法が難しくて良く分からないという方は、こちらを採用すればGithub連携で画像が使えます。

### Zennの「画像をアップロード」の流れ
Zennの管理画面にログインして、下記の操作を実施してください。

1. 画面右上のユーザーアイコンをクリックする
![](/images/github-zenn-img-mgmt-20230511/img-2023-05-11-13.35.37.png)
2. 「〜の管理」をクリックする
![](/images/github-zenn-img-mgmt-20230511/img-2023-05-11-13.46.47.png =300x)
3. 画像をアップロードする
![](/images/github-zenn-img-mgmt-20230511/img-2023-05-11-13.48.41.png =600x)
4. 画像URLをコピーする
![](/images/github-zenn-img-mgmt-20230511/img-2023-05-11-13.55.04.png =600x)
5. 記事や本にコピーしたURLを `![](![](https://~20230511.jpg)` の形式で埋め込む
```
![](https://~20230511.jpg) # コピーしたURLを（）内に貼り付ける
```
6. 記事や本をプレビューするコマンドを実施する
```
$ npx zenn preview # プレビュー開始
$ 👀 Preview: http://localhost:8000
```
ブラウザから`http://localhost:8000`でアクセスして画像が表示されていればOKです。

7. Githubにコミット・プッシュする
```
$ git branch -M main # ブランチ名を main にする
$ git add . # ステージングする
$ git commit -m "first commit" # コミットする
$ git push -u origin main # pushする
```
Githubにアクセスして、記事が作成されていればOKです。

:::message
使用頻度の高いスクリーンショットを便利にアップロードする方法
下記の操作を実施するだけです。

1. 画像をスクリーンショットする
2. Zennの画像アップロード画面で ペースト（`Cmd+V`）する
3. 画像URLをコピーする

これだけなので簡単ですね！
:::

Github連携での記事の書き方がわからない方は、下記の記事を参考にしていください。
https://zenn.dev/eguchi244_dev/articles/github-zenn-linkage-20230501#%E2%91%A2%E8%A8%98%E4%BA%8B%E3%82%92github%E3%81%A7%E3%83%90%E3%83%BC%E3%82%B8%E3%83%A7%E3%83%B3%E7%AE%A1%E7%90%86%E3%81%99%E3%82%8B

# GitHubリポジトリ連携で画像をアップロードする方法
Githubリポジトリで画像を管理するメリットは、Githubレポジトリで画像を保存するので、画像のバックアップができることです。Zennの「画像をアップロード」では、Zennのサービスが終了すると画像も消滅してしまいます。これではGithubを使う利点が減ってしまいます。

そこで下記の具体的な流れに沿って画像管理をしてみましょう。

1. `/images` ディレクトリを設置して画像を保存する
2. 記事や本に `![](/images/sample.png)` のように画像を埋め込む
3. Githubにコミット・プッシュする

念のために公式記事も掲載しておきます。
https://zenn.dev/zenn/articles/deploy-github-images

### ①/images ディレクトリを設置して画像を保存する
画像ファイルはリポジトリ直下に `/images` ディレクトリを配置します。この位置に配置しないと Zenn CLI による管理対象になりません。`/images` ディレクトリの中の構造に制限はありません。必要に応じてカスタマイズしてください。
```
.
├─ articles
│  └── example-article-1.md
└─ images
   ├── example-image1.png
   └── example-article-1
       └─ image1.png
```
今回はリポジトリ直下に、`/images/blog-slug-name/` の構成でディレクトリを設置します。
```
$ mkdir images # imagesディレクトリを作成
$ cd images # imagesディレクトリに移動
$ mkdir example-article-1 # 必要に応じて任意の記事名でディレクトリを作成
$ cd .. # リポジトリ直下に戻る
```
次に上記に作成したディレクトリに画像を配置する
```
.
└─ images
   └── example-article-1
       └─ image1.png
```
これで`/images` ディレクトリの設置と画像の配置は完了です。

### ②記事や本に `![](/images/sample.png)` のように画像を埋め込む
今回、作成している記事に、下記のようにPathを指定して記事を埋め込んでください。
```
![](/images/blog-slug-name/sample.png) # blog-slug-nameは、任意で決めたリポジトリ名です
```
埋め込まれた画像が正しく表示されているかプレビューしてみましょう。
```
$ npx zenn preview # プレビュー開始
$ 👀 Preview: http://localhost:8000
```
ブラウザから`http://localhost:8000`でアクセスして画像が表示されていればOKです。

これで記事や本への画像の埋め込みは完了です。

### ③Githubにコミット・プッシュする
最後にGithubに下記のコマンドを使用して、コミット・プッシュしましょう。
```
$ git branch -M main # ブランチ名を main にする
$ git add . # ステージングする
$ git commit -m "first commit" # コミットする
$ git push -u origin main # pushする
```
Githubにアクセスして、記事が作成されていればOKです。

# スクリーンショット画像を便利に画像管理する方法
使用頻度の高いスクリーンショットの画像管理ですが、Githubリポジトリに保存しておこうと思うと大変です。Zennの「画像をアップロード」を使用する場合は、その画面でペースト `(CTRL)Cmd+V` するだけです。しかし、Githubリポジトリに保存するには下記の操作が必要です。

1. `/images` ディレクトリに画像を配置する
2. 記事や本に `![](/images/sample.png)` のように画像を埋め込む

OSによっては、画像パスの修正が必要になったりで、煩わしさを感じてしまいます。
そこで、この操作を省略できる方法をご紹介します。
下記の記事が非常に参考になりますので掲載しておきます。

https://zenn.dev/team_zenn/articles/image-paste-zenn-upload?redirected=1

### ①VSCodeに「VSCode Paste Image」を導入して設定する
1. VSCode Paste Image をインストールする

https://marketplace.visualstudio.com/items?itemName=mushan.vscode-paste-image

2. プラグインの設定をする

Zenn専用にpath指定をするので、ワークスペース設定での利用をお勧めします。

まずは、リポジトリ直下に、`.vscode/settings.json`を配置します。
```
$ mkdir .vscode # .vscodeディレクトリを作成
$ cd .vscode # .vscodeディレクトリに移動
$ touch settings.json # settings.jsonを作成
$ cd .. # リポジトリ直下に戻る
```
次に`settings.json`に設定を記述する
```
{
    "pasteImage.insertPattern": "${imageSyntaxPrefix}/images/${currentFileNameWithoutExt}/${imageFileName}${imageSyntaxSuffix}",
    "pasteImage.path": "${projectRoot}/images/${currentFileNameWithoutExt}"
}
```
:::message
解説
・"pasteImage.insertPattern"は、貼り付け文字列をmarkdown形式で設定します
今回は、`![](/images/blog-slug-name/2023-05-11-15-43-36.png)`という形式です。
・"pasteImage.path"は、画像の保存場所を指定しています
今回は、`/images/blog-slug-name/image-name.png`というようなPathに保存されます。
:::

### ②スクリーンショットのファイル名を 日付のみ にする
OSによっては、画像パスの修正が必要です。例えば、Macのスクリーンショット名は下記の画像のように「スクリーンショット 2023-05-12 14.10.03.png」な感じに長ったらしく、全角カナ、半角スペースまで入ってしまっています。ブラウザによっては画像として認識しないものもあると思いますので、正しく画像が表示されるか心配になります。そのため、スクリーンショットのファイル名を **日付だけ** にしておきましょう。
![](/images/github-zenn-img-mgmt-20230511/2023-05-12-14-14-13.png =200x)

下記のコマンドを実行すればOKです。
```
$ defaults write com.apple.screencapture name ""
```
元に戻すには下記のコマンドを実行してください。
```
$ defaults write com.apple.screencapture name スクリーンショット
```
:::message
解説
Macのデフォルトでは、スクリーンショットは「スクリーンショット [日付] [時刻]. png」という名前でデスクトップに保存されます。今回は、先頭のファイル名を無指定（""）で、指定することにより日付のみにしています。コマンドの解説は下記の通りです。

1. 「defaults write」→「設定を書き込む」
2. 「com.apple.screencapture」→「apple.comのスクリーンキャプについて」
3. 「name ""」→「ファイル名を指定なしにする」

下記の記事が詳細で参考になるので掲載しておきます。
https://chiilabo.com/2020-09/macos-screenshot-default-name-change/
:::

### ③記事に画像をコピー貼り付けする
まずはスクリーンショット画像をクリップボードに保存する形でコピーしてください。
Windowsはデフォルトでクリップボードにコピーされますが、Macは下記の操作が必要です。

- `Command＋Control＋Shift＋3` → 全画面をクリップボードにコピー
- `Command＋Control＋Shift＋4` → 選択範囲をクリップボードにコピー

その次にエディターで貼り付け`CTRL(cmd)+ALT(option)+V`を押します。
以下のような画像リンクがmarkdown形式で作成されます。
```
![](/images/blog-slug-name/2023-05-11-15-43-36.png)
```
これで一連の流れは完了です。
Zennの「画像管理のアップロード」を使用する場合の煩わしい部分が解消されたと思います。
バックアップをしながら、簡単に画像リンクを作れるので便利です。
ぜひ活用していただければと思います。

# まとめ
如何だったでしょうか。今回はGithub連携でZennの画像管理をする方法を3つご紹介しました。
それぞれに長所と短所がありますので、皆様の状況に応じて選択していただければと思います。
内容としては簡単なものから少し難しいものもあったと思います。
しかし、使いこなすことができれば多くのメリットを享受できるようになります。
ぜひ、挑戦していただければと思っております。