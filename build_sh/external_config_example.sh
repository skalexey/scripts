
function job()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/os.sh

	if is_windows; then
		export {TPL_NAME}_deps="${HOME}/Projects"
	else
		export {TPL_NAME}_deps="${HOME}/Projects"
	fi

	[ ! -z {TPL_NAME}_deps ] && build_deps=${TPL_NAME}_deps
}

job $@