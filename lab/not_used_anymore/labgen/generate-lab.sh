#!/bin/bash

:<< C
This script will generate a lab with 3 VMs:
    - VM1: Apache server
    - VM2: Client with httperf
    - VM3: Packet capture
C

VM1_NAME="apache_server_vm"
VM2_NAME="client_httperf_vm"
# VM3_NAME="packet_capture_vm"
BRIDGE_NAME="virbr10"
ISO_PATH="debian.iso"

get_host_ip() {
    # This assumes you are using a common subnet. You might want to adjust the grep command if not.
    ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d/ -f1 | head -n 1
}
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
    sleep 3
    if ! ps -p "$HTTP_SERVER_PID" &> /dev/null; then
        echo "HTTP server could not be started"
        # exit 1
    else
        echo "HTTP server started successfully"
    fi
}


stop_http_server() {
    if [ -f "/tmp/http_server.pid" ]; then
        HTTP_SERVER_PID=$(cat /tmp/http_server.pid)
        kill "$HTTP_SERVER_PID"
        rm /tmp/http_server.pid
    fi
}

# VM configuration
configure_vm() {
    DISK_SIZE=6
    RAM="2048"

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
    local log_file="/tmp/log/${vm_name}_install.log"
    local host_ip=$(get_host_ip)

    virt-install \
        --name "${vm_name}" \
        --ram ${RAM} \
        --initrd-inject="preseed.cfg" \
        --disk path="/var/lib/libvirt/images/${vm_name}.qcow2,size=${DISK_SIZE}" \
        --vcpus 1 \
        --os-variant debian12 \
        --network network=${BRIDGE_NAME} \
        --graphics spice \
        --console pty,target_type=serial \
        --location ${ISO_PATH} \
        --extra-args "console=tty1 url=http://${host_ip}:8000/preseed.cfg" \
        --debug 2>&1 | tee "${log_file}" &
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
    wait
    echo "Done"
}

# Run the main script if no args
if [ $# -eq 0 ]; then
    main
fi

# if arg delete is passed, delete the lab
if [ "$1" == "delete" ]; then
    stop_http_server
    virsh destroy ${VM1_NAME}
    virsh undefine ${VM1_NAME}
    virsh destroy ${VM2_NAME}
    virsh undefine ${VM2_NAME}
    virsh net-destroy ${BRIDGE_NAME}
    virsh net-undefine ${BRIDGE_NAME}
    rm /var/lib/libvirt/images/${VM1_NAME}.qcow2
    rm /var/lib/libvirt/images/${VM2_NAME}.qcow2
    # rm debian.iso
    # rm preseed.cfg
    echo "Lab deleted"
    exit 0
fi