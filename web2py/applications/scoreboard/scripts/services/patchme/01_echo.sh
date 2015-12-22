#!/bin/bash
source tests/test_shell

expected="echo"
expected=".+$expected.*"
output=$(echo echo | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi

