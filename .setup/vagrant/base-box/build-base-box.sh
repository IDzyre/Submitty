#!/usr/bin/env bash
# build-base-box.sh - Build an Ubuntu 22.04 VirtualBox base box for Vagrant from the live server ISO.
#
# Requires: packer, VirtualBox
set -euo pipefail

usage() {
  cat >&2 <<EOF
Usage: $0 [-i ISO] [-c CHECKSUM] [-o BOX_FILE] [-d DISK_MB] [-m MEMORY_MB] [-n CPUS] [-g] [-a]
  -i  Path or URL of an Ubuntu 22.04 live server ISO
      (default: download ubuntu-22.04.5-live-server-amd64.iso from releases.ubuntu.com)
  -c  ISO checksum, e.g. sha256:abc... (default: verified against Ubuntu's SHA256SUMS
      for the download, skipped for a local ISO)
  -o  Output .box file (default: output/ubuntu-22.04-virtualbox.box next to this script)
  -d  Max disk size in MB (default: 65536)
  -m  Memory in MB used during the build (default: 4096)
  -n  CPUs used during the build (default: 2)
  -g  Show the VirtualBox window instead of building headless
  -a  Add the finished box to Vagrant as ubuntu-22.04-local
EOF
  exit 1
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ISO=""; CHECKSUM=""; BOX_FILE="$SCRIPT_DIR/output/ubuntu-22.04-virtualbox.box"
DISK=65536; MEMORY=4096; CPUS=2; HEADLESS=true; ADD_BOX=false
while getopts "i:c:o:d:m:n:gah" opt; do
  case $opt in
    i) ISO=$OPTARG ;; c) CHECKSUM=$OPTARG ;; o) BOX_FILE=$OPTARG ;;
    d) DISK=$OPTARG ;; m) MEMORY=$OPTARG ;; n) CPUS=$OPTARG ;;
    g) HEADLESS=false ;; a) ADD_BOX=true ;; *) usage ;;
  esac
done

command -v packer >/dev/null || {
  echo "Error: packer is not installed. See https://developer.hashicorp.com/packer/install" >&2
  echo "       (Windows: choco install packer / winget install Hashicorp.Packer)" >&2
  exit 1
}
if ! command -v VBoxManage >/dev/null && [[ ! -x "${VBOX_INSTALL_PATH:-/c/Program Files/Oracle/VirtualBox}/VBoxManage.exe" ]]; then
  echo "Error: VirtualBox is not installed" >&2
  exit 1
fi

# Packer is a native binary, so on Git Bash it needs Windows-style paths.
native_path() {
  if command -v cygpath >/dev/null; then cygpath -m "$1"; else echo "$1"; fi
}

VARS=(-var "disk_size=$DISK" -var "memory=$MEMORY" -var "cpus=$CPUS" -var "headless=$HEADLESS")

if [[ -n $ISO ]]; then
  # The 22.04 desktop ISO ignores autoinstall and just boots to a live desktop.
  if [[ $(basename "$ISO") == *desktop* ]]; then
    echo "Error: $ISO looks like a desktop ISO; use the live server ISO (ubuntu-22.04.5-live-server-amd64.iso)" >&2
    exit 1
  fi
  if [[ $ISO =~ ^[a-z]+:// ]]; then
    VARS+=(-var "iso_url=$ISO")
  else
    [[ -f $ISO ]] || { echo "Error: no such file: $ISO" >&2; exit 1; }
    ISO_ABS="$(cd "$(dirname "$ISO")" && pwd)/$(basename "$ISO")"
    VARS+=(-var "iso_url=$(native_path "$ISO_ABS")")
    CHECKSUM=${CHECKSUM:-none}
  fi
fi
[[ -n $CHECKSUM ]] && VARS+=(-var "iso_checksum=$CHECKSUM")

mkdir -p "$(dirname "$BOX_FILE")"
BOX_ABS="$(cd "$(dirname "$BOX_FILE")" && pwd)/$(basename "$BOX_FILE")"
rm -f "$BOX_ABS"
VARS+=(-var "output_box=$(native_path "$BOX_ABS")")

TEMPLATE=$(native_path "$SCRIPT_DIR/ubuntu-22.04.pkr.hcl")

echo "==> Installing Packer plugins..."
packer init "$TEMPLATE"

echo "==> Building box (the unattended install takes 15-30 minutes)..."
# Packer's working directory holds the VM and export; keep it next to the template.
cd "$SCRIPT_DIR"
packer build -force "${VARS[@]}" "$TEMPLATE"

echo
echo "Done: $BOX_ABS"

if $ADD_BOX; then
  vagrant box add --force --name ubuntu-22.04-local "$(native_path "$BOX_ABS")"
  echo "Use it with: VAGRANT_BOX=ubuntu-22.04-local vagrant up"
else
  cat <<EOF

Try it locally:
  vagrant box add --name ubuntu-22.04-local "$BOX_ABS"
  VAGRANT_BOX=ubuntu-22.04-local vagrant up

Publish it:
  ./push-to-r2.sh -f "$BOX_ABS" -v <version> -n <box name>
EOF
fi
