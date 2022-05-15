#!/bin/bash

# This script runs any job passed
[ -z $1 ] && echo "[run script]: No job specified" && exit # job

# include invironment helper
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/include/env.sh

# collect all extra jobs passed as arguments to this script
arg_includes=()
for arg in "$@" 
do
	if [[ $arg =~ "_job.sh" ]]; then
		arg_includes+=($arg)
	fi
done
echo "		arg_includes: ${arg_includes[@]}"

# create env directory in the location of the passed job script
# with copies of all scripts from the job script directory
target_dir=$(dirname $1)
setup_environment $target_dir $target_dir ${arg_includes[@]}

# go to the environment directory and call the same script from there
ENV_ORIGINAL_DIR=${PWD}
cd $ENV_DIR

job=$(basename $1)
source $ENV_DIR/$job

# call the job
jobname=$(echo $job| cut -d. -f1)
$jobname ${@:2}
