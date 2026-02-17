from secureclaw import Agent, load_tools, list_tools

agent = Agent('cli_agent')
load_tools(agent_id='cli_agent')

def main():
    print("SecureClaw CLI. Commands: tools, grant, revoke, run, quit")
    while True:
        try:
            cmd = input("> ").strip().split()
            if not cmd: continue
            match cmd[0]:
                case 'quit': break
                case 'tools': list_tools()
                case 'grant': agent.grant(f"tool.{cmd[1]}"); print(f"✓ Granted tool.{cmd[1]}")
                case 'revoke': agent.revoke(f"tool.{cmd[1]}"); print(f"✓ Revoked tool.{cmd[1]}")
                case 'run': print(agent.run(cmd[1], **dict(a.split('=') for a in cmd[2:])))
                case _: print("Unknown command")
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__": main()
