#!/bin/bash
echo "Checking IPTables rules, creating if not there already"
python /home/iptcheck.py
echo "Current podman IPtables rules"
iptables -t nat -nL POSTROUTING  
