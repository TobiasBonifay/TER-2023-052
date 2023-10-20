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
    for cmd in virt-install virsh wget python3; do
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

# Run the HTTP server to serve the preseed file
start_http_server() {
    echo "Starting HTTP server..."
    python3 -m http.server 8000 &> /dev/null &
    HTTP_SERVER_PID=$!
    echo "HTTP server started with PID: $HTTP_SERVER_PID"
    sleep 3
    if ! ps -p $HTTP_SERVER_PID &> /dev/null; then
        echo "HTTP server could not be started"
        exit 1
    else
        echo "HTTP server started"
    fi
}

# VM configuration
configure_vm() {
    VM1_NAME="apache_server_vm"
    VM2_NAME="client_httperf_vm"
    VM3_NAME="packet_capture_vm"
    DISK_SIZE="5G"
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
        --disk size=${DISK_SIZE} \
        --vcpus 1 \
        --os-type linux \
        --os-variant debian12 \
        --network network=${BRIDGE_NAME} \
        --graphics none \
        --console pty,target_type=serial \
        --location ${ISO_PATH} \
        --extra-args 'console=ttyS0,115200n8 serial auto url=http://localhost:8000/preseed.cfg'
}

# Main script
main() {
    check_commands
    check_iso
    start_http_server
    configure_vm
    echo "Creating the VMs..."
    create_vm ${VM1_NAME}
    create_vm ${VM2_NAME}
    create_vm ${VM3_NAME}
    echo "Done"
    echo "Cleaning up..."
    kill $HTTP_SERVER_PID
    echo "Done"
}

# Run the main script
main