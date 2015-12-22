#!/bin/bash
source tests/test_shell

expected="Welcome to the universe of Eliza commander...
Planet[Eliza] Cash[  1000] Fuel[ 10000] Hold[     0]:"

output=$(echo|nc -v $HOST $PORT 2>&1)
if [[ "$output" != *"$expected"* ]]; then
	echo "$output";
	exit 1;
fi
