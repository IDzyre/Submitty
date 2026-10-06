packer {
  required_plugins {
    virtualbox = {
      version = ">= 1.1.0"
      source  = "github.com/hashicorp/virtualbox"
    }
    vagrant = {
      version = ">= 1.1.0"
      source  = "github.com/hashicorp/vagrant"
    }
  }
}

variable "iso_url" {
  type    = string
  default = "https://releases.ubuntu.com/22.04/ubuntu-22.04.5-live-server-amd64.iso"
}

variable "iso_checksum" {
  type    = string
  default = "file:https://releases.ubuntu.com/22.04/SHA256SUMS"
}

variable "output_box" {
  type    = string
  default = "output/ubuntu-22.04-virtualbox.box"
}

variable "cpus" {
  type    = number
  default = 2
}

variable "memory" {
  type    = number
  default = 4096
}

# In MB. The disk is dynamically allocated, so this is only the maximum size.
variable "disk_size" {
  type    = number
  default = 65536
}

variable "headless" {
  type    = bool
  default = true
}

source "virtualbox-iso" "ubuntu" {
  vm_name       = "ubuntu-22.04-base"
  guest_os_type = "Ubuntu_64"
  iso_url       = var.iso_url
  iso_checksum  = var.iso_checksum

  cpus      = var.cpus
  memory    = var.memory
  disk_size = var.disk_size
  headless  = var.headless

  hard_drive_interface     = "sata"
  hard_drive_discard       = true
  hard_drive_nonrotational = true

  # Serves http/user-data and http/meta-data to the installer.
  http_directory = "${path.root}/http"

  # Drop to the GRUB console and boot the installer with autoinstall enabled.
  boot_wait = "5s"
  boot_command = [
    "c<wait>",
    "linux /casper/vmlinuz --- autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/<enter><wait>",
    "initrd /casper/initrd<enter><wait>",
    "boot<enter>",
  ]

  ssh_username = "vagrant"
  ssh_password = "vagrant"
  ssh_timeout  = "60m"
  # The installer's own SSH server is up during install and rejects us; keep retrying until the real system boots.
  ssh_handshake_attempts = 500

  shutdown_command = "echo 'vagrant' | sudo -S shutdown -P now"

  guest_additions_mode = "upload"
  guest_additions_path = "VBoxGuestAdditions.iso"

  vboxmanage = [
    ["modifyvm", "{{ .Name }}", "--graphicscontroller", "vmsvga"],
    ["modifyvm", "{{ .Name }}", "--vram", "16"],
    ["modifyvm", "{{ .Name }}", "--rtcuseutc", "on"],
    ["modifyvm", "{{ .Name }}", "--audio-enabled", "off"],
  ]
}

build {
  sources = ["source.virtualbox-iso.ubuntu"]

  provisioner "shell" {
    execute_command   = "echo 'vagrant' | {{ .Vars }} sudo -S -E bash -eu '{{ .Path }}'"
    script            = "${path.root}/scripts/update.sh"
    expect_disconnect = true
  }

  provisioner "shell" {
    execute_command = "echo 'vagrant' | {{ .Vars }} sudo -S -E bash -eu '{{ .Path }}'"
    pause_before    = "30s"
    scripts = [
      "${path.root}/scripts/vagrant.sh",
      "${path.root}/scripts/guest-additions.sh",
      "${path.root}/scripts/cleanup.sh",
    ]
  }

  post-processor "vagrant" {
    output            = var.output_box
    compression_level = 6
  }
}
