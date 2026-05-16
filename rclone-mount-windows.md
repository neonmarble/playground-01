# Mount a Remote Directory via SSH on Windows 11 with `rclone mount`

## Prerequisites

### 1. Install rclone

```powershell
winget install rclone.rclone
```

Or download from https://rclone.org/downloads/

### 2. Install WinFsp

[https://winfsp.dev](https://winfsp.dev) — **Required.** rclone mount on Windows depends on WinFsp to provide the FUSE emulation layer.

Download the `.msi` installer and run it:

```powershell
winget install winfsp.winfsp
```

Reboot after installation.

---

## Step 1: Configure the SFTP Remote

Run the interactive config wizard:

```powershell
rclone config
```

Walkthrough:

```
n) New remote
name> myserver          # pick a short name
Storage> sftp           # type "sftp" or pick the number
host> 192.168.1.100     # your server's IP or hostname
user> myuser            # SSH username
port> 22                # SSH port (default 22)
```

You will be asked for authentication method:

| Method | When to use |
|--------|-------------|
| **Key file** (recommended) | Provide path to your private key, e.g. `C:\Users\You\.ssh\id_ed25519` |
| **Password** | rclone will prompt for the password each time (use `rclone config password` to set it) |
| **SSH agent** | If you already have `ssh-agent` / Pageant running |

After setup, verify it works:

```powershell
rclone ls myserver:/home/myuser
```

---

## Step 2: Mount the Remote

### Option A — Fixed disk drive (default)

Mount to an automatically assigned drive letter (starts from Z: backwards):

```powershell
rclone mount myserver:/home/myuser *
```

Mount to a specific drive letter:

```powershell
rclone mount myserver:/home/myuser X:
```

Mount to an empty directory path:

```powershell
rclone mount myserver:/home/myuser C:\mnt\remote
```

> The parent directory must exist, and the mount subdirectory must **not** exist.

### Option B — Network drive (recommended for SSH remotes)

Network mode is often more stable for high-latency connections like SSH:

```powershell
rclone mount myserver:/home/myuser X: --network-mode
```

Or specify a UNC volume name directly:

```powershell
rclone mount myserver:/home/myuser \\MyServer\home
```

> `--network-mode` tells Windows to treat the drive as a network share rather than a fixed disk. This avoids some compatibility issues.

---

## Step 3: Recommended Flags for Daily Use

A production-quality mount command:

```powershell
rclone mount myserver:/home/myuser X: `
  --network-mode `
  --volname "Remote Home" `
  --vfs-cache-mode writes `
  --cache-dir C:\rclone-cache `
  --vfs-cache-max-age 1h `
  --vfs-cache-max-size 2G `
  --file-perms 0777 `
  --dir-perms 0777 `
  --vfs-fast-fingerprint `
  --transfers 4 `
  --buffer-size 32M `
  --attr-timeout 5s `
  --dir-cache-time 10m `
  --log-file C:\rclone-logs\mount.log `
  --log-level INFO
```

### What each flag does

| Flag | Purpose |
|------|---------|
| `--network-mode` | Mount as a network drive (better latency handling) |
| `--volname` | Custom label shown in Windows Explorer |
| `--vfs-cache-mode writes` | Buffers writes to disk before uploading (enables seeking, retries) |
| `--cache-dir` | Where VFS cache files are stored on disk |
| `--vfs-cache-max-age 1h` | Evict cached files not accessed for 1 hour |
| `--vfs-cache-max-size 2G` | Limit total cache size |
| `--file-perms 0777` | Give read/write/execute to everyone (needed to launch .exe from mount) |
| `--dir-perms 0777` | Same for directories |
| `--vfs-fast-fingerprint` | Skip slow hash reads for change detection (important for SFTP) |
| `--transfers 4` | Parallel upload threads |
| `--buffer-size 32M` | Read-ahead buffer per open file |
| `--attr-timeout 5s` | Cache file attributes for 5 seconds |
| `--dir-cache-time 10m` | Cache directory listings for 10 minutes |
| `--log-file` | Log output to a file |
| `--log-level INFO` | Detail level for logs |

### Cache mode comparison

| Mode | Read Speed | Write Support | Disk Usage | Best For |
|------|-----------|---------------|------------|----------|
| `off` | Direct from remote | Sequential only, no seeks | None | Read-only browsing |
| `minimal` | Direct | Limited, no read+write on same file | Minimal | Occasional edits |
| `writes` | Direct for reads | Full write support with retries | Moderate | **General use (recommended)** |
| `full` | Cached (fastest) | Full support, all data cached | High | Heavy editing, large files |

---

## Step 4: Run as a Windows Service (auto-start) with Servy

[Servy](https://github.com/aelassas/servy) is a professional-grade, open-source Windows service wrapper — a modern alternative to NSSM. It lets you run any executable as a native Windows service with health checks, log rotation, pre/post-launch hooks, environment variables, and more.

### 4.1 Install Servy

From an **elevated** (Run as Administrator) PowerShell terminal:

```powershell
winget install servy
```

The CLI (`servy-cli.exe`) is added to your `PATH` automatically.

### 4.2 Install the rclone mount as a service

```powershell
servy-cli install `
  --name="RcloneMount" `
  --displayName="Rclone SSH Mount" `
  --description="Mounts remote SFTP server via rclone to X: drive" `
  --path="C:\Program Files\rclone\rclone.exe" `
  --startupDir="C:\Program Files\rclone" `
  --params="mount myserver:/home/myuser X: --network-mode --vfs-cache-mode writes --cache-dir C:\rclone-cache --vfs-cache-max-age 1h --vfs-cache-max-size 2G --file-perms 0777 --dir-perms 0777 --vfs-fast-fingerprint --log-file C:\rclone-logs\mount.log --log-level INFO --config C:\Users\You\.config\rclone\rclone.conf" `
  --startupType="AutomaticDelayedStart" `
  --priority="Normal" `
  --stdout="C:\rclone-logs\service-stdout.log" `
  --stderr="C:\rclone-logs\service-stderr.log" `
  --enableSizeRotation `
  --rotationSize=10 `
  --enableHealth `
  --heartbeatInterval=30 `
  --maxFailedChecks=3 `
  --recoveryAction="RestartService" `
  --maxRestartAttempts=5 `
  --startTimeout=30 `
  --stopTimeout=15
```

> **Important**: The service runs as `LocalSystem` by default. Use `--config` to explicitly point to your rclone.conf, since the SYSTEM account won't read your user config by default.

### 4.3 Start the service

```powershell
servy-cli start --name="RcloneMount"
```

Or via `sc.exe`:

```powershell
sc.exe start RcloneMount
```

### 4.4 Manage the service

| Action | Command |
|--------|---------|
| Check status | `servy-cli status --name="RcloneMount"` |
| Stop | `servy-cli stop --name="RcloneMount"` |
| Restart | `servy-cli restart --name="RcloneMount"` |
| Uninstall | `servy-cli uninstall --name="RcloneMount"` |

### 4.5 What the flags do

| Servy flag | Purpose |
|------------|---------|
| `--startupType=AutomaticDelayedStart` | Starts shortly after boot, reducing boot-time pressure |
| `--stdout` / `--stderr` | Capture rclone output to separate log files |
| `--enableSizeRotation --rotationSize=10` | Rotate logs when they exceed 10 MB |
| `--enableHealth --heartbeatInterval=30` | Monitor rclone health every 30 seconds |
| `--maxFailedChecks=3 --recoveryAction=RestartService` | Restart the service after 3 failed health checks |
| `--maxRestartAttempts=5` | Give up after 5 consecutive restart failures |
| `--startTimeout=30` | Allow up to 30 seconds for the mount to come up |
| `--stopTimeout=15` | Allow up to 15 seconds for graceful unmount |

### 4.6 Using a dedicated service account (optional)

If the mount needs access to network shares or specific permissions beyond LocalSystem:

```powershell
# Set the password in the environment (not on the command line — security best practice)
$env:SERVY_PASSWORD = "your_secret_password"

servy-cli install `
  --name="RcloneMount" `
  --path="C:\Program Files\rclone\rclone.exe" `
  --params="...<same as above>..." `
  --user=".\rclonesvc" `
  --startupType="AutomaticDelayedStart"

# Clear the password from memory immediately
Remove-Item Env:SERVY_PASSWORD
```

> **Security**: Never pass `--password` directly on the CLI — it is visible in process listings and shell history. Always use the `SERVY_PASSWORD` environment variable instead.

### 4.7 GUI alternative: Servy Desktop App

Servy includes a desktop GUI for managing services visually:

```powershell
servy-desktop
```

From there you can create, configure, start/stop services, view live CPU/RAM graphs, browse logs, and export/import configurations.

### 4.8 Servy Manager (monitoring)

Servy ships with a Manager app for real-time monitoring of all installed services:

```powershell
servy-manager
```

This provides live performance graphs, log preview, service dependency visualization, and service event notifications (including email alerts on failures).

---

## SSH Key Setup (Passwordless Auth)

### Generate a key on Windows:

```powershell
ssh-keygen -t ed25519 -f C:\Users\You\.ssh\id_ed25519
```

### Copy the public key to the remote server:

```powershell
type C:\Users\You\.ssh\id_ed25519.pub | ssh myuser@192.168.1.100 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

### Configure rclone to use the key:

```powershell
rclone config
# Edit myserver -> key_file = C:\Users\You\.ssh\id_ed25519
```

Or non-interactively:

```powershell
rclone config update myserver key_file="C:\Users\You\.ssh\id_ed25519"
```

---

## Important Windows Caveats

### Elevated vs. Non-Elevated

> Drives mounted from an **Administrator** command prompt are **not visible** in Windows Explorer (which runs non-elevated).

**Fix**: Always mount from a **non-elevated** terminal (PowerShell/CMD without "Run as Administrator").

If you need the mount in both elevated and non-elevated contexts, enable linked connections in the registry:

```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLinkedConnections" -Value 1 -PropertyType DWORD
```

Reboot after setting.

### FileSecurity / Permission Issues

If applications report "Permission denied" when writing, add the WinFsp `FileSecurity` option to grant full write access to everyone:

```powershell
rclone mount myserver:/home/myuser X: -o FileSecurity="D:P(A;;FRFWFX;;;WD)"
```

`FRFWFX` = File Read + File Write + File Execute, `WD` = Everyone.

### WinFsp Logs

If the mount fails silently, check WinFsp logs:

```
%ProgramData%\WinFsp\winfsp.log
```

### GUI Alternative

rclone has a built-in web GUI:

```powershell
rclone rcd --rc-web-gui
```

Open `http://localhost:5572` in your browser — you can configure remotes and mount from the UI.

---

## Quick Reference

```powershell
# One-liner: configure, mount, done
rclone config                        # set up "myserver" SFTP remote first
rclone ls myserver:/                 # test connectivity
rclone mount myserver:/home/myuser X: --network-mode --vfs-cache-mode writes --cache-dir C:\rclone-cache --vfs-fast-fingerprint --file-perms 0777 --dir-perms 0777 --log-file C:\rclone-logs\mount.log --log-level INFO
```

To unmount: press `Ctrl+C` in the terminal, or kill the rclone process.

---

## References

- [rclone mount documentation](https://rclone.org/commands/rclone_mount/)
- [WinFsp](https://winfsp.dev/)
- [rclone SFTP backend](https://rclone.org/sftp/)
- [EnableLinkedConnections](https://docs.microsoft.com/en-us/troubleshoot/windows-client/networking/mapped-drives-not-available-from-elevated-command)
