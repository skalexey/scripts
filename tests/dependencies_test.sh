#!/bin/bash

deps_dir="tmp/deps"

function download_dependency_test()
{
	local dep_dir=$deps_dir/$1
	log "download_dependency_test('$1' '$2' '$3')"
	[ -d "$dep_dir" ] && rm -rf "$dep_dir"
	download_dependency "$1" "$2" "$3"
	[ ! -d "$dep_dir" ] && log_error "Test failed" && return 1 || log_success "Test finished successfully"
}

function download_test()
{
	[ ! -d "$deps_dir" ] && mkdir "$deps_dir"
	download_dependency_test "Utils" "$deps_dir" "git@github.com:skalexey/Utils.git"
	download_dependency_test "asio-1.19.1" "$deps_dir" "https://sourceforge.net/projects/asio/files/asio/1.19.1%20%28Development%29/asio-1.19.1.tar.bz2/download"
}

function tests()
{
	source "$scripts_dir/build_sh/dependencies.sh"
	download_test $@
}
