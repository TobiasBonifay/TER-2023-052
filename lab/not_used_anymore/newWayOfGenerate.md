Install KVM stuff
```bash
sudo apt update
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
```

Add user to group
```bash
sudo adduser `id -un` libvirt
sudo adduser `id -un` kvm
```

```bash
sudo apt install virt-manager
```
    
Adding a new network bridge
```bash
sudo nano /etc/network/interfaces
```
```text
auto br0
iface br0 inet dhcp
bridge_ports eth0
bridge_stp off
bridge_fd 0
bridge_maxwait 0
```
```bash
sudo systemctl restart networking
```


Install apache benchmark
```bash
sudo apt install apache2-utils
```

Install python dependencies
```bash
pip install -r requirements.txt
```

