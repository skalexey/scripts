#/usr/bin/bash

function job()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/log.sh
	script_name=$(basename $0)
	local log_prefix="[$script_name] "
	source $scripts_dir/include/os.sh
	if is_windows; then
		powershell -Command "Get-Process python | Stop-Process -Force"
	else
		ps aux | grep python | awk '{print $2}' | xargs kill -9
	fi
	code=$?
	[ $code -ne 0 ] && log_error "Failed. Error code: $code" && return 1 || log_success "Done"
}

job