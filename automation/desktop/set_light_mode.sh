#!/bin/bash

function set_light_mode()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[set_light_mode]: "

	source $THIS_DIR/../../include/file_utils.sh
	file_replace "C:\Users\skoro\AppData\Roaming\Code\User\settings.json" "Dark" "Light"
	return 0
}

set_light_mode $@
[ $? -ne 0 ] && exit