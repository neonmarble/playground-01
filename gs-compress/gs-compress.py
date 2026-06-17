#!/usr/bin/env python3
"""
Compresses PDF files in the current directory using Ghostscript.

This is a Python port of gs-compress.ps1.
"""

import argparse
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

BANNER_SEP: str = "-" * 40
LOG_HEADER_SEP: str = "=" * 60
LOG_ENTRY_SEP: str = "-" * 60
VERSION: str = "2.0"
DEFAULT_GS_EXE: str = "gswin64c"
DEFAULT_PDF_SETTINGS: str = "/ebook"
DEFAULT_OUTPUT_DIR: str = "compressed"
BYTES_PER_MB: float = 1024 * 1024


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compresses PDF files in the current directory using Ghostscript."
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f'Destination directory for compressed PDFs. Defaults to "{DEFAULT_OUTPUT_DIR}".',
    )
    parser.add_argument(
        "--pdf-settings", "-s",
        default=DEFAULT_PDF_SETTINGS,
        choices=["/screen", "/ebook", "/printer", "/prepress", "/default"],
        help=f"Ghostscript PDFSETTINGS preset. Defaults to {DEFAULT_PDF_SETTINGS}.",
    )
    parser.add_argument(
        "--gs-exe", "-g",
        default=DEFAULT_GS_EXE,
        help=f'Path to the Ghostscript executable. Defaults to "{DEFAULT_GS_EXE}".',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without compressing any files.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging.",
    )
    return parser.parse_args()


def locate_gs(gs_exe: str) -> Path:
    """Find the Ghostscript executable on PATH or at an absolute/relative path."""
    gs_path = shutil.which(gs_exe)
    if gs_path:
        return Path(gs_path)

    p = Path(gs_exe)
    if p.is_file():
        return p.resolve()

    # Friendly fallback for Linux/macOS when the Windows default is used
    if gs_exe == DEFAULT_GS_EXE:
        gs_path = shutil.which("gs")
        if gs_path:
            return Path(gs_path)

    raise FileNotFoundError(f"Ghostscript executable not found: {gs_exe}")


