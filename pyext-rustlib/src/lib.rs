#[macro_use]
extern crate cpython;

use cpython::{Python, PyResult};

//#[derive(Debug, Clone, Copy)]
//type GameMap = Vec<Vec<i8>>;

/*#[derive(Clone, Copy)]
struct GameMap {
    data: Vec<Vec<i8>>
}*/



/*
calculate_collision_to_z_buffer(
                    ray_angle,  f64
                    ray_position_x,  f64
                    ray_position_y,  f64
                    game_map, 20x20 vec
                    game_map_size_x, usize / i32  20
                    game_map_size_y, usize / i32  20
                    player_pos_x, f64
                    player_pos_y, f64
                    player_angle, f64
                    config_is_perspective_correction_on bool

*/

/*
.get_x_cor_ordered_z_buffer_data(
                    player_angle=player_angle, f64
                    player_pos_x=player_pos_x, f64
                    player_pos_y=player_pos_y, f64
                    config_fov=config_fov, usize i32
                    config_pixel_size=config_pixel_size, usize/i32
                    config_is_perspective_correction_on=config_is_perspective_correction_on, bool
                    mini_map_offset_x=mini_map_offset_x, usize / i32
                    game_map_size_x=game_map_size_x, usize / i32
                    game_map_size_y=game_map_size_y, usize / i32
                    game_map=game_map_data vec of vec 20x20
*/

fn calculate_collision_to_z_buffer (
    ray_angle: f64,
    ray_position_x: f64,
    ray_position_y: f64,
    game_map: &Vec<Vec<i8>>,
    game_map_size_x: usize,
    game_map_size_y: usize,
    player_pos_x: f64,
    player_pos_y: f64,
    player_angle: f64,
    config_is_perspective_correction_on: bool) -> (i32, f64, i32, f64, f64, f64, f64){

        /*returns
        
        object_type,
                    ray_distance_from_player_with_perspective_correction,
                    object_on_the_map_type_id % 10,  # 0 - 9 objects, 10+ walls
                    ray_position_x - ray_position_for_map_collision_x,
                    ray_position_y - ray_position_for_map_collision_y,
                    ray_position_x,
                    ray_position_y,
        */
        let mut ray_position_for_map_collision_x: i8 = ray_position_x.floor() as i8;
        if 90.0 < ray_angle && ray_angle < 270.0 {
            ray_position_for_map_collision_x = f64::ceil(ray_position_x - 1.0) as i8;
        }
        let mut ray_position_for_map_collision_y: i8 = ray_position_y.floor() as i8;

        if 180.0 < ray_angle && ray_angle < 360.0 {
            ray_position_for_map_collision_y = f64::ceil(ray_position_y - 1.0) as i8;
        }
            

        if 0 <= ray_position_for_map_collision_x && ray_position_for_map_collision_x < game_map_size_x as i8 &&
                00 <= ray_position_for_map_collision_y && ray_position_for_map_collision_y < game_map_size_y as i8 {

            let object_on_the_map_type_id = game_map[
                ray_position_for_map_collision_y as usize][ray_position_for_map_collision_x as usize];
            /*let ray_position_offset_from_the_object_edge = (
                    (ray_position_x - ray_position_for_map_collision_x)
                    + (ray_position_y - ray_position_for_map_collision_y)
            )*/

            // object_on_the_map_type_id_with_offset = object_on_the_map_type_id + ray_position_offset_from_the_object_edge

            let ray_distance_from_player = f64::hypot(player_pos_x - ray_position_x, player_pos_y - ray_position_y);
            
            let mut object_type = 2; // wall by default
            if object_on_the_map_type_id < 0 {  // floor/ceiling
                object_type = 3
            } else if  0 <= object_on_the_map_type_id && object_on_the_map_type_id < 10 {
                object_type = 1  // object
            }

            if config_is_perspective_correction_on {
                let ray_perspective_correction_angle = ray_angle - player_angle;
                let ray_distance_from_player_with_perspective_correction = f64::cos(
                    f64::to_radians(ray_perspective_correction_angle)
                ) * ray_distance_from_player;
                return (
                    object_type,
                    ray_distance_from_player_with_perspective_correction,
                    object_on_the_map_type_id as i32 % 10,  // 0 - 9 objects, 10+ walls
                    ray_position_x - ray_position_for_map_collision_x as f64,
                    ray_position_y - ray_position_for_map_collision_y as f64,
                    ray_position_x,
                    ray_position_y,
                )
            } else {
                return (
                    object_type,
                    ray_distance_from_player,
                    object_on_the_map_type_id as i32  % 10,  // 0 - 9 objects, 10+ walls
                    ray_position_x - ray_position_for_map_collision_x as f64,
                    ray_position_y - ray_position_for_map_collision_y as f64,
                    ray_position_x,
                    ray_position_y,
                )
            }
    }
    (1, 1.0, 1, 1.0, 1.0, 1.0, 1.0)

}


