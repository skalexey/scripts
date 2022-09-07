#!/bin/bash

function box()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"
	source "automation_config.sh"
	source $automation_dir/run.sh scripts_tests_job.sh
}

box $@