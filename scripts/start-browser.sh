#!/usr/bin/env bash
set -e
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source /opt/ros/jazzy/setup.bash
mkdir -p "$project_dir/build"
exec 9>"$project_dir/build/.simulation-build.lock"
flock 9
cmake -S "$project_dir/simulation" -B "$project_dir/build/simulation" >/dev/null
cmake --build "$project_dir/build/simulation" -j2 >/dev/null
flock -u 9
exec 9>&-
exec python3 "$project_dir/scripts/browser_server.py" "$@"
