from machine import Pin, SPI, ADC
import time
import math
import uasyncio as asyncio

# Constants
MOTOR_STEPS = 200
MICROSTEPS = 16
DEGREES_PER_REVOLUTION = 360.0
STEERING_SENSOR_MAX_VALUE = 4095.0
STEERING_GEAR_RATIO = 55.0 / 12.0
STEERING_CORRECTION_INTERVAL = 50000  # microseconds
SMALL_MOVEMENT_THRESHOLD = 0.5
STALL_DETECTION_COUNT = 10
STEERING_MAX_ALLOWED_ERROR = 2.0
DRIVE_ERROR_GAIN = 0.1
DRIVE_STALL_THRESHOLD = 0.5
DRIVE_MAX_STALL_COUNT = 5
MAX_STEP_ACCEL = 200.0

class SteeringMotor:
    def __init__(self, cs_pin, adc_pin):
        self.cs = Pin(cs_pin, Pin.OUT)
        self.adc = ADC(Pin(adc_pin))
        self.angle_offset = 187.5
        self.target_angle = 0.0
        self.last_external_angle = 0.0
        self.last_correction_us = time.ticks_us()
        self.stall_counter = 0
        self.last_applied_speed = None
        # SPI placeholder
        self.spi = SPI(1, baudrate=1000000, polarity=1, phase=1, sck=Pin(12), mosi=Pin(11), miso=Pin(13))

    def normalize_angle(self, angle):
        while angle > 180.0:
            angle -= DEGREES_PER_REVOLUTION
        while angle < -180.0:
            angle += DEGREES_PER_REVOLUTION
        return angle

    def get_steering_angle(self):
        raw = self.adc.read()
        angle = (raw / STEERING_SENSOR_MAX_VALUE) * DEGREES_PER_REVOLUTION
        return angle

    def set_target_angle(self, angle):
        self.target_angle = self.normalize_angle(-angle)
        # TODO: write SPI commands to set TMC target

    def update_position(self):
        now = time.ticks_us()
        if time.ticks_diff(now, self.last_correction_us) < STEERING_CORRECTION_INTERVAL:
            return
        self.last_correction_us = now

        current_angle = self.normalize_angle(self.get_steering_angle() - self.angle_offset)
        error = self.normalize_angle(self.target_angle - current_angle)

        if abs(current_angle - self.last_external_angle) < SMALL_MOVEMENT_THRESHOLD:
            self.stall_counter += 1
        else:
            self.stall_counter = 0
        self.last_external_angle = current_angle

        if self.stall_counter > STALL_DETECTION_COUNT:
            # Full resync
            self.stall_counter = 0
            # TODO: reset TMC actual/target positions via SPI

class DriveMotor:
    def __init__(self, cs_pin):
        self.cs = Pin(cs_pin, Pin.OUT)
        self.step_rate_cmd = 0.0
        self.target_steps_per_sec = 0.0
        self.current_rpm = 0.0
        self.target_rpm = 0.0
        self.last_enc = 0
        self.last_time = time.ticks_us()
        self.stall_counter = 0
        # SPI placeholder
        self.spi = SPI(1, baudrate=1000000, polarity=1, phase=1, sck=Pin(12), mosi=Pin(11), miso=Pin(13))

    def set_speed(self, rpm):
        self.target_rpm = rpm
        self.target_steps_per_sec = abs(rpm) / 60.0 * MOTOR_STEPS * MICROSTEPS

    def update_control_loop(self):
        # TODO: read encoder via SPI
        now = time.ticks_us()
        dt = time.ticks_diff(now, self.last_time)
        if dt <= 0:
            return
        # Placeholder for encoder delta
        delta_enc = 0
        measured_ticks_per_sec = delta_enc * 1e6 / dt
        measured_steps_per_sec = abs(measured_ticks_per_sec * (MOTOR_STEPS * MICROSTEPS / 4000.0))
        self.current_rpm = measured_steps_per_sec / (MOTOR_STEPS * MICROSTEPS) * 60.0

        error = self.target_steps_per_sec - measured_steps_per_sec
        adjustment = error * DRIVE_ERROR_GAIN

        if measured_steps_per_sec < DRIVE_STALL_THRESHOLD * self.step_rate_cmd:
            self.stall_counter += 1
        else:
            self.stall_counter = 0

        if self.stall_counter > DRIVE_MAX_STALL_COUNT:
            self.step_rate_cmd -= 250 * self.stall_counter
            if self.step_rate_cmd < 0:
                self.step_rate_cmd = 0
        else:
            self.step_rate_cmd += adjustment
            if self.step_rate_cmd < 0:
                self.step_rate_cmd = 0

        max_step_change = MAX_STEP_ACCEL * (dt / 1e6)
        if self.target_steps_per_sec > self.step_rate_cmd + max_step_change:
            self.step_rate_cmd += max_step_change
        elif self.target_steps_per_sec < self.step_rate_cmd - max_step_change:
            self.step_rate_cmd -= max_step_change
        else:
            self.step_rate_cmd = self.target_steps_per_sec

        # TODO: send step_rate_cmd to TMC via SPI
        self.last_enc = 0  # TODO: update from encoder
        self.last_time = now

class Car:
    def __init__(self, right_cs, left_cs, steer_cs):
        self.right_motor = DriveMotor(right_cs)
        self.left_motor = DriveMotor(left_cs)
        self.steering_motor = SteeringMotor(steer_cs, adc_pin=18)
        self.speed = 0.0
        self.steering_angle = 0.0
        self.lock = asyncio.Lock()

    async def update_control_loops(self):
        async with self.lock:
            self.right_motor.update_control_loop()
            self.left_motor.update_control_loop()
            self.steering_motor.update_position()

    async def set_steering_angle(self, angle):
        async with self.lock:
            self.steering_angle = angle
            self.steering_motor.set_target_angle(angle)

    async def set_speed(self, rpm, wheelbase, track_width):
        async with self.lock:
            self.speed = rpm
            steering_angle_rad = math.radians(self.steering_angle)
            min_turn_angle = 0.01
            if abs(steering_angle_rad) < min_turn_angle:
                self.right_motor.set_speed(rpm)
                self.left_motor.set_speed(-rpm)
                return

            R = wheelbase / math.tan(steering_angle_rad)
            R_L = R - track_width / 2.0
            R_R = R + track_width / 2.0

            v_L = rpm * (R_L / R)
            v_R = rpm * (R_R / R)

            self.right_motor.set_speed(v_R)
            self.left_motor.set_speed(-v_L)

    async def get_motor_rpms(self):
        async with self.lock:
            return self.right_motor.current_rpm, self.left_motor.current_rpm

