#!/bin/bash

# create_from_template_file.sh $name $target_path
# Creates a file with name $name at $target_path

function create_from_template_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
		"$scripts_dir/include/os.sh" \
	)
	env_include ${includes[@]}
	source templates_config.sh
	source log.sh
	local log_prefix="[create_from_template_job]: "
	[ -z "$1" ] && log_error "No template path provided" && return 1 || local tpl_path="$1"
	[ -z "$2" ] && log_error "No file name provided" && return 2 || local file_name="$2"
	[ -z "$3" ] && log_error "No target path provided" && return 3 || local target_path="$3"

	[ ! -f "$tpl_path" ] && log_error "No template exists at '$tpl_path'" && return 8
	[ ! -d "$target_path" ] && log_error "No path exists at '$target_path'" && log_warning "Working directory: '${PWD}'" && return 4
	# local absolute_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

	local ext=$(file_extension "$tpl_path")
	local file="$file_name.$ext"
	local file_path="$target_path/$file"
	[ -f "$file_path" ] && log_error "This file already exists ('$file_path')" && return 5
	cp "$tpl_path" "$file_path"
	[ $? -ne 0 ] && log_error "Errors during template delivering at '$file_path'" && return 6

	file_replace "$file_path" "\{TPL_NAME\}" "$file_name"
	[ $? -ne 0 ] && log_error "Errors during template initialization at '$file_path'" && return 7

	log_success "Template '$(basename "$tpl_path")' successfully instantiated at '$file_path'"
	return 0
}

function job()
{
	create_from_template_job $@
}
