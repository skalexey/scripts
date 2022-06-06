#!/bin/bash

function deps_scenario()
{
    source dependencies.sh
    source deps_config.sh

    download_dependency "$vlDirRel" "$depsLocationFull" "git@github.com:skalexey/VL.git"
    download_dependency "$rapidjsonDirRel" "$depsLocationFull" "https://github.com/Tencent/rapidjson.git"
}

deps_scenario $@
