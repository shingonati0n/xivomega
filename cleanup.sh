#!/bin/bash
echo "Removing elements from XIVOmega.."
echo "Cleaning routes"
sudo -S ip route del 124.150.157.0/24 via 10.88.0.7
sudo -S ip route del 153.254.80.0/24 via 10.88.0.7
sudo -S ip route del 202.67.52.0/24 via 10.88.0.7
sudo -S ip route del 204.2.29.0/24 via 10.88.0.7
sudo -S ip route del 80.239.145.0/24 via 10.88.0.7
echo "Stopping and removing podman containers and network..."
sudo -S podman stop xivomega
sudo -S podman rm xivomega
sudo -S podman network rm xivlanc
echo "Removing ipvlan adapter and ip"
sudo -S ip link set xivlanh down
sudo -S ip link del xivlanh
echo "Default routes restored, please check: "
sudo -S ip route
echo "All Done, Thank you for Playing"