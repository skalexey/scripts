#!/usr/bin/bash

source ~/Scripts/include/command_utils.sh
source ~/Scripts/include/log.sh
source ~/Scripts/automation/tmp/openai_config.sh

r=$(curl https://api.openai.com/v1/completions \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $openai_token" \
  -d "{
  \"model\": \"text-davinci:003\",
  \"prompt\": \"$1\",
  \"temperature\": \"0\"
}")
log_into_file "$r"
log "$r"