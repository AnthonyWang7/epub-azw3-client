# EPUB to AZW3 Client

Read this in:
[English](README.md) |
[中文](README.zh-CN.md) |
[Français](README.fr.md) |
[Deutsch](README.de.md) |
[Español](README.es.md) |
[Italiano](README.it.md) |
[العربية](README.ar.md) |
[한국어](README.ko.md) |
[日本語](README.ja.md)

A local, browser-based EPUB to AZW3 converter for macOS and Windows.

The app provides a simple Kindle-inspired interface for batch uploading EPUB files, converting them with Calibre's `ebook-convert`, tracking conversion status, and downloading individual AZW3 files or a selected ZIP bundle.

## Interface Preview

![EPUB to AZW3 Client interface](docs/interface-preview.png)

## Features

- Batch upload by drag-and-drop or file picker
- Left-side upload queue with upload time, file type, status dots, select all, and remove
- Right-side overall conversion progress
- Kindle-style conversion history panel
- Single-file download and multi-file ZIP download
- Custom output/download folder selection
- macOS and Windows launch scripts
- Uses local Calibre only; files stay on your machine

## Requirements

- Python 3
- Calibre

The app auto-detects Calibre in common locations:

- macOS: `/Applications/calibre.app/Contents/MacOS/ebook-convert`
- Windows: `C:\Program Files\Calibre2\ebook-convert.exe`
- Bundled paths:
  - `vendor/calibre.app/Contents/MacOS/ebook-convert`
  - `vendor/Calibre2/ebook-convert.exe`

## Install Calibre

macOS with Homebrew:

```zsh
brew install --cask calibre
```

Windows with winget:

```bat
winget install --id calibre.calibre -e
```

You can also download Calibre from the official website:

https://calibre-ebook.com/download

## Run

macOS:

```zsh
./start.command
```

Or double-click `start.command`.

Windows:

```bat
start.bat
```

Or double-click `start.bat`.

The app starts a local server and opens the browser automatically.

Default local URL:

```text
http://127.0.0.1:8765
```

If the port is already in use, the app automatically tries the next available port.

## Usage

1. Drag EPUB files into the left upload panel, or click the panel to choose files.
2. Select the files you want to convert.
3. Optional: set an output/download folder on the right.
4. Click `转换选中`.
5. Download files from the Kindle-style conversion history.

For multiple selected conversion records, the app downloads a ZIP containing all selected AZW3 files.

## Examples

This repository includes two sample EPUB files in `examples/`:

- `当年明月：明朝那些事儿 (全7册).epub`
- `尤瓦尔·赫拉利：人类简史——从动物到上帝.epub`

You can drag these into the app to test conversion.

## Notes

- AZW3 files may appear as `E-book` or `Mobipocket E-book version 8` in Finder or command-line file inspectors. That is normal for Kindle KF8/AZW3 files.
- DRM-protected EPUB files cannot be converted by default Calibre.
- Convert only files you have the right to process.

## Project Structure

```text
.
├── index.html
├── server.py
├── start.command
├── start.bat
└── examples/
```

## License

This project is provided as a local utility script. Calibre is a separate GPL-licensed project; if you bundle Calibre with this tool, keep Calibre's license files and comply with Calibre's license terms.
