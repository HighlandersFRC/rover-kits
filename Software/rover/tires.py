from machine import Pin, PWM

class Tires():
    def __init__(self):
        pass


    def apply_power(self, left_forward, left_back, right_forward, right_back):
        drivetrain.set_effort(left_forward,right_forward)

