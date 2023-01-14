#!/usr/bin/bash

source ~/Scripts/include/command_utils.sh
source ~/Scripts/include/log.sh
source ~/Scripts/automation/tmp/openai_config.sh

r=$(curl https://api.openai.com/v1/images/generations \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $openai_token" \
  -d "{
  \"prompt\": \"$1\",
  \"n\": 2,
  \"size\": \"1024x1024\"
}")
log_into_file "$r"
log "$r"