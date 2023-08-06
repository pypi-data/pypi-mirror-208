use ket::{Process, QuantumGate, Result};

fn main() -> Result<()> {
    let n = 4;

    let mut p = Process::new(1);

    let mut qubits = (0..n)
        .map(|_| p.allocate_qubit(false))
        .collect::<Vec<_>>()
        .into_iter()
        .collect::<Result<Vec<_>>>()?;

    let head = qubits.first().unwrap();
    let tail: Vec<_> = qubits.iter().skip(1).collect();

    for qubit in &qubits {
        p.apply_gate(QuantumGate::Hadamard, qubit)?;
    }

    let steps = (std::f64::consts::PI / 4.0 * f64::sqrt((1 << n) as f64)) as i32;

    for _ in 0..steps {
        p.ctrl_push(&tail)?;
        p.apply_gate(QuantumGate::PauliZ, head)?;
        p.ctrl_pop()?;

        for qubit in &qubits {
            p.apply_gate(QuantumGate::Hadamard, qubit)?;
            p.apply_gate(QuantumGate::PauliX, qubit)?;
        }

        p.ctrl_push(&tail)?;
        p.apply_gate(QuantumGate::PauliZ, head)?;
        p.ctrl_pop()?;

        for qubit in &qubits {
            p.apply_gate(QuantumGate::PauliX, qubit)?;
            p.apply_gate(QuantumGate::Hadamard, qubit)?;
        }
    }

    let _ = p.measure(&mut qubits.iter_mut().collect::<Vec<_>>());

    p.prepare_for_execution()?;
    println!("{:#?}", p.blocks());

    Ok(())
}
