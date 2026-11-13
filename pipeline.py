"""هماهنگ‌کنندهٔ خط تولید (فعلاً فقط برنامهٔ مراحل)."""

from __future__ import annotations

from .config.models import Channel
from .stages import STAGES


def plan_lines(channel: Channel) -> list[str]:
    """توضیح فارسی مراحل برای یک کانال."""
    lines = [
        f"کانال: {channel.name} ({channel.id})",
        f"تعداد مراحل: {len(STAGES)}",
    ]
    for index, stage in enumerate(STAGES, start=1):
        status = "آماده" if stage.implemented else "در فاز بعد"
        lines.append(
            f"  {index}. {stage.title_fa} — خروجی: {stage.output} — وضعیت: {status}"
        )
    return lines


def implemented_stages() -> list[str]:
    return [stage.id for stage in STAGES if stage.implemented]
