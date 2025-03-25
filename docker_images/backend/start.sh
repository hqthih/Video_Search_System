#!/bin/bash

source env.sh

function run() {
   echo $SCRIPT
   echo $APP_HOME
   echo $ROOT_FOLDER
   exec python -u $APP_HOME/app.py $ARGS
}

run