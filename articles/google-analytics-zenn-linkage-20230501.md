---
title: "ZennにGoogleAnalyticsを導入する"
emoji: "👻"
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
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-06-20.png)

### ③アカウント設定
まずは、「アカウント設定」を行います。適当なアカウント名を設定してください。
また、「アカウントのデータ共有設定」は、何も触らずに進んでOKです。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-08-01.png)

### ④プロパティ設定
下記の画像のように「プロパティ設定」をしてください。プロパティ名は適当でOKです。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-09-09.png)

### ⑤ビジネス情報設定
必要に応じて「ビジネスの説明」を設定してください。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-10-42.png)

### ⑥ビジネス目標設定
ビジネス目標に応じた「ビジネス目標」を設定していください。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-12-05.png)
「利用規約」の画面が出てくるので、画面に従って同意してください。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-12-59.png)

### ⑦データストリームの作成
データの収集先を指定して「データストリーム」を設定していきます。
今回は「ウェブ」を指定します。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-14-02.png)
「データストリーム」の設定では、URL名とストリーム名を指定します。
ここでは、URL名を「zenn.dev」に、ストリーム名を「Zenn PV」にします。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-14-55.png)
下記のように「データストリーム」が作成されました。この「測定ID」が重要です。
クリップボードにコピーをしておきましょう。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-15-41.png)

### ⑧メール配信設定
プロパティやGoogleAnalyticsの設定が完了すると「メール配信設定」がポップアップしてきます。
特に必要なければ、「保存」または「すべてをオフにして保存」ボタンを押してください。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-16-34.png)

### ⑨GoogleAnalytics設定の完了
これでGoogleAnalyticsの設定は完了です。
「測定ID」については、GoogleAnalyticsの「管理」＞「データストリーム」からいつでも確認できます。

# Zennのアカウント設定の変更
ZennをGoogleAnalyticsと連携していきます。
ヘッダーの自分のアイコンをクリックして、「アカウント設定」を選択します。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-17-35.png)
アカウント画面から「GoogleAnalytics」の「トラッキングIDを設定」ボタンを押します。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-18-39.png)
トラッキングIDの入力画面に、コピーしておいたID（ G- から始まる文字列）を入力して保存します。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-20-24.png)
Google Analyticsの項目のところにトラッキングIDが表示されていたら成功です。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-21-19.png)
以上で、設定は完了です。

# GoogleAnalyticsの動作確認
自分の、 [GoogleAnalyticsページ](https://analytics.google.com) にアクセスしてみましょう。
GoogleAnalyticsにアクセス履歴が表示されていれば成功です。
下記の画面は、GoogleAnalyticsの「レポート」＞「リアルタイム」から確認できます。
![](/images/google-analytics-zenn-linkage-20230501/2023-05-12-13-22-52.png)

# まとめ
今回は、zennのアクセス解析にGoogle Analyticsを導入してみました。
Zennは優れたエンジニア情報共有サービスですので、アクセス解析できるのは嬉しいですよね。
投げ銭も出来るサービスということで将来性も抜群です。
そのため、Zennのアクセス解析は、その重要度を増すばかりです。
本記事を参考に、Zennにアクセス解析を導入していただければ幸いです。