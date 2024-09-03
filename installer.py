import os
import subprocess 
import shlex

class RootRequiredError(RuntimeError):
    pass

class BinaryExistsException(Exception):
	pass

class NotAcceptedException(Exception):
	pass

try:
	if os.getuid() != 0:
		raise RootRequiredError

	if os.path.isfile('/var/lib/flatpak/exports/bin/xivomega'):
		raise BinaryExistsException

	print("Welcome to the installer for XIVOmega")
	print("This will install the binary for xivomega on /var/lib/flatpak/exports/bin")
	print("This is done to avoid SteamOS wiping the binary when upadting the firmware")
	ins = input("Please confirm installation (Y/N):\n")

	if ins.lower() == "n":
		raise NotAcceptedException 
	else:
		app_path = os.path.dirname(__file__) + "/run.py"
		os.chmod(app_path, 0o777)
		subprocess.run(shlex.split("cp " + app_path + " /var/lib/flatpak/exports/bin/xivomega"))
		print("Binary successfully installed to /var/lib/flatpak/exports/bin/xivomega")
		print("To run program, type 'sudo xivomega'.")

except RootRequiredError:
	print("This program requires root permissions - use sudo") 

except BinaryExistsException:
	print("Binary executable already installed.")

except NotAcceptedException:
	print("Installation not accepted. Good Bye")



#/usr/local/sbin:/usr/local/bin:/usr/bin:/var/lib/flatpak/exports/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl