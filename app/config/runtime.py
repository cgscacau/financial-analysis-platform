"""Runtime helpers (paths, environment)."""
from __future__ import annotations
import sys
from pathlib import Path


def ensure_project_root_on_path(current_file: str) -> Path:
    root = Path(current_file).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root
