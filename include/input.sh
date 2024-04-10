#!/bin/bash

function request_input() {
	read -p "$@" input
	[ $? -ne 0 ] && return 1
	echo $input
}

function request_input_silent() {
	read -s -p "$@" input
	[ $? -ne 0 ] && return 1
	echo $input
}

function ask_user() {
	[ -z "$1" ] && echo "[ask_user]: No question provided" && return 1

	local res=false

	while true; do
		local answer=$(request_input "$@ (y/n): ")
		case $answer in
			[yY] ) res=true
				break;;
			[nN] ) res=false
				break;;
			* ) echo invalid response;;
		esac
	done

	$res
}
