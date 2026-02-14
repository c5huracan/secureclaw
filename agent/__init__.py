from secureclaw.permissions import store

SKILL_REGISTRY = {}

def register_skill(name, fn):
    SKILL_REGISTRY[name] = fn

class Agent:
    def __init__(self, agent_id):
        self.id = agent_id

    def grant(self, scope):
        store.grant(self.id, scope)

    def run(self, skill_name, **kwargs):
        if skill_name not in SKILL_REGISTRY:
            raise ValueError(f"Unknown skill: {skill_name}")
        return SKILL_REGISTRY[skill_name](self.id, **kwargs)
