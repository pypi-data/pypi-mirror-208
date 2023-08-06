# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`simple_gyro`
================================================================================

Displayio Gyro representation


* Author(s): Jose D. Montoya


"""
# pylint: disable=too-many-arguments, unused-variable, too-many-locals, too-many-statements
# pylint: disable=too-many-instance-attributes
from math import pi, cos, sin
import displayio
from bitmaptools import draw_circle, rotozoom
from vectorio import Polygon


__version__ = "0.1.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_SIMPLE_GYRO.git"


DEG_TO_RAD = pi / 180


class Gyro:
    """
    Gyro Graphical Representation
    """

    def __init__(
        self,
        posx=100,
        posy=100,
        radius=50,
        padding=10,
        line_roll_height=10,
        color_circle=0x440044,
        color_needle=0x123456,
        color_indicator=0x112299,
        color_tick_indicator=0xFF0000,
    ):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.padding = padding
        self._line_roll_height = line_roll_height
        self._line_roll_length = (2 * self.radius - 2 * self.padding) // 2

        self.group = displayio.Group()

        self._palette = displayio.Palette(6)
        self._palette.make_transparent(0)
        self._palette[1] = color_circle
        self._palette[2] = color_needle
        self._palette[3] = color_indicator
        self._palette[4] = color_tick_indicator
        self._palette[5] = 0xFFFF00

        self.dial_bitmap = displayio.Bitmap(2 * radius + 1, 2 * radius + 1, 10)
        background = displayio.TileGrid(
            self.dial_bitmap,
            pixel_shader=self._palette,
            x=posx - radius,
            y=posy - self.radius,
        )

        self._draw_level()
        self._draw_inclination_line()
        self._draw_indicator()

        self.group.append(background)
        self.group.append(self.level)
        self.group.append(self.needle)
        self.group.append(self.indicator)

        draw_circle(self.dial_bitmap, radius, radius, radius, 1)
        self._draw_tick_indicator()
        self._draw_ticks_level()

    def _draw_inclination_line(self):
        points_polygono = [
            (0, 0),
            (self._line_roll_length, 0),
            (self._line_roll_length, self._line_roll_height),
            (-self._line_roll_length, self._line_roll_height),
            (-self._line_roll_length, 0),
        ]

        self.needle = Polygon(
            points=points_polygono,
            pixel_shader=self._palette,
            x=self.posx,
            y=self.posy,
            color_index=2,
        )
        self.original_values = self.needle.points

    def _draw_indicator(self):
        points_indicator = [(0, 0), (20, 0), (20, -6), (0, -6)]
        self.indicator = Polygon(
            pixel_shader=self._palette,
            points=points_indicator,
            x=self.posx - 5,
            y=self.posy - 30,
            color_index=3,
        )
        self.indicator_original_values = self.indicator.points
        self.indix, self.indiy = self.indicator.location
        self.update_roll(0)

    def _draw_tick_indicator(self):
        tick_stroke = 1
        tick_length = 30

        tick_bitmap = displayio.Bitmap(tick_stroke, tick_length, 5)
        tick_bitmap.fill(4)

        pos = [-90, -80, -70, -60, -100, -110, -120]
        for i in pos:
            this_angle = i * DEG_TO_RAD

            target_position_x = self.radius + self.radius * cos(this_angle)
            target_position_y = self.radius + self.radius * sin(this_angle)

            rotozoom(
                self.dial_bitmap,
                ox=round(target_position_x),
                oy=round(target_position_y),
                source_bitmap=tick_bitmap,
                px=round(tick_bitmap.width / 2),
                py=0,
                angle=this_angle + 90 * DEG_TO_RAD,  # in radians
            )

    def _draw_level(self, padding_level=10):
        points_level = [
            (0, 0),
            (self._line_roll_length - padding_level, 0),
            (self._line_roll_length - padding_level, self._line_roll_height // 3),
            (-self._line_roll_length + padding_level, self._line_roll_height // 3),
            (-self._line_roll_length + padding_level, 0),
        ]
        self.level = Polygon(
            pixel_shader=self._palette,
            points=points_level,
            x=self.posx,
            y=self.posy - self._line_roll_height // 2,
            color_index=1,
        )
        self.level_origin_y = self.level.y

    def _draw_ticks_level(self):
        tick2_stroke = 2
        tick2_length = 30

        tick2_bitmap = displayio.Bitmap(tick2_length, tick2_stroke, 5)
        tick2_bitmap.fill(5)
        pos = [0, 15, 30, -15, -30]
        for i in pos:
            this_angle = i * DEG_TO_RAD

            target_position_x = (
                (self.radius * cos(this_angle)) + self.radius - tick2_length
            )
            target_position_y = (self.radius * sin(this_angle)) + self.radius

            rotozoom(
                self.dial_bitmap,
                ox=round(target_position_x),
                oy=round(target_position_y),
                source_bitmap=tick2_bitmap,
                px=0,
                py=0,
                angle=0,  # in radians
            )

        pos = [150, 165, 180, 195, 210]
        for i in pos:
            this_angle = i * DEG_TO_RAD

            target_position_x = (self.radius * cos(this_angle)) + self.radius
            target_position_y = (self.radius * sin(this_angle)) + self.radius

            rotozoom(
                self.dial_bitmap,
                ox=round(target_position_x),
                oy=round(target_position_y),
                source_bitmap=tick2_bitmap,
                px=0,
                py=0,
                angle=0,  # in radians
            )

    def update_roll(self, angle):
        """
        update roll/pitch
        """
        starting_angle = -90 * DEG_TO_RAD

        angle = (angle * DEG_TO_RAD) + starting_angle

        deltax = round((self.radius - 2 * self.padding) * cos(angle))
        deltay = round((self.radius - 2 * self.padding) * sin(angle))

        self.indicator.location = (self.indix + deltax + 5, self.indiy + deltay + 30)

        dummy = [(0, 0), (0, 0), (0, 0), (0, 0)]
        for j, element in enumerate(self.indicator.points):
            dummy[j] = round(
                self.indicator_original_values[j][0] * cos(angle)
                - self.indicator_original_values[j][1] * sin(angle)
            ), round(
                self.indicator_original_values[j][1] * cos(angle)
                + self.indicator_original_values[j][0] * sin(angle)
            )
        self.indicator.points = dummy

    def update_pitch(self, angle):
        """
        Update pitch/roll
        """

        angle = angle * 0.017
        dummy = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        for j, element in enumerate(self.needle.points):
            dummy[j] = round(
                self.original_values[j][0] * cos(angle)
                - self.original_values[j][1] * sin(angle)
            ), round(
                self.original_values[j][1] * cos(angle)
                + self.original_values[j][0] * sin(angle)
            )
        self.needle.points = dummy

    def update_tilt(self, value):
        """
        update roll/pitch
        """
        self.level.y = value + self.level_origin_y
