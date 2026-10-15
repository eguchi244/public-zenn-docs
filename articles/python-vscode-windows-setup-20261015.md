---
title: "【Windows】Python + VSCodeで環境構築"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python", "vscode", "Windows"]
published: true # 公開に指定する
---
# はじめに
この記事では「Python + VSCodeで環境構築すること」を目指します。
上記はシンプルな構成での環境構築なのではじめの一歩のための記事です。

但し、Pythonは後から違うバージョンのPythonを再インストールするだけで動かなくなります。
そのため、Pythonを使うのならば下記の記事を参考に環境構築することをお勧めします。

https://zenn.dev/hoshinagi1219/articles/091bdb6755b16f#4.-%E5%AE%9F%E8%B7%B5%EF%BC%9A%E4%BB%BB%E6%84%8F%E3%81%AE%E3%83%90%E3%83%BC%E3%82%B8%E3%83%A7%E3%83%B3%E3%81%AE%E4%BB%AE%E6%83%B3%E7%92%B0%E5%A2%83%E3%82%92%E4%BD%9C%E6%88%90%E3%81%99%E3%82%8B

![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-15.webp =400x)

# 目的
WindowsにPythonとVisual Studio Code（VSCode）を導入し、VSCodeでPythonのプログラムを書いて実行できるようにする。

# 内容
Python + VSCodeの環境構築は、下記の4ステップです。

1. Pythonを導入する
2. Visual Studio Codeを導入する
3. Visual Studio CodeでPythonを使う
4. pipでライブラリをインストールして動作確認する

さっそく、はじめてみましょう。

# 環境構築の目標
下記の構成で環境構築することを目標とします。

:::message
【環境構築の目標】

- Python：Python 3.12.10 (長期安定版)
- IDE・テキストエディタ：Visual Studio Code latest
:::

# Pythonを導入する
Pythonの導入は下記手順だと5分で完了します。

### ①Pythonインストーラーをダウンロードする
Pythonの公式サイトからダウンロードを行います。
https://www.python.org/downloads/

### ②インストーラーを実行する
ダウンロードしたインストーラーをダブルクリックもしくは右クリックから実行でインストールします。

:::message
画像は Python 3.12.1 のインストーラーの画面です。3.12.10 でも手順は同じです。
:::

![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-17.png =500x)

下の「Add python.exe to PATH」にチェックを入れてから、【Install Now】をクリックする。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-18.png =500x)

プログレスバー（緑色のやつ）が一番右に行くまで待ちます。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-19.png =500x)

「Setup was successfully」が表示されたら、【close】ボタンをクリックして閉じます。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-20.png =500x)

これでpython本体のインストールは完了です。

### ③Pythonを実行してみる（動作確認）
実際にpythonが実行できるか確認してみましょう。

「コマンドプロンプト」を使用するために、下の検索バーに「cmd」と入力し、検索結果に出てきた「コマンドプロンプト」を開きます。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-21.png =500x)

「コマンドプロンプト」が表示されたら、「python」と入力し、Enterキーを押す。

```shell:cmd
python
```