def get_gs_version(gs_path: Path) -> str:
    """Run Ghostscript with --version and return the first line of output."""
    result = subprocess.run(
        [str(gs_path), "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()[0]


def main() -> None:
    """Main entry point for the PDF compressor."""
    args = parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        stream=sys.stdout,
    )

    # ── Locate Ghostscript ────────────────────────────────────────────────
    try:
        gs_path = locate_gs(args.gs_exe)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    try:
        gs_version = get_gs_version(gs_path)
    except subprocess.CalledProcessError as exc:
        logger.error("Error detecting Ghostscript version: %s", exc)
        sys.exit(1)
    except FileNotFoundError as exc:
        logger.error("Ghostscript executable not found: %s", exc)
        sys.exit(1)

    gs_exe_name: str = gs_path.stem

    # ── Collect PDFs ──────────────────────────────────────────────────────
    pdf_files: list[Path] = sorted([f for f in Path(".").glob("*.pdf") if f.is_file()])
    if not pdf_files:
        logger.info("No PDF files found in the current directory.")
        sys.exit(0)

    # ── Ensure output directory ───────────────────────────────────────────
    output_dir: Path = Path(args.output_dir).resolve()
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # ── Counters ───────────────────────────────────────────────────────────
    total: int = len(pdf_files)
    total_original_size: int = 0
    total_compressed_size: int = 0

    # ── Banner ────────────────────────────────────────────────────────────
    logger.info("")
    logger.info(BANNER_SEP)
    logger.info("  Ghostscript PDF Compressor v%s", VERSION)
    logger.info(BANNER_SEP)
    logger.info("  Ghostscript : %s (%s)", gs_version, gs_exe_name)
    logger.info("  PDF Settings: %s", args.pdf_settings)
    logger.info("  Output Dir  : %s", output_dir)
    logger.info(BANNER_SEP)
    logger.info("")

    # ── Log file ──────────────────────────────────────────────────────────
    now: datetime = datetime.now().astimezone()
    timestamp: str = now.isoformat(timespec="seconds")
    safe_timestamp: str = timestamp.replace(":", "")
    log_file: Path = output_dir / f"log-{safe_timestamp}.txt"

    log_header_lines: list[str] = [
        LOG_HEADER_SEP,
        f"  Ghostscript PDF Compressor v{VERSION} - Log",
        LOG_HEADER_SEP,
        f"  Date        : {timestamp}",
        f"  Ghostscript : {gs_version} ({gs_exe_name})",
        f"  PDF Settings: {args.pdf_settings}",
        f"  Output Dir  : {output_dir}",
        LOG_HEADER_SEP,
        "",
    ]

    if not args.dry_run:
        log_file.write_text("\n".join(log_header_lines) + "\n", encoding="utf-8")

    # ── Processing loop ──────────────────────────────────────────────────
    with tempfile.TemporaryDirectory(prefix="gs-compress-", ignore_cleanup_errors=True) as _td:
        temp_dir: Path = Path(_td)

        for i, pdf in enumerate(pdf_files, start=1):
            if args.dry_run:
                logger.info("[%d/%d] %s -> %s", i, total, pdf.name, output_dir / pdf.name)
                continue

            output_file: Path = output_dir / pdf.name

            # Sanitize filename for Ghostscript (handles %, &, spaces, [], etc.)
            safe_name: str = re.sub(r"[^a-zA-Z0-9._-]", "_", pdf.stem) + ".pdf"
            temp_input: Path = temp_dir / safe_name
            temp_output: Path = temp_dir / f"compressed_{safe_name}"

            shutil.copy2(pdf, temp_input)

            # ── Ghostscript arguments ──────────────────────────────────
            # Order matters: -dPDFSETTINGS is applied first, then explicit
            # overrides follow so they take precedence.
            gs_args: list[str] = [
                str(gs_path),
                "-sDEVICE=pdfwrite",
                f"-dPDFSETTINGS={args.pdf_settings}",
                # ── Structure / fidelity preservation ─────────────────────
                "-dCompatibilityLevel=2.0",                 # support latest PDF features
                "-dPreserveOverprintSettings=true",                  # keep overprint info
                "-dPreserveOPIComments=true",                       # keep OPI metadata
                "-dUCRandBGInfo=/Preserve",                        # keep UCR/black generation
                "-dAutoRotatePages=/None",                         # don't auto-rotate
                "-dPreserveEPSInfo=true",                          # keep EPS metadata
                "-dPreserveMarkedContent=true",                    # keep marked content
                # ── Lossless optimizations ────────────────────────────────
                "-dDetectDuplicateImages=true",   # dedup identical images
                "-dFastWebView=true",              # linearize for web streaming
                "-dSubsetFonts=true",               # embed only used glyphs
                "-dCompressFonts=true",             # lossless font compression
                "-dRemoveUnusedResources=true",     # strip unused objects
                "-dPassThroughJPEGImages=true",     # avoid recompressing JPEGs
                # ── Standard flags ────────────────────────────────────────
                "-dNOPAUSE",
                "-dBATCH",
                f"-sOutputFile={temp_output}",
                str(temp_input),
            ]

            # Run Ghostscript and capture output
            gs_output_file: Path = temp_dir / f"gs_output_{i}.txt"
            try:
                result = subprocess.run(
                    gs_args,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                gs_output_file.write_text(result.stdout, encoding="utf-8")
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        result.returncode, gs_args, output=result.stdout
                    )
            except subprocess.CalledProcessError as exc:
                logger.error(
                    "Ghostscript failed on '%s' (exit code: %d).\n%s",
                    pdf.name,
                    exc.returncode,
                    exc.output,
                )
                sys.exit(1)
            except FileNotFoundError as exc:
                logger.error("Ghostscript executable not found: %s", exc)
                sys.exit(1)

            # Append raw GS output to log file
            gs_raw: str = gs_output_file.read_text(encoding="utf-8").strip()
            log_entry_lines: list[str] = [
                LOG_ENTRY_SEP,
                f"  [{i}/{total}] {pdf.name}",
                LOG_ENTRY_SEP,
                gs_raw,
                "",
            ]
            with log_file.open("a", encoding="utf-8") as lf:
                lf.write("\n".join(log_entry_lines) + "\n")

            # Copy result back with original filename
            shutil.copy2(temp_output, output_file)

            # ── Compression ratio reporting ──────────────────────────────
            original_size: int = pdf.stat().st_size
            compressed_size: int = output_file.stat().st_size
            total_original_size += original_size
            total_compressed_size += compressed_size

            if original_size > 0:
                ratio: float = round((1 - compressed_size / original_size) * 100, 1)
            else:
                ratio = 0.0

            orig_mb: float = round(original_size / BYTES_PER_MB, 2)
            comp_mb: float = round(compressed_size / BYTES_PER_MB, 2)
            logger.info("[%d/%d] %s... %s MB -> %s MB (%s%%)", i, total, pdf.name, orig_mb, comp_mb, ratio)

    # ── Summary ───────────────────────────────────────────────────────────
    logger.info("")
    if total_original_size > 0:
        total_ratio: float = round((1 - total_compressed_size / total_original_size) * 100, 1)
        total_orig_mb: float = round(total_original_size / BYTES_PER_MB, 2)
        total_comp_mb: float = round(total_compressed_size / BYTES_PER_MB, 2)
        logger.info(
            "  Total: %d file(s)  |  %s MB -> %s MB  (%s%%)",
            total, total_orig_mb, total_comp_mb, total_ratio,
        )
    else:
        logger.info("  Compressed files are in '%s'.", output_dir)
    logger.info(BANNER_SEP)
    logger.info("")


if __name__ == "__main__":
    main()
