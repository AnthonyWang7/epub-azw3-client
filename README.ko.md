# 로컬 EPUB to AZW3 클라이언트

Calibre를 사용해 EPUB 파일을 AZW3 / Kindle KF8 형식으로 변환하는 로컬 시각화 도구입니다. 일괄 드래그 앤 드롭, 변환 진행률, 변환 기록, 개별 다운로드, ZIP 일괄 다운로드를 지원합니다.

## 인터페이스 미리보기

![EPUB to AZW3 인터페이스](docs/interface-preview.png)

## 기능

- EPUB를 AZW3로 로컬 변환
- 드래그 앤 드롭 및 파일 선택 일괄 업로드
- 이름, 업로드 시간, 파일 유형, 상태가 있는 대기열
- 전체 진행률 표시
- Kindle 스타일 변환 기록
- 개별 다운로드 또는 ZIP 다운로드
- 출력 폴더 설정
- macOS 및 Windows 지원

## 요구 사항

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

## 실행

macOS: `start.command`를 더블 클릭합니다.

Windows: `start.bat`을 더블 클릭합니다.

## 사용 방법

1. EPUB 파일을 왼쪽 패널에 드롭하거나 클릭해서 선택합니다.
2. 변환할 파일을 선택합니다.
3. 선택 사항: 출력 폴더를 지정합니다.
4. `선택 항목 변환`을 클릭합니다.
5. 변환 기록에서 AZW3 파일을 다운로드합니다.

파일은 로컬 컴퓨터에만 남습니다. DRM 보호 EPUB는 기본 Calibre로 변환할 수 없습니다.
