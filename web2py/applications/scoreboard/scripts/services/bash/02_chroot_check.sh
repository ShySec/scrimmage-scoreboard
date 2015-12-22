#!/usr/bin/env bash
source tests/test_shell

expected="/bin/readlink"

expected=".*$expected.*"
output=$(echo 'exec readlink /proc/self/exe' | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi
