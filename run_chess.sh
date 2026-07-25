#!/bin/bash
cd /c/Users/dhany/OneDrive/PythonProjects/Chess
python ChessMain.py > output.txt 2>&1 &
pid=$!
sleep 2
kill $pid
cat output.txt