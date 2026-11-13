"""آزمون ساخت پیام تأیید فارسی."""

from __future__ import annotations

from pathlib import Path

from autopsy.config.loader import load_channel, load_settings
from autopsy.telegram.messages import (
    EMPTY_SUMMARY_FALLBACK,
    normalize_summary,
    render_approval_message,
)

ROOT = Path(__file__).resolve().parents[1]


def test_message_contains_persian_labels_and_summary() -> None:
    settings = load_settings(ROOT)
    channel = load_channel("empire-autopsy", ROOT)
    text = render_approval_message(
        settings,
        channel,
        topic="سقوط برند نمونه",
        summary_fa="این یک خلاصهٔ فارسی کوتاه است.",
        duration_minutes=9,
        preview_url="https://example.com/v.mp4",
    )
    assert "Empire Autopsy" in text
    assert "سقوط برند نمونه" in text
    assert "این یک خلاصهٔ فارسی کوتاه است." in text
    assert "✅ تأیید" in text
    assert "❌ رد" in text
    assert "9" in text


def test_summary_is_truncated_to_limit() -> None:
    settings = load_settings(ROOT)
    max_chars = settings.approval.summary_max_chars
    long_text = "الف " * (max_chars * 2)
    result = normalize_summary(long_text, max_chars)
    assert len(result) <= max_chars
    assert result.endswith("…")


def test_empty_summary_uses_fallback() -> None:
    assert normalize_summary("   ", 100) == EMPTY_SUMMARY_FALLBACK


def test_message_without_optional_fields() -> None:
    settings = load_settings(ROOT)
    channel = load_channel("empire-autopsy", ROOT)
    text = render_approval_message(settings, channel, topic="", summary_fa="")
    assert EMPTY_SUMMARY_FALLBACK in text
    assert "—" in text
