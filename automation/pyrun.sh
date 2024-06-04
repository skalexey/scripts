#!/bin/bash

function job()
{
	# Iterate over arguments
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	local script_name=$(basename "${BASH_SOURCE[0]}")
	echo "Script name: $script_name"
	source $THIS_DIR/automation_config.sh
	source $scripts_dir/include/log.sh
	source $scripts_dir/include/os.sh
	source $scripts_dir/include/file_utils.sh
	
	local log_prefix="-- [$script_name]: "
	local index_shift=0
	local python_args=" "
	local log_on=false
	for arg in "$@"
	do
		# Lowercase the argument
		arg_lowered=$(echo $arg | tr '[:upper:]' '[:lower:]')
		log "Arg: '$arg_lowered'"
		if [[ "$arg_lowered" == "-o" ]]; then
			log_info "Optimization flag passed"
			python_args="$python_args -OO"
			index_shift=$((index_shift+1))
		elif [[ "$arg_lowered" == "-d" ]]; then
			log_info "Debug flag passed"
			python_args="$python_args -m debugpy --listen 5555 --wait-for-client"
			index_shift=$((index_shift+1))
		elif [[ "$arg_lowered" == "-l" ]]; then
			log_info "Logging flag passed"
			log_on=true
			index_shift=$((index_shift+1))
		# If any other flags are passed, they will be passed to the python interpreter
		# Check if the argument is a flag
		elif [[ "$arg_lowered" == -* ]]; then
			log_info "A direct flag passed: '$arg'"
			# If a flag is present, remove it from the arguments
			python_args="$python_args $arg"
			index_shift=$((index_shift+1))
		fi
	done
	log "Python args: '$python_args'"
	log "Index shift: $index_shift"
	if is_windows; then
		python_path="/c/Python397/python.exe"
	else
		python_path="python3.7"
	fi
	local script_path=${@:((1 + index_shift)):1}
	local data_fpath=$(echo ${@:((2 + index_shift))})
	log_info "Script path: '$script_path'"
	log_info "Data file path: '$data_fpath'"
	if $log_on; then
		# Create log file with data file name + current date and time
		local python_script_name=$(echo ${@:((1 + index_shift)):1})
		local log_fpath=$(echo $python_script_name | sed 's/\.[^.]*$//')
		[ ! -d "logs" ] && mkdir "logs"
		log_fpath="logs/$log_fpath-$(date +'%Y-%m-%d-%H-%M-%S').log"
		log "Log file path: '$log_fpath'"
		local cmd_suffix=" > $log_fpath 2>&1"
	fi
	if [ ! -z "$data_fpath" ]; then
		local data_fpath_arg=" \"$data_fpath\""
	fi
	# Avoid converting symlinks paths to real
	local abs_scirpt_path=$(full_path "$script_path")
	log "Absolute script path: '$abs_scirpt_path'"
	system_script_path=$(system_path "$abs_scirpt_path")
	log "System path: '$system_script_path'"
	echo "System path: '$system_script_path'"
	# Run the python script
	local cmd="$python_path$python_args \"$system_script_path\"$data_fpath_arg$cmd_suffix"
	log_info "Run command: '$cmd'"
	eval "$cmd"
	local code=$?
	[ $code -eq 0 ] && log_success "Done" || log_error "Exited with error: $code"
}

job $@