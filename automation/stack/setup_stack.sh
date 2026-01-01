#!/bin/bash

function validate_install() {
	if grep -q "stack.sh" "$1"; then
		return 0
	fi
	return 1
}

# Setup a command "stack" which calls the stack.sh script in this directory
function job() {
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/log.sh
	local stack_script_path="$THIS_DIR/stack.sh"
	[ ! -f "$stack_script_path" ] && log_error "Stack script not found at '$stack_script_path'" && return 1

	# Locate the bashrc file
	# Ask user to enter bashrc directory
	read -p "Enter the directory containing your .bashrc file: " bashrc_dir
	[ ! -d "$bashrc_dir" ] && log_error "Bashrc directory not found at '$bashrc_dir'" && return 1
	local bashrc_file="$bashrc_dir/.bashrc"
	[ ! -f "$bashrc_file" ] && log_error "Bashrc file not found at '$bashrc_file'" && return 1
	# Check if the command has already been set up
	if validate_install "$bashrc_file"; then
		log_warning "Stack command is already set up in '$bashrc_file'"
		return 0
	fi
	# Append the wrapper function to the bashrc file
	echo "function stack() { \"$stack_script_path\" \"\$@\"; }" >> "$bashrc_file"
	echo "" >> "$bashrc_file"
	if ! validate_install "$bashrc_file"; then
		log_error "Failed to set up stack command in '$bashrc_file'. Could not validate the modification."
		return 1
	fi
	# Create the config file
	local config_file="$THIS_DIR/stack.conf"
	if [ ! -f "$config_file" ]; then
		touch "$config_file"
		# Write the stack file path to the config file
		read -p "Enter the stack text file directory path: " stack_text_file_dir
		echo "stack_file=\"$stack_text_file_dir/stack.txt\"" >> "$config_file"
		echo "" >> "$config_file"
	else
		log_warning "Config file already exists at '$config_file'"
	fi
	log_success "Stack command set up successfully in '$bashrc_file'. Please restart your terminal or run 'source $bashrc_file' to apply the changes."
}

job $@