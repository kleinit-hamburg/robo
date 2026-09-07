#!/usr/bin/env bash
# Native Installation auf Ubuntu 24.04; mit sudo bash aufrufen.
set -euo pipefail
if (( EUID != 0 )); then
  echo 'Bitte mit sudo bash scripts/install-simulation.sh starten.' >&2
  exit 1
fi
source /etc/os-release
if [[ ${ID:-} != ubuntu || ${VERSION_ID:-} != 24.04 ]]; then
  echo 'Dieses Skript unterstützt ausschließlich Ubuntu 24.04.' >&2
  exit 1
fi
case "$(dpkg --print-architecture)" in
  amd64|arm64) ;;
  *) echo 'Nur amd64 oder arm64 unterstützt.' >&2; exit 1 ;;
esac
command -v curl >/dev/null
work_dir=$(mktemp -d /tmp/garden-ros-install.XXXXXX)
trap 'rm -rf -- "$work_dir"' EXIT
# Offizielles ros-infrastructure-Release, am 2026-09-07 geprüft.
source_package="$work_dir/ros2-apt-source.deb"
curl --fail --show-error --location --retry 3 --max-time 120 \
  https://github.com/ros-infrastructure/ros-apt-source/releases/download/1.2.0/ros2-apt-source_1.2.0.noble_all.deb \
  --output "$source_package"
echo "0804d9b13db770eb87019be414cd78378835228ad5fa801fc88758596dd8f7e5  $source_package" | sha256sum --check -
dpkg -i "$source_package"
apt-get update
packages=(
  ros-jazzy-desktop
  ros-jazzy-ros-gz
  ros-jazzy-gz-ros2-control
  ros-jazzy-ros2-control
  ros-jazzy-ros2-controllers
  ros-jazzy-xacro
  ros-jazzy-joint-state-publisher-gui
  ros-dev-tools
  build-essential
  cmake
  ninja-build
  python3-venv
  mesa-utils
)
# Kein automatisches Entfernen bestehender Pakete und kein globales Upgrade.
apt-get --no-remove --assume-yes install "${packages[@]}"
if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  rosdep init
fi
set +u
source /opt/ros/jazzy/setup.bash
set -u
for package in ros_gz_sim ros_gz_bridge gz_ros2_control controller_manager xacro; do
  ros2 pkg prefix "$package"
done
gz sim --versions
cmake --version
colcon --help >/dev/null
df -h /
echo 'Pakete installiert. ROS-/Gazebo-Laufzeittests stehen noch aus.'
echo 'Im normalen Benutzerterminal anschließend: source /opt/ros/jazzy/setup.bash && rosdep update --rosdistro jazzy'
