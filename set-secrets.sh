#!/usr/bin/env bash
# ثبت کلیدها در GitHub Secrets — مقدارها در ترمینال نمایش داده نمی‌شوند.
# پیش‌نیاز: gh auth login  و اجرا داخل همان پوشهٔ مخزن.
set -euo pipefail

NAMES=(
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID_EMPIRE_AUTOPSY
  OPENAI_API_KEY
  ELEVENLABS_API_KEY
  YOUTUBE_CREDENTIALS_JSON
)

cd "$(dirname "$0")"

if ! gh auth status >/dev/null 2>&1; then
  echo "✗ اول وارد شوید:  gh auth login"
  exit 1
fi

echo "برای هر مورد، مقدار را بچسبانید و Enter بزنید (خالی = رد شود)."
echo
for name in "${NAMES[@]}"; do
  value=""
  read -r -s -p "مقدار $name: " value || true
  echo
  if [ -n "$value" ]; then
    printf '%s' "$value" | gh secret set "$name"
    echo "✓ $name ثبت شد"
  else
    echo "– $name رد شد"
  fi
done

echo
echo "فهرست Secretهای ثبت‌شده:"
gh secret list
