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

import math
import time
import tkinter
from PIL import Image

# constants
from models.config import Config
from models.keyboard import Keyboard
from models.map import Map
from models.painter import Painter
from models.player import Player


WINDOW_WIDTH, WINDOW_HEIGHT = 320, 200
ENGINE_PIXEL_SIZE = 5
NUMBER_OF_HORIZONTAL_BIG_PIXELS = WINDOW_WIDTH/ENGINE_PIXEL_SIZE

MICROSECONDS_IN_SECOND = 1_000_000
NANOSECONDS_IN_SECOND = 1_000_000_000

COLOR_WHITE = '#FFFFFF'
COLOR_BLACK = '#000000'
COLOR_CYAN = '#0000FF'
COLOR_GREEN = '#00FF00'
COLOR_RED = '#FF0000'

# tkinter init

texture = Image.open("static/textures.png")
pixel_data = texture.load()

tk = tkinter.Tk()
frame = tkinter.Frame(tk, width=100, height=100)
msgL1 = tkinter.StringVar()
msgL1.set('Keyboard')
msgL2 = tkinter.StringVar()
msgL2.set('Player')
msgL3 = tkinter.StringVar()
msgL3.set('Frametimes')
msgL4 = tkinter.StringVar()
msgL4.set('Player - additional')
label = tkinter.Label(frame, textvariable=msgL1)
label.pack()
label = tkinter.Label(frame, textvariable=msgL2)
label.pack()
label = tkinter.Label(frame, textvariable=msgL3)
label.pack()
label = tkinter.Label(frame, textvariable=msgL4)
label.pack()
frame.pack()


tStart = 0
tEnd = int(round(time.time() * 1_000_000))  # μs
xCor = WINDOW_WIDTH // 2
yCor = WINDOW_HEIGHT // 2
canvas = tkinter.Canvas(tk, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=COLOR_BLACK)
canvas.pack()


keyboard = Keyboard()

frame.bind_all('<KeyPress>', keyboard.key_press_handler)
frame.bind_all('<KeyRelease>', keyboard.key_release_handler)

#init entities
player = Player(3, 3, 100)
config = Config(100, True, True)
game_map = Map()

mini_map_offset_x = WINDOW_WIDTH/ENGINE_PIXEL_SIZE - game_map.size_x
mini_map_offset_y = 0
isAlive = True

painter = Painter(canvas, ENGINE_PIXEL_SIZE)



def draw_minimap(mini_map_offset_x, mini_map_offset_y):
    # render minimap (player, )
    # draw objects
    for id_y, y in enumerate(game_map.data):
        for id_x, x in enumerate(y):
            if x < 0:
                color = COLOR_BLACK
            elif x >= 0 and x < 9:
                color = COLOR_RED
            else:
                color = COLOR_GREEN
            painter.colored_rectangle(mini_map_offset_x + id_x, mini_map_offset_y + id_y, color)
    # draw player
    # player base
    player_on_minimap_x = mini_map_offset_x + int(player.x)
    player_on_minimap_y = mini_map_offset_y + int(player.y)
    painter.colored_rectangle(player_on_minimap_x,
                            player_on_minimap_y,
                            COLOR_CYAN)
    player_on_minimap_x += math.cos(math.radians(player.angle))
    player_on_minimap_y += math.sin(math.radians(player.angle))
    painter.colored_rectangle(player_on_minimap_x,
                            player_on_minimap_y,
                            COLOR_WHITE)


def draw_from_z_buffer_wall(z_buffer_wall, screen_x, param, param1):
    for entry in sorted(z_buffer_wall, reverse=True):
        # Actual line by line rendering of the visible object
        if entry[0] < 1:
            continue
        start = int(WINDOW_HEIGHT / 2 - WINDOW_HEIGHT / (entry[0] * 2))
        #end = int(WINDOW_HEIGHT / 2 + WINDOW_HEIGHT / (entry[0] * 2))
        wall_vertical_length = int(2 * WINDOW_HEIGHT / (entry[0] * 2))

        size_of_texture_pixel = int(wall_vertical_length / 64)
        one_artificial_pixel_size = size_of_texture_pixel if size_of_texture_pixel > ENGINE_PIXEL_SIZE else ENGINE_PIXEL_SIZE

        last_pixel_position = None
        for vertical_wall_pixel in range(0, wall_vertical_length, one_artificial_pixel_size):
            #if (color_pixel > 63):
            #    color_pixel = 63

            #yCorTexture = 64 + color_pixel
            yCorTexture = 64 + 64/wall_vertical_length*vertical_wall_pixel

            xCorTexture = int(entry[1] * 64)

            if (xCorTexture <= 1):
                xCorTexture = 1

            red, green, blue, alpha = pixel_data[xCorTexture, yCorTexture]
            #imgColor = Color(imgObjects.getRGB(xCorTexture, 64 + color_pixel))
            distance_dark_blue = int(entry[0]*3)
            distance_dark = distance_dark_blue*2
            red -= distance_dark if red > distance_dark else red
            green -= distance_dark if green > distance_dark else green
            blue -= distance_dark_blue if blue > distance_dark_blue else blue
            result_color_list = ['#']
            result_color_list.append(str(format(red, 'x')).zfill(2))
            result_color_list.append(str(format(green, 'x')).zfill(2))
            result_color_list.append(str(format(blue, 'x')).zfill(2))
            result_color_string = ''.join(result_color_list)
            # colors skipped
            #if (start + wall_vertical_length / 64 * color_pixel >= -64 and start + wall_vertical_length / 64 * color_pixel <= 450):
            current_pixel_position = (start + vertical_wall_pixel)/ENGINE_PIXEL_SIZE
            painter.colored_line(screen_x,
                               current_pixel_position,
                               last_pixel_position if last_pixel_position else current_pixel_position + 1,
                               result_color_string)
            last_pixel_position = current_pixel_position
        break


