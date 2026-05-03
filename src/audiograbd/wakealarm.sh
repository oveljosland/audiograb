#!/usr/bin/env bash

if [[ ! "$1" =~ ^\+?[0-9]+$ ]]; then
    echo "error: argument must be a positive integer" >&2
    exit 1
fi

echo "$1" > /sys/class/rtc/rtc0/wakealarm