```
   ╔══════════════════════════════════╗
   ║     PLAYGROUND 01 🎮            ║
   ║  where i yeet code into the void ║
   ╚══════════════════════════════════╝
```

this is where i break things, fix them (mostly), and occasionally learn something along the way. no production code, no stress, just vibes.

---

## 🎪 what's inside

### 📄 gs-compress — *shrink ray for PDFs*

got a 200mb pdf that's basically just a scan of a receipt? feed it to ghostscript and watch it come out the other side a fraction of the size. originals never get touched — no oopsies.

```
gs-compress/
├── gs-compress.ps1      # PowerShell (fancy -WhatIf / -Confirm)
├── gs-compress.py        # Python 3 (zero external deps, works everywhere)
└── README-gs-compress.ps1.md
```

```powershell
.\gs-compress\gs-compress.ps1 -PdfSettings /screen -OutputDir small
```

```bash
python gs-compress\gs-compress.py --pdf-settings /screen -o small
```

> **fun fact**: the python version was born because someone on the internet said "why would you write this in powershell?"

### 📡 ping_monitors — *"is it down or is it just me?"*

pings a host. if it dies, you get a telegram message. when it comes back, you get another one. and it won't blow up your phone every 60 seconds while it's still down — because that would be annoying.

this one went through a whole evolution:

| # | file | lang | vibes |
|---|------|------|-------|
| 1 | `ping_monitor-g54m.sh` | bash | the og. hardcoded host, but had the state tracking brain cell |
| 2 | `ping_monitor-dsv4f.sh` | bash | cleaner. took cli args. forgot the state tracking at home |
| 3 | `ping_monitor-mimo-v2_5-v01.sh` | bash | final form. all the good parts, none of the oops |
| 4 | `ping_monitor-mimo-v2_5-v01.py` | python | same deal, but now it runs on windows too |

```bash
export TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="..."
./ping_monitors/ping_monitor-mimo-v2_5-v01.sh 1.1.1.1
```

```bash
python ping_monitors/ping_monitor-mimo-v2_5-v01.py 1.1.1.1 -i 30
```

### 💾 rclone-mount-windows.md — *ssh folder as a windows drive*

wrote this after spending an afternoon fighting with rclone so i wouldn't have to fight with it again. covers config, caching, network mode, and running it as a windows service so it survives reboots. future me will be grateful.

---

## 🚀 quick start

```bash
git clone https://github.com/neonmarble/playground-01.git
cd playground-01
```

## 🧸 what i'm messing with

| thing | how it's going |
|-------|---------------|
| **git** | branching, rebasing, the occasional `git reflog` panic |
| **github actions** | getting those green checkmarks |
| **bash / powershell / python** | whatever gets the job done |
| **devops-adjacent chaos** | monitoring, file sync, automation, you name it |

## 📎 links that live in my bookmarks bar

- [git docs](https://git-scm.com/doc) — for when i inevitably forget how rebase works
- [github actions docs](https://docs.github.com/en/actions)
- [ghostscript](https://www.ghostscript.com/) — the real mvp
- [rclone](https://rclone.org/) — ssh folders on windows? yes please
- [oh shit, git!?!](https://ohshitgit.com/) — we've all been there

---

<p align="center">
🧪 learning in public<br>
<sub><sup>last updated whenever i felt like it</sup></sub>
</p>