def draw_scene(param, param1):
    player_angle = player.angle
    player_angle_start = player_angle - config.fov / 2


    for screen_x in range(1, int(mini_map_offset_x)):
        ray_angle = player_angle_start + config.fov / mini_map_offset_x * screen_x

        # degrees fixed to range 0 - 359
        if ray_angle < 0:
            ray_angle += 360
        elif ray_angle >= 360:
            ray_angle -= 360

        ray_position_x = player.x  # start position of ray on X axis
        ray_position_y = player.y  # start position of ray on Y axis

        z_buffer_wall = []
        z_buffer_object = []

        #ray_length_delta_x = 0.0
        #ray_length_delta_y = 0.0
        #ray_angle_to_tile_edge = 0
        #ray_perspective_correction_angle = 0

        ray_position_previous_x = 0
        ray_position_previous_y = 0

        ray_time_to_die = 50

        while (ray_position_x > 0 and
               ray_position_y > 0 and
               ray_position_x < game_map.size_x and
               ray_position_y < game_map.size_y and
               ray_time_to_die > 0):

            ray_time_to_die-=1

            if (ray_position_previous_x == ray_position_x and ray_position_previous_y == ray_position_y):
                break
            ray_position_for_map_collision_x = int(ray_position_x)

            if (ray_angle > 90 and ray_angle < 270):
                ray_position_for_map_collision_x = math.ceil(ray_position_x - 1)
            ray_position_for_map_collision_y = int(ray_position_y)

            if (ray_angle > 180 and ray_angle < 360):
                ray_position_for_map_collision_y = math.ceil(ray_position_y - 1)

            if (ray_position_for_map_collision_x >= 0 and
                    ray_position_for_map_collision_y >= 0 and
                    ray_position_for_map_collision_x < game_map.size_x and
                    ray_position_for_map_collision_y < game_map.size_y):
                object_on_the_map_type_id = game_map.get_at(int(ray_position_for_map_collision_y), int(ray_position_for_map_collision_x))
                ray_position_offset_from_the_object_edge = ((ray_position_x - ray_position_for_map_collision_x) + (ray_position_y - ray_position_for_map_collision_y))

                object_on_the_map_type_id_with_offset = object_on_the_map_type_id + ray_position_offset_from_the_object_edge;

                if (object_on_the_map_type_id != -1): # read the map and save it to zbuffer

                    ray_distance_from_player_x = player.x - ray_position_x
                    ray_distance_from_player_y = player.y - ray_position_y
                    ray_distance_from_player = math.sqrt(math.pow(ray_distance_from_player_x, 2) + math.pow(ray_distance_from_player_y, 2));
                    if object_on_the_map_type_id >= 10:  # solid walls
                        if config.is_perspective_correction_on:
                            ray_perspective_correction_angle = abs(ray_angle) - abs(player_angle)
                            ray_distance_from_player_with_perspective_correction = math.cos(math.radians(ray_perspective_correction_angle)) * ray_distance_from_player
                            z_buffer_wall.append((ray_distance_from_player_with_perspective_correction, object_on_the_map_type_id_with_offset - 10))
                        else:
                            z_buffer_wall.append((ray_distance_from_player, object_on_the_map_type_id_with_offset - 10))
                        break
                    else:  # transparent walls
                        if (config.is_perspective_correction_on):
                            ray_perspective_correction_angle = abs(ray_angle) - abs(player_angle)
                            ray_distance_from_player_with_perspective_correction = math.cos(math.radians(ray_perspective_correction_angle)) * ray_distance_from_player
                            z_buffer_object.append((ray_distance_from_player_with_perspective_correction, object_on_the_map_type_id_with_offset))
                        else:
                            z_buffer_object.append((ray_distance_from_player, object_on_the_map_type_id_with_offset))


            # QUADRANTS:
            # 1
            # 0 - 90
            # 2
            # 90 - 180
            # 3
            # 180 - 270
            # 4
            # 270 - 360
            if ray_angle >= 0 and ray_angle <= 90:
                ray_length_delta_x = 1 + int(ray_position_x) - ray_position_x
                ray_length_delta_y = 1 + int(ray_position_y) - ray_position_y

                ray_angle_to_tile_edge = math.degrees(math.atan(ray_length_delta_y / ray_length_delta_x))

                if ray_angle_to_tile_edge >= ray_angle:
                    ray_position_x = ray_position_x + ray_length_delta_x
                    ray_position_y += math.tan(math.radians(ray_angle)) * ray_length_delta_x
                else:
                    ray_position_x += ray_length_delta_y / math.tan(math.radians(ray_angle))
                    ray_position_y = ray_position_y + ray_length_delta_y


            elif ray_angle > 90 and ray_angle < 180:
                ray_length_delta_x = 1 - int(math.ceil(ray_position_x)) + ray_position_x
                ray_length_delta_y = 1 + int(ray_position_y) - ray_position_y
                ray_angle_to_tile_edge = 90 + math.degrees(math.atan(ray_length_delta_x / ray_length_delta_y))

                if (ray_angle_to_tile_edge <= ray_angle):
                    ray_position_x = ray_position_x - ray_length_delta_x
                    ray_position_y += ray_length_delta_x / math.tan(math.radians(ray_angle - 90))
                else:
                    ray_position_x -= math.tan(math.radians(ray_angle - 90)) * ray_length_delta_y
                    ray_position_y = ray_position_y + ray_length_delta_y

            elif (ray_angle >= 180 and ray_angle < 270):
                ray_length_delta_x = 1 - int(math.ceil(ray_position_x)) + ray_position_x
                ray_length_delta_y = 1 - int(math.ceil(ray_position_y)) + ray_position_y
                ray_angle_to_tile_edge = 180 + math.degrees(math.atan(ray_length_delta_y / ray_length_delta_x))

                if (ray_angle_to_tile_edge > ray_angle):
                    ray_position_x = ray_position_x - ray_length_delta_x
                    ray_position_y -= math.tan(math.radians(ray_angle - 180)) * ray_length_delta_x
                else:
                    ray_position_x -= ray_length_delta_y / math.tan(math.radians(ray_angle - 180))
                    ray_position_y = ray_position_y - ray_length_delta_y

            elif (ray_angle >= 270 and ray_angle < 360):
                ray_length_delta_x = 1 + int(ray_position_x) - ray_position_x
                ray_length_delta_y = 1 - int(math.ceil(ray_position_y)) + ray_position_y
                ray_angle_to_tile_edge = 270 + math.degrees(math.atan(ray_length_delta_x / ray_length_delta_y))

                if (ray_angle_to_tile_edge > ray_angle):
                    ray_position_x += math.tan(math.radians(ray_angle - 270)) * ray_length_delta_y
                    ray_position_y = ray_position_y - ray_length_delta_y
                else:
                    ray_position_x = ray_position_x + ray_length_delta_x
                    ray_position_y -= ray_length_delta_x / math.tan(math.radians(ray_angle - 270))


            #paintColoredDotInMenu(g2d, ray_position_x, rayPositionY, Color.green);
            ray_position_previous_x = ray_position_y
            ray_position_previous_y = ray_position_x

        draw_from_z_buffer_wall(z_buffer_wall, screen_x, 0, 0)
        #drawFromZBufferObject(zBufferObject, screenCoordinateX, threadCurrentNumberFinal, threadStartCor);


