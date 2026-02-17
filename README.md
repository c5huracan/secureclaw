# SecureClaw 🛡️

**OpenClaw power, without the YOLO.**

SecureClaw is a permission-first AI agent framework in a single file. Agents can only act when you've explicitly granted them access. They propose tools at runtime; humans approve or reject with feedback; approved tools persist, get auto-scoped, and are immediately usable.

*Human-directed, AI-accelerated.*

## Why?

OpenClaw proved the demand for personal AI agents. But 100k+ users gave autonomous access to a system with no formal security model. We call it SecureClaw because security is our north star. Bug bounty coming - seeking sponsors to fund it.

## How It Works

One file: `secureclaw.py`. Tools persist in `tools.json`, rejections in `rejections.json`.

```
propose → compile check → human approves → tools.json + auto-grant to creator
                        → human rejects  → rejections.json (with reason, for learning)

>>> from secureclaw import Agent, load_tools
>>> agent = Agent('my_agent')
>>> load_tools(agent_id='my_agent')
>>> agent.run('list_files', pattern='*.py')
>>> agent.propose('word_count', 'def word_count(path): return len(open(path).read().split())', 'Count words')
```

**Frontends:** Discord bot (`python discord_bot.py`) and CLI (`python cli.py`). Both need `ANTHROPIC_API_KEY`; Discord also needs `SECURECLAW_DISCORD_TOKEN` and optionally `SECURECLAW_ALLOWED_USERS`.

## Defense Layers

- **Two-layer permissions** — human approves creation, agent needs scope grant for execution
- **Auto-grant for creator** — proposing agent gets immediate access; others must be explicitly granted
- **Syntax validation** — `compile()` check before approval prompt
- **Dependency tracking** — `tool_deps()` shows which tools call which
- **Safe removal** — `remove_tool()` warns if other tools depend on it
- **Rejection feedback** — logged with reasons so agents learn from past rejections
- **Versioning** — overwritten tools archived with timestamps; `rollback_tool()` to undo
- **Rate limiting** — configurable per-user sliding window

## Status

Phase 3 complete. Self-improving agent loop tested end-to-end. Building toward multi-agent trust (Phase 4).

## Philosophy

> Logs are for auditors, proof is for users.

Zero friction by default, full transparency on demand.

## License

MIT
