"""ساخت پیام تأیید تلگرام (فارسی) برای هر کانال."""

from __future__ import annotations

import re

from ..config.models import Channel, Settings

EMPTY_SUMMARY_FALLBACK = "خلاصه‌ای ثبت نشده است."
UNKNOWN_DURATION = "؟"


def normalize_summary(text: str, max_chars: int) -> str:
    """فاصله‌ها را یکدست و خلاصه را به سقف کاراکتر محدود می‌کند."""
    collapsed = re.sub(r"\s+", " ", (text or "").strip())
    if not collapsed:
        return EMPTY_SUMMARY_FALLBACK
    if len(collapsed) <= max_chars:
        return collapsed
    return collapsed[: max_chars - 1].rstrip() + "…"


def approval_chat_env(channel: Channel, settings: Settings) -> str:
    """نام Secretی که شناسهٔ چت این کانال در آن است."""
    return channel.telegram.chat_id_env or settings.telegram.chat_id_env


def render_approval_message(
    settings: Settings,
    channel: Channel,
    *,
    topic: str,
    summary_fa: str,
    duration_minutes: int | None = None,
    preview_url: str | None = None,
) -> str:
    template = settings.approval.message_template
    return template.format(
        channel_name=channel.name,
        topic=topic.strip() or "—",
        summary_fa=normalize_summary(summary_fa, settings.approval.summary_max_chars),
        duration_minutes=duration_minutes
        if duration_minutes is not None
        else UNKNOWN_DURATION,
        preview_url=preview_url or "—",
        approve_label=settings.approval.buttons.approve,
        reject_label=settings.approval.buttons.reject,
    )
