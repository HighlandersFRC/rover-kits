from XRPLib.defaults import *

# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here
webserver.start_network(ssid="XRP_{robot_id}", robot_id=42, password="xrp")
webserver.start_server()