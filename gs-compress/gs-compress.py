#!/usr/bin/env python3
"""
Compresses PDF files in the current directory using Ghostscript.

This is a Python port of gs-compress.ps1.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compresses PDF files in the current directory using Ghostscript."
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="compressed",
        help='Destination directory for compressed PDFs. Defaults to "compressed".',
    )
    parser.add_argument(
        "--pdf-settings", "-s",
        default="/ebook",
        choices=["/screen", "/ebook", "/printer", "/prepress", "/default"],
        help="Ghostscript PDFSETTINGS preset. Defaults to /ebook.",
    )
    parser.add_argument(
        "--gs-exe", "-g",
        default="gswin64c",
        help='Path to the Ghostscript executable. Defaults to "gswin64c".',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without compressing any files.",
    )
    return parser.parse_args()


def locate_gs(gs_exe):
    """Find the Ghostscript executable on PATH or at an absolute/relative path."""
    gs_path = shutil.which(gs_exe)
    if gs_path:
        return Path(gs_path)

    p = Path(gs_exe)
    if p.is_file():
        return p.resolve()

    # Friendly fallback for Linux/macOS when the Windows default is used
    if gs_exe == "gswin64c":
        gs_path = shutil.which("gs")
        if gs_path:
            return Path(gs_path)

    raise FileNotFoundError(f"Ghostscript executable not found: {gs_exe}")


def get_gs_version(gs_path):
    """Run Ghostscript with --version and return the first line of output."""
    result = subprocess.run(
        [str(gs_path), "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()[0]


def main():
    args = parse_args()

    # ── Locate Ghostscript ────────────────────────────────────────────────
    try:
        gs_path = locate_gs(args.gs_exe)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        gs_version = get_gs_version(gs_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Error detecting Ghostscript version: {exc}", file=sys.stderr)
        sys.exit(1)

    gs_exe_name = gs_path.stem

    # ── Collect PDFs ──────────────────────────────────────────────────────
    pdf_files = sorted([f for f in Path(".").glob("*.pdf") if f.is_file()])
    if not pdf_files:
        print("No PDF files found in the current directory.")
        sys.exit(0)

    # ── Ensure output directory ───────────────────────────────────────────
    output_dir = Path(args.output_dir).resolve()
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # ── Counters ───────────────────────────────────────────────────────────
    total = len(pdf_files)
    total_original_size = 0
    total_compressed_size = 0

    # ── Banner ────────────────────────────────────────────────────────────
    banner_sep = "-" * 40
    print()
    print(banner_sep)
    print("  Ghostscript PDF Compressor v2.0")
    print(banner_sep)
    print(f"  Ghostscript : {gs_version} ({gs_exe_name})")
    print(f"  PDF Settings: {args.pdf_settings}")
    print(f"  Output Dir  : {output_dir}")
    print(banner_sep)
    print()

    # ── Log file ──────────────────────────────────────────────────────────
    now = datetime.now().astimezone()
    timestamp = now.isoformat(timespec="seconds")
    safe_timestamp = timestamp.replace(":", "")
    log_file = output_dir / f"log-{safe_timestamp}.txt"
    log_header_sep = "=" * 60

    log_header_lines = [
        log_header_sep,
        "  Ghostscript PDF Compressor v2.0 - Log",
        log_header_sep,
        f"  Date        : {timestamp}",
        f"  Ghostscript : {gs_version} ({gs_exe_name})",
        f"  PDF Settings: {args.pdf_settings}",
        f"  Output Dir  : {output_dir}",
        log_header_sep,
        "",
    ]

    if not args.dry_run:
        log_file.write_text("\n".join(log_header_lines) + "\n", encoding="utf-8")

    # ── Processing loop ──────────────────────────────────────────────────
    with tempfile.TemporaryDirectory(prefix="gs-compress-", ignore_cleanup_errors=True) as _td:
        temp_dir = Path(_td)

        for i, pdf in enumerate(pdf_files, start=1):
            if args.dry_run:
                print(f"[{i}/{total}] {pdf.name} -> {output_dir / pdf.name}")
                continue

            print(f"[{i}/{total}] {pdf.name}... ", end="", flush=True)

            output_file = output_dir / pdf.name

            # Sanitize filename for Ghostscript (handles %, &, spaces, [], etc.)
            safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", pdf.stem) + ".pdf"
            temp_input = temp_dir / safe_name
            temp_output = temp_dir / f"compressed_{safe_name}"

            shutil.copy2(pdf, temp_input)

            gs_args = [
                str(gs_path),
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.7",
                f"-dPDFSETTINGS={args.pdf_settings}",
                "-dNOPAUSE",
                "-dBATCH",
                f"-sOutputFile={temp_output}",
                str(temp_input),
            ]

            # Capture Ghostscript's noisy stdout (and stderr) to a temp file
            gs_output_file = temp_dir / f"gs_output_{i}.txt"
            try:
                result = subprocess.run(
                    gs_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
                gs_output_file.write_text(result.stdout, encoding="utf-8")
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        result.returncode, gs_args, output=result.stdout
                    )
            except Exception as exc:  # noqa: BLE001
                print(
                    f"Ghostscript failed on '{pdf.name}' (exit code: {result.returncode}).\n{result.stdout}",
                    file=sys.stderr,
                )
                sys.exit(1)

            # Append raw GS output to log file
            gs_raw = gs_output_file.read_text(encoding="utf-8").strip()
            log_entry_sep = "-" * 60
            log_entry_lines = [
                log_entry_sep,
                f"  [{i}/{total}] {pdf.name}",
                log_entry_sep,
                gs_raw,
                "",
            ]
            with log_file.open("a", encoding="utf-8") as lf:
                lf.write("\n".join(log_entry_lines) + "\n")

            # Copy result back with original filename
            shutil.copy2(temp_output, output_file)

            # ── Compression ratio reporting ──────────────────────────────
            original_size = pdf.stat().st_size
            compressed_size = output_file.stat().st_size
            total_original_size += original_size
            total_compressed_size += compressed_size

            if original_size > 0:
                ratio = round((1 - compressed_size / original_size) * 100, 1)
            else:
                ratio = 0

            orig_mb = round(original_size / (1024 * 1024), 2)
            comp_mb = round(compressed_size / (1024 * 1024), 2)
            print(f"{orig_mb} MB -> {comp_mb} MB ({ratio}%)")

    # ── Summary ───────────────────────────────────────────────────────────
    print()
    if total_original_size > 0:
        total_ratio = round((1 - total_compressed_size / total_original_size) * 100, 1)
        total_orig_mb = round(total_original_size / (1024 * 1024), 2)
        total_comp_mb = round(total_compressed_size / (1024 * 1024), 2)
        print(
            f"  Total: {total} file(s)  |  {total_orig_mb} MB -> {total_comp_mb} MB  ({total_ratio}%)"
        )
    else:
        print(f"  Compressed files are in '{output_dir}'.")
    print(banner_sep)
    print()


if __name__ == "__main__":
    main()
