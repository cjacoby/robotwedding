#!/usr/bin/env bash

echo "Starting Robot"
espeak "Good Morning"

# Set directory to directory of script.
cd "${0%/*}"

# Run the robot code in the pipenv
pipenv run ./main.py
