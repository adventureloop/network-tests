#!/bin/sh

if ! [ $(id -u) = 0 ]; then
   echo "$0 must be run as root"
   exit 1
fi

v4echoserver="127.0.0.1"
v6echoserver="::1"

echo "Running test:"

runcount=0
passcount=0

for i in *_test.py; do
	[ -f "$i" ] || break
	runcount=$((runcount+1))
	printf "\t%s\n" $i
	python2.7 ./$i
done
