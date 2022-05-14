#!/bin/bash

source copy_job.sh
source print_args_job.sh
source all_build_files_dir_job.sh

cnt=0
for td in ${test_dir_list[@]}; do
	echo "test_dir_list[$cnt]: $td"
	target_dir="$td"
	mkdir -p $target_dir
	d=${take_dir_list[$cnt]}
	echo "correspoding take_dir_list[$cnt]: $d"
	#all_build_files_dir_job $d print_args_job.sh $td/
	all_build_files_dir_job $d copy_job.sh $td/
	((cnt++))
done
