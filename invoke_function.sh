#!/bin/bash

function job()
{
	local this_script_name="$(basename "${BASH_SOURCE[0]}")"
	local usage="Usage: $this_script_name <script> <command>"
	[ -z "$1" ] && echo "No script provided. $usage" && exit 1 || local script="$1"
	[ -z "$2" ] && echo "No command provided. $usage" && exit 2 || local command="$2"
	source $script
	"${@:2}"
}

job "$@"