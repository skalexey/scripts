#!/bin/bash
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cur_dir=${PWD}
cd $2
dir=${PWD}
cd "$cur_dir"
~/Scripts/automation/run.sh ~/Scripts/automation/templates/cpp_cmake_exe_job.sh "$1" "$dir" ${@:3}
#./build.sh . configure
