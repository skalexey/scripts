#!/bin/bash

buildFolderPrefix="Build"
extraArg=" -DDEPS=${depsLocationFull} -DINCLUDES=${HOME}/Projects/Utils/include"
extraArgWin=$extraArg
extraArgMac=$extraArg
buildConfig="Debug"
logArg=" -DLOG_ON=ON"
