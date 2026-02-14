from .scopes import SCOPES
from functools import wraps

class GrantStore:
    def __init__(self):
        self.grants = {}

    def grant(self, agent_id, scope):
        if scope not in SCOPES:
            raise ValueError(f"Unknown scope: {scope}")
        self.grants.setdefault(agent_id, set()).add(scope)

    def revoke(self, agent_id, scope):
        if agent_id in self.grants:
            self.grants[agent_id].discard(scope)

    def has(self, agent_id, scope):
        return scope in self.grants.get(agent_id, set())

store = GrantStore()

def require_scope(scope):
    def decorator(fn):
        @wraps(fn)
        def wrapper(agent_id, *args, **kwargs):
            if not store.has(agent_id, scope):
                raise PermissionError(f"Scope \'{scope}\' not granted")
            return fn(agent_id, *args, **kwargs)
        return wrapper
    return decorator
