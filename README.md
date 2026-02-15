# 🛡️ SecureClaw

**OpenClaw power, without the YOLO.**

SecureClaw is a permission-first AI agent framework. Agents can only act when you've explicitly granted them access.

*Human-directed, AI-accelerated.*

## Why?

OpenClaw proved the demand for personal AI agents. But 100k+ users gave autonomous access to a system with no formal security model. We call it SecureClaw because security is our north star. Bug bounty coming - seeking sponsors to fund it.

## Discord Setup

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application**, name it (e.g., "SecureClaw")
3. Go to **Bot** tab → **Add Bot**
4. Copy the **Token** - you'll need this
5. Enable **Message Content Intent** under Privileged Gateway Intents
6. Go to **OAuth2 → URL Generator**
7. Check **bot** under Scopes
8. Check **Send Messages** and **Read Message History** under Bot Permissions
9. Copy the URL, open it, and invite the bot to your server

## Quick Start

```bash
pip install -r requirements.txt
export SECURECLAW_DISCORD_TOKEN="your_token"
export ANTHROPIC_API_KEY="your_key"
python -m secureclaw.discord_bot
```

## Commands

| Command | Description |
|---------|-------------|
| `!scopes` | List available permission scopes |
| `!grant <scope>` | Grant a scope to your agent |
| `!revoke <scope>` | Revoke a scope |
| `!grants` | See your current grants |

Or just chat naturally - Claude will request permissions as needed.

## Scopes

**Working now:**
- `filesystem.read` - Read files
- `filesystem.list` - List directory contents
- `network.http` - Fetch URLs

**Defined (not yet wired):**
- `filesystem.write` - Write files
- `email.read` / `email.send` - Email access
- `messaging.send` - Send messages
- `shell.execute` - Run shell commands

## Defense Layers

- **Rate limiting** - 10 requests per minute per user (configurable)
- **User allowlist** - Optionally restrict to specific Discord user IDs:
  ```bash
  export SECURECLAW_ALLOWED_USERS="123456789,987654321"
  ```
  Leave unset to allow all users.

## Status

**MVP** - This is early. Security model is "verifiable by default, visible on demand." We're building in public and welcome feedback.

## Philosophy

> Logs are for auditors, proof is for users.

We collect everything, show almost nothing. Zero friction by default, full transparency on demand.

## License

MIT
