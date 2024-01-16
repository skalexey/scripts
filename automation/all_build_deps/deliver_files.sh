#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh
source $scripts_dir/include/log.sh
log_prefix="[deliver_files.sh]: "

[ -z $1 ] && log_error "No directory provided" && exit || input_dir=$1
[ -z $2 ] && log_error "No files dir job provided" && exit || files_job_path=$2

source $scripts_dir/include/file_utils.sh
[[ $files_job_path == /* ]] && files_job_path_full=$files_job_path || files_job_path_full=$(full_path $files_job_path)

#log "files_job_path: $files_job_path"
#log "files_job_path_full: $files_job_path_full"
$automation_dir/run.sh \
    $automation_dir/include/helpers/files_in_dir_to_list_job.sh \
        $THIS_DIR/all_build_deps_job.sh \
        $input_dir \
        $files_job_path_full \
        copy_job.sh
