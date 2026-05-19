#!/usr/bin/env bash
set -euo pipefail

# Telegram bot environment bootstrapper.
# Stores credentials in a private user config file outside this public scripts folder.
#
# Before running:
#   1. Open Telegram and message @BotFather: /newbot
#   2. Copy the token it gives you (looks like 123456:ABCdef...)
#   3. Start a chat with your new bot and send any message (so it appears in getUpdates)

CONFIG_FILE="${TG_CONFIG_FILE:-$HOME/.config/automation/telegram.env}"
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

# HTTP helpers: try WSL curl first, fall back to Windows PowerShell if empty (WSL2 network issue)
tg_curl() {
  local url="$1"
  local result=""
  result="$(curl -sL --max-time 10 "$url" 2>/dev/null || true)"
  if [[ -z "$result" ]] && command -v powershell.exe &>/dev/null; then
    result="$(powershell.exe -NoProfile -NonInteractive -Command "try { (Invoke-WebRequest -Uri '$url' -UseBasicParsing).Content } catch { '' }" 2>/dev/null | tr -d '\r' || true)"
  fi
  printf '%s' "$result"
}

tg_post() {
  local url="$1"
  local body="$2"
  local result=""
  result="$(curl -sL --max-time 10 -X POST -H 'Content-Type: application/json' -d "$body" "$url" 2>/dev/null || true)"
  if [[ -z "$result" ]] && command -v powershell.exe &>/dev/null; then
    local tmp_body
    tmp_body="$(mktemp)"
    printf '%s' "$body" > "$tmp_body"
    local win_tmp
    win_tmp="$(wslpath -w "$tmp_body")"
    result="$(powershell.exe -NoProfile -NonInteractive -Command "try { \$b = Get-Content '$win_tmp' -Raw; (Invoke-WebRequest -Uri '$url' -Method POST -ContentType 'application/json' -Body \$b -UseBasicParsing).Content } catch { '' }" 2>/dev/null | tr -d '\r' || true)"
    rm -f "$tmp_body"
  fi
  printf '%s' "$result"
}

echo "Config file: $CONFIG_FILE"
echo ""

bot_token="$(prompt_secret "Bot token (from @BotFather)")"
bot_token="${bot_token%/}"        # strip accidental trailing slash
bot_token="$(printf '%s' "$bot_token" | tr -d '\r\n ')"  # strip CR/LF/spaces from paste

if [[ -z "$bot_token" ]]; then
  echo "Bot token is required."
  exit 2
fi

# Try to auto-fetch chat_id from the most recent message in getUpdates
echo ""
echo "Clearing any active webhook (required for getUpdates to work)..."
tg_curl "https://api.telegram.org/bot${bot_token}/deleteWebhook" > /dev/null

echo "Fetching chat_id from getUpdates..."
echo "  (Send a message to your bot now if you haven't already, then wait a moment...)"
updates_json=""
for attempt in 1 2 3; do
  updates_json="$(tg_curl "https://api.telegram.org/bot${bot_token}/getUpdates")"
  if [[ -z "$updates_json" ]]; then
    echo "  Attempt $attempt: no response from API, retrying in 3s..."
  else
    result_count="$(printf '%s' "$updates_json" | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('result',[])))" 2>/dev/null || echo 0)"
    if [[ "$result_count" -gt 0 ]]; then break; fi
    echo "  Attempt $attempt: no messages yet, retrying in 3s..."
  fi
  sleep 3
done
auto_chat_id=""
if [[ -n "$updates_json" ]]; then
  # Extract the first chat.id from the results array
  auto_chat_id="$(printf '%s' "$updates_json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
results = data.get('result', [])
if results:
    msg = results[-1]
    chat_id = (
        msg.get('message', {}).get('chat', {}).get('id') or
        msg.get('channel_post', {}).get('chat', {}).get('id') or
        msg.get('my_chat_member', {}).get('chat', {}).get('id')
    )
    if chat_id is not None:
        print(chat_id)
" 2>/dev/null || true)"
fi

if [[ -n "$auto_chat_id" ]]; then
  echo "  Found chat_id: $auto_chat_id"
  chat_id="$(prompt_default "Use this chat_id?" "$auto_chat_id")"
else
  echo "  No messages found. Send any message to your bot first, then re-run, or enter the chat_id manually."
  echo "  (You can also get it from: https://api.telegram.org/bot${bot_token}/getUpdates)"
  chat_id="$(prompt_default "Chat ID")"
fi

if [[ -z "$chat_id" ]]; then
  echo "Chat ID is required."
  exit 2
fi

# Send a test message to verify
echo ""
echo "Sending test message to chat $chat_id..."
test_result="$(tg_post "https://api.telegram.org/bot${bot_token}/sendMessage" "{\"chat_id\": \"${chat_id}\", \"text\": \"[HBOT] Telegram notifications configured successfully.\"}")"
if printf '%s' "$test_result" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('ok') else 1)" 2>/dev/null; then
  echo "  Test message sent."
else
  echo "  WARNING: Test message may have failed. Response: $test_result"
  echo "  Continuing anyway — double-check the token and chat_id."
fi

umask 077
cat > "$CONFIG_FILE" <<EOF
export HBOT_TG_BOT_TOKEN="$bot_token"
export HBOT_TG_CHAT_ID="$chat_id"
EOF

chmod 600 "$CONFIG_FILE"

echo ""
echo "Saved Telegram configuration to $CONFIG_FILE"
echo "Load it with: source \"$CONFIG_FILE\""
