#!/bin/bash

function deps_scenario()
{
    source dependencies.sh
    source deps_config.sh

    download_dependency "VL" "$depsLocation" "git@github.com:skalexey/VL.git"
    download_dependency "rapidjson" "$depsLocation" "https://github.com/Tencent/rapidjson.git"
}

deps_scenario $@
