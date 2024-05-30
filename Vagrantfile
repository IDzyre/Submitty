def gen_script()
  setup_cmd = 'bash ${GIT_PATH}/.setup/'
  
  setup_cmd += 'vagrant/setup_vagrant.sh --no_submissions'

  script = <<SCRIPT
    GIT_PATH=/usr/local/submitty/GIT_CHECKOUT/Submitty
    DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
    VERSION=$(lsb_release -sr | tr '[:upper:]' '[:lower:]')
    mkdir -p ${GIT_PATH}/.vagrant/logs
    cd /usr/local/submitty/GIT_CHECKOUT
    sudo rm Submitty -r
    git clone https://github.com/Submitty/Submitty.git
    git clone https://github.com/Submitty/AnalysisTools.git
    git clone https://github.com/Submitty/AnalysisToolsTS.git
    git clone https://github.com/Submitty/Lichen.git
    git clone https://github.com/Submitty/RainbowGrades.git
    git clone https://github.com/Submitty/Tutorial.git
    git clone https://github.com/Submitty/SysadminTools.git
    git clone https://github.com/Submitty/Localization.git
SCRIPT
  return script
end

Vagrant.configure("2") do |config|
  config.vm.box = "perk/ubuntu-2204-arm64"
  config.ssh.insert_key = false
  vm_name = 'ubuntu-22.04'
  config.vm.provider "qemu" do |qe|
    qe.machine = 'virt,accel=tcg,highmem=on'
    qe.memory = '8G'
    qe.net_device = "virtio-net-pci"
    qe.cpu = "max"
    qe.qemu_dir = "/usr/bin/qemu-system-x86_64"
    qe.smp = 3
    config.vm.boot_timeout = 600
  end
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.define vm_name, primary: true do |ubuntu|
    ubuntu.vm.provision 'shell', inline: gen_script()
  end
end