# gs-compress

Batch-compress PDF files using Ghostscript, right from PowerShell.

## Overview

`gs-compress.ps1` scans the current directory for all `*.pdf` files and runs each one through Ghostscript's `pdfwrite` device, producing smaller, compressed copies in a separate output directory. The original files are never touched.

The script is wrapped in the advanced function `Compress-Pdf` with `SupportsShouldProcess`, enabling `-WhatIf` and `-Confirm` for safe previewing.

## Prerequisites

- **PowerShell 5.1+** (or PowerShell Core)
- **Ghostscript** installed and available on your system
  - Download: [ghostscript.com](https://www.ghostscript.com/)
  - The default executable name is `gswin64c` (Windows 64-bit). Adjust via the `-GsExe` parameter if needed.

## Usage

### Basic — compress everything with default settings

```powershell
.\gs-compress.ps1
```

Scans `.\*.pdf` and writes compressed versions to `.\compressed\`.

### Choose a compression preset

```powershell
.\gs-compress.ps1 -PdfSettings /screen
```

| Preset       | Best for                              | Typical quality |
|--------------|---------------------------------------|-----------------|
| `/screen`    | Web preview, email attachments        | Low (smallest)  |
| `/ebook`     | **Default** — e-readers, tablets      | Medium          |
| `/printer`   | Office printing                       | High            |
| `/prepress`  | Professional print / publishing       | Very high       |
| `/default`   | Ghostscript's built-in default        | Varies          |

### Custom output directory

```powershell
.\gs-compress.ps1 -OutputDir small
```

Writes compressed PDFs into `.\small\` instead of the default `.\compressed\`.

### Custom Ghostscript path

```powershell
.\gs-compress.ps1 -GsExe "C:\Program Files\gs\gs10.07.1\bin\gswin64c.exe"
```

Useful when Ghostscript isn't on your `PATH` or you need a specific version.

### Preview without compressing

```powershell
.\gs-compress.ps1 -WhatIf
```

Shows what would happen without actually compressing any files.

### Prompt before each file

```powershell
.\gs-compress.ps1 -Confirm
```

Prompts for confirmation before compressing each file.

### All together

```powershell
.\gs-compress.ps1 -PdfSettings /printer -OutputDir print_ready -Verbose
```

## Parameters

| Parameter      | Type   | Default      | Description |
|----------------|--------|--------------|-------------|
| `-OutputDir`   | string | `compressed` | Subdirectory where compressed PDFs are written |
| `-PdfSettings` | string | `/ebook`     | Ghostscript quality preset (validated) |
| `-GsExe`       | string | `gswin64c`   | Ghostscript executable name or full path |
| `-WhatIf`      | switch |              | Preview mode — shows actions without executing |
| `-Confirm`     | switch |              | Prompts for confirmation before each file |
| `-Verbose`     | switch |              | Shows Ghostscript path and directory creation details |

## How it works

1. **Ghostscript lookup** — locates the Ghostscript binary via `Get-Command` and detects its version.
2. **PDF discovery** — collects all `*.pdf` files in the current directory.
3. **Directory prep** — creates the output folder (only if PDFs exist).
4. **Banner** — displays Ghostscript version, PDF settings preset, and output directory.
5. **Log file** — writes a timestamped `log-*.txt` header to the output directory.
6. **Processing loop** — each file is sent through Ghostscript with:
   - `-sDEVICE=pdfwrite`
   - `-dCompatibilityLevel=1.7`
   - `-dPDFSETTINGS=<preset>`
   - `-dNOPAUSE -dBATCH`
   - All Ghostscript stdout output is captured to a temp file (keeps terminal clean)
7. **Per-file reporting** — single-line output with filename, size before/after, and reduction percentage.
8. **Log appending** — raw Ghostscript output for each file is appended to the log file.
9. **Summary** — prints total file count, sizes, and overall reduction percentage.

## Error handling

- **No PDFs found** → prints a message and exits cleanly.
- **Ghostscript not found** → throws a terminating error immediately.
- **Ghostscript fails on a file** → throws a terminating error with the filename, exit code, and the captured Ghostscript output.

## Example output

```
----------------------------------------
  Ghostscript PDF Compressor v2.0
----------------------------------------
  Ghostscript : 10.07.1 (gswin64c)
  PDF Settings: /ebook
  Output Dir  : D:\projects\compressed
----------------------------------------

  [1/3] "annual_report.pdf"  |  21.16 MB -> 1.29 MB  (93.9%)
  [2/3] "user_guide.pdf"  |  4.52 MB -> 0.31 MB  (93.1%)
  [3/3] "brochure.pdf"  |  2.10 MB -> 0.15 MB  (92.9%)

  Total: 3 file(s)  |  27.78 MB -> 1.75 MB  (93.7%)
----------------------------------------
```

## Log file

Each run creates a timestamped log file in the output directory:

```
compressed/log-2026-05-22T165252+0630.txt
```

The log file contains:
- A header with run timestamp, Ghostscript version, settings, and output path
- Raw Ghostscript output for each processed file (copyright banners, font substitution warnings, PDF repair messages, etc.)

This keeps the terminal clean while preserving full diagnostic output for troubleshooting.

## Notes

- **Original files are never modified** — only copies are written to the output directory.
- Output filenames are identical to the inputs — re-running will overwrite previous results.
- No pipeline output is produced; the script only writes to disk.
- Use `-Verbose` to see Ghostscript path resolution and directory creation messages.
- Special characters in filenames (`#`, `%`, `&`, `[]`, `$`, `!`, `+`, etc.) are handled safely via `-LiteralPath` throughout.
