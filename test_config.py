"""آزمون پیکربندی چندکاناله."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from autopsy.config.loader import (
    ConfigError,
    discover_channels,
    load_channel,
    load_settings,
    resolve_channel,
)

ROOT = Path(__file__).resolve().parents[1]


def test_settings_load_with_five_minute_polling() -> None:
    settings = load_settings(ROOT)
    assert settings.approval.poll_interval_minutes == 5
    assert settings.approval.buttons.approve == "✅ تأیید"
    assert settings.approval.buttons.reject == "❌ رد"


def test_only_empire_autopsy_exists_and_is_enabled() -> None:
    channels = discover_channels(ROOT)
    assert [c.id for c in channels] == ["empire-autopsy"]
    assert channels[0].enabled is True
    assert resolve_channel(None, ROOT).id == "empire-autopsy"


def test_template_channel_is_ignored() -> None:
    assert (ROOT / "channels" / "_template" / "channel.yaml").is_file()
    assert all(not c.id.startswith("_") for c in discover_channels(ROOT))


def test_unknown_channel_raises() -> None:
    with pytest.raises(ConfigError):
        load_channel("does-not-exist", ROOT)


def test_disabled_channel_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    shutil.copytree(ROOT / "config", root / "config")
    shutil.copytree(ROOT / "channels" / "empire-autopsy", root / "channels" / "empire-autopsy")
    channel_file = root / "channels" / "empire-autopsy" / "channel.yaml"
    channel_file.write_text(
        channel_file.read_text(encoding="utf-8").replace(
            "enabled: true", "enabled: false"
        ),
        encoding="utf-8",
    )
    assert discover_channels(root)[0].enabled is False
    with pytest.raises(ConfigError):
        resolve_channel(None, root)


def test_unknown_key_in_channel_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    shutil.copytree(ROOT / "config", root / "config")
    shutil.copytree(ROOT / "channels" / "empire-autopsy", root / "channels" / "empire-autopsy")
    channel_file = root / "channels" / "empire-autopsy" / "channel.yaml"
    channel_file.write_text(
        channel_file.read_text(encoding="utf-8") + "\ntypo_key: 1\n", encoding="utf-8"
    )
    with pytest.raises(ConfigError):
        discover_channels(root)


def test_channel_dir_name_must_match_id(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    shutil.copytree(ROOT / "config", root / "config")
    shutil.copytree(ROOT / "channels" / "empire-autopsy", root / "channels" / "other-name")
    with pytest.raises(ConfigError):
        discover_channels(root)
