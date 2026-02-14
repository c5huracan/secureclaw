from secureclaw.agent import Agent, register_skill
from secureclaw.skills import read_file
from secureclaw.permissions import SCOPES

register_skill('read_file', read_file)
agent = Agent('cli_agent')

def main():
    print("SecureClaw CLI. Commands: grant, revoke, scopes, run, quit")
    while True:
        try:
            cmd = input("> ").strip().split()
            if not cmd:
                continue
            match cmd[0]:
                case 'quit': break
                case 'scopes': print(SCOPES)
                case 'grant': agent.grant(cmd[1])
                case 'revoke': 
                    from secureclaw.permissions import store
                    store.revoke(agent.id, cmd[1])
                case 'run': print(agent.run(cmd[1], **dict(a.split('=') for a in cmd[2:])))
                case _: print("Unknown command")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
