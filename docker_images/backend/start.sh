#!/bin/bash
function run() {
   exec python -u $APP_HOME/app.py $ARGS
}

run