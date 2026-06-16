# Workspace Setup

Use this reference only when the workspace is fresh, missing helpers/config, missing `forge-std`, or Forge fails because imports/config are absent.

Run from the workspace root:

```bash
python "$SKILL_DIR/scripts/setup_workspace.py"
```

The script:

- creates `cases/` when missing.
- copies missing shared helpers into `cases/`: `basetest.sol`, `interface.sol`, `StableMath.sol`, and `tokenhelper.sol`.
- writes missing `foundry.toml` from bundled assets.
- appends missing remappings from bundled assets.
- installs current `forge-std` only when `lib/forge-std/src/Test.sol` is missing.

Options:

```bash
python "$SKILL_DIR/scripts/setup_workspace.py" --skip-forge-std
python "$SKILL_DIR/scripts/setup_workspace.py" --forge-std-ref <tag-or-commit>
```

Use `--skip-forge-std` when network access should be avoided or `forge-std` will be provided separately. Use `--forge-std-ref` only when the user explicitly asks for a pinned `forge-std` dependency.

Do not reinstall or overwrite existing helpers/config when they already exist; the script is intended to add missing pieces only.
