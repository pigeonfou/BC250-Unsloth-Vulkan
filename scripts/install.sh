#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG="$HOME/.unsloth/studio/unsloth_studio/lib/python3.13/site-packages/studio/backend/core/inference"
BIN="$HOME/ai-build/stable-diffusion.cpp/build-vulkan/bin"
SERVICE="skillfish-unsloth.service"
command -v sudo >/dev/null
[[ -f "$PKG/sd_cpp_backend.py" && -f "$PKG/sd_cpp_server.py" ]] || { echo 'Unsloth version/path differs; adapt manually' >&2; exit 1; }
for x in sd-cli sd-server; do
  [[ -x "$BIN/$x" ]] || { echo "Missing $BIN/$x" >&2; exit 1; }
  "$BIN/$x" --list-devices 2>&1 | grep -q 'Vulkan0' || { echo "$x does not expose Vulkan0" >&2; exit 1; }
done
python3 "$ROOT/scripts/patch.py" --directory "$PKG" --check
sudo install -d -m 755 "/etc/systemd/system/$SERVICE.d"
printf '[Service]\nEnvironment="UNSLOTH_BC250_VULKAN=1"\nEnvironment="SD_CLI_PATH=%s/sd-cli"\nEnvironment="SD_SERVER_PATH=%s/sd-server"\n' "$BIN" "$BIN" | sudo tee "/etc/systemd/system/$SERVICE.d/bc250-vulkan.conf" >/dev/null
sudo install -d -m 755 /usr/local/lib/bc250-unsloth-vulkan
sudo install -m 755 "$ROOT/scripts/patch.py" /usr/local/lib/bc250-unsloth-vulkan/patch.py
sudo install -m 755 "$ROOT/scripts/maintain.sh" /usr/local/lib/bc250-unsloth-vulkan/maintain.sh
sudo install -m 644 "$ROOT/systemd/bc250-unsloth-watch.service" /etc/systemd/system/
sudo install -m 644 "$ROOT/systemd/bc250-unsloth-watch.timer" /etc/systemd/system/
if pgrep -f '/sd-server .*--diffusion-model' >/dev/null; then
  echo 'A model is resident. Unload it and rerun installation to patch safely.'
  exit 0
fi
set +e
python3 "$ROOT/scripts/patch.py" --directory "$PKG"
rc=$?
set -e
[[ "$rc" == 0 || "$rc" == 2 ]] || exit "$rc"
sudo systemctl daemon-reload
sudo systemctl enable --now bc250-unsloth-watch.timer
sudo systemctl restart "$SERVICE"
systemctl is-active "$SERVICE"
