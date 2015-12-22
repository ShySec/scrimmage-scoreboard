#!/bin/bash
source tests/test_shell

expected="Eliza Help Guide:
Commands:
help   - Displays the help menu
buy    - Used to buy items from a planet
sell   - Used to sell items to a planet
info   - Describes information about a specific planet
jump   - Jumps to another planet within range
quit   - Exits the game
hold   - Lists items in your cargo hold
local  - Lists planets within range and there economies
market - Displays the market in your region or on a planet

Use help <command> to get a more detailed usage listing"

output=$(echo help | nc -v $HOST $PORT 2>&1)
if [[ "$output" != *"$expected"* ]]; then
	echo "$output";
	exit 1;
fi
