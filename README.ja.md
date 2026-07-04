# ローカル EPUB から AZW3 クライアント

Calibre を使って EPUB ファイルを AZW3 / Kindle KF8 に変換するローカルのビジュアルツールです。複数ファイルのドラッグ＆ドロップ、変換進捗、変換履歴、個別ダウンロード、ZIP 一括ダウンロードに対応しています。

## インターフェースプレビュー

![EPUB から AZW3 の画面](docs/interface-preview.png)

## 機能

- EPUB から AZW3 へのローカル変換
- ドラッグ＆ドロップまたはファイル選択による一括追加
- ファイル名、追加時刻、種類、状態を表示するキュー
- 全体の進捗表示
- Kindle 風の変換履歴
- 個別ダウンロードまたは ZIP ダウンロード
- 出力フォルダの指定
- macOS と Windows に対応

## 必要環境

- Python 3
- Calibre

macOS:

```zsh
brew install --cask calibre
```

Windows:

```bat
winget install --id calibre.calibre -e
```

## 起動

macOS: `start.command` をダブルクリックします。

Windows: `start.bat` をダブルクリックします。

## 使い方

1. EPUB ファイルを左側パネルにドロップするか、クリックして選択します。
2. 変換するファイルを選択します。
3. 任意で出力フォルダを設定します。
4. `選択を変換` をクリックします。
5. 変換履歴から AZW3 ファイルをダウンロードします。

ファイルはローカル環境に残ります。DRM 付き EPUB は標準の Calibre では変換できません。
