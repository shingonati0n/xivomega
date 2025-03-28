If using Steam Deck, please try using [this Decky Plugin instead](https://github.com/shingonati0n/xivomega-decky). If you don't want to use Decky or are using Linux, you can go ahead and use this solution. 

![ksnip_20240901-215038](https://github.com/user-attachments/assets/3acf5a6b-81b7-4616-9d13-f51f5a0576c5)

XIVOmega - Latency Mitigator for Linux based on XivMitmLatencyMitigator
----------------------------------------------------------------------------

Playing Final Fantasy XIV on Linux and unable to doubleweave things?? 

Troubled because [XivAlexander](https://github.com/Soreepeong/XivAlexander) doesn't run natively on your distro and don't want to install Windows or deal with Wine stuff??

Don't have another PC where you can run [XivMitmLatencyMitigator](https://github.com/Soreepeong/XivMitmLatencyMitigator)?? 

![xivom1](https://github.com/user-attachments/assets/ee3e43e9-e1b2-4ddc-a945-f763b42b0d05)

![20240831184558_1](https://github.com/user-attachments/assets/9ea2f37b-22dd-4286-8109-de6dd59d22ef)

![20240831184705_1](https://github.com/user-attachments/assets/cfdad1ff-7e45-4f40-85c5-9c995176e643)

This solution is for you!! - Run XivMitmLatencyMitigator on your distro with a container acting as bare metal man-in-the-middle. 

This Python Script relies on Podman to create and run the container - This was originally built for Steam Deck, which comes with podman, but repurposing for linux instead. 

This script also handles all networking steps to enable the mitigator without having to enter additional commands and allow customization of some variables. 

- How to use: 

**For Linux**: 
--------------

- Download from releases and uncompress in any location on your PC. 
- Open a terminal on the location where you decompressed the file, enter the xivomega folder and run **sudo python run.py** - you can add chmod -x run.py to run using **sudo ./run.py**
- You can now open the game and leave this running in the background. 
- When finished, press Ctrl+C to close it and remove all network elements and the container. 


**For Steam Deck: Again, use [this Decky Plugin instead](https://github.com/shingonati0n/xivomega-decky).**
-----------------------------------------------------------------------------------------------------------


The instructions below are legacy or just in case you don't want to have Decky Loader installed. **Moving onwards this solution will be geared towards Linux**


- Add Konsole as a Steam App, so you can open it from game mode. How to set up Konsole in game mode is outside the scope of this document, so look it up. 
- Go to Desktop Mode in Steam Deck and download from latest releases ([link here ](https://github.com/shingonati0n/xivomega/releases)) - extract the contents to **/home/deck**. you should end up with a folder called **xivomega** on **/home/deck**
- Open Konsole and and run the installer (**sudo python /home/deck/xivomega/installer.py**) - this will install the binary in **/var/lib/flatpak/exports/bin/xivomega** so it's easier to call it later on. 

- This can run in both Desktop and Game Modes:
	- **If using Desktop Mode**: 
			- Open Konsole and execute **sudo xivomega** and wait until the mitigator starts running -
			- Open FFXIV and game
	- **If using from Game Mode without Decky**: 
			- Open Konsole from your library 
			- from inside Konsole, run **sudo xivomega** 
			- wait until the mitigator starts running
			- Press the Steam Button and open your launcher and game

When running the script, the output of XIVMitmLatencyMitigator will be displayed on the console running it - just like if using it on another PC like the traditional XIVMitmLatencyMitigator, and just like it when running the output of the actions you execute should display on the console. 

Once you finish gaming, **press Ctrl-C** - this will stop the whole the program and will automatically remove all container/network elements created by it. Run sudo xivomega again if starting a new play session. 

Options and Customization:
-------------------------

This program creates 2 virtual network adapters to allow the container to communicate with the internet - By default, this happens on the program:

 - 2 IPVlan adapters are created using whatever device is connected. Ethernet has the priority.
 - Each got assigned 2 random available IPs from the subnetwork your machine is running.

 If you need to customize the IP addresses - you can do so from the config.ini file inside the /xivomega folder - just change the values from default - to the desired IP addresses - make sure both are part of the same subnet you are connected in. 


FAQ:
---

-**Q: Why is there a message saying "Failed to read previous opcode definition files: Definitions file older than an hour" every time I run this thing?**

-**A**: That's because each time XIVOmega runs, it creates a new container everytime, which gets removed after exiting the program via Ctrl-C. Since the container itself is new, it goes thru the rule set up in XivMitmLatencyMitigator, which downloads the opcodes file for use with the game if the file is older than one hour. 

-**Q: I stopped playing and turned the Deck off quickly because reasons - what happens with this thing??**

-**A**: Although the recommended way of exiting will always be by Ctrl+C to have everything cleaned up, there are no problems. The next time you start the script, it will autoclean any dangling elements and will recreate the container and all the networking steps without hassle. 

-**Q: Why putting the binary in /var/lib/flatpak/exports/bin/ and not in some other more common location like /usr/bin**

-**A**: This location was selected due to how the SteamOS purges almost everything whenever an OS update is applied to the deck - the exception being the home/ folder and most of var/.

-**Q: I need to type my password everytime I run sudo xivomega - is there anyway to avoid this??**

-**A**: Although I'll sound repeating, if using Steam Deck, just go for the plugin. The usage on the plugin version is as simple as clicking a toggle. 

-**Q: Will this always need/require a terminal to run??**

-**A**: Just if you don't want to use Decky and the Plugin.

-**Q: What happens if I play XIV on Linux, but not SteamOS?? Will this app work??**

-**A**: The latest update was made for the people playing on Linux. A lot of hardcoded stuff was removed and a couple of improvements were introduced. If running in Linux, just make sure your machine has:
	- Podman 4.4+
	- Netavark 1.13.0 
Older version don't support ipvlan driver.

-**Q: It's Patch day and the opcodes from XivAlex aren't updated yet - Anything I can do to avoid the wait for opcodes to be updated??**

-**A**: Yes you can! In v.1.2.0 - there's the option to configure custom opcodes via the opcode_conf.ini file. Set use_custom_opcodes to true and change the values of the opcodes below. They're mostly published on the XivAlex repo by the community shortly after a patch releases. They get officially updated eventually, but there might be time gaps in between. Also consider using the method described here to find the opcodes: https://github.com/Soreepeong/XivAlexander/wiki/How-to-find-opcodes 

Special Thanks:
--------------

- **Soreepeong** for creating the original XivMitmLatencyMitigator script and XivAlexander
- **Bankjaneo** for inspiring this by creating the Docker version of XivMitmLatencyMitigator.
- **bbnuy** for helping with testing on a clean setup and helping me finding and improving stuff. 

License
-------

Apache License 2.0



