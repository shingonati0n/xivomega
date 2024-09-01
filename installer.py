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

	if os.path.isfile('/hone/deck/.local/bin/xivomega'):
		raise BinaryExistsException

	print("Welcome to the installer for XIVOmega")
	print("This will install the binary for xivomega on /home/deck/.local/bin")
	print("This is done to avoid SteamOS wiping the binary wihen upadting the firmware")
	ins = input("Please confirm installation (Y/N)")

	if ins.lower() == "n":
		raise NotAcceptedException 
	else:
		app_path = os.path.dirname(__file__) + "/run.py"
		os.chmod(app_path, 0o777)
		subprocess.run(shlex.split("cp " + app_path + " /home/deck/.local/bin/xivomega"))
		print("Binary successfully installed to /home/deck/.local/bin/xivomega")
		print("To run program, type 'sudo xivomega' ")

except RootRequiredError:
	print("This program requires root permissions - use sudo") 

except BinaryExistsException:
	print("Binary executable already installed.")

except NotAcceptedException:
	print("Installation not accepted. Good Bye")
#chmod+x run.py
#cp /xivomega/run.py /home/deck/.local/bin/xivomega
