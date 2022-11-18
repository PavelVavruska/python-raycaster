#[macro_use]
extern crate cpython;

use std::cmp::{max, min};
use std::vec;

use cpython::{Python, PyResult, PySet, PyBytes};

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
        let mut ray_position_for_map_collision_x: i32 = ray_position_x as i32;
        if 90.0 < ray_angle && ray_angle < 270.0 {
            ray_position_for_map_collision_x = f64::ceil(ray_position_x - 1.0) as i32;
        }
        let mut ray_position_for_map_collision_y: i32 = ray_position_y as i32;

        if 180.0 < ray_angle && ray_angle < 360.0 {
            ray_position_for_map_collision_y = f64::ceil(ray_position_y - 1.0) as i32;
        }
            

        if 0 <= ray_position_for_map_collision_x && ray_position_for_map_collision_x < game_map_size_x as i32 &&
                0 <= ray_position_for_map_collision_y && ray_position_for_map_collision_y < game_map_size_y as i32 {

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
    !unreachable!()
    //(1, 1.0, 1, 1.0, 1.0, 1.0, 1.0)

}

fn inner_x_cor_ordered_z_buffer(player_angle: f64, 
    player_pos_x: f64, 
    player_pos_y: f64, 
    config_fov: usize,
    config_pixel_size: usize,
    config_is_perspective_correction_on: bool,
    mini_map_offset_x: usize,
    game_map_size_x: usize,
    game_map_size_y: usize,
    game_map: Vec<Vec<i8>>) -> [u8; WINDOW_WIDTH*WINDOW_HEIGHT*4] {
        let config_fov_f = config_fov as f64;

        let player_angle_start = player_angle - config_fov_f / 2.0;
        let mut x_cor_z_buffer_objects: Vec<(usize, Vec<(f64,f64,f64,f64,f64,f64,usize,f64)>)> = vec![];

        for screen_x in (0..WINDOW_WIDTH).step_by(config_pixel_size) {
            let mut ray_angle = player_angle_start + config_fov_f / WINDOW_WIDTH as f64 * screen_x as f64;
            
            // degrees fixed to range 0 - 359
            ray_angle %= 360.0;
            

            if ray_angle < 0.0 {
                ray_angle += 360.0;
            }

            let mut ray_position_x = player_pos_x;  // start position of ray on X axis
            let mut ray_position_y = player_pos_y;  // start position of ray on Y axis

            let mut z_buffer_objects: Vec<(f64,f64,f64,f64,f64,f64,usize,f64)> = vec![];
            let mut ttl = 30;
           
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
            x_cor_z_buffer_objects.push((screen_x, z_buffer_objects));
        }    
        //  x_cor_z_buffer_objects.append((screen_x, z_buffer_objects))
        //Ok(vec![(1.0, vec![(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2, 1.0)])])
        
        
        
        //Ok(x_cor_z_buffer_objects)
        /*let mut result = vec![vec![]];
        for line in draw_from_z_buffer_objects(player_angle, x_cor_z_buffer_objects) {
            result.push(line.to_vec());
        }*/
        const BYTES_LEN: usize = WINDOW_WIDTH*WINDOW_HEIGHT*4 as usize;
        let mut result2 = [125 as u8; BYTES_LEN];
        /*for i in (0..20000).step_by(4) {
            result2[i] = 255;
            result2[i+1] = 0;
            result2[i+2] = 0;
            result2[i+3] = 255;
        }*/
        /*result2[1010] = 255;
        result2[2010] = 0;
        result2[3010] = 255;
        result2[4010] = 0;
        result2[5010] = 255;
        result2[1011] = 0;
        result2[2011] = 255;
        result2[3011] = 0;
        result2[4011] = 255;
        result2[5011] = 0;*/
        /*const BYTES_LEN: usize = 1000*600*4 as usize;
        let a = 10;

        
        */
        //let mut result2 = [0 as u8; BYTES_LEN];
        let mut index = 0;
        for row in draw_from_z_buffer_objects(player_angle, x_cor_z_buffer_objects) {
            
            for tuple in row {
                //println!("{tuple:?}");
                
                result2[index] = tuple.0 as u8;
                index += 1;
                result2[index] = tuple.1 as u8;
                index += 1;
                result2[index] = tuple.2 as u8;
                index += 1;
                result2[index] = 254 as u8;
                index += 1;
            }
        }

        /*let boxed_slice = v.into_boxed_slice();
        let boxed_array: Box<[T; 4]> = match boxed_slice.try_into() {
            Ok(ba) => ba,
            Err(o) => panic!("Expected a Vec of length {} but it was {}", 4, o.len()),
        };
        *boxed_array*/
        result2
    }



