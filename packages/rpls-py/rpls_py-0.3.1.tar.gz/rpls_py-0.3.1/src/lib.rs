#![warn(
     clippy::all,
     clippy::pedantic,
     clippy::nursery,
     clippy::cargo,
 )]

use pyo3::prelude::*;
use rpls;

fn convert_bd_pairs(bd_pairs: Vec<(f32, f32)>) -> Vec<rpls::birthdeath::BirthDeath>{
    bd_pairs.into_iter().map(|pair| rpls::birthdeath::BirthDeath{birth: pair.0, death: pair.1}).collect()
}

fn convert_landscape(landscapes: Vec<Vec<rpls::persistencelandscape::PointOrd>>) -> Vec<Vec<(f32, f32)>>{
    landscapes
        .into_iter()
        .map(|landscape|
             landscape
             .into_iter()
             .map(|point| (point.x.0, point.y.0))
             .collect::<Vec<(f32, f32)>>()
             )
        .collect::<Vec<Vec<(f32, f32)>>>()
}

#[pyfunction]
fn pairs_to_landscape(bd_pairs: Vec<(f32, f32)>, k: usize, debug: bool) -> PyResult<Vec<Vec<(f32, f32)>>> {
    let bd_pairs = convert_bd_pairs(bd_pairs);
    let landscapes = rpls::rpls::pairs_to_landscape(bd_pairs, k, debug).unwrap();

    Ok(convert_landscape(landscapes))

}

#[pyfunction]
fn pairs_to_l2_norm(bd_pairs: Vec<(f32, f32)>, k: usize, debug: bool) -> PyResult<f32> {
    let bd_pairs = convert_bd_pairs(bd_pairs);
    Ok(rpls::rpls::pairs_to_l2_norm(bd_pairs, k, debug).unwrap())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rpls_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(pairs_to_landscape, m)?)?;
    m.add_function(wrap_pyfunction!(pairs_to_l2_norm, m)?)?;
    Ok(())
}
