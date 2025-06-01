# Rover Software
These are the steps to set up an XRP kit with the Pestolink library. 
# Prerequisites
1.  A fully assembled XRP
2.  A USB-Mini to USB data transfer cable
3.  A computer with Thonny installed
## Flash the Pi Pico
1.  To set up a rover with its software, grab the UF2 file to flash the rover's PI [here](https://github.com/Open-STEM/XRP_MicroPython/releases/download/v2.0.0/micropython_xrp_controller_beta.uf2)   
2.  Unplug the Battery to turn off the Pi
3.  Hold the BOOTSEL button on the pi while you plug it into your computer via USB cable
4.  A new RP1-RP2 drive will appear. Copy the UF2 file onto this drive
## Download Code to Rover
1.  Launch the Thonny IDE and open the Tools > Options Menu
2.  Select the "MicroPython (Raspberry Pi Pico)" interpreter
3.  Set the Port or WebREPL to "< Try to detect port automatically >", then click OK
4.  The bottom right of the Thonny IDE should say "MicroPython (Raspberry Pi Pico) - Board CDC @ COM[Serial Port]"
5.  Download this github code onto your computer and unzip it
6.  Navigate to the downloaded code on the left side of the Thonny IDE and open the "rover" directory
7.  Delete Everything which is currently on the Pi
8.  Right click on the lib directory and select "Upload to /"
9.  Repeat step 7 for main.py
10.  Change the robot_name variable in main.py to be a unique identifier
11.  Reboot the Pi and try to control the rover
## Controlling the Rover
1.  Open the [Pestolink Dashboard](pestol.ink) on your desired device
2.  Give the webpage permissions to bluetooth
3.  Click on the chain link Icon and select the name of your rover in the menu
4.  Ensure that "Mobile Layout" and "Override axes/buttons" are turned on
5.  Drive with the joystick and use the buttons to control the servos