fn get_x_cor_ordered_z_buffer_data_rust(py: Python,
    player_angle: f64, 
    player_pos_x: f64, 
    player_pos_y: f64, 
    config_fov: usize,
    config_pixel_size: usize,
    config_is_perspective_correction_on: bool,
    mini_map_offset_x: usize,
    game_map_size_x: usize,
    game_map_size_y: usize,
    game_map: Vec<Vec<i8>>) -> PyResult<PyBytes> {// PyResult<Vec<Vec<(i32, i32, i32)>>> {//PyResult<[[(i32, i32, i32); 480]; 640]> {//PyResult<Vec<Vec<(i8,i8,i8)>>> {
    /*PyResult<Vec<(f64, Vec<(f64,f64,f64,f64,f64,f64,usize,f64)>)>> {*/
        //let map = GameMap { data: game_map };

        let array = inner_x_cor_ordered_z_buffer(player_angle,player_pos_x,player_pos_y,config_fov,config_pixel_size,config_is_perspective_correction_on,mini_map_offset_x,
            game_map_size_x,game_map_size_y,game_map);

        let result = PyBytes::new(py, &array);
        
        Ok(result)
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
            let ray_length_delta_x = 1.0 + ray_position_x as i32 as f64 - ray_pos_x;
            let ray_length_delta_y = 1.0 + ray_position_y as i32 as f64 - ray_pos_y;

            let ray_angle_to_tile_edge = f64::to_degrees(f64::atan(ray_length_delta_y / ray_length_delta_x));

            if ray_angle_to_tile_edge >= ray_angle {
                ray_pos_x = ray_pos_x + ray_length_delta_x;
                ray_pos_y += f64::tan(f64::to_radians(ray_angle)) * ray_length_delta_x;
            }else{
                ray_pos_x += ray_length_delta_y / f64::tan(f64::to_radians(ray_angle));
                ray_pos_y = ray_pos_y + ray_length_delta_y;
            }

        } else if 90.0 < ray_angle && ray_angle < 180.0 {
            let ray_length_delta_x = 1.0 - f64::ceil(ray_position_x) as i32 as f64 + ray_position_x;
            let ray_length_delta_y = 1.0 + ray_position_y as i32 as f64 - ray_position_y;
            let ray_angle_to_tile_edge = 90.0 + f64::to_degrees(f64::atan(ray_length_delta_x / ray_length_delta_y));

            if ray_angle_to_tile_edge <= ray_angle {
                ray_pos_x = ray_pos_x - ray_length_delta_x;
                ray_pos_y += ray_length_delta_x / f64::tan(f64::to_radians(ray_angle - 90.0));
            } else {
                ray_pos_x -= f64::tan(f64::to_radians(ray_angle - 90.0)) * ray_length_delta_y;
                ray_pos_y = ray_pos_y + ray_length_delta_y;
            }

        } else if  180.0 <= ray_angle && ray_angle < 270.0 {
            let ray_length_delta_x = 1.0 - f64::ceil(ray_position_x) as i32 as f64  + ray_position_x;
            let ray_length_delta_y = 1.0 - f64::ceil(ray_position_y) as i32 as f64  + ray_position_y;
            let ray_angle_to_tile_edge = 180.0 + f64::to_degrees(f64::atan(ray_length_delta_y / ray_length_delta_x));

            if ray_angle_to_tile_edge > ray_angle {
                ray_pos_x = ray_pos_x - ray_length_delta_x;
                ray_pos_y -= f64::tan(f64::to_radians(ray_angle - 180.0)) * ray_length_delta_x;
            }else {
                ray_pos_x -= ray_length_delta_y / f64::tan(f64::to_radians(ray_angle - 180.0));
                ray_pos_y = ray_pos_y - ray_length_delta_y;
            }

        } else if  270.0 <= ray_angle && ray_angle < 360.0 {
            let ray_length_delta_x = 1.0 + ray_pos_x as i32 as f64  - ray_pos_x;
            let ray_length_delta_y = 1.0 - f64::ceil(ray_position_y) as i32 as f64  + ray_position_y;
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

fn draw_from_z_buffer_objects(player_angle: f64, x_cor_ordered_z_buffer_objects: Vec<(usize, Vec<(f64,f64,f64,f64,f64,f64,usize,f64)>)>) -> [[(u8, u8, u8); WINDOW_WIDTH]; WINDOW_HEIGHT] {//Vec<Vec<(i8,i8,i8)>> {
    //let row = [(0,0,0); 480].to_vec();
    let mut canvas = [[(0,0,0); WINDOW_WIDTH]; WINDOW_HEIGHT]; //vec![vec![]];
    let dynamic_lighting = true;
    let pixel_size = 1;
    let window_height = WINDOW_HEIGHT;
    let half_window_height = window_height / 2;
    let double_window_height = window_height * 2;
    for (screen_x, z_buffer_wall) in x_cor_ordered_z_buffer_objects {
        
        let mut last_floor_position = None;
        let mut last_ceiling_position = None;
        let last_offset_x = 0;
        let last_offset_y = 0;
        //let reverse_z_buffer_wall = z_buffer_wall.iter().rev();
        for entry in z_buffer_wall.iter().rev() {

            // actual line by line rendering of the visible object
            let (mut object_distance, object_id, offset_x, offset_y, ray_x, ray_y, object_type, ray_angle) = *entry;
            if object_distance < 0.01 {
                object_distance = 0.01;
            }
                
            let start = half_window_height as f64 - window_height as f64 / (object_distance * 2.0);
            let wall_vertical_length_full = double_window_height as f64 / (object_distance * 2.0);

            let size_of_texture_pixel = (wall_vertical_length_full / 64.0) as i32;
            let mut one_artificial_pixel_size = size_of_texture_pixel;
            if size_of_texture_pixel <= 0 {
                one_artificial_pixel_size = 1;
            }

            let mut last_pixel_position = None;

            if last_ceiling_position.is_none() {
                last_ceiling_position = Some(0);
            }
            if last_floor_position.is_none(){
                last_floor_position = Some(window_height);
            }

            let texture_start_x = ray_x * 48.0 % 64.0;  // TODO
            let texture_start_y = ray_y * 48.0 % 64.0;
            let texture_start_x_delta = texture_start_x - last_offset_x as f64;
            let texture_start_y_delta = texture_start_y - last_offset_y as f64;
            if let Some(last_ceiling_position_some) = last_ceiling_position {// && object_type != 2 {  // skip only for walls
                if object_type != 2 {
                    // draw ceiling and floor


                    let y_ceiling_start = max(0, start as i32);
                    let y_ceiling_end = min(half_window_height, last_ceiling_position_some);
                    let ceiling_pos_delta: i32 = y_ceiling_end as i32 - y_ceiling_start;
                    let color = max(0, min(255, (255 - i32::abs(object_distance as i32 * 30)) as i32));
                    let mut x = 0;
                    for position_move in (y_ceiling_start..y_ceiling_end.try_into().unwrap()).step_by(pixel_size) {
                        let mut x_cor_texture = last_offset_x + texture_start_x_delta as i32 / ceiling_pos_delta * x * pixel_size as i32;
                        let mut y_cor_texture = last_offset_y + texture_start_y_delta as i32 / ceiling_pos_delta * x * pixel_size as i32;
                        x += 1;
                        if x_cor_texture <= 1 {
                            x_cor_texture = 1;
                        }

                        if y_cor_texture <= 1 {
                            y_cor_texture = 1;
                        }

                        x_cor_texture = max(0, min(x_cor_texture, 511));
                        y_cor_texture = max(0, min(y_cor_texture, 127));
                        let (red, green, blue, alpha) = (255 as u8,255 as u8,255 as u8,50 as u8); //TODO FIX cls.grass_pixel_data.get_at((int(x_cor_texture), int(y_cor_texture)));

                        // ceiling
                        /*pygame.draw.line(surface, (0, 0, blue), (screen_x, position_move),
                                            (
                                                screen_x, position_move + pixel_size),
                                            pixel_size)*/
                        if screen_x < WINDOW_WIDTH && position_move < WINDOW_HEIGHT.try_into().unwrap() {
                            canvas[position_move as usize][screen_x] = (red, green, blue);
                        }
                    }

                    // FLOOR
                    let mut floor_position = 0;
                    if let Some(position) = last_floor_position {
                        floor_position = position;
                    }
                    let tile_pos_start = max(half_window_height, floor_position);
                    let tile_pos_end = min(window_height, start as usize + wall_vertical_length_full as usize);
                    let tile_pos_delta = tile_pos_end - tile_pos_start;

                    x = 0;
                    for position_move in (tile_pos_start..tile_pos_end).step_by(pixel_size) {
                        let mut x_cor_texture = last_offset_x + texture_start_x_delta as i32 / tile_pos_delta as i32 * x * pixel_size as i32;
                        let mut y_cor_texture = last_offset_y + texture_start_y_delta as i32 / tile_pos_delta as i32 * x * pixel_size as i32;
                        x += 1;
                        if x_cor_texture <= 1 {
                            x_cor_texture = 1;
                        }                            

                        if y_cor_texture <= 1 {
                            y_cor_texture = 1;
                        }
                            

                        x_cor_texture = max(0, min(x_cor_texture, 511));
                        y_cor_texture = max(0, min(y_cor_texture, 127));
                        let (red, green, blue, alpha) = (255 as u8,255 as u8,50 as u8,50 as u8);; //TODO FIX cls.grass_pixel_data.get_at((int(x_cor_texture), int(y_cor_texture)));

                        // floor
                        /*pygame.draw.line(surface, (red, green, blue), (screen_x, position_move),
                                            (
                                                screen_x, position_move + pixel_size),
                                            pixel_size)*/
                        if screen_x < WINDOW_WIDTH && position_move < WINDOW_HEIGHT {
                            canvas[position_move as usize][screen_x] = (red, green, blue);
                        }
                        
                    }
                }
            }

            if object_type != 3 {  // for walls and objects  # and object_distance > 0.4
                let object_id_with_offset = object_id + offset_x + offset_y;
                for vertical_wall_pixel in (0..(wall_vertical_length_full) as i32).step_by(one_artificial_pixel_size.try_into().unwrap()) {

                
                    let mut y_cor_texture = (64.0 / wall_vertical_length_full * vertical_wall_pixel as f64) as i32;
                    if object_type == 2 {
                        y_cor_texture += 64;
                    }
                        
                    let mut x_cor_texture = (object_id_with_offset * 64.0) as i32;

                    if x_cor_texture <= 1 {
                        x_cor_texture = 1;
                    }

                    x_cor_texture = max(0, min(x_cor_texture, 511));
                    y_cor_texture = max(0, min(y_cor_texture, 127));
                    let (red, green, blue, alpha) = (50 as u8,50 as u8,255 as u8,255 as u8);;//TODO FIX cls.pixel_data.get_at((x_cor_texture, y_cor_texture))

                    let current_pixel_position = start as i32 + vertical_wall_pixel;
                    if green > 0 {                    

                        /*TODO LATER if dynamic_lighting {
                            distance_dark_blue = (object_distance * 3) as i32;
                            distance_dark = distance_dark_blue * 2;
                            red -= distance_dark if red > distance_dark else red;
                            green -= distance_dark if green > distance_dark else green;
                            blue -= distance_dark_blue if blue > distance_dark_blue else blue;
                        }*/

                        let result_color_tuple = (red, green, blue);

                        let mut pixel_position = 0;
                        if let Some(position) = last_pixel_position {
                            pixel_position = position;
                        } else {
                            pixel_position = current_pixel_position + 1;
                        }
                        for y in pixel_position..current_pixel_position {
                            if y < 0 || y >= WINDOW_HEIGHT.try_into().unwrap()  {
                                continue;
                            }
                                
                            //# walls
                            /*pygame.draw.line(surface, result_color_tuple, (screen_x, y),
                                                (
                                                    screen_x, y + pixel_size),
                                                pixel_size)*/
                            if screen_x < WINDOW_WIDTH {
                                canvas[y as usize][screen_x] = (red, green, blue);
                            }
                        }
                    }                    
                    last_pixel_position = Some(current_pixel_position);
                }
            }

            last_ceiling_position = Some(start as usize);
            last_floor_position = Some(start as usize + wall_vertical_length_full as usize);
            //let (last_offset_x, last_offset_y) = (texture_start_x, texture_start_y);
        }
    }
    
    
    
    //let a = 
    canvas
}


extern crate piston_window;



use piston_window::types::Color;
use piston_window::*;
use piston_window::color::{WHITE, RED, BLUE, GREEN, YELLOW, GRAY, CYAN, MAGENTA, MAROON};

const BACK_COLOR: Color = [0.0, 0.0, 0.0, 1.0];
// ZX Spectrum resolution 256×192
const WINDOW_WIDTH: usize = 1000;
const WINDOW_HEIGHT: usize = 600;

pub const TEXT_COLOR: Color = [1.0, 1.0, 1.0, 1.0];



pub struct Pos {
    pub x: f64,
    pub y: f64,
}

fn main_rust(_py: Python, text: f64) -> PyResult<f64> {
    // Prepare fonts
   
    // Prepare window settings
    let mut window_settings = piston_window::WindowSettings::new(
        "Raycaster",
        [
            WINDOW_WIDTH as u32,
            WINDOW_HEIGHT as u32,
        ],
    )
    .exit_on_esc(true);

    // Fix vsync extension error for linux
    window_settings.set_vsync(true);

    // Create a window
    let mut window: piston_window::PistonWindow = window_settings.build().unwrap();    
    let mut game_score:usize = 0;
    // how to text https://github.com/PistonDevelopers/piston-examples/blob/master/examples/hello_world.rs

    let mut is_player_dead = false;

    // Event loop
    if let Some(event) = window.next() {       
                
        // Draw all of them
        window.draw_2d(&event, |c, g, device| {
            piston_window::clear(BACK_COLOR, g);
            
            //let result = game.compute_one_tick(&c, g);
            let transform = c.transform.trans(10.0, WINDOW_HEIGHT as f64 - 12.0);
            
            rectangle(
                TEXT_COLOR,
                [
                    5.0,
                    5.0,
                    300.0,
                    300.0,
                ],
                transform,
                g,
            );
           //draw_rectange( color, scaled_x as f64, scaled_z as f64, 3, 3, &c, g);
         
             
            // Update glyphs before rendering.
            

            });
        }
        Ok(1.0)

}


py_module_initializer!(rustlib, |py, m | {
    m.add(py, "__doc__", "This module is implemented in Rust")?;
    //m.add(py, "move_ray_rust", py_fn!(py, move_ray_rust(ray_angle: f64, ray_position_x: f64, ray_position_y: f64)))?;
    /*m.add(py, "get_x_cor_ordered_z_buffer_data_rust", py_fn!(py, get_x_cor_ordered_z_buffer_data_rust(player_angle: f64, 
        player_pos_x: f64, 
        player_pos_y: f64, 
        config_fov: usize,
        config_pixel_size: usize,
        config_is_perspective_correction_on: bool,
        mini_map_offset_x: usize,
        game_map_size_x: usize,
        game_map_size_y: usize,
        game_map: Vec<Vec<i8>>)))?;*/
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
    m.add(py, "main_rust", py_fn!(py, main_rust(text: f64)))?;
    
    Ok(())
});




pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn inner_x_cor_ordered_z_buffer_test() {
        /*player_pos_x: f64, 
    player_pos_y: f64, 
    config_fov: usize,
    config_pixel_size: usize,
    config_is_perspective_correction_on: bool,
    mini_map_offset_x: usize,
    game_map_size_x: usize,
    game_map_size_y: usize,
    game_map: Vec<Vec<i8>>) -> [u8; 1000*600*4] { */
        let player_angle = 90.0;
        let player_pos_x = 2.5;
        let player_pos_y = 2.5;
        let config_fov = 90 as usize;
        let config_pixel_size = 1 as usize;
        let config_is_perspective_correction_on = true;
        let mini_map_offset_x = WINDOW_WIDTH as usize;
        let game_map_size_x = 4 as usize;
        let game_map_size_y = 4 as usize;
        let game_map = vec![vec![10,10,10,10],vec![10,-1,-1,10],vec![10,-1,-1,10],vec![10,10,10,10]];

        let array = inner_x_cor_ordered_z_buffer(player_angle, player_pos_x,
            player_pos_y,config_fov,config_pixel_size,config_is_perspective_correction_on,
            mini_map_offset_x,game_map_size_x,game_map_size_y,game_map);
        let a = 10;
        assert_eq!(1,1);
}


    #[test]
    fn draw_from_z_buffer_objects_test() {

/*
get_x_cor_ordered_z_buffer_data_rust(
                    player_angle=player_angle,
                    player_pos_x=player_pos_x,
                    player_pos_y=player_pos_y,
                    config_fov=config_fov,
                    config_pixel_size=config_pixel_size,
                    config_is_perspective_correction_on=config_is_perspective_correction_on,
                    mini_map_offset_x=mini_map_offset_x,
                    game_map_size_x=game_map_size_x,
                    game_map_size_y=game_map_size_y,
                    game_map=game_map_data
                ) */
        let player_angle = 75;
        let player_pos_x = 4.481568175759901;
        let player_pos_y = 4.592744307579827;
        let config_fov = 80;
        let config_pixel_size = 3;
        let config_is_perspective_correction_on = true;
        let mini_map_offset_x = 400;
        let game_map_size_x = 20;
        let game_map_size_y = 20;
        let game_map_data = [[1,1,1],[1,0,1],[1,1,1]];



        /*let result = draw_from_z_buffer_objects(
            2.0, 
            vec![(0.0,vec![(1.0,1.0,1.0,1.0,1.0,1.0, 1 as usize, 1.0)])],
        );
        let a = 2;*/
        assert_eq!(2, 2);
    }
}
