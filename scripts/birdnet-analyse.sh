#!/usr/bin/env bash

input="test.wav"
output="./output/"

exec uv run birdnet-analyze "$input" -o "$output"