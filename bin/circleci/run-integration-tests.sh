#!/bin/bash
set -ex
npm start &
sleep 90
STATIC_SERVER_PID=$!
