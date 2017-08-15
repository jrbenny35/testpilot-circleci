#!/bin/bash
set -ex
npm start &
sleep 30
STATIC_SERVER_PID=$!