fn get_x_cor_ordered_z_buffer_data_rust(_py: Python,
    player_angle: f64, 
    player_pos_x: f64, 
    player_pos_y: f64, 
    config_fov: usize,
    config_pixel_size: usize,
    config_is_perspective_correction_on: bool,
    mini_map_offset_x: usize,
    game_map_size_x: usize,
    game_map_size_y: usize,
    game_map: Vec<Vec<i8>>) -> PyResult<Vec<(f64, Vec<(f64,f64,f64,f64,f64,f64,usize,f64)>)>> {
        //let map = GameMap { data: game_map };

        let config_fov_f = config_fov as f64;

        let player_angle_start = player_angle - config_fov_f / 2.0;
        let mut x_cor_z_buffer_objects: Vec<(f64, Vec<(f64,f64,f64,f64,f64,f64,usize,f64)>)> = vec![];

        for screen_x in (0..mini_map_offset_x).step_by(config_pixel_size) {
            let mut ray_angle = player_angle_start + config_fov_f / mini_map_offset_x as f64 * screen_x as f64;
            
            // degrees fixed to range 0 - 359
            ray_angle %= 360.0;

            let mut ray_position_x = player_pos_x;  // start position of ray on X axis
            let mut ray_position_y = player_pos_y;  // start position of ray on Y axis

            let mut z_buffer_objects: Vec<(f64,f64,f64,f64,f64,f64,usize,f64)> = vec![];
            let mut ttl = 1000;

            while 0.0 < ray_position_x && ray_position_x < game_map_size_x as f64 &&
                0.0 < ray_position_y && ray_position_y < game_map_size_y as f64 && ttl > 0
             {
                ttl -= 1;
                let detected = calculate_collision_to_z_buffer(
                    ray_angle, ray_position_x, ray_position_y,
                    &game_map, game_map_size_x, game_map_size_y,
                    player_pos_x, player_pos_y, player_angle,
                    config_is_perspective_correction_on
                );

                match detected {
                    (1, 1.0, 1, 1.0, 1.0, 1.0, 1.0) => {},
                    _ => {z_buffer_objects.push(  //TODO REFACTOR
                        (detected.1, 
                        detected.2 as f64, 
                        detected.3, 
                        detected.4, 
                        detected.5, 
                        detected.6, 
                        detected.0 as usize,
                        ray_angle));
                    if detected.0 == 2 {
                        break; // cannot see behind the first wall                        
                    }}
                }
                let obj = move_ray_rust(ray_angle, ray_position_x, ray_position_y);
                ray_position_x = obj[0]; //TODO REFACTOR
                ray_position_y = obj[1];

            }
            x_cor_z_buffer_objects.push((screen_x as f64, z_buffer_objects));
        }    
        //  x_cor_z_buffer_objects.append((screen_x, z_buffer_objects))
        //Ok(vec![(1.0, vec![(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2, 1.0)])])
        Ok(x_cor_z_buffer_objects)
}

