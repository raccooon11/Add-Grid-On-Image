# Add-Grid-On-Image

このプロジェクトは、Customtkinterなどを使用した画像にグリッドを追加するGUIアプリケーションです。
画像の上にカスタマイズ可能なグリッドを描画し、保存することができます。
これにより、デジタルイラストで模写する際ガイド線が必要な場合などに便利です。

## スクリーンショット
![Image](https://cdn.discordapp.com/attachments/1149904320221941763/1359487066710478940/image.png?ex=67f7a87e&is=67f656fe&hm=5fe9b16703c5d01ee7843a21e1a4330a0089c6db0553fe1cb942a42c43bb3aec&)

## 機能

- 画像にグリッドを追加
- グリッドの線の色、太さ、分割数をカスタマイズ
- 画像のリサイズ、切り取り、同一サイズの透過画像を作成(必要に応じて)
- グリッドが追加された画像を保存

## 必要なライブラリ

このプロジェクトを実行するために必要なPythonライブラリはrequirements.txtに記載されています

インストールは以下のコマンドで行えます：

### インストール方法

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

### 3. 使用方法

`main.pyw`を実行し、表示されたウィンドウで画像を読み込み、グリッドのカスタマイズなどを行います。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳しくは `LICENSE` ファイルをご覧ください。

## 注意事項

- サイズがかなり巨大な画像を読み込みリサイズなどの操作をすると、処理が間に合わずに不具合を起こす場合があります。
