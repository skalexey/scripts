#!/bin/bash

[ -z $script_includes_dir ] && script_includes_dir="."

folderName=${PWD##*/}

source $script_includes_dir/log.sh
log_prefix="-- [${folderName} build script]: "

log "Build for OS: $OSTYPE" " -" " ---"

extraArg=" "
extraArgWin=$extraArg
extraArgMac=$extraArg

if [ -f "deps_config.sh" ]; then
	source deps_config.sh
fi

source build_config.sh
source $script_includes_dir/os.sh

if is_windows; then
	generatorArg=" "
	extraArg=$extraArgWin
elif is_mac; then
	generatorArg=" -GXcode"
	extraArg=$extraArgMac
else
	generatorArg=" "
fi

[ ! -z "$extraArg" ] && log "Extra arguments: '$extraArg'" " -"

source build_utils.sh

parse_args $@

enterDirectory=${pwd}

if [ -f "get_dependencies.sh" ]; then
	source get_dependencies.sh $@
	retval=$?
	if [ $retval -ne 0 ]; then
		log "Dependencies resolution error" " --"
		exit 1
	else
		log "Done with dependencies" " --"
		cd "$enterDirectory"
	fi
fi

[ ! -d "$rootDirectory" ] && log "Non-existent project directory passed '$rootDirectory'" " -" && exit 1 || cd "$rootDirectory"

if [[ "$rootDirectory" != "." ]]; then
	folderName=$rootDirectory
fi

echo "--- [${folderName}]: Configure with CMake"

build="${buildFolderPrefix}-cmake"

log "Output directory: '$build'" " -"

[ ! -d "$build" ] && mkdir $build || echo "	already exists"
cd $build

cmake ..$generatorArg$logArg$extraArg

retval=$?
if [ $retval -ne 0 ]; then
	log "CMake configure error" " -"
	cd "$enterDirectory"
	exit
else
	log "CMake configuring has been successfully done" " -"
fi

[ "$onlyConfig" == true ] && log "Exit without build" " -" && exit || log "Run cmake --build" " -"

cmake --build . --config=$buildConfig

retval=$?
if [ $retval -ne 0 ]; then
	log "CMake build error" " -"
	cd "$enterDirectory"
	exit
else
	log "CMake building is successfully done" "-" " ---"
fi

cd "$enterDirectory"

log "Finished build" " -" " ---"