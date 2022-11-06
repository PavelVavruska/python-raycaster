#[macro_use]
extern crate cpython;

use cpython::{Python, PyResult};

fn move_ray_rust(_py: Python, ray_angle: f64, ray_position_x: f64, ray_position_y: f64) -> PyResult<Vec<f64>> {
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
    Ok(vec![ray_pos_x, ray_pos_y])

}

py_module_initializer!(rustlib, |py, m | {
    m.add(py, "__doc__", "This module is implemented in Rust")?;
    m.add(py, "move_ray_rust", py_fn!(py, move_ray_rust(ray_angle: f64, ray_position_x: f64, ray_position_y: f64)))?;
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
