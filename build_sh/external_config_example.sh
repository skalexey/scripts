
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/os.sh

if is_windows; then
	export {TPL_NAME}_deps="${HOME}/Projects"
	# export {TPL_NAME}_asio_path="C:/lib/asio-1.22.1/include"
else
	export {TPL_NAME}_deps="${HOME}/Projects"
	# export {TPL_NAME}_asio_path="~/lib/asio-1.22.1/include"
fi

[ ! -z {TPL_NAME}_deps ] && build_deps=${TPL_NAME}_deps