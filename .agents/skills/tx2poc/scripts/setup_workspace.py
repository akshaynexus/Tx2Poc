from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
FOUNDRY_ASSET_DIR = SKILL_ROOT / "assets" / "foundry-helpers"

HELPERS = ("basetest.sol", "interface.sol", "StableMath.sol", "tokenhelper.sol")
FORGE_STD_REF = "3353993420c6e488a2914ce02d88174e80ad80f8"

def copy_if_missing(source: Path, target: Path) -> bool:
    if not source.exists():
        raise RuntimeError(f"missing bundled asset: {source}")
    if target.exists():
        return False
    shutil.copy2(source, target)
    return True


def ensure_remappings(source: Path, target: Path) -> bool:
    if not source.exists():
        raise RuntimeError(f"missing bundled asset: {source}")
    if not target.exists():
        shutil.copy2(source, target)
        return True

    existing = target.read_text(encoding="utf-8").splitlines()
    wanted = [line for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    missing = [line for line in wanted if line not in existing]
    if not missing:
        return False

    suffix = "" if existing and existing[-1] == "" else "\n"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(suffix + "\n".join(missing) + "\n")
    return True


def copy_helpers(workspace: Path) -> list[str]:
    cases = workspace / "cases"
    cases.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for name in HELPERS:
        source = FOUNDRY_ASSET_DIR / name
        target = cases / name
        if not source.exists():
            raise RuntimeError(f"missing bundled helper: {source}")
        if not target.exists():
            shutil.copy2(source, target)
            copied.append(str(target))
    return copied


def ensure_forge_std(workspace: Path, skip_install: bool) -> str:
    test_sol = workspace / "lib" / "forge-std" / "src" / "Test.sol"
    if test_sol.exists():
        return "already present"
    if skip_install:
        return "missing, install skipped"

    command = [
        "forge",
        "install",
        "--root",
        str(workspace),
        f"foundry-rs/forge-std@{FORGE_STD_REF}",
        "--no-git",
    ]
    try:
        subprocess.run(command, cwd=workspace, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("forge is not installed or not on PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("forge-std install failed") from exc

    if not test_sol.exists():
        raise RuntimeError(f"forge-std install finished but {test_sol} is missing")
    return "installed"


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a workspace for tx2poc output.")
    parser.add_argument("--workspace-root", default=".", help="Workspace/repo root to prepare")
    parser.add_argument("--skip-forge-std", action="store_true", help="Do not install missing forge-std")
    args = parser.parse_args()

    workspace = Path(args.workspace_root).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    copied = copy_helpers(workspace)
    wrote_foundry = copy_if_missing(FOUNDRY_ASSET_DIR / "foundry.toml", workspace / "foundry.toml")
    updated_remappings = ensure_remappings(FOUNDRY_ASSET_DIR / "remappings.txt", workspace / "remappings.txt")
    forge_std_status = ensure_forge_std(workspace, args.skip_forge_std)

    print(f"workspace: {workspace}")
    print(f"helpers copied: {len(copied)}")
    print(f"foundry.toml written: {str(wrote_foundry).lower()}")
    print(f"remappings updated: {str(updated_remappings).lower()}")
    print(f"forge-std: {forge_std_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
