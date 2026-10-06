#!/usr/bin/env bash
# Build and install VirtualBox Guest Additions from the ISO Packer uploaded.
export DEBIAN_FRONTEND=noninteractive
ISO=/home/vagrant/VBoxGuestAdditions.iso

apt-get install -y build-essential dkms bzip2 "linux-headers-$(uname -r)"

mkdir -p /mnt/vbox
mount -o loop "$ISO" /mnt/vbox
# Exits non-zero when there is no X server to configure, even on success.
/mnt/vbox/VBoxLinuxAdditions.run --nox11 || true
umount /mnt/vbox
rm -rf /mnt/vbox "$ISO"

modinfo vboxsf >/dev/null || { echo "Guest additions failed to install" >&2; exit 1; }
