# oh-my-pi — Recent Changes (week of Aug 24–30, 2026)

## What it is
oh-my-pi (`omp`) is a terminal-based AI coding agent — an enhanced fork of Mario Zechner's "Pi" coding agent. It adds a modern TUI, git integration, LSP support, browser tools, subagents, and extensibility. Repo: https://github.com/can1357/oh-my-pi

## Release cadence
Very active: 8 releases in one week (v18.0.4 → v18.0.11, Aug 24–29, 2026). Auto-published by GitHub Actions.

## Key changes this week (plain language)

### New models & providers
- Added Z.AI GLM-5.3-Flash (fast model, 1M-token context, image input).
- Default xAI model bumped to grok-4.6.
- DeepInfra support for image_gen and tts tools (MP3/WAV output).
- Model discovery now refreshes from shared catalog so new models appear without a release.

### Git workflow polish
- Faster, smarter auto-generated conventional commit messages (shared between git TUI and `omp commit --legacy`).
- Sidebar: collapse/expand Unstaged/Staged sections; shortcuts to stage/unstage whole sections.
- New/untracked files grouped separately from tracked changes.
- Whitespace-only / formatting-only / import-only changes filtered out of diffs (TS, JS, Rust, Go).

### Retry improvements
- In-place retry of failed tool calls via F5 / Alt+R / `/retry` — no extra model round trip.
- Transport errors after complete tool calls retry through retry budgets / fallback chains instead of ending the turn.
- Credential rotation on HTTP 402 (payment required) before model fallback.

### Update channels
- `omp update --canary` (prereleases from npm canary dist-tag) and `omp update --stable`; channel persists and drives startup update check.

### Usage / billing visibility
- Z.AI GLM Coding Plan credit quotas (5h + weekly) shown in `omp usage` and status line.
- `omp usage clients` reports per-client token usage by provider (`--days`, `--json`).
- Application-level usage attribution via `OMP_APP_NAME`.

### Memory
- New "Sharpshooter" memory backend for friction-earned project decisions; `/memory queue` and `/memory sync` controls.

### Misc quality-of-life
- `/restart` relaunches omp with original flags and resumes session.
- Thinking level shown as compact icon in status line (`statusLine.compactThinkingLevel` to disable).
- Gallery previews for composer/status-line components.
- Clickable OSC 8 hyperlinks in chat when `tui.hyperlinks=always`.
- Reduced idle CPU usage while agent is working.
- Prompt history persisted immediately; session DB checkpointed on exit.

### Notable fixes
- Windows: Python eval hanging on native modules (NumPy); stale update launchers; CRLF handling in git TUI.
- Logins: Perplexity 2FA, Z.AI, Qianfan, Cloudflare AI Gateway, OpenRouter browser sign-in.
- Streaming: long thinking output continues into scrollback; thinking-block visibility toggle fixed.
- Browser: orphaned pages/iframes/workers cleanup; relay hangs fixed.
- Misc: MCP OAuth discovery for nested paths (Keycloak), LSP diagnostics false-success, `omp plugin features` for marketplace plugins.

## Sources
- Releases: https://github.com/can1357/oh-my-pi/releases
- v18.0.11: https://github.com/can1357/oh-my-pi/releases/tag/v18.0.11
- v18.0.10: https://github.com/can1357/oh-my-pi/releases/tag/v18.0.10
- v18.0.9: https://github.com/can1357/oh-my-pi/releases/tag/v18.0.9
- v18.0.8: https://github.com/can1357/oh-my-pi/releases/tag/v18.0.8
- v18.0.7: https://newreleases.io/project/github/can1357/oh-my-pi/release/v18.0.7
- v18.0.6: https://github.com/can1357/oh-my-pi/releases/tag/v18.0.6
- Changelog: https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/CHANGELOG.md

## Open questions / gaps
- No independent coverage of user sentiment or adoption found; summary is based solely on release notes.
- If deeper detail needed: memory system design, update channel mechanics, or git TUI feature set.