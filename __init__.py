"""ارتباط با تلگرام.

در فاز ۳ تکمیل می‌شود: ارسال پیام با دکمه‌های شیشه‌ای ✅ تأیید / ❌ رد،
و بررسی پاسخ‌ها با getUpdates هر ۵ دقیقه (بدون Cloudflare).
"""

from .messages import (
    approval_chat_env,
    normalize_summary,
    render_approval_message,
)

__all__ = [
    "approval_chat_env",
    "normalize_summary",
    "render_approval_message",
]
