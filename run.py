#!/usr/bin/python
import socket
import sys 
import os
import ipaddress
import struct
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
from getpass import getpass
import shlex
import time
import io
import configparser
import gi
gi.require_version("NM", "1.0")
from gi.repository import GLib, NM
from pathlib import Path
import random 
from random import randint, sample

#append py_modules to PYTHONPATH
sys.path.append(str(Path(__file__).parent / "py_modules"))

from scapy.all import ARP, Ether, srp

#pth = "/home/deck/xivomega/"
pth = os.getcwd()

#region aux functions and classes
class WorkerClass:
	def get_current_device(self):
		client = NM.Client.new(None)
		devices = client.get_devices()
		netdevices = {}
		curr_netd = ""
		saved_eth = {}
		saved_wifi = {}

		for device in devices:
		    netdevices[device.get_iface()] = device.get_type_description() + ";" + device.get_state().value_nick

		i = 1
		j = 1
	#priority is ethernet first, then wifi - if more than one of each, then make user pick
		for netd, netdet in netdevices.items():
			netd_type, netd_state = netdet.split(";")
			if netd_type in ("ethernet") and netd_state in ("activated"):
				saved_eth[i] = netd #ethernet = enp0s*
				i += 1
			elif netd_type in ("wifi") and netd_state in ("activated"):
				saved_wifi[j] = netd #wifi = wlan* or wlp*
				j += 1

		if len(saved_eth) > 1:
			while True:
				print("More than one Ethernet adapter has been detected - Please choose one now to proceed: ")
				print("To avoid picking everytime, you can save the name of your preferred adapter into config.ini in this folder")
				print("Detected Ethernet Adapters: ")
				for k,v in saved_eth.items():
					print(f"{k} - {v}")
				pref_adapter = input("Enter the number of the adapter you would like to use: ")
				try:
					curr_netd = saved_eth.get(pref_adapter)
				except Exception as e:
					print("The option selected is not valid. Please select a valid option")
					continue
				else:
					break
		elif len(saved_eth) == 1:
			curr_netd = saved_eth.get(1)
		
		if len(saved_eth) == 0 and len(saved_wifi) > 1:
			while True:
				print("More than one Wifi adapter has been detected - Please choose one now to proceed: ")
				print("To avoid picking everytime, you can save the name of your preferred adapter into config.ini in this folder")
				print("Detected Wifi Adapters: ")
				for k,v in saved_wifi.items():
					print(f"{k} - {v}")
				pref_adapter = input("Enter the number of the adapter you would like to use: ")
				try:
					curr_netd = saved_wifi.get(pref_adapter)
				except Exception as e:
					print("The option selected is not valid. Please select a valid option")
					continue
				else:
					break
		elif len(saved_wifi) == 1 and len(saved_eth) == 0:
			curr_netd = saved_wifi.get(1)
				
		return curr_netd #you get nothing, you lose, good day, sir!
	
	def validateCustomNetDev(self,dev_name):
		client = NM.Client.new(None)
		devices = client.get_devices()
		netdevices = {}
		valid_dev = ''

		for device in devices:
		    netdevices[device.get_iface()] = device.get_type_description() + ";" + device.get_state().value_nick

		if dev_name not in netdevices.keys():
			print("Invalid Network Adapter specified in config file")
			print("XIVOmega will now retrieve the actual list of devices, so please pick one")
			valid_dev = self.get_current_device()
		else:
			valid_dev = dev_name 

		return valid_dev


	def fixPodmanStorage(self):
		podstorecmd = f"cp {pth}/storage/storage.conf /etc/containers/storage.conf"
		psf = subprocess.run(shlex.split(podstorecmd),check=True,capture_output=True)
		try:
		   	if psf.returncode==0:
		   		#print(f"/etc/containers/storage.conf was patched")
		   		pass
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())

	def SetRoutes(self,rt14):
		for r in rt14:
			way = f"ip route add {r} via 10.88.0.7"
			nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
			try:
		   		if nav.returncode==0:
		   			print(f"route to {r} added")
			except subprocess.CalledProcessError as e:
				print(e.stderr.decode())

	def ClearNetavarkRules(self):
		subprocess.run(shlex.split("iptables -F INPUT"),check=True,capture_output=True)
		subprocess.run(shlex.split("iptables -F FORWARD"),check=True,capture_output=True)
		subprocess.run(shlex.split("iptables -F OUTPUT"),check=True,capture_output=True)

	def PrintLogo(self):
		subprocess.call(pth + "/titleCard.sh")

	def ReconnectProtocol(self):
		subprocess.run(shlex.split("podman restart xivomega"),check=True,capture_output=True)
		subprocess.run(shlex.split("podman exec xivomega iptables -t nat -F POSTROUTING"),check=True,capture_output=True)
		subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)

	def CDTimer(self):
		for i in range(10, 0, -1):
			print(i, end = ' \r')
			time.sleep(1)

	def CreateHostAdapter(self,virtual_ip,netbits,broadcast):
		ntdev = self.get_current_device()
		ipvl1 = f"ip link add xivlanh link {ntdev} type ipvlan mode l2"
		ipvl2 = f"ip addr add {virtual_ip}/{netbits} brd {broadcast} dev xivlanh"
		ipvl3 = f"ip link set xivlanh up"
		
		try:
			ipvlh1 = subprocess.run(shlex.split(ipvl1),check=True,capture_output=True)
			if ipvlh1.returncode == 0:
				print("host ipvlan interface created")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		
		try:
			ipvlh2 = subprocess.run(shlex.split(ipvl2),check=True,capture_output=True)
			if ipvlh2.returncode == 0:
				print(f"host ipvlan interface IP is {virtual_ip}")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		
		try:
			ipvlh3 = subprocess.run(shlex.split(ipvl3),check=True,capture_output=True)
			if ipvlh3.returncode == 0:
				print("host ipvlan interface is up")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())

	def SelfDestructProtocol(self):
		print("Terminating Mitigation Protocol and XIVOmega")
		for r in roadsto14:
			way = f"ip route del {r} via 10.88.0.7"
			nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
			try:
		   		if nav.returncode==0:
		   			print(f"route to {r} deleted")
			except subprocess.CalledProcessError as e:
					print(e.stderr.decode())
		try:
			panto = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if panto.returncode == 0:
				print("XIVOmega Container Stopped")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		try:
			atomic = subprocess.run(shlex.split("podman network disconnect xivlanc xivomega"),check=True,capture_output=True)
			if atomic.returncode == 0:
				print("XIVOmega IPVlan Disconnected")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		try:
			flame = subprocess.run(shlex.split("podman network rm xivlanc"),check=True,capture_output=True)
			if flame.returncode == 0:
				print("XIVOmega IPVlan Removed")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		try:
			bworld = subprocess.run(shlex.split("podman rm xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				print("XIVOmega Container removed")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		try:
			lanhdie = subprocess.run(shlex.split("ip link set xivlanh down"),check=True,capture_output=True)
			if lanhdie.returncode == 0:
				print("Host IPVlan turned off")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		try:
			lanhrm = subprocess.run(shlex.split("ip link del xivlanh"),check=True,capture_output=True)
			if lanhrm.returncode == 0:
				print("Host IPVlan removed")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		print("All done - Goodbye")

#Self Cleaning - in case last session was ended by user and they didn't closed using Ctrl+C
	def SelfCleaningProtocol(self):
		ccnt = 0
		for r in roadsto14:
			way = f"ip route del {r} via 10.88.0.7"
			try:
				nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
				if nav.returncode==0:
		   			ccnt = ccnt + 1
		   			#print(f"route to {r} deleted")
			except subprocess.CalledProcessError as e:
				#print(e.stderr.decode())
				pass
		try:
			bworld = subprocess.run(shlex.split("podman stop xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			#print(e.stderr.decode())
		try:
			bworld = subprocess.run(shlex.split("podman rm xivomega"),check=True,capture_output=True)
			if bworld.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			#print(e.stderr.decode())
		try:
			flame = subprocess.run(shlex.split("podman network rm xivlanc"),check=True,capture_output=True)
			if flame.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			#print(e.stderr.decode())
		try:
			lanhdie = subprocess.run(shlex.split("ip link set xivlanh down"),check=True,capture_output=True)
			if lanhdie.returncode == 0:
				ccnt = ccnt + 1
		except subprocess.CalledProcessError as e:
			pass
			#print(e.stderr.decode())
		try:
			lanhrm = subprocess.run(shlex.split("ip link del xivlanh"),check=True,capture_output=True)
			if lanhrm.returncode == 0:
				ccnt = ccnt +1
		except subprocess.CalledProcessError as e:
			pass
		if (ccnt > 0):
			print("Dangling elements from previous play session detected. CleanUp Protocol Activated and Completed")


#read config file

#get subnet mask and subnet
def cidr_to_netmask(cidr):
	network, net_bits = cidr.split('/')
	host_bits = 32 - int(net_bits)
	netmask = socket.inet_ntoa(struct.pack('!I',(1 << 32) - (1 << host_bits)))
	return network, netmask

#get config files parms
def read_config():
	cfg = configparser.ConfigParser()
	cfg.read(pth + '/config.ini')

	ipvlan_host = cfg.get('General','ipvlan_host').lower()
	ipvlan_cont = cfg.get('General','ipvlan_cont').lower()
	pref_netdev = cfg.get('General','network_adapter')

	#create dictionary with Config Parms
	cfg_val = {
	'ipvlan_host': ipvlan_host,
	'ipvlan_cont': ipvlan_cont,
	'network_adapter': pref_netdev
	}

	return cfg_val

#validate IP Address
def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

#scapy methods to get network info - get all IPs in use
def scan(ip):
	arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
	result = srp(arp_request, timeout=1, verbose=False)[0]
	devices = [{'ip': received.psrc, 'mac': received.hwsrc} for sent, received in result]
	return devices

def get_device_names(devices):
	device_names = []
	for device in devices:
		try:
			host_name, _, _ = socket.gethostbyaddr(device['ip'])
			device_names.append({'ip': device['ip'], 'mac': device['mac'], 'name': host_name})
		except socket.herror:
		   
			device_names.append({'ip': device['ip'], 'mac': device['mac'], 'name': 'Unknown'})
	return device_names

def get_vip_lip(ipaddr,subnaddr):
	ips = []
	target_ip = ipaddr
	devices_list = scan(target_ip)
	for device in devices_list:
		for k,v in device.items():
			if k in 'ip':
				ips.append(device[k])
	devices_with_names = get_device_names(devices_list)
	
	print("IPs in use:")
	for uip in ips:
		print(uip)
	allip = [str(ip) for ip in ipaddress.IPv4Network(subnaddr)]
	useable_ip = allip[3:-2]
	# Removing elements present in other list
	# using list comprehension
	res = [i for i in useable_ip if i not in ips]
	print("Chosen IPs:")
	vip, lip = sample(res,2)
	print(f"VlanIP: {vip}")
	print(f"Last IP: {lip}")
	return vip, lip

#end of scapy methods


#end aux region

#Static knicknacks

roadsto14 = ["124.150.157.0/24","153.254.80.0/24","202.67.52.0/24","204.2.29.0/24","80.239.145.0/24"]

#Custom Classes and Exceptions
class RootRequiredError(RuntimeError):
    pass

class InvalidIPException(Exception):
	pass

class ConnectionFailedError(Exception):
	pass

class NonExistentException(Exception):
	pass

#main program
def __main__() -> int:
	
	#bring config parms
	config_v = read_config()

	#check this is running in Linux:
	if sys.platform != 'linux':
		print("Only Linux is supported for this app")
		return -1

	#Check Python Version - 3.8 
	if sys.version_info < (3, 8):
		print("This program requires at least python 3.8")
		return -1

	omegaBeetle = WorkerClass()
	rc = 0

	try:
		#check if running as sudo
		if os.getuid() != 0:
			raise RootRequiredError
		#patch /etc/containers/storage.conf 
		omegaBeetle.SelfCleaningProtocol()
		omegaBeetle.fixPodmanStorage()
		#get IP address with cidr from wlan0 - need to add eth0 for cabled connections if any

		#override if config file is populated!
		netdev = ''

		if config_v['network_adapter'] == 'default':
			netdev = omegaBeetle.get_current_device()
		else:
			netdev = omegaBeetle.validateCustomNetDev(config_v['network_adapter'])

		ipv4 = os.popen('ip addr show ' + netdev).read().split("inet ")[1].split(" brd")[0] 
		#print(ipv4)
		ipv4n, netb = ipv4.split('/')
		
		#print(cidr_to_netmask(ipv4)[1])
		subn = ipaddress.ip_network(cidr_to_netmask(ipv4)[0]+'/'+cidr_to_netmask(ipv4)[1], strict=False)
		sdgway = '.'.join(ipv4n.split('.')[:3]) + ".1"
		#brd = '.'.join(ipv4n.split('.')[:3]) + ".255"
		sdsubn = str(subn.network_address) + "/" + netb
		
		#get first and last ips from current network
		
		#use config file - validate if values are not Default first
		nt = ipaddress.IPv4Network(sdsubn)
		fip = str(nt[1])

		dvip, dlip = get_vip_lip(ipv4n,subn)

		if config_v['ipvlan_host'] != 'default' and config_v['ipvlan_cont'] != 'default' :
			if is_valid_ipv4_address(config_v['ipvlan_host']) == True and is_valid_ipv4_address(config_v['ipvlan_host']) == True:
				vip = config_v['ipvlan_host']
				lip = config_v['ipvlan_cont']
			else:
				raise InvalidIPException
		elif config_v['ipvlan_host'] != 'default' and config_v['ipvlan_cont'] == 'default': 
			if is_valid_ipv4_address(config_v['ipvlan_host']) == True:
				vip = config_v['ipvlan_host']
				lip = dlip
			else:
				raise InvalidIPException
		elif config_v['ipvlan_host'] == 'default' and config_v['ipvlan_cont'] != 'default': 
			if is_valid_ipv4_address(config_v['ipvlan_cont']) == True:
				vip = dvip
				lip = config_v['ipvlan_cont']
			else:
				raise InvalidIPException
		else: 
			vip, lip = dvip, dlip

		brd = str(nt.broadcast_address)

		#create podman network
		#This is using ipvlan 		
		print("Welcome to XIVOmega v.0.01a")
		print(f"Network Adapter in use: {netdev}")
		podnet = f"podman network create --subnet={sdsubn} --gateway={sdgway} --driver=ipvlan -o parent={netdev} xivlanc"
		try:
			xivnet = subprocess.run(shlex.split(podnet),check=True,capture_output=True)  # shell=False
			if xivnet.returncode == 0:
				print("podman ipvlan network xivlanc has been created")
		except subprocess.CalledProcessError as e: 
			print(e.stderr.decode())
			rc = -1
		
		# create host ipvlan adapter
		omegaBeetle.CreateHostAdapter(vip,netb,brd)
				
		print("Creating podman container")
		
		#create podman container - assigns IP 10.88.0.7 because yes
		#todo: manually assign via config file
		#desired end state: get dhcp - maybe in the future as podman makes it available
		
		omegapod = f"""podman create \
		  --replace \
		  --name=xivomega \
		  --ip=10.88.0.7 \
		  --sysctl net.ipv4.ip_forward=1 \
		  --sysctl net.ipv4.conf.all.route_localnet=1 \
		  --net=podman \
		  --cap-add=NET_RAW,NET_ADMIN \
		  -ti quay.io/shingonati0n/xivomega:latest /bin/sh"""
		
		try:
			xivomega = subprocess.run(shlex.split(omegapod),check=True,capture_output=True)
			if xivomega.returncode == 0:
				print("podman container created successfully")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
			rc = -1
		
		#connect created container to podman ipvlan network - using IP address from either default or config file
		hclosew = f"podman network connect xivlanc xivomega --ip={lip}"
		try:
			hclosew = subprocess.run(shlex.split(hclosew),check=True,capture_output=True)
			if hclosew.returncode == 0:
				print("hooked to podman ipvlan network")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		
		#Start
		#print logo
		omegaBeetle.PrintLogo() 
		#subprocess.call(pth + "titleCard.sh")
		try:
			hworld = subprocess.run(shlex.split("podman start xivomega"),check=True,capture_output=True)
			if hworld.returncode == 0:
				print("XIVOmega says - Hello World")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		
		#add routes to the game's IPs in the host
		omegaBeetle.SetRoutes(roadsto14)

		#run mitigator on container - 
		#remove iptables rles from podman
		omegaBeetle.ClearNetavarkRules()
		print("Activating mitigation protocol")
		
		#run iptables on podman
		try:
			cosmo = subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)
			if cosmo.returncode == 0:
				print("IPTables in Omega: Complete")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())

		ctx = 1
		print("Establishing network connection...")
		while(ctx > 0):
			try:
				dice = subprocess.run(shlex.split("podman exec xivomega ping 204.2.29.7 -c 5"),check=True,capture_output=True)
				if dice.returncode == 0:
					print("Network Established")
					ctx = 0
				else:
					print("Retrying Connection..")
					ctx = ctx + 1
					omegaBeetle.ReconnectProtocol()
					omegaBeetle.ClearNetavarkRules()
					omegaBeetle.SetRoutes(roadsto14)
					if(ctx > 5):
						raise ConnectionFailedError
			except subprocess.CalledProcessError as e:
				print("Retrying Connection...")
				ctx = ctx + 1
				omegaBeetle.ReconnectProtocol()
				omegaBeetle.ClearNetavarkRules()
				omegaBeetle.SetRoutes(roadsto14)
				if(ctx > 5):
					raise ConnectionFailedError

		print("Mitigation in 10 seconds...")
		omegaBeetle.CDTimer()
		print("MITIGATOR EXECUTING")
		#execute mitigator
		omega = f"podman exec -it xivomega /home/omega_alpha.sh"
		Popen(shlex.split(omega), stdout=sys.stdout, stderr=sys.stderr).communicate()
	
	except RootRequiredError:
		print("This program requires root permissions - use sudo")
		rc = -1

	except InvalidIPException:
		print("Invalid IP Address detected in config file")
		print("If not sure, just put default ")
		rc = -1

	except ConnectionFailedError:
		print("Connection could not be established correctly.")
		print("Try again after program closes")
		rc = 4
	
	except KeyboardInterrupt:
		pass
	
	finally:
		#Close routine - do same thing as xivostop
		if rc >= 0:
			#remove everything
			omegaBeetle.SelfDestructProtocol()
	return rc 

if __name__ == "__main__":
    exit(__main__())