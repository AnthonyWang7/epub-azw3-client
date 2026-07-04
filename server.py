#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import webbrowser
import zipfile
from email import policy
from email.parser import BytesParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse


APP_DIR = Path(__file__).resolve().parent
UPLOAD_ROOT = APP_DIR / "work/uploads"
HOST = "127.0.0.1"
PORT = 8765

jobs = {}
jobs_lock = threading.Lock()


def calibre_candidates():
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    names = [
        str(APP_DIR / "vendor/calibre.app/Contents/MacOS/ebook-convert"),
        str(APP_DIR / "vendor/Calibre2/ebook-convert.exe"),
        str(APP_DIR / "vendor/calibre/ebook-convert.exe"),
        shutil.which("ebook-convert"),
        shutil.which("ebook-convert.exe"),
        "/Applications/calibre.app/Contents/MacOS/ebook-convert",
        str(Path.home() / "Applications/calibre.app/Contents/MacOS/ebook-convert"),
        str(Path(program_files) / "Calibre2/ebook-convert.exe"),
        str(Path(program_files_x86) / "Calibre2/ebook-convert.exe"),
    ]
    return [Path(item) for item in names if item]


def find_ebook_convert():
    for candidate in calibre_candidates():
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def find_system_calibre_app():
    for candidate in [
        Path("/Applications/calibre.app"),
        Path.home() / "Applications/calibre.app",
    ]:
        converter = candidate / "Contents/MacOS/ebook-convert"
        if converter.exists() and os.access(converter, os.X_OK):
            return candidate
    return None


