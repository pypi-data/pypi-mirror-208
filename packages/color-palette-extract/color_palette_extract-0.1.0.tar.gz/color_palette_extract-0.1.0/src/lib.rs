use pyo3::prelude::*;
use pyo3::types::PyBytes;

use colors_transform::Rgb;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn extract_from_bytes(data: &PyBytes) -> PyResult<Vec<String>> {
    let mut result: Vec<String> = Vec::new();

    let img = image::load_from_memory(data.as_bytes()).unwrap();

    let colors = dominant_color::get_colors(img.to_rgb8().into_raw().as_slice(), false);

    let mut group: Vec<f32> = Vec::new();
    for color in colors {
        group.push(color as f32);
        if group.len() == 3 {
            let rgb = Rgb::from(group[0], group[1], group[2]);
            group.clear();
            result.push(rgb.to_css_hex_string());
        }
    }

    Ok(result)
}

/// A Python module implemented in Rust.
#[pymodule]
fn color_palette_extract(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_from_bytes, m)?)?;
    Ok(())
}
