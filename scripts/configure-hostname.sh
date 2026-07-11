#!/usr/bin/env bash
# Set the machine hostname to 'footpass' and enable mDNS so the appliance is
# reachable at http://footpass.local. Debian/Ubuntu.
#
# WARNING: this renames the WHOLE machine. If this box runs other services,
# make sure that's what you want.
set -euo pipefail

TARGET="${1:-footpass}"

echo "== FootPass hostname + mDNS setup =="
echo "Setting system hostname to: ${TARGET}"
sudo hostnamectl set-hostname "${TARGET}"

echo "Installing Avahi (mDNS)..."
sudo apt-get update -y
sudo apt-get install -y avahi-daemon avahi-utils
sudo systemctl enable --now avahi-daemon

echo "Waiting for mDNS to come up..."
sleep 2
if command -v avahi-resolve >/dev/null 2>&1; then
  avahi-resolve -n "${TARGET}.local" || echo "(mDNS not resolving yet — give it a moment)"
fi

IP="$(hostname -I | awk '{print $1}')"
echo ""
echo "Local IP address : ${IP}"
echo "Access FootPass at: http://${TARGET}.local   (or http://${IP}/)"
