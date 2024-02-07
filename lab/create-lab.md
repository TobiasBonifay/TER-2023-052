# Lab Setup Guide

This guide will walk you through setting up a lab environment using KVM, including creating a network bridge and setting
up virtual machines for an Apache server and a client.

## Prerequisites

Ensure your system supports virtualization and you have sudo or root access.

## Steps

1. **Install KVM and Other Required Packages:**

    ```bash
    sudo apt update
    sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
    ```

2. **Add Your User to the Libvirt Group:**

    ```bash
    sudo usermod -aG libvirt $(whoami)
    ```

3. **Set Up a Network Bridge:**

   Open the network interfaces configuration file:

    ```bash
    sudo nano /etc/network/interfaces
    ```

   Add the following lines to the file:

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

   Save and close the file, then restart the networking service:

    ```bash
    sudo systemctl restart networking # or sudo systemctl restart NetworkManager
    ```

4. **Create Virtual Machines:**

   Replace `/path/to/ubuntu.iso` with the actual path to your ISO file:

    ```bash
    virt-install --name=apache-vm --vcpus=2 --ram=2048 --cdrom=/path/to/ubuntu.iso --disk path=/var/lib/libvirt/images/apache-vm.qcow2,size=20 --os-variant=ubuntu20.04 --network bridge=br0
    virt-install --name=client-vm --vcpus=2 --ram=2048 --cdrom=/path/to/ubuntu.iso --disk path=/var/lib/libvirt/images/client-vm.qcow2,size=20 --os-variant=ubuntu20.04 --network bridge=br0
    ```

5. **Start the Virtual Machines:**

    ```bash
    virsh start apache-vm
    virsh start client-vm
    ```

6. **On the Apache Server, Install Apache2:**

    ```bash
    sudo apt update
    sudo apt install -y apache2
    ```

7. **On Both the Client and Apache Server:**

   Install git and clone the repository:

    ```bash
    sudo apt install -y git
    git clone https://github.com/TobiasBonifay/TER-2023-052.git
    cd TER-2023-052/lab/
    ```

   Install the required packages:

    ```bash
    sudo apt install -y python3-pip
    pip3 install -r requirements.txt
    ```

   Modify the configuration file to match your environment settings:

    ```bash
    nano config.json
    ```

   Update the IP addresses of each VM to match the IP addresses of the virtual machines. Use `ip a` to find the IP
   addresses of the virtual machines.

   Change the `cgrouppath` to the path of the cgroup of the virtual machines.

8. **On the Host Machine, Start the Client:**

    ```bash
    sudo python3 Main.py
    ```
