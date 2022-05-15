#!/bin/bash

local lastFolderName=$folderName
local folderName=${PWD##*/}

source log.sh
local last_log_prefix=$log_prefix
local log_prefix="-- [${folderName} dependencies script]: "

local buildFolderPrefix="Build"
local onlyLibArg=" "
local cmakeTestsArg=" "
local cmakeGppArg=" "
local buildConfig="Debug"
local logArg=" local -DLOG_ON=ON"
local build=""
local rootDirectory="."
local onlyConfig=false

parse_args()
{
	local argIndex=0
	for arg in "$@" 
	do
		#echo "arg[$argIndex]: '$arg'"
		
		if [[ $argIndex -eq 0 ]]; then
			local rootDirectory=$arg
		else
			if [[ "$arg" == "only-lib" ]]; then
				log "'only-lib' option passed. Build only library without tests" " --"
				local onlyLibArg=" only-lib"
				local cmakeTestsArg=" "
			elif [[ "$arg" == "g++" ]]; then
				log "'g++' option passed. Build with g++ compiler" " --"
				local cmakeGppArg= -DCMAKE_CXX_COMPILER=g++ -DCMAKE_C_COMPILER=gpp
				local gppArg="g++"
				local buildFolderPrefix="Build-g++"
			elif [[ "$arg" == "no-log" ]]; then
				log "'no-log' option passed. Turn off LOG_ON compile definition" " --"
				local logArg=" "
			elif [[ "$arg" == "release" ]]; then
				log "'release' option passed. Set Release build type" " --"
				local buildConfig="Release"
			elif [[ "$arg" == "configure" ]]; then
				log "'configure' option passed. Will not build the project. Only make the config" " --"
				local onlyConfig=true
			fi
		fi	
		local argIndex=$((argIndex + 1))
	done
}

local folderName=$lastFolderName
local log_prefix=$last_log_prefix
