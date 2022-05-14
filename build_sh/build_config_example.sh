#!/bin/bash

buildFolderPrefix="Build"
extraArg=" -DDEPS=${depsLocationFull} -DVL_DIR=${vlDirFull} -DRAPIDJSON_DIR=${rapidjsonDirFull}"
extraArgWin=$extraArg
extraArgMac=$extraArg
buildConfig="Debug"
logArg=" -DLOG_ON=ON"
