# Lokaler EPUB-zu-AZW3-Client

Ein lokales visuelles Tool zum Konvertieren von EPUB-Dateien in AZW3 / Kindle KF8 mit Calibre. Es unterstützt Batch-Drag-and-drop, Fortschrittsanzeige, Verlauf, Einzeldownloads und ZIP-Downloads für mehrere Dateien.

## Oberfläche

![EPUB-zu-AZW3-Oberfläche](docs/interface-preview.png)

## Funktionen

- EPUB zu AZW3 lokal konvertieren
- Batch-Upload per Drag-and-drop oder Dateiauswahl
- Warteschlange mit Name, Uploadzeit, Dateityp und Status
- Gesamtfortschritt
- Kindle-ähnlicher Konvertierungsverlauf
- Einzelner Download oder ZIP-Download
- Ausgabeordner auswählbar
- macOS- und Windows-Unterstützung

## Voraussetzungen

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

## Starten

macOS: `start.command` doppelklicken.

Windows: `start.bat` doppelklicken.

## Nutzung

1. EPUB-Dateien links ablegen oder per Klick auswählen.
2. Dateien auswählen.
3. Optional den Ausgabeordner festlegen.
4. `Auswahl konvertieren` anklicken.
5. AZW3-Dateien im Verlauf herunterladen.

Alle Dateien bleiben lokal. DRM-geschützte EPUBs können mit Calibre standardmäßig nicht konvertiert werden.
