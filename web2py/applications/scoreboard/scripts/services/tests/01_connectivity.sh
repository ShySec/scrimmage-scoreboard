#!/bin/bash
source tests/test_shell

nc -v -z -w2 $HOST $PORT
