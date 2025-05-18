#!/usr/bin/sudo python
import socket
import ipaddress
import subprocess
import os
import fcntl
import struct

ifname = (socket.if_nameindex())

def iptables_conf(packet_ip,subnet_ip,interf):

   cmd=f"iptables -t nat -A POSTROUTING -s {packet_ip} -o {interf} -j MASQUERADE"
   lcmd=f"iptables -t nat -L POSTROUTING | grep {subnet_ip}"

   if len(subprocess.getoutput(lcmd)) > 0:
        print("Already exists")
   else:
        print(cmd)
        subprocess.run(cmd,shell=True)
        print(f"Rule has been added")

for i in ifname:
        if i[1] == 'eth1' or i[1] == 'wlan0':
                intf = i[1]
                ipaddr = os.popen(f"ip addr show {i[1]}").read().split("inet ")[1].split(" brd")[0]
                subn = '.'.join(ipaddr.split('.')[:3])
                break
        else:
                intf = 'fail'

#hostname = socket.gethostname()
#ipv4, netb = ipaddr.split('/') 
#print(len(subprocess.getoutput("iptables -t nat -L POSTROUTING | grep {subnet_ip}")))
#subn = '.'.join(ipaddr.split('.')[:3])
#print(hostname)
#print(intf)
#print(ipaddr)
#print(subn)
if intf != 'fail':
        iptables_conf(ipaddr,subn,intf)
else:
        print("IPVlan Interface not found")
