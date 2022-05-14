#!/bin/bash

# This script runs any job passed
[ -z $1 ] && exit && echo "[run script]: No job specified" # job

# include invironment helper
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/include/env.sh

# create env directory in the location of the passed job script
# with copies of all scripts from the job script directory
setup_environment $(dirname $1)

# go to the environment directory and call the same script from there
cd $ENV_DIR

job=$(basename $1)
source $ENV_DIR/$job

# call the job
jobname=$(echo $job| cut -d. -f1)
$jobname ${@:2}
