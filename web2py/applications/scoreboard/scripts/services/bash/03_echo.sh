#!/usr/bin/env bash
source tests/test_shell

expected="$NEXT_TOKEN"
expected=".*$expected.*"
output=$(echo echo ":$NEXT_TOKEN:" | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi
