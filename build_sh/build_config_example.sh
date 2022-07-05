#!/bin/bash

source external_config.sh

buildFolderPrefix="Build"
extraArg=" -DDEPS=${depsLocation} -DINCLUDES=${HOME}/Projects/Utils/include"
extraArgWin=$extraArg
extraArgMac=$extraArg
buildConfig="Debug"
logArg=" -DLOG_ON=ON"
