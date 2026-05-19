#!/usr/bin/env bash
set -euo pipefail

# Generic SMTP environment bootstrapper.
# Stores credentials in a private user config file outside this public scripts folder.

CONFIG_FILE="${SMTP_CONFIG_FILE:-$HOME/.config/automation/smtp.env}"
mkdir -p "$(dirname "$CONFIG_FILE")"

prompt_default() {
  local prompt_text="$1"
  local default_value="${2:-}"
  local value=""
  if [[ -n "$default_value" ]]; then
    read -r -p "$prompt_text [$default_value]: " value
    value="${value:-$default_value}"
  else
    read -r -p "$prompt_text: " value
  fi
  printf '%s' "$value"
}

prompt_secret() {
  local prompt_text="$1"
  local value=""
  read -r -s -p "$prompt_text: " value
  echo
  printf '%s' "$value"
}

echo "Config file: $CONFIG_FILE"

default_port="587"
default_starttls="true"

smtp_host="$(prompt_default "SMTP host (example: smtp.example.com)")"
smtp_port="$(prompt_default "SMTP port" "$default_port")"
smtp_user="$(prompt_default "SMTP username")"
echo "  (Google users: create an App Password at https://myaccount.google.com/apppasswords)"
smtp_password="$(prompt_secret "SMTP password or app password")"
smtp_from="$(prompt_default "SMTP from address (optional; defaults to SMTP username)")"
smtp_starttls="$(prompt_default "Use STARTTLS (true/false)" "$default_starttls")"

if [[ -z "$smtp_host" ]]; then
  echo "SMTP host is required."
  exit 2
fi

if [[ -z "$smtp_port" ]]; then
  echo "SMTP port is required."
  exit 2
fi

umask 077
cat > "$CONFIG_FILE" <<EOF
export HBOT_SMTP_HOST="$smtp_host"
export HBOT_SMTP_PORT="$smtp_port"
export HBOT_SMTP_USER="$smtp_user"
export HBOT_SMTP_PASSWORD="$smtp_password"
export HBOT_SMTP_FROM="$smtp_from"
export HBOT_SMTP_STARTTLS="$smtp_starttls"
EOF

chmod 600 "$CONFIG_FILE"

echo "Saved SMTP configuration to $CONFIG_FILE"
echo "Load it with: source \"$CONFIG_FILE\""
