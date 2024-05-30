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
  config.vm.provider :libvirt do |libvirt|
      libvirt.features = ["apic"]
      libvirt.cpu_mode = 'host-passthrough'
      libvirt.cpus = 2
      libvirt.machine_arch = "aarch64"
      # appears these are needed otherwise most VMs appear to hang, possibly waiting for a key to pressed
      libvirt.input :type => "mouse", :bus => "usb"
      libvirt.input :type => "keyboard", :bus => "usb"
      libvirt.usb_controller :model => "qemu-xhci"
  
      libvirt.machine_type = "virt-5.2"
  
      # javiervela/ubuntu20.04-arm64 requires the following settings in addition
      #libvirt.machine_arch = "aarch64"
      #libvirt.channel :type => 'unix', :target_type => 'virtio', :target_name => 'org.qemu.guest_agent.0', :target_port => '1', :source_path => '/var/lib/libvirt/qemu/channel/target/domain-1-ubuntu20.04/org.qemu.guest_agent.0', :source_mode => 'bind'
  end
  
  config.vm.define vm_name, primary: true do |ubuntu|
    ubuntu.vm.provision 'shell', inline: gen_script()
  end
end