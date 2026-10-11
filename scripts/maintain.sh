#!/usr/bin/env bash
# Fail-closed post-update patch check; never downloads model or updates packages.
set -euo pipefail
USER_HOME=/home/bc
PKG="$USER_HOME/.unsloth/studio/unsloth_studio/lib/python3.13/site-packages/studio/backend/core/inference"
BIN="$USER_HOME/ai-build/stable-diffusion.cpp/build-vulkan/bin"
[[ -f "$PKG/sd_cpp_backend.py" && -f "$PKG/sd_cpp_server.py" ]] || { echo 'Unsloth path missing; refusing'; exit 1; }
[[ -x "$BIN/sd-server" && -x "$BIN/sd-cli" ]] || { echo 'Vulkan executables missing; refusing'; exit 1; }
for b in sd-server sd-cli; do "$BIN/$b" --list-devices 2>&1 | grep -q 'Vulkan0' || exit 1; done
if pgrep -f '/sd-server .*--diffusion-model' >/dev/null; then
  echo 'Resident model loaded; deferring patch/restart.'
  exit 0
fi
set +e
/usr/bin/python3 /usr/local/lib/bc250-unsloth-vulkan/patch.py --directory "$PKG"
status=$?
set -e
case "$status" in
  0) exit 0 ;;
  2) systemctl restart skillfish-unsloth.service; systemctl is-active skillfish-unsloth.service ;;
  *) echo "Unsloth changed incompatibly; patch refused (exit $status)" >&2; exit 1 ;;
esac