```text:実行結果
Python 3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

上記の例のように、「Python 3.12.10 ...」みたいなのが表示されて、>>>（入力待ち状態）になったらOKです。

適当にプログラムに計算させてみましょう！

```python:cmd
>>> 18782+18782
37564
```

18782（いやなやつ）+18782=37564（皆殺し）になりました。　あってますね！

コマンドプロンプトは、右上の×マークで消してOKです。

# Visual Studio Codeを導入する
VSCodeの導入は下記手順だと5分で完了します。

### ①VSCodeインストーラーをダウンロードする
VSCodeの公式サイトからダウンロードします。
https://code.visualstudio.com/

### ②VSCodeをインストールする
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-25.webp)
ダウンロードしたインストーラーをダブルクリックもしくは右クリックから実行でインストールします。

あとは下記画像の通りに進めてください。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-26.webp =500x)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-27.webp =500x)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-28.webp =500x)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-29.webp =500x)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-30.webp =500x)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-31.webp =500x)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-32.webp =500x)

VSCodeのインストールが完了したら，PCを再起動してください。

# Visual Studio CodeでPythonを使う
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-33.png)
Visual Studio CodeでPythonを使えるようにする作業は15分で完了します。

タスクバーのWindowsボタンを押して，Visual Studio Codeと打てば起動できます。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-34.webp)

### ①Python用の拡張機能を追加する
VSCodeは拡張パックを導入することで，機能を追加し便利にできます。
Python extension for Visual Studio CodeというPython専用の拡張パックを導入します。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-35.webp)

### ②PythonのPathを設定する
Python: Default Interpreter Pathと検索し，python.exeまでのパスを入力します。
python.exeの場所，パス取得方法は画像より下に記述しました。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-36.webp)

:::message
Python: Default Interpreter Pathが表示されない場合は，VSCodeを再起動してみましょう！
:::

:::details python.exeまでのパスの探し方
①タスクバーの Windowsボタンからファイルの場所を開きます。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-37.webp)
②python.exeを右クリックしてパスをコピーします（パスの“〇“は後で削除してください）。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-38.webp)
:::

### ③Pythonおよびライブラリの動作確認をする
Pythonファイルを作成して実際にVSCodeで プログラミングできるか試します。

:::message
【動作確認手順】
①フォルダを新たに作成する
②VSCodeでフォルダを開く
③フォルダ内にpythonファイルtest.pyを作成する
④コードを書いて，F5を押して実行する→Pythonの動作確認
⑤importを含めたコードをF5で実行する→ライブラリの動作確認
:::

①フォルダを新たに作成する
②VSCodeでフォルダを開く
③フォルダ内にpythonファイルtest.pyを作成する
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-39.webp)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-40.webp)

④コードを書いて，F5を押して実行する→Pythonの動作確認
test.pyにコードを書いていきます。

```python:test.py
print('設定完了')
```

上記のコードを書いてキーボードのF5か右上の三角マークを押してPythonを実行します。
VSCodeの下部にあるTerminalで設定完了という文字が出力されるはずです。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-41.webp)
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-42.webp)

⑤importを含めたコードをF5で実行する→ライブラリの動作確認
test.pyにimport datetimeを加えて，コードを書いていきます。

```python:test.py
import datetime

print(datetime.datetime.today())

# 2023-02-11 16:51:22.854424
```

上記のコードを書いてキーボードのF5を押してPythonを実行します。
VSCodeの下部にあるTerminalで今日の日付，時間が出力されるはずです。

# pipでライブラリをインストールする
最後にライブラリを追加して実行できるか確認します。

### ①Numpyをインストールする
AIでの計算に必ず使用されている数値計算用ライブラリの[Numpy](https://numpy.org/)をインストールします。
![](/images/python-vscode-windows-setup-20261015/2026-04-16-20-55-43.webp)

```shell:cmd
pip install numpy
```

```text:実行結果
Collecting numpy
  Downloading numpy-2.5.4-cp312-cp312-win_amd64.whl.metadata (6.6 kB)
Downloading numpy-2.5.4-cp312-cp312-win_amd64.whl (12.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.6/12.6 MB 20.7 MB/s eta 0:00:00
Installing collected packages: numpy
Successfully installed numpy-2.5.4
```

### ②Numpyの動作確認をする
インストールに成功したら，numpyでコードを書いて実行します。

```python:test.py
import numpy

# 数値リストを作成
x = [1, 31, 56 , 74]
# sumで合計値計算
print(numpy.sum(x))

# 162
```

ここまで完了すれば，あとは自分の思うとおりに開発していくのみです。
お疲れさまでした。

# まとめ
今回はWindowsにPythonとVisual Studio Codeを導入し、VSCodeでPythonを実行できるようにしました。
Pythonの導入、VSCodeの導入、VSCodeの設定、pipによるライブラリのインストールまでできれば、Pythonで開発を始める準備は完了です。
はじめの一歩として、ぜひ挑戦していただければと思います。

# 参考文献
https://www.useful-python.com/env-python-vscode-windows/
