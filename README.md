# everyday-ai-tools

**AI tools for the unglamorous parts of life and work: appeals letters,
meeting-heavy inboxes, hours of unwatched video, a Mac that panics at 3am.**
Each tool here was built for a real recurring problem, is in genuine daily
use, and earns its place by doing something the obvious alternatives don't.
Upstream projects are credited where a tool builds on them.

| Tool | What it does | Why it beats the alternatives |
|---|---|---|
| [**formal-appeals**](skills/formal-appeals/SKILL.md) (Claude skill) | A complete playbook for appeals, reconsiderations and formal complaints to institutions: evidence verification, conclusion-first structure, a rejected-vs-shipped wording table, adversarial review, print-ready document packs | Not template letters but a working method where every rule was earned through a rejected draft |
| [**transcription**](transcription/) (scripts) | Local transcription + speaker diarization on Apple Silicon: audio in, speaker-labelled transcript out | Runs on the Apple GPU via MLX at 18–28× realtime (not the slow CPU path), integrates diarization *aligned* with the transcript (the part most local guides skip), proven on a 22-hour real-world corpus, free and fully private. Built on [mlx-whisper](https://github.com/ml-explore/mlx-examples) and [pyannote.audio](https://github.com/pyannote/pyannote-audio), with all credit for the models to those projects |
| [**gmail-writer**](gmail-writer/) (MCP server) | Gmail write operations (label, move, archive, attachments) for Claude via a local MCP server | Exists because of a diagnosed platform bug: the hosted Gmail MCP's tool cap makes it negotiate read-only OAuth scopes, so its write tools are visible but permanently broken. This is the fix, with the post-mortem in its README |
| [**panic-watch**](panic-watch/) (shell + launchd) | Pushes a notification to your phone when your Mac writes a new kernel panic report | Kernel panics during sleep are invisible; you just find your Mac rebooted. Forty lines of shell and a launchd agent make them impossible to miss, via [ntfy.sh](https://ntfy.sh) |

Each tool is also published as its own standalone repository, so this
bundle is the collected edition and the standalone repos ([formal-appeals](https://github.com/haniabdemai/formal-appeals),
[local-transcription](https://github.com/haniabdemai/local-transcription),
[gmail-writer-mcp](https://github.com/haniabdemai/gmail-writer-mcp),
[mac-panic-watch](https://github.com/haniabdemai/mac-panic-watch)) are the
same tools packaged individually.

## Install

To install the Claude skill, copy it into your skills directory:

```bash
cp -r skills/formal-appeals ~/.claude/skills/
```

The script tools each carry their own README with setup, dependencies, and
adaptation notes.

## Status

Extracted July 2026 from tools in daily personal use. The transcription
scripts and panic-watch are macOS-specific (MLX needs Apple Silicon;
launchd is the scheduler); the formal-appeals skill and gmail-writer are portable.

## Licence

[MIT](LICENSE)
