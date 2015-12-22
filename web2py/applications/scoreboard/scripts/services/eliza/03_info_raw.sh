#!/bin/bash
source tests/test_shell

expected="Info what commander\?  Use info <planet name> to get information about a planet."

expected=".+$expected.+"
output=$(echo info | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi

