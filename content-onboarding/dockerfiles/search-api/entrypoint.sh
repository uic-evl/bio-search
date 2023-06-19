#!/bin/bash
# entrypoint.sh

set -eu
#tmux new -s foo -d && tmux ls && 
flask run --host=0.0.0.0
#exec "$@"
