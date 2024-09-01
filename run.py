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

#region aux functions
#read config file

#pth = os.path.dirname(__file__) + "/"
pth = "/home/deck/xivomega/"

def read_config():
	cfg = configparser.ConfigParser()
	cfg.read(pth + 'config.ini')

	ipvlan_host = cfg.get('General','ipvlan_host').lower()
	ipvlan_cont = cfg.get('General','ipvlan_cont').lower()

	#create dictionary with Config Parms
	cfg_val = {
	'ipvlan_host': ipvlan_host,
	'ipvlan_cont': ipvlan_cont
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

	rc = 0

	try:
		#check if running as sudo
		if os.getuid() != 0:
			raise RootRequiredError
		#get IP address with cidr from wlan0 - need to add eth0 for cabled connections if any
		ipv4 = os.popen('ip addr show wlan0').read().split("inet ")[1].split(" brd")[0] 
		#print(ipv4)
		ipv4n, netb = ipv4.split('/')
		
		#get subnet mask and subnet
		def cidr_to_netmask(cidr):
			network, net_bits = cidr.split('/')
			host_bits = 32 - int(net_bits)
			netmask = socket.inet_ntoa(struct.pack('!I',(1 << 32) - (1 << host_bits)))
			return network, netmask
		
		#print(cidr_to_netmask(ipv4)[1])
		subn = ipaddress.ip_network(cidr_to_netmask(ipv4)[0]+'/'+cidr_to_netmask(ipv4)[1], strict=False)
		sdgway = '.'.join(ipv4n.split('.')[:3]) + ".1"
		#brd = '.'.join(ipv4n.split('.')[:3]) + ".255"
		sdsubn = str(subn.network_address) + "/" + netb
		
		#get first and last ips from current network
		
		#use config file - validate if values are not Default first
		nt = ipaddress.IPv4Network(sdsubn)
		fip = str(nt[1])

		if config_v['ipvlan_host'] != 'default' and config_v['ipvlan_cont'] != 'default' :
			if is_valid_ipv4_address(config_v['ipvlan_host']) == True and is_valid_ipv4_address(config_v['ipvlan_host']) == True:
				vip = config_v['ipvlan_host']
				lip = config_v['ipvlan_cont']
			else:
				raise InvalidIPException
		elif config_v['ipvlan_host'] != 'default' and config_v['ipvlan_cont'] == 'default': 
			if is_valid_ipv4_address(config_v['ipvlan_host']) == True:
				vip = config_v['ipvlan_host']
				lip = str(nt[-3])
			else:
				raise InvalidIPException
		elif config_v['ipvlan_host'] == 'default' and config_v['ipvlan_cont'] != 'default': 
			if is_valid_ipv4_address(config_v['ipvlan_cont']) == True:
				vip = str(nt[-4])
				lip = config_v['ipvlan_cont']
			else:
				raise InvalidIPException
		else: 
			vip, lip = str(nt[-4]), str(nt[-3])

		brd = str(nt.broadcast_address)

		#create podman network
		#This is using ipvlan - as Freddie said - AND NOW I KNOW!
		# What made this so hard
		# - As per kernel rules, a virtual interface cannot communicate with its parent interface
		# - this means IPVlan alone won't do the job
		# - Bridge could probably do alone but that needs meddling with a lot of iptables rules and stuff
		# - So we use both! Since Podman Default Bridge is not a child interface of wlan0, its valid to move traffic there
		# - and back thru ipvlan to the internet
		
		print("Welcome to XIVOmega v.0.01a")
		podnet = f"podman network create --subnet={sdsubn} --gateway={sdgway} --driver=ipvlan -o parent=wlan0 xivlanc"
		try:
			xivnet = subprocess.run(shlex.split(podnet),check=True,capture_output=True)  # shell=False
			if xivnet.returncode == 0:
				print("podman ipvlan network xivnet has been created")
		except subprocess.CalledProcessError as e: 
			print(e.stderr.decode())
		
		# create host ipvlan adapter
		
		ipvl1 = f"ip link add xivlanh link wlan0 type ipvlan mode l2"
		ipvl2 = f"ip addr add {vip}/{netb} brd {brd} dev xivlanh"
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
				print(f"host ipvlan interface IP is {vip}")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		
		try:
			ipvlh3 = subprocess.run(shlex.split(ipvl3),check=True,capture_output=True)
			if ipvlh3.returncode == 0:
				print("host ipvlan interface is up")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		
		
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
		subprocess.call(pth + "titleCard.sh")
		try:
			hworld = subprocess.run(shlex.split("podman start xivomega"),check=True,capture_output=True)
			if hworld.returncode == 0:
				print("XIVOmega says - Hello World")
		except subprocess.CalledProcessError as e:
			print(e.stderr.decode())
		
		#add routes to the game's IPs in the host
		for r in roadsto14:
			way = f"ip route add {r} via 10.88.0.7"
			nav = subprocess.run(shlex.split(way),check=True,capture_output=True)
			try:
		   		if nav.returncode==0:
		   			print(f"route to {r} added")
			except subprocess.CalledProcessError as e:
					print(e.stderr.decode())
		
		#run mitigator on container - 
		#remove iptables rles from podman
		subprocess.run(shlex.split("iptables -F INPUT"),check=True,capture_output=True)
		subprocess.run(shlex.split("iptables -F FORWARD"),check=True,capture_output=True)
		subprocess.run(shlex.split("iptables -F OUTPUT"),check=True,capture_output=True)

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
					print(dice.returncode)
					print("Network Established")
					ctx = 0
				else:
					print("Retrying Connection")
					ctx = ctx + 1
					subprocess.run(shlex.split("podman exec xivomega iptables -t nat -F POSTROUTING"),check=True,capture_output=True)
					subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)
					if(ctx > 5):
						print(dice.returncode)
						raise ConnectionFailedError
			except subprocess.CalledProcessError as e:
				print("Retrying Connection")
				ctx = ctx + 1
				subprocess.run(shlex.split("podman exec xivomega iptables -t nat -F POSTROUTING"),check=True,capture_output=True)
				subprocess.run(shlex.split("podman exec xivomega /home/iptset.sh"),check=True,capture_output=True)
				if(ctx > 5):
					print(dice.returncode)
					raise ConnectionFailedError

		print("Mitigation in 15 seconds...")

		time.sleep(15)
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
			#remov  e routes
			print("Terminating Mitigation Protocol and XIVOmega")
			#add routes to the game's IPs in the host
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
			print("All done - goodbye")

	return rc 

if __name__ == "__main__":
    exit(__main__())