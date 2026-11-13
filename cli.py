"""رابط خط فرمان: اعتبارسنجی پیکربندی، فهرست کانال‌ها، برنامهٔ مراحل، پیش‌نمایش پیام تأیید."""

from __future__ import annotations

import argparse
import sys

from .config.loader import (
    ConfigError,
    discover_channels,
    find_project_root,
    load_settings,
    resolve_channel,
)
from .pipeline import implemented_stages, plan_lines
from .stages import STAGES
from .telegram.messages import approval_chat_env, render_approval_message

SAMPLE_SUMMARY = (
    "این ویدئو داستان یک شرکت بزرگ را روایت می‌کند که در اوج رشد، با تصمیم‌های "
    "پرریسک و بدهی پنهان به فروپاشی رسید. سه نقطهٔ چرخش کلیدی بررسی می‌شود: "
    "توسعهٔ سریع بدون سود، پنهان‌کاری مالی، و لحظه‌ای که اعتماد سرمایه‌گذاران از "
    "دست رفت. درس اصلی: رشد بدون حاشیهٔ سود، فقط بدهی گران‌تر است."
)


def _ok(message: str) -> None:
    print(f"✓ {message}")


def _fail(message: str) -> None:
    print(f"✗ {message}", file=sys.stderr)


def cmd_config_validate(args: argparse.Namespace) -> int:
    root = find_project_root()
    settings = load_settings(root)
    channels = discover_channels(root)
    _ok(f"پیکربندی سراسری سالم است (نسخهٔ {settings.version}).")
    _ok(
        "بازهٔ بررسی تأیید تلگرام: هر "
        f"{settings.approval.poll_interval_minutes} دقیقه"
    )
    _ok(
        "دکمه‌ها: "
        f"{settings.approval.buttons.approve} / {settings.approval.buttons.reject}"
    )
    _ok(f"تعداد کانال‌های تعریف‌شده: {len(channels)}")
    for channel in channels:
        flag = "فعال" if channel.enabled else "غیرفعال"
        _ok(f"کانال {channel.id} ({channel.name}) — {flag}")
    active = [c for c in channels if c.enabled]
    if not active:
        _fail("هیچ کانال فعالی وجود ندارد.")
        return 1
    _ok(f"کانال‌های فعال: {', '.join(c.id for c in active)}")
    return 0


def cmd_channels_list(args: argparse.Namespace) -> int:
    channels = discover_channels(find_project_root())
    if not channels:
        _fail("هیچ کانالی تعریف نشده است.")
        return 1
    print("شناسه | نام | وضعیت | Secret چت")
    for channel in channels:
        print(
            f"{channel.id} | {channel.name} | "
            f"{'فعال' if channel.enabled else 'غیرفعال'} | "
            f"{channel.telegram.chat_id_env}"
        )
    return 0


def cmd_pipeline_plan(args: argparse.Namespace) -> int:
    channel = resolve_channel(args.channel, find_project_root())
    for line in plan_lines(channel):
        print(line)
    ready = implemented_stages()
    print("مراحل پیاده‌سازی‌شده: " + (", ".join(ready) if ready else "هیچ‌کدام"))
    print(f"کل مراحل تعریف‌شده: {len(STAGES)}")
    return 0


def cmd_approval_preview(args: argparse.Namespace) -> int:
    root = find_project_root()
    settings = load_settings(root)
    channel = resolve_channel(args.channel, root)
    text = render_approval_message(
        settings,
        channel,
        topic="سقوط امپراتوری: نمونهٔ نمایشی",
        summary_fa=SAMPLE_SUMMARY,
        duration_minutes=channel.script.target_minutes,
        preview_url="https://example.com/preview.mp4",
    )
    print(text)
    print("\n---")
    print(f"Secret چت این کانال: {approval_chat_env(channel, settings)}")
    print(
        "دکمه‌های شیشه‌ای: "
        f"{settings.approval.buttons.approve} | {settings.approval.buttons.reject}"
    )
    return 0


def cmd_approval_poll(args: argparse.Namespace) -> int:
    """جای‌نگهدار: بررسی پاسخ‌های تلگرام در فاز ۳ پیاده‌سازی می‌شود."""
    root = find_project_root()
    settings = load_settings(root)
    channel = resolve_channel(args.channel, root)
    print(
        f"[بررسی تأیید] کانال {channel.id} — بازهٔ {settings.approval.poll_interval_minutes} دقیقه."
    )
    print("[بررسی تأیید] این مرحله هنوز پیاده‌سازی نشده است (فاز ۳).")
    print("[بررسی تأیید] بدون خطا خارج شد تا زمان‌بندی Actions خراب نشود.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autopsy",
        description="خط تولید خودکار ویدئو — ساختار چندکاناله",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("config", help="مدیریت پیکربندی")
    config_sub = config_parser.add_subparsers(dest="config_command", required=True)
    validate = config_sub.add_parser("validate", help="اعتبارسنجی پیکربندی")
    validate.set_defaults(func=cmd_config_validate)

    channels_parser = subparsers.add_parser("channels", help="مدیریت کانال‌ها")
    channels_sub = channels_parser.add_subparsers(dest="channels_command", required=True)
    listing = channels_sub.add_parser("list", help="فهرست کانال‌ها")
    listing.set_defaults(func=cmd_channels_list)

    pipeline_parser = subparsers.add_parser("pipeline", help="خط تولید")
    pipeline_sub = pipeline_parser.add_subparsers(dest="pipeline_command", required=True)
    plan = pipeline_sub.add_parser("plan", help="نمایش مراحل")
    plan.add_argument("--channel", default=None)
    plan.set_defaults(func=cmd_pipeline_plan)

    approval_parser = subparsers.add_parser("approval", help="تأیید تلگرام")
    approval_sub = approval_parser.add_subparsers(dest="approval_command", required=True)
    preview = approval_sub.add_parser("preview", help="پیش‌نمایش پیام تأیید")
    preview.add_argument("--channel", default=None)
    preview.set_defaults(func=cmd_approval_preview)
    poll = approval_sub.add_parser("poll", help="بررسی پاسخ‌ها (فاز ۳)")
    poll.add_argument("--channel", default=None)
    poll.set_defaults(func=cmd_approval_poll)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ConfigError as exc:
        _fail(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
