def gen_script(machine_name)
  no_submissions = !ENV.fetch('NO_SUBMISSIONS', '').empty?
  
  setup_cmd = 'bash ${GIT_PATH}/.setup/'
  setup_cmd += 'vagrant/setup_vagrant.sh'
  if no_submissions
    setup_cmd += ' --no_submissions'
  end
  
  setup_cmd += " 2>&1 | tee ${GIT_PATH}/.vagrant/logs/#{machine_name}.log"

  script = <<SCRIPT
    GIT_PATH=/usr/local/submitty/GIT_CHECKOUT/Submitty
    DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
    VERSION=$(lsb_release -sr | tr '[:upper:]' '[:lower:]')
    mkdir -p ${GIT_PATH}/.vagrant/logs
    #{setup_cmd}
SCRIPT
  return script
end
# Don't buffer output.
$stdout.sync = true
$stderr.sync = true

require 'json'

ON_CI = !ENV.fetch('CI', '').empty?

Vagrant.configure(2) do |config|
  if Vagrant.has_plugin?('vagrant-env')
    config.env.enable
  end
  config.ssh.username = 'root'
  vm_name = 'ubuntu-22.04'
  config.vm.define vm_name, primary: true do |ubuntu|
    ubuntu.vm.network 'forwarded_port', guest: 1511, host: ENV.fetch('VM_PORT_SITE', 1511)
    ubuntu.vm.network 'forwarded_port', guest: 8443, host: ENV.fetch('VM_PORT_WS',   8443)
    ubuntu.vm.network 'forwarded_port', guest: 5432, host: ENV.fetch('VM_PORT_DB',  16442)
    ubuntu.vm.network 'forwarded_port', guest: 7000, host: ENV.fetch('VM_PORT_SAML', 7000)
    ubuntu.vm.network 'forwarded_port', guest:   22, host: ENV.fetch('VM_PORT_SSH',  2222), id: 'ssh'
    # ubuntu.vm.provision 'shell', inline: gen_script(vm_name)
  end

  config.vm.provider "libvirt" do |libvirt, override|
    override.vm.box = "submitty_temp/ubuntu-arm"
    libvirt.driver = "qemu" # Use QEMU as the driver
    libvirt.memory = 2048 # Set memory size
    libvirt.cpus = 2 # Set number of CPUs
    libvirt.cpu_mode = "host-model" # Use host-model CPU mode
    libvirt.qemu_use_session = true # Use QEMU session mode
    libvirt.machine_type = "virt" # Use the 'virt' machine type for ARM
    libvirt.graphics_type = 'none'
    libvirt.features = []
    libvirt.inputs = []
    libvirt.machine_arch = "aarch64" # Specify ARM architecture
    # libvirt.net_device = "virtio-net-device" # Use virtio network device
  end

  config.vm.provision :shell, :inline => " sudo timedatectl set-timezone America/New_York", run: "once"
end