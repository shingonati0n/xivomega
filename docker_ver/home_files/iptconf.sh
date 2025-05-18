#!/bin/bash
ip route add 192.168.100.82 via 10.88.0.1
iptables -t nat -A POSTROUTING -s 192.168.100.114/24 -o eth0 -j MASQUERADE
#iptables -t nat -A POSTROUTING -s 10.88.0.7/16 -o eth1 -j MASQUERADE
