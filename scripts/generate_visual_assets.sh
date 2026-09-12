#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$project_dir/assets/visual" "$project_dir/assets/cad"
blender --background --python "$project_dir/scripts/asset_tools/generate_blender_visuals.py"
freecad_common="${HOME}/snap/freecad/common/robo-assets"
mkdir -p "$freecad_common/out"
cp "$project_dir/scripts/asset_tools/generate_freecad_parts.py" "$freecad_common/generate_freecad_parts.py"
/snap/bin/freecad.cmd -c "exec(open('${freecad_common}/generate_freecad_parts.py').read())"
cp "$freecad_common/out/"*.step "$project_dir/assets/cad/"
cp "$freecad_common/out/"*.stl "$project_dir/assets/cad/"
