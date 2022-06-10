#!/bin/bash

# this config is copied to environment directories,
# so it should contain absolute paths not dependent on its location
# or paths to scripts from the environment

source os.sh
if is_mac ; then
	templates_dir="${HOME}/Projects/templates"
else
	templates_dir="${HOME}/Projects/Templates"
fi
