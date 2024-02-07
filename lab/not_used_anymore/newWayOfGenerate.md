Install KVM stuff
```bash
sudo apt update
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients virt-manager
```

Add user to group
```bash
sudo adduser `id -un` libvirt
sudo adduser `id -un` kvm
```

```bash
sudo apt install virt-manager
```

Adding a new network bridge, for instance br0
```bash
sudo apt-get install bridge-utils
sudo nano /etc/network/interfaces
```
```text
auto br0
iface br0 inet dhcp
    bridge_ports eth0
        address 192.168.100.100
        netmask 255.255.255.0
        gateway 192.168.100.1
        broadcast 192.168.100.255
    bridge_stp off
    bridge_fd 0
    bridge_maxwait 0
```
```bash
# sudo systemctl restart networking
sudo systemctl restart NetworkManager
```

Create a new virtual machine, for instance

```bash
virt-install --name=apache-vm --vcpus=2 --ram=2048 --cdrom=ubuntu.iso --disk path=/var/lib/libvirt/images/ubuntu-vm.qcow2,size=20 --os-variant=ubuntu20.04 --network bridge=br0
virt-install --name=client-vm --vcpus=2 --ram=2048 --cdrom=ubuntu.iso --disk path=/var/lib/libvirt/images/ubuntu-vm.qcow2,size=20 --os-variant=ubuntu20.04 --network bridge=br0
```

Start the virtual machine

```bash
virsh start apache-vm
virsh start client-vm
```

Install apache2

```bash
sudo apt install apache2
```

Install apache benchmark
```bash
sudo apt install apache2-utils
```

Install python dependencies
```bash
sudo apt install python3-pip
pip install -r requirements.txt
```
