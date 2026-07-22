# gmail-writer

**A local MCP server that gives Claude working Gmail write operations,
because the hosted Gmail MCP's write tools are broken by design.**

Also published standalone at [github.com/haniabdemai/gmail-writer-mcp](https://github.com/haniabdemai/gmail-writer-mcp).

## The bug this fixes

The claude.ai hosted Gmail MCP *shows* write tools (`label_thread`,
`unlabel_thread`, …) but every call fails with "insufficient
authentication scopes". Root cause, found the hard way: the hosted MCP has
a tool cap during OAuth negotiation, and under it it only requests
`gmail.readonly`, never `gmail.modify`. The write tools are advertised
but can never work. This server sidesteps the whole path: a local MCP
process with its own Desktop OAuth client requesting the correct scope.

## Tools

| Tool | Description |
|---|---|
| `gmail_modify_thread` | Add/remove labels on a thread to move, archive, star, or mark read/unread |
| `gmail_search_threads` | Search threads with Gmail query syntax |
| `gmail_list_labels` | List all labels with IDs |
| `gmail_list_attachments` | Find attachments across messages matching a query (metadata only) |
| `gmail_download_attachment` | Download one attachment by ID |
| `gmail_download_all_attachments` | Bulk-download every attachment matching a query, foldered per email |

Also included: `label-for-deletion.mjs`, a standalone script that applies a
review label to inbox junk matching your queries (edit the `QUERIES` array;
set `GMAIL_DELETION_LABEL_ID`) so you bulk-delete from the Gmail UI with
one filtered view.

## Setup

Prerequisites: Node 18+ and Python 3 (for the one-off OAuth bootstrap).

1. In Google Cloud Console: create a project, enable the Gmail API, create
   a **Desktop app** OAuth client, and download its client secret JSON.
2. Run the bundled bootstrap:

   ```bash
   uv run --with google-auth-oauthlib oauth_bootstrap.py path/to/client_secret.json
   ```

   It opens a browser consent flow with scope
   `https://www.googleapis.com/auth/gmail.modify` and writes
   `~/.gmail_token.json` (permissions 600) as
   `{client_id, client_secret, token, refresh_token, expiry, scopes}`. The
   file is self-contained and the server refreshes it automatically.
3. `npm install`, then register with Claude Code:

   ```bash
   claude mcp add gmail-writer -- node /path/to/gmail-writer/index.js
   ```

4. `node test.js` runs the non-destructive test suite against your mailbox
   (test 5 stars a real thread and immediately unstars it, restoring its
   original state).

Note on token lifetime: if your Google Cloud OAuth consent screen is in
**Testing** status, Google expires refresh tokens after 7 days and you will
have to re-run the bootstrap weekly. Publish the app to Production (it can
stay unverified for your own account) to get long-lived refresh tokens.

## Security notes

The token file grants mail write access, so keep it out of any repo
(`chmod 600`, never commit). The server runs locally and talks only to
Google's API; nothing is proxied through third parties.

This server cannot send email: it exposes no send or compose tool. Bear in
mind, though, that the `gmail.modify` scope itself would permit sending,
so protect the token file accordingly.

`gmail.modify` does allow moving mail to the bin (adding the `TRASH`
label), although not permanent, immediate deletion. Treat label changes
suggested by an AI with the same care you would any bulk mail operation.

## Licence

MIT.
