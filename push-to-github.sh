#!/usr/bin/env bash
# ساخت مخزن عمومی گیت‌هاب و فرستادن کد — روی کامپیوتر خودتان اجرا کنید.
#
# پیش‌نیاز (یک‌بار):
#   1) نصب GitHub CLI:  https://cli.github.com
#   2) ورود:            gh auth login
#      مسیر: GitHub.com → HTTPS → Login with a web browser
#
# اجرا:
#   bash push-to-github.sh                     # نام پیش‌فرض: empire-autopsy-pipeline
#   bash push-to-github.sh my-repo-name        # با نام دلخواه
set -euo pipefail

REPO_NAME="${1:-empire-autopsy-pipeline}"

if ! command -v gh >/dev/null 2>&1; then
  echo "✗ GitHub CLI نصب نیست. از https://cli.github.com نصب کنید."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "✗ اول یک‌بار وارد شوید:  gh auth login"
  echo "  مسیر: GitHub.com → HTTPS → Login with a web browser"
  exit 1
fi

cd "$(dirname "$0")"

if [ ! -d .git ]; then
  git init -q
fi
git branch -M main
git add -A
if ! git diff --cached --quiet; then
  git commit -q -m "فاز ۲: اسکلت پروژه و پیکربندی چندکاناله"
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "→ remote «origin» از قبل هست؛ فقط push می‌کنم."
  git push -u origin main
else
  echo "→ ساخت مخزن عمومی «$REPO_NAME» و ارسال کد..."
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
fi

OWNER="$(gh api user --jq .login)"
echo
echo "✓ آماده است:  https://github.com/$OWNER/$REPO_NAME"
echo "قدم بعد: bash set-secrets.sh   (ثبت کلیدها در Secrets)"
