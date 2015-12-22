#!/bin/bash
source tests/test_shell

expected="Traceback .+assert hash.hexdigest\(\) == 'b55d7aa58f900cac2462b104e8d36ec31e86fc1881b3eed75aeb5660361dfcff'
AssertionError"

expected=".*$expected.*"
output=$(echo -e '127.0.0.1\n0\nhello' | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi
