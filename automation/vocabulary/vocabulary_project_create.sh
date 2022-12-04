#!/bin/bash
function job()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	local CUR_DIR=${PWD}

	cd "$THIS_DIR"
	source vocabulary_config.sh
	source ~/Scripts/automation/automation_config.sh
	
	source $scripts_dir/include/file_utils.sh
	source $scripts_dir/include/input.sh
	source $scripts_dir/include/log.sh

	log_prefix="[vocabulary_project_create] "

	# remove the project folder if exists
	if [ -d "$project_dir" ]; then
		if ask_user "Project already exists. Remove its directory? ($project_dir)"; then
			rm -rf "$project_dir"
			ask_user "Removed?"
		else
			log_info "Exiting..."
			return 0
		fi
	fi

	# create new project folder from template
	../templates/cpp_cmake_project.sh $project_name $project_parent_dir exe

	local project_automation_path="$automation_dir/$project_name"
	local cmake_file="$project_dir/CMakeLists.txt"

	# comment out some extra directories
	file_insert_before "$cmake_file" "include_directories\(\".\"\)" "#"
	
	local templates_dir="$projects_dir/templates"

	# deliver build scripts
	cp "$templates_dir/Scripts/update_scripts.sh" "$project_dir/"
	cp "$automation_dir/automation_config.sh" "$project_dir/"
	# call to update the scripts
	$project_dir/update_scripts.sh
}

job $@