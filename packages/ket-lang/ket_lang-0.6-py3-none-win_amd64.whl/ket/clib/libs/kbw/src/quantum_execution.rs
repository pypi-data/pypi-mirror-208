use crate::error::{KBWError, Result};
use ket::code_block::CodeBlock;
use ket::instruction::{ClassicalOp, EndInstruction, Instruction, QuantumGate};
use ket::ir::{Metrics, ResultData};
use ket::Process;
use std::time::Instant;

pub trait QuantumExecution {
    fn new(metrics: &Metrics) -> Result<Self>
    where
        Self: Sized;
    fn pauli_x(&mut self, target: usize, control: &[usize]);
    fn pauli_y(&mut self, target: usize, control: &[usize]);
    fn pauli_z(&mut self, target: usize, control: &[usize]);
    fn hadamard(&mut self, target: usize, control: &[usize]);
    fn phase(&mut self, lambda: f64, target: usize, control: &[usize]);
    fn rx(&mut self, theta: f64, target: usize, control: &[usize]);
    fn ry(&mut self, theta: f64, target: usize, control: &[usize]);
    fn rz(&mut self, theta: f64, target: usize, control: &[usize]);
    fn unitary(&mut self, gate: &[[(f64, f64); 2]; 2], target: usize, control: &[usize]);
    fn measure(&mut self, target: usize) -> bool;
    fn dump(&mut self, qubits: &[usize]) -> ket::DumpData;
    fn plugin(&mut self, name: &str, args: &str, target: &[usize]) -> Result<()>;
}

