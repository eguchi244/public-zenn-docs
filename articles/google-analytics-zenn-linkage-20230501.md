---
title: "ZennにGoogleAnalyticsを導入する"
emoji: "😽"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Zenn", "GoogleAnalytics"]
published: true # 公開に指定する
---
# はじめに
GoogleAnalyticsでZennのPVをカウントしようと調べてみたところ、過去の関連記事とは一部の画面が変わっているようですので、最新版に対応するための本記事を執筆します。
(2023/04/27時点)

# 目的
ZennのPVをカウントできるように、GoogleAnalyticsを設定して、Zennと連携していきます。

# 内容
ZennとGoogleAnalyticsを連携するには、下記の3ステップだけです。

1. GoogleAnalyticsの設定
2. Zennのアカウント設定の変更
3. GoogleAnalyticsの動作確認

さっそく、はじめてみましょう。

# GoogleAnalyticsの設定
### ①Googleアカウント作成
Googleアカウントがある前提で説明をします。アカウント作成は下記を参照してください。
https://support.google.com/accounts/answer/27441?hl=ja

### ②Google Analytics にアクセス
まず最初に、 [GoogleAnalyticsの公式ページ](https://analytics.google.com) にアクセスしてください。
「測定を開始」ボタンを押してセットアップを開始します。
![](https://storage.googleapis.com/zenn-user-upload/7338ba1fa7b4-20230427.png)

### ③アカウント設定
まずは、「アカウント設定」を行います。適当なアカウント名を設定してください。
また、「アカウントのデータ共有設定」は、何も触らずに進んでOKです。
![](https://storage.googleapis.com/zenn-user-upload/644d4aaf4963-20230427.png)

### ④プロパティ設定
下記の画像のように「プロパティ設定」をしてください。プロパティ名は適当でOKです。
![](https://storage.googleapis.com/zenn-user-upload/75a988799525-20230427.png)

### ⑤ビジネス情報設定
必要に応じて「ビジネスの説明」を設定してください。
![](https://storage.googleapis.com/zenn-user-upload/be931ff62517-20230427.png)

### ⑥ビジネス目標設定
ビジネス目標に応じた「ビジネス目標」を設定していください。
![](https://storage.googleapis.com/zenn-user-upload/14ef21cd8212-20230427.png)
「利用規約」の画面が出てくるので、画面に従って同意してください。
![](https://storage.googleapis.com/zenn-user-upload/f8f0beac81f1-20230427.png)

### ⑦データストリームの作成
データの収集先を指定して「データストリーム」を設定していきます。
今回は「ウェブ」を指定します。
![](https://storage.googleapis.com/zenn-user-upload/9fcb84145eff-20230427.png)
「データストリーム」の設定では、URL名とストリーム名を指定します。
ここでは、URL名を「zenn.dev」に、ストリーム名を「Zenn PV」にします。
![](https://storage.googleapis.com/zenn-user-upload/120615d9029b-20230427.png)
下記のように「データストリーム」が作成されました。この「測定ID」が重要です。
クリップボードにコピーをしておきましょう。
![](https://storage.googleapis.com/zenn-user-upload/0bf2bc74bd0b-20230427.png)

### ⑧メール配信設定
プロパティやGoogleAnalyticsの設定が完了すると「メール配信設定」がポップアップしてきます。
特に必要なければ、「保存」または「すべてをオフにして保存」ボタンを押してください。
![](https://storage.googleapis.com/zenn-user-upload/9ad0c1e02718-20230427.png)

### ⑨GoogleAnalytics設定の完了
これでGoogleAnalyticsの設定は完了です。
「測定ID」については、GoogleAnalyticsの「管理」＞「データストリーム」からいつでも確認できます。

# Zennのアカウント設定の変更
ZennをGoogleAnalyticsと連携していきます。
ヘッダーの自分のアイコンをクリックして、「アカウント設定」を選択します。
![](https://storage.googleapis.com/zenn-user-upload/68cd2aee4c65-20230427.png)
アカウント画面から「GoogleAnalytics」の「トラッキングIDを設定」ボタンを押します。
![](https://storage.googleapis.com/zenn-user-upload/62d42f5ed738-20230427.png)
トラッキングIDの入力画面に、コピーしておいたID（ G- から始まる文字列）を入力して保存します。
![](https://storage.googleapis.com/zenn-user-upload/c2e25a830567-20230427.png)
Google Analyticsの項目のところにトラッキングIDが表示されていたら成功です。
![](https://storage.googleapis.com/zenn-user-upload/fa0a0a12c56b-20230427.png)
以上で、設定は完了です。

# GoogleAnalyticsの動作確認
自分の、 [GoogleAnalyticsページ](https://analytics.google.com) にアクセスしてみましょう。
GoogleAnalyticsにアクセス履歴が表示されていれば成功です。
下記の画面は、GoogleAnalyticsの「レポート」＞「リアルタイム」から確認できます。
![](https://storage.googleapis.com/zenn-user-upload/4e4891a68f11-20230428.png)

# まとめ
今回は、zennのアクセス解析にGoogle Analyticsを導入してみました。
Zennは優れたエンジニア情報共有サービスですので、アクセス解析できるのは嬉しいですよね。
投げ銭も出来るサービスということで将来性も抜群です。
そのため、Zennのアクセス解析は、その重要度を増すばかりです。
本記事を参考に、Zennにアクセス解析を導入していただければ幸いです。