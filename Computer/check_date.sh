#!/bin/bash
current_year=$(date +%Y)
if [ "$current_year" -eq 2019 ]; then
    echo "Incorrect date detected, initiating restart..."
    exit 1
fi
