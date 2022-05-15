#!/bin/bash

# This job simply calls cp $1 $2 on the given two arguments

copy_job()
{
	[ -z "$1" ] && echo "[copy_job]: too few arguments 0 of 2" && exit
	[ -z "$2" ] && echo "[copy_job]: too few arguments 1 of 2" && exit
	echo "[copy_job]: cp \"$1\" \"$2\""
	cp "$1" "$2"
}

job()
{
	copy_job $@
}
