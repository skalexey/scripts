#!/bin/bash
ssh user@host  << HERE
	echo "Pull the repo"
	cd domains/mydomain.com
	git pull
	cd ..
	echo "Finished"
HERE
