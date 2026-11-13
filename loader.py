"""بارگذاری و اعتبارسنجی پیکربندی سراسری و کانال‌ها."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import Channel, Settings

SETTINGS_RELATIVE_PATH = Path("config") / "settings.yaml"
CHANNELS_DIRNAME = "channels"
CHANNEL_FILENAME = "channel.yaml"


class ConfigError(Exception):
    """خطای خواندن یا اعتبارسنجی پیکربندی."""


def find_project_root(start: Path | None = None) -> Path:
    """ریشهٔ پروژه را از روی وجود config/settings.yaml پیدا می‌کند."""
    origin = Path(start).resolve() if start is not None else Path(__file__).resolve()
    current = origin if origin.is_dir() else origin.parent
    for candidate in (current, *current.parents):
        if (candidate / SETTINGS_RELATIVE_PATH).is_file():
            return candidate
    raise ConfigError(
        f"ریشهٔ پروژه پیدا نشد: هیچ‌کدام از والدها فایل {SETTINGS_RELATIVE_PATH} را ندارد"
    )


def _read_yaml(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"خواندن {path} ممکن نشد: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigError(f"YAML نامعتبر در {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path} باید یک نگاشت (key/value) باشد")
    return data


def load_settings(root: Path | None = None) -> Settings:
    base = find_project_root(root)
    path = base / SETTINGS_RELATIVE_PATH
    data = _read_yaml(path)
    try:
        return Settings.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"پیکربندی سراسری نامعتبر است ({path}):\n{exc}") from exc


def _channel_files(root: Path) -> list[Path]:
    channels_dir = root / CHANNELS_DIRNAME
    if not channels_dir.is_dir():
        raise ConfigError(f"پوشهٔ کانال‌ها پیدا نشد: {channels_dir}")
    files = []
    for child in sorted(channels_dir.iterdir()):
        if not child.is_dir() or child.name.startswith(("_", ".")):
            continue
        channel_file = child / CHANNEL_FILENAME
        if channel_file.is_file():
            files.append(channel_file)
    return files


def discover_channels(root: Path | None = None) -> list[Channel]:
    base = find_project_root(root)
    channels: list[Channel] = []
    for path in _channel_files(base):
        data = _read_yaml(path)
        try:
            channel = Channel.model_validate(data)
        except ValidationError as exc:
            raise ConfigError(f"کانال نامعتبر در {path}:\n{exc}") from exc
        if channel.id != path.parent.name:
            raise ConfigError(
                f"شناسهٔ کانال («{channel.id}») با نام پوشه («{path.parent.name}») یکی نیست"
            )
        channels.append(channel)

    duplicate_ids = {c.id for c in channels if [x.id for x in channels].count(c.id) > 1}
    if duplicate_ids:
        raise ConfigError(f"شناسهٔ تکراری کانال: {sorted(duplicate_ids)}")

    chat_envs = [c.telegram.chat_id_env for c in channels]
    duplicate_envs = {env for env in chat_envs if chat_envs.count(env) > 1}
    if duplicate_envs:
        raise ConfigError(
            "دو کانال نباید به یک Secret چت تلگرام اشاره کنند: "
            f"{sorted(duplicate_envs)}"
        )
    return channels


def enabled_channels(root: Path | None = None) -> list[Channel]:
    return [c for c in discover_channels(root) if c.enabled]


def load_channel(channel_id: str, root: Path | None = None) -> Channel:
    for channel in discover_channels(root):
        if channel.id == channel_id:
            return channel
    known = ", ".join(c.id for c in discover_channels(root)) or "—"
    raise ConfigError(f"کانال «{channel_id}» پیدا نشد. کانال‌های موجود: {known}")


def resolve_channel(
    channel_id: str | None = None, root: Path | None = None
) -> Channel:
    """کانال موردنظر برای اجرا را برمی‌گرداند و فعال‌بودنش را بررسی می‌کند."""
    if channel_id:
        channel = load_channel(channel_id, root)
    else:
        active = enabled_channels(root)
        if not active:
            raise ConfigError("هیچ کانال فعالی وجود ندارد (enabled: true نیست)")
        if len(active) > 1:
            names = ", ".join(c.id for c in active)
            raise ConfigError(
                "بیش از یک کانال فعال است؛ با --channel مشخص کنید: " + names
            )
        channel = active[0]
    if not channel.enabled:
        raise ConfigError(f"کانال «{channel.id}» غیرفعال است (enabled: false)")
    return channel
