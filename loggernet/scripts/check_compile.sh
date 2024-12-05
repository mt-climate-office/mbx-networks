#!/bin/bash

# Make virtual display so that wine can run
Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 &
XVFB_PID=$!

# Ensure cleanup on script exit
trap "kill $XVFB_PID > /dev/null 2>&1" EXIT

# Test that the program can compile
DISPLAY=:99 wine /opt/cr1000xcomp.exe "$1" 2> >(grep -v "X connection to :99 broken" >&2)
kill $XVFB_PID > /dev/null 2>&1