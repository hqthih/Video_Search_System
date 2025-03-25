#!/bin/bash

# Export variable to set the APP_HOME/ROOT_FOLDER as the directory containts the script
export APP_HOME=$(dirname "$(readlink -f "$0")")
export ROOT_FOLDER='backend'