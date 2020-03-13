import math


class Raycaster:

    @classmethod
    def calculate_collision_to_z_buffer(cls, ray_angle, ray_position_x, ray_position_y,
                                        game_map, game_map_size_x, game_map_size_y,
                                        player_pos_x, player_pos_y, player_angle,
                                        config_is_perspective_correction_on,
                                        ):
        ray_position_for_map_collision_x = int(ray_position_x)
        if 90 < ray_angle < 270:
            ray_position_for_map_collision_x = math.ceil(ray_position_x - 1)
        ray_position_for_map_collision_y = int(ray_position_y)

        if 180 < ray_angle < 360:
            ray_position_for_map_collision_y = math.ceil(ray_position_y - 1)

        if (0 <= ray_position_for_map_collision_x < game_map_size_x and
                0 <= ray_position_for_map_collision_y < game_map_size_y):

            object_on_the_map_type_id = game_map[
                int(ray_position_for_map_collision_y)][
                int(ray_position_for_map_collision_x)
            ]
            ray_position_offset_from_the_object_edge = (
                    (ray_position_x - ray_position_for_map_collision_x)
                    + (ray_position_y - ray_position_for_map_collision_y)
            )

            object_on_the_map_type_id_with_offset = object_on_the_map_type_id + ray_position_offset_from_the_object_edge

            if object_on_the_map_type_id != -1:  # read the map and save it to zbuffer

                ray_distance_from_player_x = player_pos_x - ray_position_x
                ray_distance_from_player_y = player_pos_y - ray_position_y
                ray_distance_from_player = math.sqrt(
                    math.pow(ray_distance_from_player_x, 2) + math.pow(ray_distance_from_player_y, 2)
                )
                isWall = True if object_on_the_map_type_id >=10 else False
                if config_is_perspective_correction_on:
                    ray_perspective_correction_angle = abs(ray_angle) - abs(player_angle)
                    ray_distance_from_player_with_perspective_correction = math.cos(
                        math.radians(ray_perspective_correction_angle)
                    ) * ray_distance_from_player
                    return (
                        isWall,
                        ray_distance_from_player_with_perspective_correction,
                        object_on_the_map_type_id_with_offset % 10
                    )
                else:
                    return (
                        isWall,
                        ray_distance_from_player,
                        object_on_the_map_type_id_with_offset - 10
                    )

    @classmethod
    def move_ray(cls, ray_angle, ray_position_x, ray_position_y):
        # QUADRANTS:
        # 1
        # 0 - 90
        # 2
        # 90 - 180
        # 3
        # 180 - 270
        # 4
        # 270 - 360
        if 0 <= ray_angle <= 90:
            ray_length_delta_x = 1 + int(ray_position_x) - ray_position_x
            ray_length_delta_y = 1 + int(ray_position_y) - ray_position_y

            ray_angle_to_tile_edge = math.degrees(math.atan(ray_length_delta_y / ray_length_delta_x))

            if ray_angle_to_tile_edge >= ray_angle:
                ray_position_x = ray_position_x + ray_length_delta_x
                ray_position_y += math.tan(math.radians(ray_angle)) * ray_length_delta_x
            else:
                ray_position_x += ray_length_delta_y / math.tan(math.radians(ray_angle))
                ray_position_y = ray_position_y + ray_length_delta_y

        elif 90 < ray_angle < 180:
            ray_length_delta_x = 1 - int(math.ceil(ray_position_x)) + ray_position_x
            ray_length_delta_y = 1 + int(ray_position_y) - ray_position_y
            ray_angle_to_tile_edge = 90 + math.degrees(math.atan(ray_length_delta_x / ray_length_delta_y))

            if ray_angle_to_tile_edge <= ray_angle:
                ray_position_x = ray_position_x - ray_length_delta_x
                ray_position_y += ray_length_delta_x / math.tan(math.radians(ray_angle - 90))
            else:
                ray_position_x -= math.tan(math.radians(ray_angle - 90)) * ray_length_delta_y
                ray_position_y = ray_position_y + ray_length_delta_y

        elif 180 <= ray_angle < 270:
            ray_length_delta_x = 1 - int(math.ceil(ray_position_x)) + ray_position_x
            ray_length_delta_y = 1 - int(math.ceil(ray_position_y)) + ray_position_y
            ray_angle_to_tile_edge = 180 + math.degrees(math.atan(ray_length_delta_y / ray_length_delta_x))

            if ray_angle_to_tile_edge > ray_angle:
                ray_position_x = ray_position_x - ray_length_delta_x
                ray_position_y -= math.tan(math.radians(ray_angle - 180)) * ray_length_delta_x
            else:
                ray_position_x -= ray_length_delta_y / math.tan(math.radians(ray_angle - 180))
                ray_position_y = ray_position_y - ray_length_delta_y

        elif 270 <= ray_angle < 360:
            ray_length_delta_x = 1 + int(ray_position_x) - ray_position_x
            ray_length_delta_y = 1 - int(math.ceil(ray_position_y)) + ray_position_y
            ray_angle_to_tile_edge = 270 + math.degrees(math.atan(ray_length_delta_x / ray_length_delta_y))

            if ray_angle_to_tile_edge > ray_angle:
                ray_position_x += math.tan(math.radians(ray_angle - 270)) * ray_length_delta_y
                ray_position_y = ray_position_y - ray_length_delta_y
            else:
                ray_position_x = ray_position_x + ray_length_delta_x
                ray_position_y -= ray_length_delta_x / math.tan(math.radians(ray_angle - 270))
        return ray_position_x, ray_position_y

    @classmethod
    def get_x_cor_ordered_z_buffer_data(cls,
                                        player_angle, player_pos_x, player_pos_y,
                                        config_fov, config_pixel_size, config_is_perspective_correction_on,
                                        mini_map_offset_x, game_map_size_x, game_map_size_y, game_map):
        # player_angle = self.player.angle
        player_angle_start = player_angle - config_fov / 2
        x_cor_z_buffer_walls = []
        x_cor_z_buffer_objects = []
        for screen_x in range(0, int(mini_map_offset_x), config_pixel_size):
            ray_angle = player_angle_start + config_fov / mini_map_offset_x * screen_x

            # degrees fixed to range 0 - 359
            ray_angle %= 360

            ray_position_x = player_pos_x  # start position of ray on X axis
            ray_position_y = player_pos_y  # start position of ray on Y axis

            z_buffer_walls = []
            z_buffer_objects = []

            while (
                    0 < ray_position_x < game_map_size_x and
                    0 < ray_position_y < game_map_size_y
            ):
                detected = cls.calculate_collision_to_z_buffer(
                    ray_angle, ray_position_x, ray_position_y,
                    game_map, game_map_size_x, game_map_size_y,
                    player_pos_x, player_pos_y, player_angle,
                    config_is_perspective_correction_on
                )
                if detected:
                    if detected[0]: # is wall
                        z_buffer_walls.append(detected)
                        break  # cannot see behind the first wall
                    else:
                        z_buffer_objects.append(detected)

                ray_position_x, ray_position_y = cls.move_ray(
                    ray_angle, ray_position_x, ray_position_y
                )

            x_cor_z_buffer_walls.append((screen_x, z_buffer_walls))
            x_cor_z_buffer_objects.append((screen_x, z_buffer_objects))
        return (x_cor_z_buffer_walls, x_cor_z_buffer_objects)
