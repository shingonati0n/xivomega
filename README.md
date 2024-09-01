XIVOmega - Latency Mitigator for Steam Deck based on XIVMitmLatencyMitigator
----------------------------------------------------------------------------

Playing Final Fantasy XIV and unable to doubleweave things?? 

Troubled because XIVAlexander doesn't run natively on SteamOS and don't want to install Windows??

Don't have another PC where you can run XIVMitmLatencyMitigator?? 

This solution is for you!! - Run MXIVMitmLatencyMitigator on your Steam Deck with a container acting as bare metal man-in-the-middle. 

This Python Script relies on Podman to create and run the container - Podman is bundled by default in Steam Deck as part of Distrobox. 

This script also handles all networking steps to enable the mitigator without having to enter additional commands and allow customization of some variables. 

- Recommendations for usage: 

For Game Mode, it's highly recommended to have Decky Loader installed with the Decky Terminal plugin (put links here). If you are not using Decky Plugins, then add Konsole as a Steam App, so you can open it from game mode. How to set up Konsole in game mode is outside the scope of this document, so look it up. 

- How to use:

	- Go to Desktop Mode in Steam Deck and download from latest releases (put link) - extract the contents to /home/deck
	- Open Konsole and and run the installer (sudo python /home/deck/xivomega/installer.py) - this will install the binary 
	so execution is later easier
	- This can run in both Desktop and Game Modes:
		If using Desktop Mode: 
			- Open Konsole and execute sudo xivomega and wait until the mitigator starts running -
			- Open FFXIV and game
		If using from Game Mode with Decky Terminal:
		    - Open the QAM (three-dotted button under the right trackpad) and open a Decky Terminal - then execute sudo xivomega - wait until the mitigator starts running 
		    - Press the Steam Button and open your launcher and game
		If using from Game Mode without Decky Terminal: 
			- Open Konsole from your library - from inside the Konsole, run:
				- cd /home/deck
				- run sudo xivomega - wait until the mitigator starts running
			- Press the Steam Button and open your launcher and game

When running the script, the output of XIVMitmLatencyMitigator will be displayed on the console running it - just like if using it on another PC like the traditional XIVMitmLatencyMitigator, and just like it when running the output of the actions you execute should display on the console. 

Pressing Ctrl-C will stop the whole the program and will automatically remove all container/network elements created by it. 

Options and Customization:

This program creates 2 virtual network adapters to allow the container to communicate with the internet - By default, this happens on the program:

 - 2 IPVlan adapters are created using wlan0 (Wifi Adapter) as parent
 - Each got assigned the last 2 IP addresses from the network the Deck is connected in

 If you need to customize the IP address - you can do so from the config.ini file inside the /xivomega folder - just change the values from default - to the desired IP addresses - make sure both are part of the same subnet. 

Special Thanks:

 Soreepeong for creating the original Mitigator script and Alexander
 Bankjaneo for inspiring this by creating the Docker version of the mitigator. 


License 

Apache License 2.0



