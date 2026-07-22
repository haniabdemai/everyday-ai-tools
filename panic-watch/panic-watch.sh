#!/bin/bash
# panic-watch.sh: notify your phone via ntfy.sh when a new kernel panic
# report appears on this Mac. Runs at login + daily via a launchd agent
# (see com.example.panic-watch.plist). Persistent monitor; removal steps
# are in the README.

STATE_DIR="$HOME/Library/Application Support/panic-watch"
STATE_FILE="$STATE_DIR/last-check"
REPORT_DIR="/Library/Logs/DiagnosticReports"
# Your private ntfy.sh topic. Treat it like a password: anyone who has
# it can read and send your notifications. Generate something random.
NTFY_TOPIC="${NTFY_TOPIC:?Set NTFY_TOPIC to your private ntfy.sh topic}"

push_notify() {
    # $1 = title, $2 = body
    /usr/bin/curl -s -o /dev/null --max-time 15 \
        -H "Title: $1" \
        -H "Priority: high" \
        -d "$2" \
        "https://ntfy.sh/${NTFY_TOPIC}"
}

mkdir -p "$STATE_DIR"

# The report directory is only readable by administrator accounts. Warn
# loudly rather than silently reporting nothing forever.
if [[ ! -r "$REPORT_DIR" || ! -x "$REPORT_DIR" ]]; then
    push_notify "panic-watch cannot read reports" \
        "panic-watch cannot read $REPORT_DIR on this Mac. Run it from an administrator account; until then no panic reports are being monitored."
    exit 1
fi

# First run: baseline silently so pre-existing (already investigated)
# panic reports don't fire a stale alert.
if [[ ! -f "$STATE_FILE" ]]; then
    touch "$STATE_FILE"
    exit 0
fi

# Only filenames are pushed, never report contents.
names=$(/usr/bin/find "$REPORT_DIR" -name "*.panic" -newer "$STATE_FILE" -print0 \
    | /usr/bin/xargs -0 -n1 /usr/bin/basename \
    | /usr/bin/head -3 | /usr/bin/tr '\n' ' ')

touch "$STATE_FILE"

if [[ -n "$names" ]]; then
    push_notify "Mac kernel panic detected" \
        "New kernel panic report(s) on this Mac: ${names}. Full reports in $REPORT_DIR."
fi
