import os, discord
from claudette import Chat
from secureclaw import Agent, load_tools, RateLimiter, SKILL_REGISTRY, store

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

agents, chats = {}, {}
limiter = RateLimiter(max_requests=10, window_seconds=60)
ALLOWED_USERS = set(filter(None, os.environ.get("SECURECLAW_ALLOWED_USERS", "").split(",")))

def get_agent(user_id):
    if user_id not in agents: agents[user_id] = Agent(str(user_id))
    return agents[user_id]

@client.event
async def on_ready():
    load_tools()
    print(f"SecureClaw connected as {client.user}")
    if ALLOWED_USERS: print(f"Allowed users: {ALLOWED_USERS}")

@client.event
async def on_message(message):
    if message.author == client.user: return
    text = message.content.strip()
    if not text: return
    uid = str(message.author.id)
    if ALLOWED_USERS and uid not in ALLOWED_USERS: return
    if not limiter.allow(uid):
        await message.channel.send("⏳ Rate limited. Try again in a minute.")
        return
    agent = get_agent(uid)
    if text.startswith("!"):
        cmd = text.split()
        try:
            match cmd[0]:
                case "!scopes": await message.channel.send(f"Available: {list(SKILL_REGISTRY.keys())}")
                case "!grant": agent.grant(f"tool.{cmd[1]}"); chats.pop(uid, None); await message.channel.send(f"✓ Granted tool.{cmd[1]}")
                case "!revoke": agent.revoke(f"tool.{cmd[1]}"); chats.pop(uid, None); await message.channel.send(f"✓ Revoked tool.{cmd[1]}")
                case "!grants": await message.channel.send(f"Your grants: {store.grants.get(uid, set()) or 'none'}")
                case "!audit":
                    hist = store.history(uid)
                    msg = "\n".join(f"{a['ts'][:19]} {a['action']} {a['scope']}" for a in hist) if hist else "No history"
                    await message.channel.send(msg)
        except Exception as e: await message.channel.send(f"Error: {e}")
        return
    try:
        tools = [v for k,v in SKILL_REGISTRY.items() if agent.has(f"tool.{k}")]
        if uid not in chats: chats[uid] = Chat(model="claude-sonnet-4-20250514", tools=tools)
        response = chats[uid](text)
        if response.stop_reason == "tool_use":
            name = response.content[0].name if hasattr(response.content[0], "name") else None
            if name and not agent.has(f"tool.{name}"):
                await message.channel.send(f"🚫 Scope 'tool.{name}' not granted. Use !grant {name}")
                return
            response = chats[uid]()
        text_content = [c.text for c in response.content if hasattr(c, "text")]
        await message.channel.send(text_content[0][:1900] if text_content else "No response")
    except Exception as e: await message.channel.send(f"Error: {e}")

client.run(os.environ["SECURECLAW_DISCORD_TOKEN"])
