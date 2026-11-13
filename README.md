# خط تولید خودکار ویدئو — ساختار چندکاناله

اسکلت پروژه برای تولید خودکار ویدئو، با تأیید تلگرام و اجرای GitHub Actions.
کانال فعال فعلی: **Empire Autopsy**. ساختار چندکاناله آماده است ولی کانال دوم الان ساخته نمی‌شود.

## تصمیم‌های قطعی فاز ۲

1. مخزن گیت‌هاب **عمومی** است. دقیقه‌های Actions نامحدود است و همهٔ کلیدها **فقط** در
   `Settings → Secrets and variables → Actions` نگهداری می‌شوند؛ هیچ کلیدی در کد یا YAML نیست.
2. فقط یک کانال: `empire-autopsy`. برای کانال دوم فقط پوشه را از `channels/_template` کپی کنید.
3. تأیید تلگرام با **بررسی هر ۵ دقیقه** و بدون Cloudflare. دکمه‌ها فارسی‌اند
   (`✅ تأیید` / `❌ رد`) و همراه پیام، یک **خلاصهٔ فارسی** از محتوای ویدئو ارسال می‌شود.

## ساختار

```
config/settings.yaml            تنظیمات سراسری (تلگرام، تأیید، قالب پیام فارسی)
channels/_template/             قالب کانال جدید (نادیده گرفته می‌شود)
channels/empire-autopsy/        تنها کانال فعال
src/autopsy/config/             مدل‌ها و بارگذاری/اعتبارسنجی پیکربندی
src/autopsy/stages/             فهرست مراحل خط تولید
src/autopsy/telegram/messages.py  ساخت پیام تأیید فارسی
src/autopsy/pipeline.py         برنامهٔ مراحل
src/autopsy/cli.py              رابط خط فرمان
.github/workflows/              زمان‌بندی ۵ دقیقه‌ای تأیید + اجرای دستی خط تولید
tests/                          آزمون پیکربندی و پیام
```

## اجرای محلی

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python -m autopsy config validate       # بررسی سالم‌بودن پیکربندی
python -m autopsy channels list         # فهرست کانال‌ها
python -m autopsy pipeline plan         # مراحل خط تولید
python -m autopsy approval preview      # پیش‌نمایش پیام تأیید فارسی
pytest -q
```

## ساخت مخزن و ارسال کد

```bash
bash push-to-github.sh          # ساخت مخزن عمومی + push (نیازمند gh auth login)
bash set-secrets.sh             # ثبت کلیدها در GitHub Secrets به‌صورت امن
```

## Secret‌های لازم (در GitHub Secrets)

| نام | کاربرد |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | توکن ربات تلگرام |
| `TELEGRAM_CHAT_ID_EMPIRE_AUTOPSY` | شناسهٔ چت کانال Empire Autopsy |
| `OPENAI_API_KEY` | تولید متن/تحقیق |
| `ELEVENLABS_API_KEY` | تولید نریشن |
| `YOUTUBE_CREDENTIALS_JSON` | انتشار در یوتیوب |

نام‌ها در `.env.example` هم آمده‌اند. مقدارها هرگز در مخزن نوشته نمی‌شوند.

## افزودن کانال دوم (بعداً)

```bash
cp -r channels/_template channels/my-channel
```

سپس در `channels/my-channel/channel.yaml`: مقدار `id` را برابر نام پوشه بگذارید،
`enabled: true` کنید و یک Secret جدا برای چت تلگرام تعریف کنید
(`chat_id_env` تکراری مجاز نیست).

## وضعیت فازها

- فاز ۱: تصمیم‌ها و طراحی (انجام‌شده در گفت‌وگوی قبلی).
- فاز ۲: اسکلت پروژه و پیکربندی چندکاناله (همین حالا).
- فاز ۳: اتصال تلگرام واقعی (ارسال پیام، دکمه‌ها، بررسی پاسخ هر ۵ دقیقه).
- فازهای بعد: مراحل تولید محتوا، صدا، تصویر، مونتاژ و انتشار.
