# vrc-patpatpat

An open hardware and software project which tries to implement haptic head pat feedback to the player in VR. This project targets only VRChat's OSC support for now.

 ## This is a WIP fork!
 
This a is a in-development fork of [https://github.com/danielfvm/Patstrap](https://github.com/danielfvm/Patstrap) (only a small amout of original code left, mostly gui and some backend) which will try to work on the following:

- (Done) switch to using osc over udp for the motor control data
- (Done) add config file to configure/load/save parameters
- implement support for more then 3 touch points
- (started) add mqtt control/feedback to server (for further integration purposes in my setup)
- (Done) add a simple osc recorder and player (for dev) (server/oscRecReplayer.py)
- (Done) add a 3d vizualizer (mostly for dev)

Other stuff to later add to the readme:

- Using ULN2003 board to drive motors
- Using [motors](https://www.aliexpress.com/item/4000245243914.html) from aliexpress
- Obv. 3d printed part won't fit more motors, revise head mounting options for > 2 motors
- Update unity guide for positioning and coordinates
- Add wiring for battery voltage measurement
- Mention that server connection indicator for hardware only is active when comms in both directions work
- To compile the wifi credentials into the esp code the wifi.ini.template needs to be renamed to wifi.ini and the values filled out with the ssid and password 

### Original Readme from here on for now

---

### Goals
* Designing a hardware that is cheap and easy for others to replicate
* Documenting everything

### ToDo's and issues
* Design casing for ESP
* Change position of Vibrators more to the side
* Batteries?
* Add Setting for changing between "Vibrate on collision" and "Vibrate on motion"
* Video and update instructions in `README.md`


## Hardware
### Electronics
An ESP8266 was used for this project, but can be switched with any other WLAN-capable IC.
For the haptic feedback two [Vibrating Mini Motor Disc](https://www.adafruit.com/product/1201) from Adafruit were used for a 3D spaced feedback on the head.
Both of them can be directly wired to the ESP but for higher performance it is recommended to switch them with two transistors like the BC547b.

![image](https://github.com/danielfvm/Patstrap/assets/23420640/da269697-d692-4068-acf2-a8210f8bc7d0)

### Hausing
The 3D-Model and the `.scad` file of the hausing, which includes some space for the Motor Discs and the ESP8266, is available under `/model` and can be 3D-Printed. Alternatively you can use a normal headband and simply hot glue the Motor Discs and the ESP on a headband.
### Battery
My design does not include an integrated battery and must be supplied externally over USB. If you want battery support you can use the [SlimeVR Docs](https://docs.slimevr.dev/diy/tracker-schematics.html) as a reference. They use a TP4056 for charging the battery and the device and include the required wiring on their docs.

## Software
### Firmware
For this project to work the ESP8266 needs to be flashed with the necessary firmware. The code is available under `/firmware` and needs to be edited for your requirements. This Project uses [Visual Studio Code](https://code.visualstudio.com/download) and [PlatformIO](https://platformio.org/platformio-ide) to work. Please refer to the [SlimeVR Docs](https://docs.slimevr.dev/firmware/setup-and-install.html) as a reference on how to install the IDE and the extension. After the installation you can download this repository and open the `/firmware` in Visual Studio Code.

Open the `platformio.ini` and change `-DWIFI_CREDS_SSID` and `-DWIFI_CREDS_PASSWD` to your local network's name and password. Keep in mind that it must be the same network your computer is running on in order for the device to communicate with the server program. If you are <ins>not using an ESP8266</ins> you will need to change `board = esp12e` to your board and most likely also the PIN-Layout in the `main.cpp` file.

After your edits you can plug-in your ESP, press build (✓) and flash (→) it. You can find the buttons in Visual Studio Code at the bottom on the left side.

![image](https://github.com/danielfvm/Patstrap/assets/23420640/beaee4ad-d02e-4107-bf20-3b0c8394fff7)

### Server
Under releases you can find the binary files to run the server on your computer. The server is the middle man that allows communication between the device and VRChat. The server supports both Windows and Linux. The server opens up a window where the current connection status is displayed. If flashing the hardware worked and the device is running you should see the text `connected`. You can also verify the connection by looking at the ESP-LED.
* Fast blinking (~10 times per second): Not connected with WLAN.
* Slow blinking (~1 time per second): Connected to WLAN, not connected with server.
* Continues light: Connected.
* No light: Not turned on?

If connection was successful `Patstrap connection` should turn green. Furthermore you can now test the hardware by clicking `Pat left` and `Pat right`.

![image](https://github.com/danielfvm/Patstrap/assets/23420640/5acc15c7-cf55-4305-8433-b824a77c9b94)


### VRChat
#### Avatar - Unity
For the Patstrap to work you will need to [enable OSC Support in VRChat](https://docs.slimevr.dev/server/osc-information.html) and edit your Avatar Model to include the required Colliders for detecting a head pat. For this you need to have a working avatar setup in unity. 

1. Create Empties

    First open up your Avatar in Unity, go to `armature -> Hips -> Spine -> Chest -> Neck -> Head` and add two `Empty` objects as a child of the head. It should look like the following image. Optionally you can rename them for better organization.
   
    ![image](https://github.com/danielfvm/Patstrap/assets/23420640/520a7821-0146-4770-a49b-028987a2f8cc)

2. Add Contact Receivers 

    Open up the just added objects and click on `Add Component` and select `VRC Contact Receiver`. 
    
    ![image](https://github.com/danielfvm/Patstrap/assets/23420640/79c20c5a-a77a-45f2-b334-a744d7d8230b)

3. Positioning 

    Now move the contact receivers to your left and right of your avatar's head. Change the size and form if required. The position and size should resemble the following.
    
    ![image](https://github.com/danielfvm/Patstrap/assets/23420640/46c971fd-c8a5-476f-8a55-a8563d6591f7)

4. Configure Contact Receivers

    Under the section `Collision Tags` click on `Add` and select `Hand` and repeat this step for `Finger`. In the section `Receiver` change `Receiver Type` to `Proximity` and the `Parameter` to one of the following fitting names.
    * `pat_right` for the collider placed on the right side
    * `pat_left` for the collider placed on the left side

    The end result should look similar to the following image. Repeat this step for the other two contact receivers.
    
    ![image](https://github.com/danielfvm/Patstrap/assets/23420640/7b309612-dcd8-4122-aa49-7cbfa56223e9)
   
5. Upload

    Now you should be ready to test and upload your avatar.

### Testing & Debugging
After you uploaded your avatar and enabled osc support, the `VRChat connection` indicator should turn green as soon as you (or someone else) touches your head. If this is not the case there a following steps you can do to find the origin of the issue.
1. Check if the just added parameters were added to your uploaded avatar. You can find the json file at `~\AppData\LocalLow\VRChat\VRChat\OSC\{userId}\Avatars\{avatarId}.json`. For more information see [VRChat's docs](https://docs.vrchat.com/docs/osc-avatar-parameters). 
2. Use [Protokol](https://hexler.net/protokol) for debugging and check if `pat_left`, `pat_right` or `pat_middle` appears in the log. Make sure you set the port to the port used by [VRChat (default 9001)](https://docs.vrchat.com/docs/osc-overview).
3. Start Patstrap Server in the CMD and look for error messages.
4. If nothing worked feel free to ask me for help on Discord: DeanCode#3641

## Changelog v0.2
* Simplified background in server application
* Fixed test buttons
* Potentially fixed a div by zero crash
* Fixed VRChat status indicator not working

## Credits
This project uses and refers to many parts from the [SlimeVR](https://www.crowdsupply.com/slimevr/slimevr-full-body-tracker) Project which is an open hardware, full body tracking solution and a great project to checkout.
