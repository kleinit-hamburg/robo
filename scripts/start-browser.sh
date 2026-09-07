#!/usr/bin/env bash
set -e
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source /opt/ros/jazzy/setup.bash
exec python3 "$project_dir/scripts/browser_server.py" "$@"
