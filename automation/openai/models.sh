#!/usr/bin/bash

source ~/Scripts/include/command_utils.sh
source ~/Scripts/include/log.sh
source ~/Scripts/automation/tmp/openai_config.sh

r=$(curl https://api.openai.com/v1/models  \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $openai_token" \
)
#log "$r"
models.py "$r"
