# gs-compress

Batch-compress PDF files using Ghostscript, right from PowerShell.

## Overview

`gs-compress.ps1` scans the current directory for all `*.pdf` files and runs each one through Ghostscript's `pdfwrite` device, producing smaller, compressed copies in a separate output directory. The original files are never touched.

## Prerequisites

- **PowerShell 5.0+** (or PowerShell Core)
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
.\gs-compress.ps1 -GsExe "C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe"
```

Useful when Ghostscript isn't on your `PATH` or you need a specific version.

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

## How it works

1. **Ghostscript lookup** — confirms Ghostscript is reachable via `Get-Command`.
2. **PDF discovery** — collects all `*.pdf` files in the current directory.
3. **Directory prep** — creates the output folder (only if PDFs exist).
4. **Processing loop** — each file is sent through Ghostscript with:
   - `-sDEVICE=pdfwrite`
   - `-dCompatibilityLevel=1.7`
   - `-dPDFSETTINGS=<preset>`
   - `-dNOPAUSE -dBATCH`
5. **Progress & logging** — a progress bar with `Write-Progress`, timestamped per-file logging, and immediate termination on Ghostscript failure.
6. **Summary** — prints where the compressed files landed.

## Error handling

- **No PDFs found** → prints a message and exits cleanly.
- **Ghostscript not found** → throws a terminating error immediately.
- **Ghostscript fails on a file** → throws a terminating error with the filename and exit code.

## Example output

```
Processing 3 PDF file(s)...
[2026-05-22 11:54:00] Compressing: annual_report.pdf
[2026-05-22 11:54:03] Compressing: user_guide.pdf
[2026-05-22 11:54:05] Compressing: brochure.pdf
Done! Compressed files are in 'compressed'.
```

## Notes

- **Original files are never modified** — only copies are written to the output directory.
- Output filenames are identical to the inputs — re-running will overwrite previous results.
- No pipeline output is produced; the script only writes to disk.
- Use `-Verbose` to see Ghostscript path resolution and directory creation messages.
