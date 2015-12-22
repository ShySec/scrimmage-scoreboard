#!/bin/bash
source tests/test_shell

expected="* OK IMAP4rev1 server ready [a-f0-9]{2,32}"

expected=".+$expected.+"
output=$(echo | nc -v $HOST $PORT 2>&1)
if [[ "$output" =~ $expected ]]; then
	exit 0;
fi

expected="oops"
expected=".+oops.*"
if [[ "$output" =~ $expected ]]; then
	exit 0;
fi
echo "$output";
exit 1;

