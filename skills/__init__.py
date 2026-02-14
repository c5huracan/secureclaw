from pathlib import Path
from secureclaw.permissions import require_scope

@require_scope('filesystem.read')
def read_file(agent_id, path):
    return Path(path).read_text()
