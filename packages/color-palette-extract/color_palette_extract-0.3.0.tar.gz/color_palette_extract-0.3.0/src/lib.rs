use pyo3::prelude::*;
use pyo3::types::PyBytes;

use colors_transform::{Color, Rgb};
use pyo3::wrap_pyfunction;

#[pyfunction]
fn extract_from_bytes(data: &PyBytes) -> PyResult<Vec<Vec<f32>>> {
    let mut result: Vec<Vec<f32>> = Vec::new();

    let img = image::load_from_memory(data.as_bytes()).unwrap();

    let colors = dominant_color::get_colors(img.to_rgb8().into_raw().as_slice(), false);

    let mut group: Vec<f32> = Vec::new();
    for color in colors {
        group.push(color as f32);
        if group.len() == 3 {
            result.push(vec![group[0], group[1], group[2]]);
            group.clear();
        }
    }

    Ok(result)
}

#[pyfunction]
fn get_hex_from_rgb(r: f32, g: f32, b: f32) -> PyResult<String> {
    let rgb = Rgb::from(r, g, b);
    Ok(rgb.to_css_hex_string())
}

#[pyfunction]
fn get_hsl_from_rgb(r: f32, g: f32, b: f32) -> PyResult<Vec<f32>> {
    let rgb = Rgb::from(r, g, b);
    let hsl = rgb.to_hsl();
    Ok(vec![
        hsl.get_hue(),
        hsl.get_saturation(),
        hsl.get_lightness(),
    ])
}

/// A Python module implemented in Rust.
#[pymodule]
fn color_palette_extract(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_from_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(get_hex_from_rgb, m)?)?;
    m.add_function(wrap_pyfunction!(get_hsl_from_rgb, m)?)?;
    Ok(())
}
