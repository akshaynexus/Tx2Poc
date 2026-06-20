from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
TX2POC_SCRIPTS = REPO_ROOT / "skills" / "tx2poc" / "scripts"


def _load_from_path(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    return module


def load_tx2poc_script(name: str) -> ModuleType:
    return _load_from_path(TX2POC_SCRIPTS / f"{name}.py", f"tx2poc_{name}")


def load_agent_skill_script(skill: str, name: str) -> ModuleType:
    path = REPO_ROOT / ".agents" / "skills" / skill / "scripts" / f"{name}.py"
    return _load_from_path(path, f"agent_{skill.replace('-', '_')}_{name}")
