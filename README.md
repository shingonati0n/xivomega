![ksnip_20240901-215038](https://github.com/user-attachments/assets/3acf5a6b-81b7-4616-9d13-f51f5a0576c5)

XIVOmega - Latency Mitigator for Steam Deck based on XivMitmLatencyMitigator
----------------------------------------------------------------------------

Playing Final Fantasy XIV on Steam Deck and unable to doubleweave things?? 

Troubled because [XivAlexander](https://github.com/Soreepeong/XivAlexander) doesn't run natively on SteamOS and don't want to install Windows??

Don't have another PC where you can run [XivMitmLatencyMitigator](https://github.com/Soreepeong/XivMitmLatencyMitigator)?? 

![xivom1](https://github.com/user-attachments/assets/ee3e43e9-e1b2-4ddc-a945-f763b42b0d05)

![20240831184558_1](https://github.com/user-attachments/assets/9ea2f37b-22dd-4286-8109-de6dd59d22ef)

![20240831184705_1](https://github.com/user-attachments/assets/cfdad1ff-7e45-4f40-85c5-9c995176e643)

This solution is for you!! - Run XivMitmLatencyMitigator on your Steam Deck with a container acting as bare metal man-in-the-middle. 

This Python Script relies on Podman to create and run the container - Podman is bundled by default in Steam Deck as part of Distrobox. 

This script also handles all networking steps to enable the mitigator without having to enter additional commands and allow customization of some variables. 

- Recommendations for usage: 

For Game Mode, it's highly recommended to have **Decky Loader** installed with the **Decky Terminal plugin** ([link here](https://github.com/SteamDeckHomebrew/decky-loader)). If you are not using Decky Loader, then add Konsole as a Steam App, so you can open it from game mode. How to set up Konsole in game mode is outside the scope of this document, so look it up. 

- How to use:

	- Go to Desktop Mode in Steam Deck and download from latest releases ([link here ](https://github.com/shingonati0n/xivomega/releases)) - extract the contents to **/home/deck**. you should end up with a folder called **xivomega** on **/home/deck**
	- Open Konsole and and run the installer (**sudo python /home/deck/xivomega/installer.py**) - this will install the binary in /home/deck/.local/bin so it's easier to call it later on.
- This can run in both Desktop and Game Modes:
	- **If using Desktop Mode**: 
			- Open Konsole and execute **sudo xivomega** and wait until the mitigator starts running -
			- Open FFXIV and game
	- **If using from Game Mode with Decky Terminal**:
		    - Open the QAM (three-dotted button under the right trackpad) and open a Decky Terminal - then execute **sudo xivomega** - wait until the mitigator starts running 
		    - Press the Steam Button and open your launcher and game
	- **If using from Game Mode without Decky Terminal**: 
			- Open Konsole from your library 
			- from inside Konsole, run **sudo xivomega** 
			- wait until the mitigator starts running
			- Press the Steam Button and open your launcher and game

When running the script, the output of XIVMitmLatencyMitigator will be displayed on the console running it - just like if using it on another PC like the traditional XIVMitmLatencyMitigator, and just like it when running the output of the actions you execute should display on the console. 

Pressing Ctrl-C will stop the whole the program and will automatically remove all container/network elements created by it. 

Options and Customization:
-------------------------

This program creates 2 virtual network adapters to allow the container to communicate with the internet - By default, this happens on the program:

 - 2 IPVlan adapters are created using wlan0 (Wifi Adapter) as parent
 - Each got assigned the last 2 IP addresses from the network the Deck is connected in

 If you need to customize the IP addresses - you can do so from the config.ini file inside the /xivomega folder - just change the values from default - to the desired IP addresses - make sure both are part of the same subnet you are connected in. 

Special Thanks:

- **Soreepeong** for creating the original XivMitmLatencyMitigator script and XivAlexander
- **Bankjaneo** for inspiring this by creating the Docker version of XivMitmLatencyMitigator.
- **bbnuy** for testing 

License
-------

Apache License 2.0



