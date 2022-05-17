#!/bin/bash

# inject_arg_job <a1, a2, a3, a4>
# Injects an argument <a4> between the given <a1> and <a2> for the <job>=<a3>
# args:
# 	a1, a2 = given 2 args
# 	a3=job
# 	a4=a4 = given third arg
# 	<other_args>
# invocation process:
# 	job(a1, a4, a2, <other_args>)
# 	literally:
# 		$a3($a1, $a4, $a2, ${@:5})
# Is used when the order of the first two arguments can't be changed

inject_arg_job()
{
	source log.sh
	local log_prefix="[inject_arg_job]: "

	[ -z "$1" ] && log_error "No agument provided 0 of 4" && exit
	[ -z "$2" ] && log_error "No agument provided 1 of 4" && exit
	[ -z "$3" ] && log_error "No job provided 2 of 4" && exit || job_path=$3
	[ -z "$4" ] && log_error "No arg provided 3 of 4" && exit

	local job=$(basename $job_path)
	source $job
	local jobname=$(echo $job| cut -d. -f1)
	$jobname "$1" "$4" "$2" ${@:5}
}

job()
{
	inject_arg_job $@
}
