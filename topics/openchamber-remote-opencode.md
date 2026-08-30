# OpenChamber remote instance: "opencode CLI is not installed on the remote machine"

**Date:** 2026-08-30
**Symptom:** Desktop app → Settings → Remote Instances → connect to a headless Ubuntu server (managed mode) fails with:

> The opencode CLI is not installed on the remote machine. Install it there, then connect again

...even though `opencode` IS installed on the remote (via Homebrew).

## Root cause

The error comes from `packages/electron/ssh-manager.mjs` in the openchamber repo
(`startRemoteServerManaged()`). Before starting the remote server, OpenChamber
resolves the `opencode` binary by probing a **fixed list of paths plus a PATH
lookup in a `sh -lc` login shell**:

```js
const REMOTE_OPENCODE_CANDIDATES = [
  '"$HOME/.opencode/bin/opencode"',
  '"${BUN_INSTALL:-$HOME/.bun}/bin/opencode"',
  '"$HOME/.local/bin/opencode"',
  '"$HOME/.openchamber/npm-global/bin/opencode"',
];
// ...
const opencodePath = await this.resolveRemoteTool(parsed, controlPath, 'opencode', REMOTE_OPENCODE_CANDIDATES);
if (!opencodePath) {
  throw new Error('The opencode CLI is not installed on the remote machine. Install it there, then connect again');
}
```

`resolveRemoteTool()` runs `sh -lc <script>` over SSH; the script checks each
candidate with `[ -x "$candidate" ]` and falls back to `command -v opencode`.

**Why a brew install fails the check:**

- Homebrew on Linux puts binaries in `/home/linuxbrew/.linuxbrew/bin`
  (root/system install) or `~/.linuxbrew/bin` (per-user install). That directory
  is in **none** of the four probed paths.
- The only escape hatch is the `command -v opencode` PATH lookup, and that only
  succeeds if brew's bin dir is on PATH in a **non-interactive login shell**.
  `sh -lc` sources `/etc/profile` and `~/.profile`, but **not** `~/.bashrc`
  (interactive-only). Homebrew's `eval "$(brew shellenv)"` line is commonly
  added only to `~/.bashrc`, so the lookup comes up empty.
- Source comment confirms the intent: *"A login shell over SSH does not source
  the user's interactive rc files, so tools installed into a home directory are
  missing from PATH even when they exist."* The probed list just doesn't include
  the brew location.

## Fixes (pick one)

1. **Symlink into a probed location (most robust — no shell-profile dependency):**
   ```sh
   mkdir -p ~/.local/bin
   ln -sf /home/linuxbrew/.linuxbrew/bin/opencode ~/.local/bin/opencode
   # or for a per-user brew install: ln -sf ~/.linuxbrew/bin/opencode ~/.local/bin/opencode
   ```
2. **Add brew to `~/.profile`** so login shells see it:
   ```sh
   echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
   ```
3. **Reinstall opencode with the official installer** — lands in
   `~/.opencode/bin`, which is the first probed path:
   ```sh
   curl -fsSL https://opencode.ai/install | bash
   ```
4. **Bypass the managed flow:** on the remote run `openchamber connect-url
   --port 3000 --server http://your-host:3000 --qr` and import the link in
   Desktop (Settings → Remote Instances → Import Link). External/connection-link
   mode skips the opencode pre-check.

## Verify

From the machine you connect from:

```sh
ssh user@host 'sh -lc "command -v opencode"'
```

- Prints a path → OpenChamber will find it (if it still fails, check versions).
- Prints nothing → PATH problem confirmed; apply fix 1 or 2.

Once resolved, OpenChamber hands the found path to the remote server via
`OPENCODE_BINARY=<path>`, so the server itself will launch opencode correctly.

## Notes / related

- Release notes (v1.14.x): "connecting to a remote machine now works when bun,
  OpenChamber or the opencode CLI live in your home directory rather than on the
  system path" — the probed home dirs are `~/.opencode/bin`, `~/.bun/bin`,
  `~/.local/bin`, `~/.openchamber/npm-global/bin`; brew's dir is not covered.
- Same class of problem documented for systemd user services: services start
  with a minimal environment and need an explicit
  `Environment="PATH=/home/linuxbrew/.linuxbrew/bin:..."` because no shell
  profile is sourced.
- Related open bug: openchamber/openchamber#2145 — machine-local settings
  (e.g. `opencodeBinary`) get synced to the remote server and can break
  OpenCode startup there.

## Sources

- Error string + detection logic: https://grep.app/search?q=opencode%20CLI%20is%20not%20installed%20on%20the%20remote%20machine
  (openchamber/openchamber `packages/electron/ssh-manager.mjs`)
- Remote Instances docs: https://docs.openchamber.dev/remote-instances/
- Remote access troubleshooting: https://docs.openchamber.dev/troubleshooting/remote-access/
- OpenChamber README (install methods, systemd PATH note): https://github.com/openchamber/openchamber
- OpenCode install methods (brew, curl → `~/.opencode/bin`): https://opencode.ai/download
- Bug #2145 (settings sync breaks remote OpenCode): https://github.com/openchamber/openchamber/issues/2145