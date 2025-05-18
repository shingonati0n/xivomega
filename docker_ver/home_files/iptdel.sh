#!/bin/bash
iptables -t nat -D POSTROUTING -s 192.168.100.114/24 -o eth0 -j MASQUERADE
iptables -t nat -D POSTROUTING -s 10.88.0.7/16 -o eth1 -j MASQUERADE
