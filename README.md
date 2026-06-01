# Playground 01

> a sandbox for scripting, automation, and devops experiments.

---

## Projects

### gs-compress
Batch-compress PDFs via Ghostscript — copies go to a subdirectory, originals untouched.

```
gs-compress/
├── gs-compress.ps1      # PowerShell (with -WhatIf / -Confirm)
├── gs-compress.py        # Python 3 (zero dependencies)
└── README-gs-compress.ps1.md
```

```powershell
.\gs-compress\gs-compress.ps1 -PdfSettings /screen -OutputDir small
```

```bash
python gs-compress\gs-compress.py --pdf-settings /screen -o small
```

### ping_monitors
Ping a host and get Telegram alerts on down/recovery — with state tracking to avoid spam.

| # | File | Lang | Notes |
|---|------|------|-------|
| 1 | `ping_monitor-g54m.sh` | Bash | original, hardcoded host, state tracking |
| 2 | `ping_monitor-dsv4f.sh` | Bash | cleaner structure, CLI arg, no state tracking |
| 3 | `ping_monitor-mimo-v2_5-v01.sh` | Bash | best of 1+2 combined |
| 4 | `ping_monitor-mimo-v2_5-v01.py` | Python | cross-platform port, argparse, zero deps |

```bash
export TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="..."
./ping_monitors/ping_monitor-mimo-v2_5-v01.sh 1.1.1.1
```

```bash
python ping_monitors/ping_monitor-mimo-v2_5-v01.py 1.1.1.1 -i 30
```

### rclone-mount-windows.md
Step-by-step guide: mount a remote SSH folder as a Windows drive using rclone + WinFsp. Covers config, caching, network mode, and running as a Windows service with Servy.

---

## Quick start

```bash
git clone https://github.com/neonmarble/playground-01.git
cd playground-01
```

## Topics

- **Git** — branching, rebasing, PRs
- **CI/CD** — GitHub Actions, pipelines
- **Scripting** — Bash, PowerShell, Python
- **DevOps tooling** — monitoring, file sync, automation

## References

- [Git docs](https://git-scm.com/doc)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Ghostscript](https://www.ghostscript.com/)
- [rclone](https://rclone.org/)
- [Oh Shit, Git!?!](https://ohshitgit.com/)

---

<p align="center">learning in public</p>
