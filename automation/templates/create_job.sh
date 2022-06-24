#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
path=$2
[ ! -d "$path" ] && echo "No path exists at '$path' relative to working directory '${PWD}'" && exit
absolute_path="$(cd "$path" && pwd)"
$THIS_DIR/../run.sh $THIS_DIR/job_template_job.sh "$1" "$absolute_path" ${@:3}
