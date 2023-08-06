# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from math import atan2, degrees
import board
import adafruit_mpu6050
import simple_gyro


def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle


def get_inclination(_sensor):
    x, y, z = _sensor.acceleration
    return vector_2_degrees(x, z), vector_2_degrees(y, z), vector_2_degrees(x, y)


display = board.DISPLAY
i2c = board.I2C()
sensor = adafruit_mpu6050.MPU6050(i2c)

gyro = simple_gyro.Gyro(
    posx=150,
    posy=150,
    radius=150,
    padding=10,
    line_roll_height=10,
    color_circle=0x440044,
    color_needle=0x123456,
    color_indicator=0x112299,
    color_tick_indicator=0xFF0000,
)

display.show(gyro.group)


while True:
    angle_xz, angle_yz, angle_xy = get_inclination(sensor)
    print(
        "XZ angle = {:6.2f}deg   YZ angle = {:6.2f}deg  XY angle = {:6.2f}deg".format(
            angle_xz, angle_yz, angle_xy
        )
    )
    gyro.update_pitch(90 - angle_yz)
    gyro.update_roll(90 - angle_xz)
    gyro.update_yaw(angle_xy + 90)
    time.sleep(0.2)
