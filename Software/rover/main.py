# Import necessary modules
from machine import Pin, ADC
import bluetooth
import time
import math

from XRPLib.defaults import *
from pestolink import PestoLinkAgent

# Choose the name your robot shows up as in the Bluetooth paring menu
# Name should be 8 characters max!
robot_name = "Demo"

# Create an instance of the PestoLinkAgent class
pestolink = PestoLinkAgent(robot_name)
print(robot_name)
# Start an infinite loop
servo_step = 0.5
drive_speed = 1
servo1_pos = 70
servo2_pos = 90
servo_one.set_angle(servo1_pos)
servo_two.set_angle(servo2_pos)
time.sleep(0.5)
while True:
    if pestolink.is_connected():  # Check if a BLE connection is established
        rotation = -1 * (pestolink.get_axis(2)+pestolink.get_axis(0))
        throttle = -1 * pestolink.get_axis(1)
        if (rotation > 1):
            rotation = 1
        if (rotation < -1):
            rotation = -1
        if (abs(rotation) < 0.40):
            rotation = 0
        drivetrain.arcade(throttle*drive_speed, rotation*drive_speed*0.70)

        if ((pestolink.get_button(7) or pestolink.get_button(3)) and servo1_pos < 110):
            servo1_pos += servo_step
        if ((pestolink.get_button(6) or pestolink.get_button(0)) and servo1_pos > 45):
            servo1_pos -= servo_step

        servo_one.set_angle(servo1_pos)

        if ((pestolink.get_button(5) or pestolink.get_button(2)) and servo2_pos < 180):
            servo2_pos += servo_step
        if ((pestolink.get_button(4) or pestolink.get_button(1)) and servo2_pos > 50):
            servo2_pos -= servo_step

        servo_two.set_angle(servo2_pos)

        print("servo1: "+str(servo_one.get_angle()) +
              ", servo2: "+str(servo_two.get_angle()))

        batteryVoltage = (
            ADC(Pin("BOARD_VIN_MEASURE")).read_u16())/(1024*64/14)
        pestolink.telemetryPrintBatteryVoltage(batteryVoltage)

    else:  # default behavior when no BLE connection is open
        drivetrain.arcade(0, 0)
        servo_one.free()
        servo_two.free()
