# panic-watch

**Your Mac kernel-panicked overnight and you'll never know unless
something tells you. This does, on your phone, within a day.**

Also published standalone at [github.com/haniabdemai/mac-panic-watch](https://github.com/haniabdemai/mac-panic-watch).

Kernel panics that happen during sleep or unattended hours leave a report
in `/Library/Logs/DiagnosticReports` and nothing else: the machine reboots
and life carries on. If you're chasing an intermittent hardware or kernel
bug, missing those reports means losing the evidence trail. panic-watch is
deliberately tiny (one shell script, one launchd agent) and makes new
panic reports impossible to miss via an [ntfy.sh](https://ntfy.sh) push
notification.

## How it works

Runs at login and once daily. Keeps a timestamp file; on each run it
`find`s panic reports newer than the last check, resets the timestamp, and
if anything new appeared, pushes a high-priority notification with the
report names. First run baselines silently so pre-existing reports don't
fire a stale alert.

Only report filenames are ever pushed to ntfy, never report contents.

## Setup

Prerequisite: the account running the agent must be an administrator.
`/Library/Logs/DiagnosticReports` is not readable by standard accounts,
and the script pushes a warning notification (rather than silently
monitoring nothing) if it cannot read the directory.

1. Pick a private ntfy topic (treat it like a password: anyone with the
   topic name can read and send on it) and subscribe to it in the ntfy app
   on your phone.
2. Install the script and agent:

```bash
mkdir -p ~/Library/Scripts
cp panic-watch.sh ~/Library/Scripts/
sed -e "s|__HOME__|$HOME|g" -e "s|__NTFY_TOPIC__|your-topic-here|g" \
    com.example.panic-watch.plist > ~/Library/LaunchAgents/com.example.panic-watch.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.panic-watch.plist
```

To remove: `launchctl bootout gui/$(id -u)/com.example.panic-watch` and
delete the plist and script.

## Licence

MIT.
