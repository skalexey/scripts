#!/bin/bash

export netlib_asio_path_win="C:/lib/asio-1.22.1/include"
export netlib_asio_path_arg_win=" -DASIO_PATH=$netlib_asio_path_win"
export netlib_asio_path_mac="~/lib/asio-1.22.1/include"
export netlib_asio_path_arg_mac=" -DASIO_PATH=$netlib_asio_path_mac"

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/os.sh
if is_windows; then
	export netlib_asio_path=$netlib_asio_path_win
else
	export netlib_asio_path=$netlib_asio_path_mac
fi