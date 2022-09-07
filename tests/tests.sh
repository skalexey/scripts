#!/bin/bash

function box()
{
	source dependencies_test.sh
	tests
}

box $@