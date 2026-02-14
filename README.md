# 🛡️ SecureClaw

**OpenClaw power, without the YOLO.**

SecureClaw is a permission-first AI agent framework. Agents can only act when you've explicitly granted them access.

## Why?

OpenClaw proved the demand for personal AI agents. But 100k+ users gave autonomous access to a system with no security model. We call it SecureClaw because we want you to prove us wrong — bug bounty coming soon.

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

Or just chat naturally — Claude will request permissions as needed.

## Scopes

- `filesystem.read` — Read files
- `filesystem.write` — Write files
- `network.http` — HTTP requests
- `email.read` / `email.send` — Email access
- `messaging.send` — Send messages
- `shell.execute` — Run shell commands

## Status

**MVP** — This is early. Security model is "verifiable by default, visible on demand." We're building in public and inviting scrutiny.

## Philosophy

> Logs are for auditors, proof is for users.

We collect everything, show almost nothing. Zero friction by default, full transparency on demand.

## License

MIT
