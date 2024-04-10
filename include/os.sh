#!/bin/bash

is_windows() {
	[[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] && return 0 || return 1
}

is_nix() {
	! is_windows
}

is_mac() {
	[[ $OSTYPE =~ .*darwin* ]] && true || false
}

is_linux() {
    [[ $OSTYPE =~ .*linux* ]] && true || false
}