while isAlive:
    tStart = tEnd
    tEnd = int(round(time.time() * MICROSECONDS_IN_SECOND))  # μs
    frameTime = tEnd - tStart
    framesPerSecond = MICROSECONDS_IN_SECOND // frameTime
    timeDelta = int(50*MICROSECONDS_IN_SECOND - frameTime)  # 15 FPS
    if timeDelta > 0:
        pass
        #time.sleep(timeDelta/NANOSECONDS_IN_SECOND)
    msgL1.set("Keys: {0:s}".format(str(keyboard.keys)))
    msgL2.set(player)
    msgL3.set("FrameTime: {0:d} μs, FramePerSecond: {1:d}, waiting: {2:d} μs".format(frameTime, framesPerSecond, timeDelta))
    msgL4.set("PA: {0:.2f}, PSX: {1:.2f}, PSY: {2:.2f}".format(player.velocity_angle,
                                                                           player.velocity_x, player.velocity_y))

    # keyboard
    if 25 in keyboard.keys:  # 25 = w
        player.set_velocity_x(player.velocity_x + math.cos(math.radians(player.angle)) / 10)
        player.set_velocity_y(player.velocity_y + math.sin(math.radians(player.angle)) / 10)
    if 39 in keyboard.keys:  # 39 = s
        player.set_velocity_x(player.velocity_x - math.cos(math.radians(player.angle)) / 10)
        player.set_velocity_y(player.velocity_y - math.sin(math.radians(player.angle)) / 10)
    if 40 in keyboard.keys:  # 40 = d
        player.set_velocity_angle(player.velocity_angle + 25)
    if 38 in keyboard.keys:  # 38 = a
        player.set_velocity_angle(player.velocity_angle - 25)
    if 9 in keyboard.keys:  # ESC = 9
        isAlive = False


    #render_graphics
    # wipe screen
    canvas.delete("all")
    draw_scene(0,0)
    draw_minimap(mini_map_offset_x, mini_map_offset_y)

    #img.put("#ffffff", (xCor, yCor))
    player.tick()
    frame.update()
    frame.update_idletasks()

# end the game
frame.quit()

