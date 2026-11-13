"""مدل‌های پیکربندی سراسری و کانال‌ها."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CHANNEL_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")


class StrictModel(BaseModel):
    """هر کلید ناشناخته در YAML خطاست تا تایپوی تنظیمات بی‌صدا نماند."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ApprovalButtons(StrictModel):
    approve: str = "✅ تأیید"
    reject: str = "❌ رد"


class ApprovalSettings(StrictModel):
    required: bool = True
    # حداقل ۵ دقیقه چون کرون GitHub Actions ریزتری ندارد
    poll_interval_minutes: int = Field(default=5, ge=5, le=60)
    timeout_hours: int = Field(default=24, ge=1, le=168)
    summary_max_chars: int = Field(default=700, ge=100, le=3500)
    buttons: ApprovalButtons = Field(default_factory=ApprovalButtons)
    message_template: str

    @field_validator("message_template")
    @classmethod
    def _template_has_required_fields(cls, value: str) -> str:
        required = {"channel_name", "topic", "summary_fa"}
        found = set(re.findall(r"\{(\w+)\}", value))
        missing = required - found
        if missing:
            raise ValueError(f"قالب پیام این جایگزین‌ها را ندارد: {sorted(missing)}")
        unknown = found - {
            "channel_name",
            "topic",
            "summary_fa",
            "duration_minutes",
            "preview_url",
            "approve_label",
            "reject_label",
        }
        if unknown:
            raise ValueError(f"جایگزین ناشناخته در قالب پیام: {sorted(unknown)}")
        return value


class TelegramSettings(StrictModel):
    token_env: str = "TELEGRAM_BOT_TOKEN"
    chat_id_env: str = "TELEGRAM_CHAT_ID"
    api_base: str = "https://api.telegram.org"


class Settings(StrictModel):
    version: int = 1
    language: Literal["fa"] = "fa"
    telegram: TelegramSettings
    approval: ApprovalSettings


class ChannelTelegram(StrictModel):
    chat_id_env: str


class ResearchSettings(StrictModel):
    min_sources: int = Field(default=3, ge=1, le=20)
    topics: list[str] = Field(default_factory=list)


class ScriptSettings(StrictModel):
    target_minutes: int = Field(default=10, ge=1, le=60)
    tone: str = ""


class VoiceSettings(StrictModel):
    provider: str = "elevenlabs"
    voice_id: str = ""
    model: str = ""


class VisualsSettings(StrictModel):
    style: str = ""
    aspect_ratio: str = "16:9"
    resolution: str = "1920x1080"


class PublishSettings(StrictModel):
    platform: str = "youtube"
    privacy: Literal["private", "unlisted", "public"] = "private"
    category: str = ""


class Channel(StrictModel):
    id: str
    name: str
    enabled: bool = True
    description: str = ""
    language: str = "en"
    audience: str = ""
    telegram: ChannelTelegram
    research: ResearchSettings = Field(default_factory=ResearchSettings)
    script: ScriptSettings = Field(default_factory=ScriptSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    visuals: VisualsSettings = Field(default_factory=VisualsSettings)
    publish: PublishSettings = Field(default_factory=PublishSettings)
    secrets: dict[str, str] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def _valid_id(cls, value: str) -> str:
        if not CHANNEL_ID_PATTERN.match(value):
            raise ValueError(
                "شناسهٔ کانال باید فقط حروف کوچک انگلیسی، عدد و خط تیره باشد "
                "(۲ تا ۴۱ نویسه)"
            )
        return value

    @field_validator("telegram")
    @classmethod
    def _chat_env_upper(cls, value: ChannelTelegram) -> ChannelTelegram:
        if not value.chat_id_env.isupper() and not re.fullmatch(
            r"[A-Z0-9_]+", value.chat_id_env
        ):
            raise ValueError("نام Secret باید با حروف بزرگ و زیرخط باشد")
        return value
