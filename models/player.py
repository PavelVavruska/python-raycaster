#  Copyright (c) 2019 Pavel Vavruska
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

MAX_VELOCITY_ANGLE = 10
MAX_VELOCITY_STEP = 2


class Player:
    def __init__(self, x, y, angle):
        self.__x = x
        self.__y = y
        self.__angle = angle
        self.__velocity_x = 0
        self.__velocity_y = 0
        self.__velocity_angle = 0

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def angle(self):
        return self.__angle

    @property
    def velocity_x(self):
        return self.__velocity_x

    @property
    def velocity_y(self):
        return self.__velocity_y

    @property
    def velocity_angle(self):
        return self.__velocity_angle

    def set_x(self, x):
        self.__x = x

    def set_y(self, y):
        self.__y = y

    def set_angle(self, angle):
        self.__angle = angle

    def set_velocity_x(self, velocity_x):
        velocity_x = max(velocity_x, -MAX_VELOCITY_STEP)
        self.__velocity_x = min(velocity_x, MAX_VELOCITY_STEP)

    def set_velocity_y(self, velocity_y):
        velocity_y = max(velocity_y, -MAX_VELOCITY_STEP)
        self.__velocity_y = min(velocity_y, MAX_VELOCITY_STEP)

    def set_velocity_angle(self, velocity_angle):
        velocity_angle = max(velocity_angle, -MAX_VELOCITY_ANGLE)
        self.__velocity_angle = min(velocity_angle, MAX_VELOCITY_ANGLE)

    def process_view_angle(self):
        angle = self.angle
        velocity_angle = self.velocity_angle
        self.set_angle(angle + velocity_angle)
        self.set_velocity_angle(velocity_angle*0.2)

        if angle < 0 or angle >= 360:
            self.set_angle(angle % 360)

    def move_player_on_map(self, game_map_data):
        player_x = self.x
        player_y = self.y
        player_velocity_x = self.velocity_x
        player_velocity_y = self.velocity_y

        wanted_x = player_x + player_velocity_x
        wanted_y = player_y + player_velocity_y

        # setting collision offset by vectors direction (strafe walk, backwards walking, etc.)
        collision_offset_x = 0.4 if player_velocity_x >= 0 else -0.4
        collision_offset_y = 0.4 if player_velocity_y >= 0 else -0.4

        collision_point_x = int(wanted_x + collision_offset_x)
        if (
                game_map_data[int(player_y)][collision_point_x] < 10 and
                game_map_data[int(player_y + collision_offset_y)][collision_point_x] < 10
           ):
            self.set_x(wanted_x)

        collision_point_y = int(wanted_y + collision_offset_y)
        if (
                game_map_data[collision_point_y][int(player_x)] < 10 and
                game_map_data[collision_point_y][int(player_x + collision_offset_x)] < 10
           ):
            self.set_y(wanted_y)
        self.set_velocity_x(player_velocity_x * 0.2)
        self.set_velocity_y(player_velocity_y * 0.2)

    def move_player(self, game_map_data):
        self.move_player_on_map(game_map_data)
        self.process_view_angle()

    def tick(self, game_map_data):
        self.move_player(game_map_data)

    def __str__(self):
        return u'Player: x {0:f}, y {1:f}, < {2:f}'.format(self.x, self.y, self.angle)