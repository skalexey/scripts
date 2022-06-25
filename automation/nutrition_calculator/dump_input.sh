#!/bin/bash
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUR_DIR=${PWD}
proj_dir=~/Projects/C++/nutrition_calculator
res_dir=${HOME}/AppData/Local/Temp
dumps_dir=$proj_dir/tmp/input_dump
echo "dumps_dir: '$dumps_dir'"
[ ! -d "$dumps_dir" ] && mkdir -p $dumps_dir
t=`date +%F-%T`
set -x #echo on
cp $res_dir/input.txt $dumps_dir/input-$t.txt
cp $res_dir/item_info.txt $dumps_dir/item_info-$t.txt
#set -x #echo off
