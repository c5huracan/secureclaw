# SecureClaw for SolveIt - Add this to your CRAFT.ipynb

from dialoghelper import find_msgs, read_msg, add_msg, update_msg

# Scopes
DIALOG_SCOPES = {'dialog.read', 'dialog.write'}

# Grant store
_dialog_grants = set()

def grant_dialog(scope):
    if scope not in DIALOG_SCOPES:
        raise ValueError(f"Unknown scope: {scope}")
    _dialog_grants.add(scope)
    print(f"✓ Granted {scope}")

def revoke_dialog(scope):
    _dialog_grants.discard(scope)
    print(f"✓ Revoked {scope}")

def dialog_grants():
    return _dialog_grants or "none"

# Wrapped dialoghelper functions
def safe_find_msgs(*args, **kwargs):
    """find_msgs with scope check."""
    if 'dialog.read' not in _dialog_grants:
        raise PermissionError("🚫 Scope 'dialog.read' not granted. Run: grant_dialog('dialog.read')")
    return find_msgs(*args, **kwargs)

def safe_read_msg(*args, **kwargs):
    """read_msg with scope check."""
    if 'dialog.read' not in _dialog_grants:
        raise PermissionError("🚫 Scope 'dialog.read' not granted. Run: grant_dialog('dialog.read')")
    return read_msg(*args, **kwargs)

def safe_add_msg(*args, **kwargs):
    """add_msg with scope check."""
    if 'dialog.write' not in _dialog_grants:
        raise PermissionError("🚫 Scope 'dialog.write' not granted. Run: grant_dialog('dialog.write')")
    return add_msg(*args, **kwargs)

def safe_update_msg(*args, **kwargs):
    """update_msg with scope check."""
    if 'dialog.write' not in _dialog_grants:
        raise PermissionError("🚫 Scope 'dialog.write' not granted. Run: grant_dialog('dialog.write')")
    return update_msg(*args, **kwargs)
