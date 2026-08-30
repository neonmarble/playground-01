# Knowledge Base Index

| Topic | Summary |
| --- | --- |
| [oh-my-pi](topics/oh-my-pi.md) | Terminal AI coding agent; 8 releases in week of Aug 24–30, 2026 — new models (GLM-5.3-Flash, grok-4.6), git TUI polish, retry improvements, canary/stable update channels, usage tracking, Sharpshooter memory. |
| [openchamber-remote-opencode](topics/openchamber-remote-opencode.md) | OpenChamber remote-instance error "opencode CLI is not installed" despite brew install — root cause is the fixed probe list + `sh -lc` PATH lookup missing Homebrew's Linux dir; fixes: symlink into `~/.local/bin`, add brew to `~/.profile`, or reinstall via official installer. |