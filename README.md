# Add-Grid-On-Image

このプロジェクトは、Customtkinterなどを使用した画像にグリッドを追加するGUIアプリケーションです。

画像の上にカスタマイズ可能なグリッドを描画し、保存することができます。

これにより、デジタルイラストで模写する際ガイド線が必要な場合などに便利です。

## スクリーンショット

![Image](https://github.com/user-attachments/assets/c3c1367d-9816-4a6e-9915-acbed0075d8a)

## 機能

- 画像にグリッドを追加
- グリッドの線の色、太さ、分割数をカスタマイズ
- 画像のリサイズ、切り取り、同一サイズの透過画像を作成(必要に応じて)
- グリッドが追加された画像を保存

## インストール

[最新リリース](https://github.com/raccooon11/Add-Grid-On-Image/releases/latest)からAdd-Grid-On-Image.zipファイルをダウンロードします。

ダウンロードしたzipファイルを任意のフォルダに解凍し、中にある`main.exe`を開きます。

'WindowsによってPCが保護されました'と警告が出た場合は'詳細情報'をクリックして実行ボタンを押してください。

### 注意

このexeはnuitkaを使用してパッケージ化されていますが、重いライブラリのNumpyやOpenCVを使用している都合上、どうしてもファイルサイズの軽量化、高速化が出来なかったため初回起動時に数秒かかる場合があります。(2回目以降の起動は早いです)

自分の環境でpythonプログラムを直接実行する場合は下のセクションを参考にしてください。

## 前提ライブラリ

このプロジェクトを実行するために必要なPythonライブラリはrequirements.txtに記載されています。

インストールは以下のコマンドで行えます：

### ライブラリのインストール

1. まず、リポジトリをクローンまたはダウンロードします：

    ```bash
    git clone https://github.com/raccooon11/Add-Grid-On-Image.git
    cd Add-Grid-On-Image
    ```

2. 次に、`requirements.txt`に記載された必要なライブラリをインストールします：

    ```bash
    pip install -r requirements.txt
    ```

これにより、プロジェクトに必要な依存関係がインストールされます。

## 使用方法

`main.pyw`を実行し、表示されたウィンドウで画像を読み込み、グリッドのカスタマイズなどを行います。

カスタマイズが完了したら、右下の保存ボタンを押してファイルに保存します。

保存形式は`指定フォルダ/年-月-日/年-月-日_時-分_幅x高さ_xxx.png`となっています。

このプログラムは保存時にその時点でのグリッドカスタマイズ設定を`config.json`ファイルに保存しますが、デフォルトに戻したい場合は`config.json`ファイルを削除して再度起動しなおしてください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳しくは `LICENSE` ファイルをご覧ください。

## 注意事項

- サイズが極端に大きい画像を読み込みリサイズなどの操作をすると、処理が間に合わず不具合を起こす可能性があります。
