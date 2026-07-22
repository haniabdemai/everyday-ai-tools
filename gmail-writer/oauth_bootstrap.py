#!/usr/bin/env python3
"""One-off OAuth bootstrap for the gmail-writer MCP server.

Runs the google-auth-oauthlib installed-app flow for the Gmail API with
scope https://www.googleapis.com/auth/gmail.modify and writes
~/.gmail_token.json (permissions 600) in the exact shape index.js and
test.js expect:

    {client_id, client_secret, token, refresh_token, expiry, scopes}

Prerequisite: a Desktop app OAuth client in Google Cloud Console, with
its client secret JSON downloaded (see README, Setup step 1).

Usage:
    uv run --with google-auth-oauthlib oauth_bootstrap.py path/to/client_secret.json

or, without uv:
    pip install google-auth-oauthlib
    python3 oauth_bootstrap.py path/to/client_secret.json
"""
import json
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH = os.path.expanduser("~/.gmail_token.json")


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: oauth_bootstrap.py path/to/client_secret.json\n"
            "(the Desktop app OAuth client JSON downloaded from Google Cloud Console)",
            file=sys.stderr,
        )
        sys.exit(1)

    secrets_path = sys.argv[1]
    if not os.path.isfile(secrets_path):
        print(f"Client secret file not found: {secrets_path}", file=sys.stderr)
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
    # access_type=offline and prompt=consent guarantee a refresh token even
    # if this client has been authorised before.
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        print(
            "Warning: Google returned no refresh token. The server will stop "
            "working when the access token expires. Re-run this script; if it "
            "persists, revoke the app at myaccount.google.com/permissions and "
            "try again.",
            file=sys.stderr,
        )

    expiry = creds.expiry.isoformat() + "Z" if creds.expiry else None
    token_data = {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "expiry": expiry,
        "scopes": list(creds.scopes or SCOPES),
    }

    # Create (or truncate) with owner-only permissions; the file holds
    # credentials that grant mail write access.
    fd = os.open(TOKEN_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(token_data, f, indent=2)
        f.write("\n")
    os.chmod(TOKEN_PATH, 0o600)  # enforce even if the file already existed

    print(f"Wrote {TOKEN_PATH} (permissions 600, scope gmail.modify).")
    print("Verify with: node test.js")


if __name__ == "__main__":
    main()