pub fn run<S: QuantumExecution>(
    sim: &mut S,
    quantum_code: &[&CodeBlock],
    metrics: &Metrics,
) -> Result<ResultData> {
    if !metrics.ready {
        return Err(KBWError::NotReadyForExecution);
    }

    let mut qubit_stack: Vec<usize> = (0..metrics.qubit_simultaneous).collect();
    let mut qubit_stack_dirty = Vec::new();
    let mut qubit_map: Vec<usize> = (0..metrics.qubit_simultaneous).collect();

    let mut int_register = vec![0; metrics.future_count];

    let mut dump_register = Vec::with_capacity(metrics.dump_count);
    for _ in 0..metrics.dump_count {
        dump_register.push(ket::DumpData::Probability {
            basis_states: Vec::new(),
            probabilities: Vec::new(),
        });
    }

    let mut current_block = 0usize;

    let qubit_vec_map = |control: &[usize], qubit_map: &[usize]| -> Vec<usize> {
        control.iter().map(|index| qubit_map[*index]).collect()
    };

    let start = Instant::now();

    'quantum_run: loop {
        for instruction in &quantum_code[current_block].instructions {
            if let Some(timeout) = metrics.timeout {
                if start.elapsed().as_secs() > timeout {
                    return Err(KBWError::Timeout);
                }
            }
            match instruction {
                Instruction::Alloc { dirty, target } => {
                    let qubit_index = if *dirty & !qubit_stack_dirty.is_empty() {
                        qubit_stack_dirty.pop().unwrap()
                    } else {
                        match qubit_stack.pop() {
                            Some(index) => index,
                            None => return Err(KBWError::OutOfQubits),
                        }
                    };
                    qubit_map[*target] = qubit_index;
                }
                Instruction::Free { dirty, target } => {
                    if *dirty {
                        qubit_stack_dirty.push(qubit_map[*target]);
                    } else {
                        qubit_stack.push(qubit_map[*target]);
                    }
                }
                Instruction::Gate {
                    gate,
                    target,
                    control,
                } => match gate {
                    QuantumGate::PauliX => {
                        sim.pauli_x(qubit_map[*target], &qubit_vec_map(control, &qubit_map))
                    }
                    QuantumGate::PauliY => {
                        sim.pauli_y(qubit_map[*target], &qubit_vec_map(control, &qubit_map))
                    }
                    QuantumGate::PauliZ => {
                        sim.pauli_z(qubit_map[*target], &qubit_vec_map(control, &qubit_map))
                    }
                    QuantumGate::Hadamard => {
                        sim.hadamard(qubit_map[*target], &qubit_vec_map(control, &qubit_map))
                    }
                    QuantumGate::Phase(lambda) => sim.phase(
                        *lambda,
                        qubit_map[*target],
                        &qubit_vec_map(control, &qubit_map),
                    ),
                    QuantumGate::RX(theta) => sim.rx(
                        *theta,
                        qubit_map[*target],
                        &qubit_vec_map(control, &qubit_map),
                    ),
                    QuantumGate::RY(theta) => sim.ry(
                        *theta,
                        qubit_map[*target],
                        &qubit_vec_map(control, &qubit_map),
                    ),
                    QuantumGate::RZ(theta) => sim.rz(
                        *theta,
                        qubit_map[*target],
                        &qubit_vec_map(control, &qubit_map),
                    ),
                    QuantumGate::Unitary(gate) => sim.unitary(
                        gate,
                        qubit_map[*target],
                        &qubit_vec_map(control, &qubit_map),
                    ),
                },
                Instruction::Measure { qubits, output } => {
                    int_register[*output] = qubits
                        .iter()
                        .rev()
                        .map(|qubit| qubit_map[*qubit])
                        .enumerate()
                        .map(|(index, qubit)| (sim.measure(qubit) as i64) << index)
                        .reduce(|a, b| a | b)
                        .unwrap_or(0);
                }
                Instruction::Plugin { name, args, target } => {
                    sim.plugin(name, args, &qubit_vec_map(target, &qubit_map))?;
                }
                Instruction::End(inst) => match inst {
                    EndInstruction::Jump { addr } => current_block = *addr,
                    EndInstruction::Branch {
                        test,
                        then,
                        otherwise,
                    } => {
                        current_block = if int_register[*test] != 0 {
                            *then
                        } else {
                            *otherwise
                        };
                    }
                    EndInstruction::Halt => break 'quantum_run,
                },
                Instruction::IntOp {
                    op,
                    result,
                    lhs,
                    rhs,
                } => match op {
                    ClassicalOp::Eq => {
                        int_register[*result] = (int_register[*lhs] == int_register[*rhs]) as i64
                    }
                    ClassicalOp::Neq => {
                        int_register[*result] = (int_register[*lhs] != int_register[*rhs]) as i64
                    }
                    ClassicalOp::Gt => {
                        int_register[*result] = (int_register[*lhs] > int_register[*rhs]) as i64
                    }
                    ClassicalOp::Geq => {
                        int_register[*result] = (int_register[*lhs] >= int_register[*rhs]) as i64
                    }
                    ClassicalOp::Lt => {
                        int_register[*result] = (int_register[*lhs] < int_register[*rhs]) as i64
                    }
                    ClassicalOp::Leq => {
                        int_register[*result] = (int_register[*lhs] <= int_register[*rhs]) as i64
                    }
                    ClassicalOp::Add => {
                        int_register[*result] = int_register[*lhs] + int_register[*rhs]
                    }
                    ClassicalOp::Sub => {
                        int_register[*result] = int_register[*lhs] - int_register[*rhs]
                    }
                    ClassicalOp::Mul => {
                        int_register[*result] = int_register[*lhs] * int_register[*rhs]
                    }
                    ClassicalOp::Div => {
                        int_register[*result] = int_register[*lhs] / int_register[*rhs]
                    }
                    ClassicalOp::Sll => {
                        int_register[*result] = int_register[*lhs] << int_register[*rhs]
                    }
                    ClassicalOp::Srl => {
                        int_register[*result] = int_register[*lhs] >> int_register[*rhs]
                    }
                    ClassicalOp::And => {
                        int_register[*result] = int_register[*lhs] & int_register[*rhs]
                    }
                    ClassicalOp::Or => {
                        int_register[*result] = int_register[*lhs] | int_register[*rhs]
                    }
                    ClassicalOp::Xor => {
                        int_register[*result] = int_register[*lhs] ^ int_register[*rhs]
                    }
                    ClassicalOp::Mod => {
                        int_register[*result] = int_register[*lhs] % int_register[*rhs]
                    }
                },
                Instruction::IntSet { result, value } => {
                    int_register[*result] = *value;
                }
                Instruction::Dump { qubits, output } => {
                    dump_register[*output] = sim.dump(&qubit_vec_map(qubits, &qubit_map));
                }
            }
        }
    }

    let exec_time = start.elapsed().as_secs_f64();

    Ok(ResultData {
        future: int_register,
        dump: dump_register,
        exec_time,
    })
}

pub fn run_and_set_result<S: QuantumExecution>(process: &mut Process) -> Result<()> {
    let metrics = process.metrics();
    let instructions = process.blocks();
    let mut sim = S::new(metrics)?;
    let result = run(&mut sim, &instructions, metrics)?;
    process.set_result(result).unwrap();
    Ok(())
}
