# EPUB 转 AZW3 本地客户端

这是一个本地运行的 EPUB 转 AZW3 可视化工具。它通过 Calibre 的 `ebook-convert` 在你的电脑上完成转换，支持批量拖拽上传、转换进度查看、转换记录管理、单个下载和多文件打包下载，适合把 EPUB 电子书转换成 Kindle 更友好的 AZW3 / KF8 格式。

## 功能特点

- 支持批量拖拽 EPUB 文件
- 支持点击选择 EPUB 文件
- 左侧上传队列显示文件名、上传时间、文件类型和转换状态
- 支持全选、移除、转换选中
- 右侧显示整体转换进度和完成数量
- Kindle 风格转换记录面板
- 转换成功后可单独下载
- 多选记录时可打包下载 ZIP
- 可提前设置 AZW3 输出/下载目录
- 支持 macOS 和 Windows
- 所有文件都在本机处理，不会上传到云端

## 环境要求

- Python 3
- Calibre

工具会自动检测常见的 Calibre 安装路径：

- macOS：`/Applications/calibre.app/Contents/MacOS/ebook-convert`
- Windows：`C:\Program Files\Calibre2\ebook-convert.exe`

## 安装 Calibre

macOS 可以使用 Homebrew：

```zsh
brew install --cask calibre
```

Windows 可以使用 winget：

```bat
winget install --id calibre.calibre -e
```

也可以从 Calibre 官网下载安装：

https://calibre-ebook.com/download

## 启动方式

macOS：

```zsh
./start.command
```

也可以直接双击 `start.command`。

Windows：

```bat
start.bat
```

也可以直接双击 `start.bat`。

启动后工具会自动打开浏览器页面。

默认地址：

```text
http://127.0.0.1:8765
```

如果端口被占用，工具会自动尝试下一个可用端口。

## 使用方法

1. 将 EPUB 文件拖入左侧上传区域，或点击上传区域选择文件。
2. 在左侧队列中选择要转换的文件。
3. 可选：在右侧设置输出/下载路径。
4. 点击「转换选中」。
5. 转换完成后，在右侧 Kindle 风格记录面板中下载 AZW3 文件。

如果选中多条转换记录并点击下载，工具会自动打包成一个 ZIP 文件下载。

## 示例文件

仓库的 `examples/` 目录包含两个示例 EPUB 文件：

- `当年明月：明朝那些事儿 (全7册).epub`
- `尤瓦尔·赫拉利：人类简史——从动物到上帝.epub`

可以直接拖入工具测试转换。

## 关于 AZW3 格式显示

macOS Finder 或命令行工具有时会把 AZW3 显示为 `E-book` 或 `Mobipocket E-book version 8`，这是正常现象。AZW3 本质上属于 Kindle KF8 格式，底层识别经常会显示为 Mobipocket/E-book。

## 注意事项

- 默认 Calibre 无法转换带 DRM 的 EPUB。
- 请只转换你有权处理的电子书文件。
- 如果你把 Calibre 一起封装到工具中分发，请保留 Calibre 自带许可证文件，并遵守 Calibre 的 GPL 许可证要求。
