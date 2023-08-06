use ket::*;

fn main() -> Result<()> {
    let p = Process::new_ptr();
    let q = Quant::new(&p, 2)?;

    h(&q.at(0))?;
    ctrl(&q.at(0), || x(&q.at(1)))??;

    let _ = dump(&q)?;

    let mut p = p.borrow_mut();
    p.prepare_for_execution()?;
    let quantum_code = p.serialize_quantum_code(ket::serialize::DataType::Json);
    if let ket::serialize::SerializedData::Json(json) = quantum_code {
        println!("{}", json);
    }

    Ok(())
}
