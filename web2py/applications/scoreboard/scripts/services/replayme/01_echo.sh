#!/bin/bash
source tests/test_shell

expected="b55d7aa58f900cac2462b104e8d36ec31e86fc1881b3eed75aeb5660361dfcff"
expected=".+$expected.*"
output=$(echo -e "0\n0\n0\n" | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi

