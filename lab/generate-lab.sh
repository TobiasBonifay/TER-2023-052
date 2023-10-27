#!/bin/bash

:<< C
This script will generate a lab with 3 VMs:
    - VM1: Apache server
    - VM2: Client with httperf
    - VM3: Packet capture
C

# Check if all commands are available
check_commands() {
    echo "Checking if all commands are available"
    for cmd in virt-install virsh wget; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "$cmd could not be found"
            exit 1
        else
            echo "$cmd found"
        fi
    done
}

# Check if the ISO is available
check_iso() {
    echo "Checking if the ISO is available"
    if [ ! -f debian.iso ]; then
        wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.2.0-amd64-netinst.iso -O debian.iso
    else
        echo "ISO found"
    fi
}

# VM configuration
configure_vm() {
    VM1_NAME="apache_server_vm"
    VM2_NAME="client_httperf_vm"
    VM3_NAME="packet_capture_vm"
    DISK_SIZE=6G
    RAM="2048"
    BRIDGE_NAME="virbr10"
    ISO_PATH="debian.iso"

    if ! virsh net-info $BRIDGE_NAME &> /dev/null; then
        virsh net-define <(echo "
<network>
  <name>${BRIDGE_NAME}</name>
  <forward mode='nat'/>
  <bridge name='${BRIDGE_NAME}' stp='on' delay='0'/>
  <ip address='192.168.100.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.100.10' end='192.168.100.254' />
    </dhcp>
  </ip>
</network>")
        virsh net-start ${BRIDGE_NAME}
        virsh net-autostart ${BRIDGE_NAME}
    fi
}

# Create VM function
create_vm() {
    local vm_name=$1
    virt-install \
        --name "${vm_name}" \
        --ram ${RAM} \
        --disk path=/var/lib/libvirt/images/"${vm_name}".qcow2,size=${DISK_SIZE} \
        --vcpus 1 \
        --os-variant debian12 \
        --network bridge=${BRIDGE_NAME} \
        --graphics none \
        --console pty,target_type=serial \
        --location ${ISO_PATH} \
        --extra-args 'console=tty0 url=http://localhost:8000/preseed.cfg'
}

# Main script
main() {
    check_commands
    check_iso
    configure_vm
    echo "Creating the VMs..."
    create_vm ${VM1_NAME}
    create_vm ${VM2_NAME}
    echo "Done"
}

# Run the main script
main
