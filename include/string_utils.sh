#!/usr/bin/bash

function date_and_time()
{
	local format=$1
	if [ -z $format ]; then
		format="%Y-%m-%d %H:%M:%S"
	fi
	echo $(date +"$format")
}

function fname_date_and_time()
{
	local format=$1
	if [ -z $format ]; then
		format="%Y-%m-%d_%H-%M-%S"
	fi
	echo $(date +"$format")
}