import json, ast
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from functools import wraps
import time

TOOL_STORE = Path('tools.json')
REJECTION_LOG = Path('rejections.json')
AUDIT_LOG = Path('audit.json')
SKILL_REGISTRY = {}
SCOPES = set()

def _read_store():
    if TOOL_STORE.exists(): return json.loads(TOOL_STORE.read_text())
    return {}

def _write_store(store): TOOL_STORE.write_text(json.dumps(store, indent=2))

def _read_rejections():
    if REJECTION_LOG.exists(): return json.loads(REJECTION_LOG.read_text())
    return []

class GrantStore:
    "In-memory permission store for agent grants with audit trail"
    def __init__(self):
        self.audit = json.loads(AUDIT_LOG.read_text()) if AUDIT_LOG.exists() else []
        self.grants = {}
        for a in self.audit:
            s = self.grants.setdefault(a['agent_id'], set())
            if a['action'] == 'grant': s.add(a['scope'])
            elif a['action'] == 'revoke': s.discard(a['scope'])
    def grant(self, agent_id, scope):
        if scope not in SCOPES: raise PermissionError(f"Unknown scope: {scope}")
        self.grants.setdefault(agent_id, set()).add(scope)
        self.audit.append(dict(action='grant', agent_id=agent_id, scope=scope, ts=str(datetime.now()))); AUDIT_LOG.write_text(json.dumps(self.audit, indent=2))
        if scope.startswith('tool.'):
            for dep in tool_deps(scope[5:]):
                dep_scope = f"tool.{dep}"
                if dep_scope in SCOPES and dep_scope not in self.grants.get(agent_id, set()): self.grant(agent_id, dep_scope)
    def revoke(self, agent_id, scope):
        self.grants.get(agent_id, set()).discard(scope)
        self.audit.append(dict(action='revoke', agent_id=agent_id, scope=scope, ts=str(datetime.now()))); AUDIT_LOG.write_text(json.dumps(self.audit, indent=2))
    def has(self, agent_id, scope): return scope in self.grants.get(agent_id, set())
    def history(self, agent_id=None):
        if agent_id: return [a for a in self.audit if a['agent_id'] == agent_id]
        return self.audit

store = GrantStore()

def require_scope(scope):
    "Decorator that checks scope before execution"
    def decorator(fn):
        @wraps(fn)
        def wrapper(agent_id, *args, **kwargs):
            if not store.has(agent_id, scope): raise PermissionError(f"Scope '{scope}' not granted")
            return fn(agent_id, *args, **kwargs)
        return wrapper
    return decorator

class RateLimiter:
    "Sliding window rate limiter per user"
    def __init__(self, max_requests=5, window_seconds=60): self.max_requests, self.window, self.requests = max_requests, window_seconds, defaultdict(list)
    def allow(self, user_id):
        now = time.time()
        self.requests[user_id] = [t for t in self.requests[user_id] if now - t < self.window]
        if len(self.requests[user_id]) >= self.max_requests: return False
        self.requests[user_id].append(now)
        return True

def list_tools():
    "Show all saved tools with descriptions"
    store = _read_store()
    if not store: return "No tools saved."
    for name, t in store.items(): print(f"  {name:20s} — {t['description']}")
    return f"\n{len(store)} tools total"

def tool_deps(name=None):
    "Show dependencies between tools"
    s = _read_store()
    names = set(s.keys())
    deps = {}
    for n, t in s.items():
        tree = ast.parse(t['code'])
        calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in names}
        calls.discard(n)
        if calls: deps[n] = calls
    if name: return deps.get(name, set())
    return deps

def past_rejections(name=None):
    "Get past rejections, optionally filtered by tool name"
    r = _read_rejections()
    if name: r = [x for x in r if x['name'] == name]
    return r