def run_osascript(script):
    proc = subprocess.run(
        ["osascript", "-e", script],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        message = proc.stderr.strip() or "Dialog cancelled"
        raise RuntimeError(message)
    return proc.stdout.strip()


def choose_epub_files():
    script = (
        'set chosenFiles to choose file with prompt "选择要转换的 EPUB 文件" with multiple selections allowed\n'
        'set outputText to ""\n'
        'repeat with oneFile in chosenFiles\n'
        'set outputText to outputText & POSIX path of oneFile & linefeed\n'
        'end repeat\n'
        'return outputText'
    )
    output = run_osascript(script)
    return [line for line in output.splitlines() if line.strip().lower().endswith(".epub")]


def choose_output_dir():
    if sys.platform == "darwin":
        script = (
            'set chosenFolder to choose folder with prompt "选择 AZW3 输出文件夹"\n'
            "return POSIX path of chosenFolder"
        )
        return run_osascript(script)

    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        chosen = filedialog.askdirectory(title="选择 AZW3 输出文件夹")
        root.destroy()
        if not chosen:
            raise RuntimeError("Dialog cancelled")
        return chosen
    except Exception as exc:
        raise RuntimeError(f"无法打开文件夹选择器：{exc}")


def open_terminal_install():
    if sys.platform.startswith("win"):
        command = "winget install --id calibre.calibre -e"
        subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", command], shell=False)
        return

    script_path = Path(tempfile.gettempdir()) / "install-calibre-for-epub-azw3.command"
    script_path.write_text(
        """#!/bin/zsh
set -e

if ! command -v brew >/dev/null 2>&1; then
  echo "未找到 Homebrew。请先安装 Homebrew：https://brew.sh/"
  echo ""
  read -n 1 -s -r "?按任意键关闭窗口"
  exit 1
fi

brew install --cask calibre
echo ""
echo "Calibre 安装流程结束，可以回到转换客户端刷新状态。"
read -n 1 -s -r "?按任意键关闭窗口"
""",
        encoding="utf-8",
    )
    script_path.chmod(0o755)
    subprocess.run(["open", "-a", "Terminal", str(script_path)], check=False)


def bundle_system_calibre():
    source = find_system_calibre_app()
    if not source:
        raise RuntimeError("未找到系统安装的 Calibre。请先安装 Calibre，再执行封装。")

    vendor_dir = APP_DIR / "vendor"
    target = vendor_dir / "calibre.app"
    tmp_target = vendor_dir / "calibre.app.copying"
    vendor_dir.mkdir(parents=True, exist_ok=True)

    if tmp_target.exists():
        shutil.rmtree(tmp_target)
    shutil.copytree(source, tmp_target, symlinks=True)
    if target.exists():
        shutil.rmtree(target)
    tmp_target.rename(target)
    return str(target)


def make_output_path(source, output_dir):
    source_path = Path(source)
    target_dir = Path(output_dir).expanduser() if output_dir else source_path.parent
    return str(target_dir / f"{source_path.stem}.azw3")


def file_label(path):
    return Path(path).name


def update_progress_from_line(job, line):
    marker = line.split("%", 1)[0].strip()
    if marker.isdigit():
        job["itemProgress"] = max(0, min(100, int(marker)))


def new_job(job_id, files, output_dir):
    return {
        "id": job_id,
        "status": "queued",
        "files": files,
        "outputDir": output_dir,
        "current": None,
        "currentLabel": None,
        "currentIndex": 0,
        "progress": 0,
        "itemProgress": 0,
        "done": [],
        "outputs": [],
        "failed": [],
        "logs": ["任务已创建，等待转换器启动。"],
        "createdAt": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def start_conversion(files, output_dir):
    job_id = uuid.uuid4().hex[:12]
    with jobs_lock:
        jobs[job_id] = new_job(job_id, files, output_dir)
    thread = threading.Thread(target=convert_worker, args=(job_id, files, output_dir), daemon=True)
    thread.start()
    return job_id


def parse_uploaded_epubs(content_type, body):
    if "multipart/form-data" not in content_type:
        raise RuntimeError("请上传 EPUB 文件。")

    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
    )
    job_id = uuid.uuid4().hex[:12]
    input_dir = UPLOAD_ROOT / job_id / "input"
    output_dir = UPLOAD_ROOT / job_id / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []
    chosen_output_dir = ""
    for part in message.iter_parts():
        filename = part.get_filename()
        if part.get_param("name", header="content-disposition") == "outputDir" and not filename:
            chosen_output_dir = (part.get_content() or "").strip()
            continue
        if not filename or not filename.lower().endswith(".epub"):
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        safe_name = Path(filename).name
        target = input_dir / safe_name
        if target.exists():
            target = input_dir / f"{target.stem}-{uuid.uuid4().hex[:6]}{target.suffix}"
        target.write_bytes(payload)
        files.append(str(target))

    if not files:
        raise RuntimeError("没有收到可转换的 EPUB 文件。")
    return job_id, files, chosen_output_dir or str(output_dir)


def make_download_zip(paths):
    temp_dir = Path(tempfile.gettempdir()) / "epub-azw3-client-downloads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    zip_path = temp_dir / f"azw3-selected-{uuid.uuid4().hex[:8]}.zip"
    used_names = set()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for raw_path in paths:
            source = Path(raw_path).expanduser()
            if not source.exists() or source.suffix.lower() != ".azw3":
                continue
            arcname = source.name
            if arcname in used_names:
                arcname = f"{source.stem}-{uuid.uuid4().hex[:6]}{source.suffix}"
            used_names.add(arcname)
            archive.write(source, arcname)

    if not used_names:
        zip_path.unlink(missing_ok=True)
        raise RuntimeError("没有可下载的 AZW3 文件。")
    return zip_path


def convert_worker(job_id, files, output_dir):
    converter = find_ebook_convert()
    with jobs_lock:
        job = jobs[job_id]
        job["status"] = "running"
        job["startedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")

    if not converter:
        with jobs_lock:
            job["status"] = "failed"
            job["logs"].append("未找到 ebook-convert。请先安装 Calibre，或点击界面里的安装按钮。")
        return

    for index, source in enumerate(files, start=1):
        output = make_output_path(source, output_dir)
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with jobs_lock:
            job["current"] = source
            job["currentLabel"] = file_label(source)
            job["currentIndex"] = index
            job["itemProgress"] = 0
            job["progress"] = int(((index - 1) / len(files)) * 100)
            job["logs"].append(f"[{index}/{len(files)}] 开始转换：{source}")
            job["logs"].append(f"输出到：{output}")

        proc = subprocess.Popen(
            [converter, source, output],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            clean = line.rstrip()
            if clean:
                with jobs_lock:
                    update_progress_from_line(job, clean)
                    job["progress"] = int((((index - 1) + (job["itemProgress"] / 100)) / len(files)) * 100)
                    job["logs"].append(clean)

        return_code = proc.wait()
        with jobs_lock:
            if return_code == 0 and Path(output).exists():
                job["done"].append(output)
                job["outputs"].append({"source": source, "path": output, "name": Path(output).name})
                job["logs"].append(f"完成：{output}")
            else:
                job["failed"].append(source)
                job["logs"].append(f"失败：{source}，退出码 {return_code}")

    with jobs_lock:
        job["status"] = "failed" if job["failed"] else "done"
        job["progress"] = 100
        job["itemProgress"] = 100
        job["finishedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
        job["current"] = None
        job["currentLabel"] = None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def log_message(self, fmt, *args):
        return

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            converter = find_ebook_convert()
            self.send_json(
                {
                    "ok": True,
                    "converter": converter,
                    "calibreInstalled": bool(converter),
                    "python": sys.executable,
                }
            )
            return
        if parsed.path == "/api/jobs":
            with jobs_lock:
                snapshot = list(jobs.values())[-20:]
            self.send_json({"jobs": snapshot})
            return
        if parsed.path == "/api/download":
            params = parse_qs(parsed.query)
            target = Path(params.get("path", [""])[0]).expanduser()
            if not target.exists() or target.suffix.lower() != ".azw3":
                self.send_json({"error": "文件不存在。"}, 404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.amazon.ebook")
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(target.name)}")
            self.send_header("Content-Length", str(target.stat().st_size))
            self.end_headers()
            with target.open("rb") as handle:
                shutil.copyfileobj(handle, self.wfile)
            return
        if parsed.path == "/api/download-zip":
            params = parse_qs(parsed.query)
            zip_path = make_download_zip(params.get("path", []))
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(zip_path.name)}")
            self.send_header("Content-Length", str(zip_path.stat().st_size))
            self.end_headers()
            with zip_path.open("rb") as handle:
                shutil.copyfileobj(handle, self.wfile)
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/select-files":
                self.send_json({"files": choose_epub_files()})
                return
            if parsed.path == "/api/select-output-dir":
                self.send_json({"outputDir": choose_output_dir()})
                return
            if parsed.path == "/api/install-calibre":
                open_terminal_install()
                self.send_json({"ok": True})
                return
            if parsed.path == "/api/bundle-calibre":
                target = bundle_system_calibre()
                self.send_json({"ok": True, "path": target})
                return
            if parsed.path == "/api/open-path":
                data = self.read_json()
                target = data.get("path")
                if target:
                    target_path = Path(target).expanduser()
                    open_target = target_path.parent if target_path.is_file() else target_path
                    if sys.platform == "darwin":
                        subprocess.run(["open", str(open_target)], check=False)
                    elif sys.platform.startswith("win"):
                        os.startfile(str(open_target))
                    else:
                        subprocess.run(["xdg-open", str(open_target)], check=False)
                self.send_json({"ok": True})
                return
            if parsed.path == "/api/convert":
                data = self.read_json()
                files = [item for item in data.get("files", []) if item.lower().endswith(".epub") and Path(item).exists()]
                output_dir = data.get("outputDir") or ""
                if not files:
                    self.send_json({"error": "请先选择存在的 EPUB 文件。"}, 400)
                    return
                job_id = start_conversion(files, output_dir)
                self.send_json({"jobId": job_id})
                return
            if parsed.path == "/api/upload-convert":
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                upload_job_id, files, output_dir = parse_uploaded_epubs(self.headers.get("Content-Type", ""), body)
                with jobs_lock:
                    jobs[upload_job_id] = new_job(upload_job_id, files, output_dir)
                    jobs[upload_job_id]["logs"].append("已接收上传文件。")
                thread = threading.Thread(target=convert_worker, args=(upload_job_id, files, output_dir), daemon=True)
                thread.start()
                self.send_json({"jobId": upload_job_id})
                return
            self.send_json({"error": "Not found"}, 404)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)


def main():
    os.chdir(APP_DIR)
    server = None
    port = PORT
    for candidate in range(PORT, PORT + 20):
        try:
            server = ThreadingHTTPServer((HOST, candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    if server is None:
        raise RuntimeError("没有找到可用端口，请关闭其他已启动的转换客户端后重试。")

    url = f"http://{HOST}:{port}"
    print(f"EPUB 转 AZW3 客户端已启动：{url}")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出。")


if __name__ == "__main__":
    main()
