#!/bin/bash
SCRIPT_DIR=$( dirname "$0" )
# Only works if in utils (trims 6 characters from the script directory string)
SCRIPT_DIR=${SCRIPT_DIR%??????}
./utils/install.sh && XDG_DATA_DIRS=$SCRIPT_DIR/build/share:$XDG_DATA_DIRS ./build/bin/bottles