def load_tools(agent_id=None):
    "Reload all saved tools from disk into SKILL_REGISTRY, optionally auto-granting to agent"
    import importlib
    s = _read_store()
    lines = ['from pathlib import Path', 'import ast, keyword']
    for tool in s.values(): lines.append(tool['code'])
    Path('_tools_gen.py').write_text('\n\n'.join(lines))
    mod = importlib.import_module('_tools_gen')
    importlib.reload(mod)
    for name in s:
        SKILL_REGISTRY[name] = getattr(mod, name)
        SCOPES.add(f"tool.{name}")
        if agent_id: store.grant(agent_id, f"tool.{name}")
    return f"Loaded {len(s)} tools: {', '.join(s.keys())}"

def propose_tool(name, code, description, agent_id=None):
    "Propose a new tool for human approval"
    try: compile(code, f'<tool:{name}>', 'exec')
    except SyntaxError as e: return f"❌ {name} has syntax error: {e}"
    s = _read_store()
    exists = name in s
    label = "TOOL PROPOSAL (overwrite)" if exists else "TOOL PROPOSAL"
    prompt = f"\n{'='*50}\n{label}: {name}\n{'='*50}\n{description}\n\nCode:\n{code}\n{'='*50}\nApprove? (y/n): "
    if input(prompt).strip().lower() != 'y':
        reason = input("Reason for rejection (or enter to skip): ").strip()
        rejections = _read_rejections()
        rejections.append(dict(name=name, description=description, code=code, reason=reason, ts=str(datetime.now())))
        REJECTION_LOG.write_text(json.dumps(rejections, indent=2))
        return f"❌ {name} rejected" + (f": {reason}" if reason else "")
    exec(code, globals())
    SKILL_REGISTRY[name] = globals()[name]
    SCOPES.add(f"tool.{name}")
    if agent_id: store.grant(agent_id, f"tool.{name}")
    if exists:
        old = s[name]
        old.setdefault('versions', []).append(dict(code=old['code'], description=old['description'], ts=str(datetime.now())))
        s[name] = dict(code=code, description=description, versions=old['versions'])
    else:
        s[name] = dict(code=code, description=description, created_by=agent_id, created_at=str(datetime.now()))
    _write_store(s)
    v = len(s[name].get('versions', []))
    return f"✅ {name} approved (v{v+1}), saved to disk"

def remove_tool(name):
    "Remove a tool, warning if others depend on it"
    s = _read_store()
    if name not in s: return f"❌ {name} not found"
    dependents = [n for n, d in tool_deps().items() if name in d]
    if dependents:
        if input(f"⚠️ {name} is used by: {', '.join(dependents)}. Remove anyway? (y/n): ").strip().lower() != 'y':
            return f"❌ {name} removal cancelled"
    del s[name]
    _write_store(s)
    SKILL_REGISTRY.pop(name, None)
    SCOPES.discard(f"tool.{name}")
    return f"✅ {name} removed"

def rollback_tool(name, version=None):
    "Roll back a tool to a previous version"
    s = _read_store()
    if name not in s: return f"❌ {name} not found"
    versions = s[name].get('versions', [])
    if not versions: return f"❌ {name} has no previous versions"
    if version is None: version = len(versions)
    v = versions[version - 1]
    exec(v['code'], globals())
    SKILL_REGISTRY[name] = globals()[name]
    versions.append(dict(code=s[name]['code'], description=s[name]['description'], ts=str(datetime.now())))
    s[name] = dict(code=v['code'], description=v['description'], versions=versions)
    _write_store(s)
    return f"✅ {name} rolled back to v{version} (now v{len(versions)+1})"

class Agent:
    "A permission-scoped agent"
    def __init__(self, agent_id): self.id = agent_id
    def grant(self, scope): store.grant(self.id, scope)
    def revoke(self, scope): store.revoke(self.id, scope)
    def has(self, scope): return store.has(self.id, scope)
    def run(self, name, **kwargs):
        if name not in SKILL_REGISTRY: raise ValueError(f"Unknown skill: {name}")
        if not self.has(f"tool.{name}"): raise PermissionError(f"Scope 'tool.{name}' not granted")
        return SKILL_REGISTRY[name](**kwargs)
    def propose(self, name, code, description): return propose_tool(name, code, description, agent_id=self.id)
