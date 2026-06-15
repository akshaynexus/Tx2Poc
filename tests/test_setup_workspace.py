from __future__ import annotations

from _load_skill_module import load_tx2poc_script


setup_workspace = load_tx2poc_script("setup_workspace")


def test_setup_workspace_copies_helpers_and_writes_config(tmp_path) -> None:
    copied = setup_workspace.copy_helpers(tmp_path)

    assert sorted(path.rsplit("/", 1)[-1] for path in copied) == sorted(setup_workspace.HELPERS)
    for helper in setup_workspace.HELPERS:
        assert (tmp_path / "cases" / helper).exists()

    foundry_asset = setup_workspace.FOUNDRY_ASSET_DIR / "foundry.toml"
    remappings_asset = setup_workspace.FOUNDRY_ASSET_DIR / "remappings.txt"

    assert setup_workspace.copy_if_missing(foundry_asset, tmp_path / "foundry.toml")
    assert not setup_workspace.copy_if_missing(foundry_asset, tmp_path / "foundry.toml")
    assert (tmp_path / "foundry.toml").read_text(encoding="utf-8") == foundry_asset.read_text(encoding="utf-8")

    assert setup_workspace.ensure_remappings(remappings_asset, tmp_path / "remappings.txt")
    assert not setup_workspace.ensure_remappings(remappings_asset, tmp_path / "remappings.txt")
    assert (tmp_path / "remappings.txt").read_text(encoding="utf-8") == remappings_asset.read_text(encoding="utf-8")

    assert setup_workspace.ensure_forge_std(tmp_path, skip_install=True) == "missing, install skipped"
