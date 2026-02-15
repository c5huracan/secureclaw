import os
import discord
from claudette import Chat
from secureclaw.agent import Agent, register_skill, SKILL_REGISTRY
from secureclaw.skills import read_file
from secureclaw.permissions import SCOPES, store
from secureclaw.permissions.ratelimit import RateLimiter

register_skill('read_file', read_file)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

agents = {}
chats = {}
limiter = RateLimiter(max_requests=10, window_seconds=60)

# Load allowed users from env var (empty = allow all)
ALLOWED_USERS = set(filter(None, os.environ.get("SECURECLAW_ALLOWED_USERS", "").split(",")))

def get_agent(user_id):
    if user_id not in agents:
        agents[user_id] = Agent(str(user_id))
    return agents[user_id]

def read_file_tool(path: str) -> str:
    """Read a file at the given path and return its contents."""
    return open(path).read()

@client.event
async def on_ready():
    print(f"SecureClaw connected as {client.user}")
    if ALLOWED_USERS:
        print(f"Allowed users: {ALLOWED_USERS}")
    else:
        print("No allowlist set — all users permitted")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text = message.content.strip()
    if not text:
        return

    uid = str(message.author.id)

    # Allowlist check (if set)
    if ALLOWED_USERS and uid not in ALLOWED_USERS:
        return  # silently ignore

    # Rate limit check
    if not limiter.allow(uid):
        await message.channel.send("⏳ Rate limited. Try again in a minute.")
        return

    agent = get_agent(uid)

    if text.startswith('!'):
        cmd = text.split()
        try:
            match cmd[0]:
                case '!scopes': await message.channel.send(f"Available: {SCOPES}")
                case '!grant':
                    agent.grant(cmd[1])
                    await message.channel.send(f"✓ Granted {cmd[1]}")
                case '!revoke':
                    store.revoke(agent.id, cmd[1])
                    await message.channel.send(f"✓ Revoked {cmd[1]}")
                case '!grants':
                    granted = store.grants.get(agent.id, set())
                    await message.channel.send(f"Your grants: {granted or 'none'}")
        except Exception as e:
            await message.channel.send(f"Error: {e}")
        return

    try:
        if uid not in chats:
            chats[uid] = Chat(model="claude-sonnet-4-20250514", tools=[read_file_tool])
        chat = chats[uid]
        response = chat(text)

        if response.stop_reason == 'tool_use':
            if not store.has(agent.id, 'filesystem.read'):
                await message.channel.send("🚫 Scope 'filesystem.read' not granted. Use !grant filesystem.read")
                return
            response = chat()

        text_content = [c.text for c in response.content if hasattr(c, 'text')]
        await message.channel.send(text_content[0][:1900] if text_content else "No response")
    except Exception as e:
        await message.channel.send(f"Error: {e}")

client.run(os.environ["SECURECLAW_DISCORD_TOKEN"])
