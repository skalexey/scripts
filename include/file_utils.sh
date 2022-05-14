#!/bin/bash

file_insert_before() {
	[ -z "$1" ] && exit # file name
	[ -z "$2" ] && exit # string before which to insert
	[ -z "$3" ] && exit # what to insert
	#sed -i "" "s/$2/$3$2/" "$1"
	# due to platform independence
	echo $(python -c "from file_utils import*; insert_before(\"$1\", \"$2\", \"$3\");")
}

file_append_line() {
	[ -z "$1" ] && exit # file name
	[ -z "$2" ] && exit # string to append at the end of the file
	echo "$2" >> "$1"
}

file_replace() {
	[ -z "$1" ] && exit # file name
	[ -z "$2" ] && exit # regex to find
	[ -z "$3" ] && exit # text to replace regex to
	
	sed -i -E "s/$2/$3/" $1
	return $?
}

file_search() {
	[ -z "$1" ] && exit # file name
	[ -z "$2" ] && exit # regex to find

	#echo "in $1 find $2"
	local contents=$(<$1)
	local nl=$'\n'
	local rest=${contents#*$2}
	local res=$(( ${#contents} - ${#rest} - ${#2} ))
	[ $res -ge 0 ] && echo $res || echo "-1"
	#[[ $(cat $1) =~ .*$2* ]] && true || false
}

dir_full_path() {
	[ -z "$1" ] && exit # directory path
	
	[ ! -d "$1" ] && exit
	local cur_dir=${PWD}
	cd "$1"
	echo ${PWD}
	cd $cur_dir
}