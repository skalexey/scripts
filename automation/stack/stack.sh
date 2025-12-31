#!/bin/bash

# Maintain a stack of strings in a file using commands:
# stack push <string>
# stack pop - removes and prints the top string
# stack peek - prints the top string
# stack size - prints the number of items in the stack


function cmd_push() {
	local item="$1"
	[ -z "$item" ] && log_error "No item provided for push." && return 1
	# Append the item to the stack file
	echo "$item" >> "$stack_file"
}

function cmd_pop() {
	# Remove and print the top item from the stack file
	local top_item=$(tail -n 1 "$stack_file")
	[ -z "$top_item" ] && log_error "Stack is empty" && return 1
	# Remove the top item from the stack file
	sed -i '$d' "$stack_file"
	echo "Retrieved: $top_item"
}

function cmd_peek() {
	# Print the top item from the stack file
	local top_item=$(tail -n 1 "$stack_file")
	[ -z "$top_item" ] && log_error "Stack is empty" && return 1
	echo "$top_item"
}

function cmd_size() {
	# Print the number of items in the stack file
	local size
	size=$(wc -l < "$stack_file")
	echo "$size"
}

function job() {
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/log.sh
	local this_script_name=$(basename "${BASH_SOURCE[0]}")
	local log_prefix="[$this_script_name] "

	[ -z "$1" ] && log_error "No command provided. Available commands: stack push <string>, stack pop, stack peek, stack size" && return 1 || local command="$1"
	# Load a config which contains path to the file
	local config_file="$THIS_DIR/stack.conf"
	[ ! -f "$config_file" ] && log_error "Config file not found at '$config_file'" && return 1
	source "$config_file"
	[ -z "$stack_file" ] && log_error "Stack file not found" && return 1
	# Command process
	# Find a function in this script with name cmd_<comand> and execute. Otherwise print an error and return
	local cmd_function="cmd_$command"
	if declare -f "$cmd_function" > /dev/null; then
		# Pass all but first args
		"$cmd_function" "${@:2}"
	else
		log_error "Unknown command: $command"
		return 1
	fi
}

job "$@"