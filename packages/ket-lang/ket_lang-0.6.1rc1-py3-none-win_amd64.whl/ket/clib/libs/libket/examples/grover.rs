use ket::*;

fn main() -> Result<()> {
    let n = 4;

    let mut features = Features::all();
    features.decompose = true;
    let p = Process::new_ptr();
    p.borrow_mut().set_features(features);

    let mut qubits = Quant::new(&p, n)?;

    h(&qubits)?;

    let steps = (std::f64::consts::PI / 4.0 * f64::sqrt((1 << n) as f64)) as i32;

    for _ in 0..steps {
        ctrl(&qubits.slice(1..), || z(&qubits.at(0)))??;

        around(
            &p,
            || {
                h(&qubits).unwrap();
                x(&qubits).unwrap();
            },
            || ctrl(&qubits.slice(1..), || z(&qubits.at(0))),
        )???;
    }

    let _ = measure(&mut qubits)?;

    let mut p = p.borrow_mut();
    p.prepare_for_execution()?;
    println!("{:#?}", p.blocks());

    Ok(())
}
