import os
from pathlib import Path
from secureclaw.permissions import require_scope

@require_scope('filesystem.list')
def list_files(agent_id, path: str) -> list:
    """List files in a directory."""
    return os.listdir(path)

@require_scope('filesystem.read')
def read_file(agent_id, path):
    return Path(path).read_text()

@require_scope('network.http')
def http_get(agent_id, url: str) -> str:
    """Fetch content from a URL."""
    import httpx
    return httpx.get(url).text
