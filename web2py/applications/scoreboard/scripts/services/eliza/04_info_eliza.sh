#!/bin/bash
source tests/test_shell

expected="Planet Eliza info:
Designation Number: [a-f0-9]{32}
Government: [a-zA-Z0-9 -]+
Primary Economy: [a-zA-Z0-9 ]+
Secondary Economy: [a-zA-Z0-9 ]+
Population: [a-zA-Z0-9 ]+
Population Growth: [a-zA-Z0-9 ]+
Location: [a-zA-Z0-9 ]+"

expected=".+$expected.+"
output=$(echo info eliza | nc -v $HOST $PORT 2>&1)
if [[ ! "$output" =~ $expected ]]; then
	echo "$output";
	exit 1;
fi

