# Playground 01

> A sandbox for scripting, automation, and DevOps experiments.

## Contents

| Directory/File | Description | Languages |
|----------------|-------------|-----------|
| [`gs-compress/`](gs-compress/) | Batch PDF compressor using Ghostscript | PowerShell, Python |
| [`ping_monitors/`](ping_monitors/) | Network uptime monitor with Telegram alerts | Bash, Python |
| [`rclone-mount-windows.md`](rclone-mount-windows.md) | Guide: mount remote SSH dirs on Windows via rclone + WinFsp | — |

### gs-compress

Compresses all PDFs in the current directory using Ghostscript. Outputs compressed copies (originals untouched), per-file compression ratios, a timestamped log file, and an overall summary.

```powershell
# PowerShell version
.\gs-compress\gs-compress.ps1

# Python version (zero dependencies)
python gs-compress\gs-compress.py --pdf-settings /screen -o small
```

Supports `-WhatIf`/`-Confirm` (PowerShell) and `--dry-run` (Python).

### ping_monitors

Pings a host and sends Telegram alerts on state changes (down / recovery). Includes multiple iterations that evolved from a minimal script to a combined best-of version.

```bash
# Bash version
export TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="..."
./ping_monitors/ping_monitor-mimo-v2_5-v01.sh 1.1.1.1 -i 30

# Python version (zero dependencies, cross-platform)
python ping_monitors/ping_monitor-mimo-v2_5-v01.py 1.1.1.1 -i 30
```

### rclone-mount-windows.md

Step-by-step guide covering SFTP remote configuration, mounting with WinFsp, performance tuning, running as a Windows service with Servy, and SSH key setup.

## Getting Started

```bash
git clone https://github.com/neonmarble/playground-01.git
cd playground-01
```

## Topics

- **Git** -- branching, PRs, rebasing
- **CI/CD** -- GitHub Actions, pipelines
- **Scripting** -- Bash, PowerShell, Python (cross-platform)
- **DevOps** -- monitoring, file syncing, automation

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Oh Shit, Git!?!](https://ohshitgit.com/)
- [Ghostscript](https://www.ghostscript.com/)
- [rclone](https://rclone.org/)
