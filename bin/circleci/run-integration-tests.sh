#!/bin/bash
set -ex
killall node
sleep 5
npm start &
STATIC_SERVER_PID=$!
