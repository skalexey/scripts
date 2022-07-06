#!/bin/bash

function ssh_exists() {
	[ -z "$1" ] && echo "[ssh_exists]: No path provided" && return 1 || local path="$1"
	[ -z "$2" ] && echo "[ssh_exists]: No host provided" && return 2 || local host="$2"
	[ -z "$3" ] && echo "[ssh_exists]: No user name provided" && return 3 || local user="$3"

	local USE_IP='-o StrictHostKeyChecking=no $user@$host'
	
	if [ ! -z "$4" ]; then # pass
		local ssh_pass='sshpass -p $4'
		[ $? -ne 0 ] && echo "[ssh_exists]: Error while using sshpass" && false && return 4
	fi

	if $ssh_pass ssh $USE_IP stat $path \> /dev/null 2\>\&1; then
		true
	else
		false
	fi
}

function ssh_copy() {
	[ -z "$1" ] && echo "[ssh_copy]: No local path provided" && return 1 || local local_path="$1"
	[ -z "$2" ] && echo "[ssh_copy]: No remote path provided" && return 1 || local remote_path="$2"
	[ -z "$3" ] && echo "[ssh_copy]: No host provided" && return 2 || local host="$3"
	[ -z "$4" ] && echo "[ssh_copy]: No user name provided" && return 3 || local user="$4"

	scp $local_path $user@$host:$remote_path
}

function ssh_rename()
{
	[ -z "$1" ] && echo "[ssh_rename]: No path provided" && return 1 || local path="$1"
	[ -z "$2" ] && echo "[ssh_rename]: No new name provided" && return 1 || local new_name="$2"
	[ -z "$3" ] && echo "[ssh_rename]: No host provided" && return 2 || local host="$3"
	[ -z "$4" ] && echo "[ssh_rename]: No user name provided" && return 3 || local user="$4"

	if [ ! -z "$5" ]; then # pass
		local ssh_pass='sshpass -p $5'
	fi

	local containing_dir=$(dirname $path)
	echo "Containing dir of '$path': '$containing_dir'"
	$ssh_pass ssh $user@$host mv "$path" "$containing_dir/$new_name"
}


