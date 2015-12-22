#!/bin/bash
source tests/test_shell

expected='Traceback.+socket.error: \[Errno 111\] Connection refused'

expected=".*$expected.*"
output=$(echo -e '127.0.0.1\n0\nZach Riggle\napple' | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi

