#!/usr/bin/env bash
set -euo pipefail

# Generic SMTP test sender for automation environments.
# Usage:
#   source ~/.config/automation/smtp.env
#   ./send_test_email.sh recipient@example.com "Optional subject"

TO_ADDR="${1:-}"
SUBJECT="${2:-Automation SMTP test}"

if [[ -z "$TO_ADDR" ]]; then
  echo "Usage: $0 <recipient_email> [subject]"
  exit 2
fi

python3 - "$TO_ADDR" "$SUBJECT" <<'PY'
import os
import smtplib
import sys
from email.message import EmailMessage

host = os.environ.get("HBOT_SMTP_HOST", "").strip()
port = int(os.environ.get("HBOT_SMTP_PORT", "587").strip())
user = os.environ.get("HBOT_SMTP_USER", "").strip()
password = os.environ.get("HBOT_SMTP_PASSWORD", "")
from_addr = os.environ.get("HBOT_SMTP_FROM", "").strip() or (user or "automation@localhost")
starttls = os.environ.get("HBOT_SMTP_STARTTLS", "true").strip().lower() not in {"0", "false", "no"}

to_addr = sys.argv[1]
subject = sys.argv[2]

if not host:
    raise SystemExit("HBOT_SMTP_HOST is missing. Source your smtp.env first.")

msg = EmailMessage()
msg["From"] = from_addr
msg["To"] = to_addr
msg["Subject"] = subject
msg.set_content("This is a generic SMTP connectivity test from automation tooling.")

with smtplib.SMTP(host, port, timeout=20) as server:
    if starttls:
        server.starttls()
    if user:
        server.login(user, password)
    server.send_message(msg)

print("SMTP test email sent")
PY