fn move_ray_rust(ray_angle: f64, ray_position_x: f64, ray_position_y: f64) -> Vec<f64> {
    /*# QUADRANTS:
        # 1
        # 0 - 90
        # 2
        # 90 - 180
        # 3
        # 180 - 270
        # 4
        # 270 - 360*/
        let mut ray_pos_x = ray_position_x;
        let mut ray_pos_y = ray_position_y;

        if 0.0 <= ray_angle && ray_angle <= 90.0 {
            let ray_length_delta_x = 1.0 + ray_position_x.floor() - ray_pos_x;
            let ray_length_delta_y = 1.0 + ray_position_y.floor() - ray_pos_y;

            let ray_angle_to_tile_edge = f64::to_degrees(f64::atan(ray_length_delta_y / ray_length_delta_x));

            if ray_angle_to_tile_edge >= ray_angle {
                ray_pos_x = ray_pos_x + ray_length_delta_x;
                ray_pos_y += f64::tan(f64::to_radians(ray_angle)) * ray_length_delta_x;
            }else{
                ray_pos_x += ray_length_delta_y / f64::tan(f64::to_radians(ray_angle));
                ray_pos_y = ray_pos_y + ray_length_delta_y;
            }

        } else if 90.0 < ray_angle && ray_angle < 180.0 {
            let ray_length_delta_x = 1.0 - f64::ceil(ray_position_x).floor() + ray_position_x;
            let ray_length_delta_y = 1.0 + ray_position_y.floor() - ray_position_y;
            let ray_angle_to_tile_edge = 90.0 + f64::to_degrees(f64::atan(ray_length_delta_x / ray_length_delta_y));

            if ray_angle_to_tile_edge <= ray_angle {
                ray_pos_x = ray_pos_x - ray_length_delta_x;
                ray_pos_y += ray_length_delta_x / f64::tan(f64::to_radians(ray_angle - 90.0));
            } else {
                ray_pos_x -= f64::tan(f64::to_radians(ray_angle - 90.0)) * ray_length_delta_y;
                ray_pos_y = ray_pos_y + ray_length_delta_y;
            }

        } else if  180.0 <= ray_angle && ray_angle < 270.0 {
            let ray_length_delta_x = 1.0 - f64::ceil(ray_position_x).floor()  + ray_position_x;
            let ray_length_delta_y = 1.0 - f64::ceil(ray_position_y).floor()  + ray_position_y;
            let ray_angle_to_tile_edge = 180.0 + f64::to_degrees(f64::atan(ray_length_delta_y / ray_length_delta_x));

            if ray_angle_to_tile_edge > ray_angle {
                ray_pos_x = ray_pos_x - ray_length_delta_x;
                ray_pos_y -= f64::tan(f64::to_radians(ray_angle - 180.0)) * ray_length_delta_x;
            }else {
                ray_pos_x -= ray_length_delta_y / f64::tan(f64::to_radians(ray_angle - 180.0));
                ray_pos_y = ray_pos_y - ray_length_delta_y;
            }

        } else if  270.0 <= ray_angle && ray_angle < 360.0 {
            let ray_length_delta_x = 1.0 + ray_pos_x.floor()  - ray_pos_x;
            let ray_length_delta_y = 1.0 - f64::ceil(ray_position_y).floor()  + ray_position_y;
            let ray_angle_to_tile_edge = 270.0 + f64::to_degrees(f64::atan(ray_length_delta_x / ray_length_delta_y));

            if ray_angle_to_tile_edge > ray_angle {
                ray_pos_x += f64::tan(f64::to_radians(ray_angle - 270.0)) * ray_length_delta_y;
                ray_pos_y = ray_pos_y - ray_length_delta_y;
            }else{
                ray_pos_x = ray_pos_x + ray_length_delta_x;
                ray_pos_y -= ray_length_delta_x / f64::tan(f64::to_radians(ray_angle - 270.0));
            }               
    }
    //Ok(vec![ray_position_x, ray_position_y])
    vec![ray_pos_x, ray_pos_y]

}

py_module_initializer!(rustlib, |py, m | {
    m.add(py, "__doc__", "This module is implemented in Rust")?;
    //m.add(py, "move_ray_rust", py_fn!(py, move_ray_rust(ray_angle: f64, ray_position_x: f64, ray_position_y: f64)))?;
    m.add(py, "get_x_cor_ordered_z_buffer_data_rust", py_fn!(py, get_x_cor_ordered_z_buffer_data_rust(player_angle: f64, 
        player_pos_x: f64, 
        player_pos_y: f64, 
        config_fov: usize,
        config_pixel_size: usize,
        config_is_perspective_correction_on: bool,
        mini_map_offset_x: usize,
        game_map_size_x: usize,
        game_map_size_y: usize,
        game_map: Vec<Vec<i8>>)))?;
    
    Ok(())
});


pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
