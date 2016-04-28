#!/bin/bash
#Title:	Ettus USRP optimization and storage init
#Author: Simon Olvhammar

# Create and mount RAMDisk
sudo mkdir /tmp/ramdisk
sudo chmod 777 /tmp/ramdisk
sudo mount -t tmpfs -o size=16384M tmpfs /tmp/ramdisk

# Configure Network Buffers
sudo sysctl -w net.core.rmem_max=33554432
sudo sysctl -w net.core.wmem_max=33554432

# Initalize Ettus USRP PCIe drivers
sudo ~/bin/niusrprio-installer/niusrprio_pcie start

#Message to User
echo "Ettus USRP PCIe drivers activated"
echo "RAMDisk is 8GB in size and located at /tmp/ramdisk"
