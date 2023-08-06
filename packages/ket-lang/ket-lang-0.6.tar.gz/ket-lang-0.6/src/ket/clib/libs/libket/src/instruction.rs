use num::complex::Complex64;
use num_derive::{FromPrimitive, ToPrimitive};
use serde::{Deserialize, Serialize};

use crate::error::{KetError, Result};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum QuantumGate {
    PauliX,
    PauliY,
    PauliZ,
    Hadamard,
    Phase(f64),
    RX(f64),
    RY(f64),
    RZ(f64),
    Unitary([[(f64, f64); 2]; 2]),
}

impl QuantumGate {
    pub fn unitary(u: [[(f64, f64); 2]; 2]) -> Result<QuantumGate> {
        let [[a, b], [c, d]] = [
            [
                Complex64::new(u[0][0].0, u[0][0].1),
                Complex64::new(u[0][1].0, u[0][1].1),
            ],
            [
                Complex64::new(u[1][0].0, u[1][0].1),
                Complex64::new(u[1][1].0, u[1][1].1),
            ],
        ];

        let zero = [
            f64::abs(a.norm_sqr() + b.norm_sqr() - 1.0),
            (a * c.conj() + b * d.conj()).norm_sqr(),
            (c * a.conj() + d * b.conj()).norm_sqr(),
            f64::abs(c.norm_sqr() + d.norm_sqr() - 1.0),
        ];

        if zero.iter().sum::<f64>() > 1e-10 {
            Err(KetError::NotUnitary)
        } else {
            Ok(QuantumGate::Unitary(u))
        }
    }

    pub fn inverse(&self) -> QuantumGate {
        match self {
            QuantumGate::PauliX => QuantumGate::PauliX,
            QuantumGate::PauliY => QuantumGate::PauliY,
            QuantumGate::PauliZ => QuantumGate::PauliZ,
            QuantumGate::Hadamard => QuantumGate::Hadamard,
            QuantumGate::Phase(lambda) => QuantumGate::Phase(-lambda),
            QuantumGate::RX(theta) => QuantumGate::RX(-theta),
            QuantumGate::RY(theta) => QuantumGate::RY(-theta),
            QuantumGate::RZ(theta) => QuantumGate::RZ(-theta),
            QuantumGate::Unitary(u) => QuantumGate::Unitary([
                [(u[0][0].0, -u[0][0].1), (u[1][0].0, -u[1][0].1)],
                [(u[0][1].0, -u[0][1].1), (u[1][1].0, -u[1][1].1)],
            ]),
        }
    }

    pub fn is_phase(&self) -> bool {
        matches!(self, QuantumGate::Phase(_))
    }

    pub fn from_phase_to_rz(&self) -> Result<QuantumGate> {
        match self {
            QuantumGate::Phase(lambda) => Ok(QuantumGate::RZ(*lambda)),
            _ => Err(KetError::NotPhaseGate),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, FromPrimitive, ToPrimitive)]
pub enum ClassicalOp {
    Eq,
    Neq,
    Gt,
    Geq,
    Lt,
    Leq,
    Add,
    Sub,
    Mul,
    Mod,
    Div,
    Sll,
    Srl,
    And,
    Or,
    Xor,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum EndInstruction {
    Jump {
        addr: usize,
    },
    Branch {
        test: usize,
        then: usize,
        otherwise: usize,
    },
    Halt,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum Instruction {
    Alloc {
        dirty: bool,
        target: usize,
    },
    Free {
        dirty: bool,
        target: usize,
    },
    Gate {
        gate: QuantumGate,
        target: usize,
        control: Vec<usize>,
    },
    Measure {
        qubits: Vec<usize>,
        output: usize,
    },
    Plugin {
        name: String,
        target: Vec<usize>,
        args: String,
    },
    IntOp {
        op: ClassicalOp,
        result: usize,
        lhs: usize,
        rhs: usize,
    },
    IntSet {
        result: usize,
        value: i64,
    },
    Dump {
        qubits: Vec<usize>,
        output: usize,
    },
    End(EndInstruction),
}

#[cfg(test)]
mod tests {

    use crate::instruction::{ClassicalOp, QuantumGate};
    use num::FromPrimitive;
    use std::f64::consts::FRAC_1_SQRT_2;

    #[test]
    fn unitary_matrix() {
        let _x =
            QuantumGate::unitary([[(0.0, 0.0), (1.0, 0.0)], [(1.0, 0.0), (0.0, 0.0)]]).unwrap();
        let _y =
            QuantumGate::unitary([[(0.0, 0.0), (0.0, -1.0)], [(0.0, 1.0), (0.0, 0.0)]]).unwrap();
        let _z =
            QuantumGate::unitary([[(1.0, 0.0), (0.0, 0.0)], [(0.0, 0.0), (0.0, -1.0)]]).unwrap();
        let _h = QuantumGate::unitary([
            [(FRAC_1_SQRT_2, 0.0), (FRAC_1_SQRT_2, 0.0)],
            [(FRAC_1_SQRT_2, 0.0), (-FRAC_1_SQRT_2, 0.0)],
        ])
        .unwrap();
        let _s =
            QuantumGate::unitary([[(1.0, 0.0), (0.0, 0.0)], [(0.0, 0.0), (0.0, 1.0)]]).unwrap();
        let _t = QuantumGate::unitary([
            [(1.0, 0.0), (0.0, 0.0)],
            [(0.0, 0.0), (FRAC_1_SQRT_2, FRAC_1_SQRT_2)],
        ])
        .unwrap();
    }

    #[test]
    fn not_unitary_matrix() {
        assert!(
            QuantumGate::unitary([[(0.0, 0.0), (0.0, 1.0)], [(0.0, 0.0), (1.0, 0.0)]]).is_err()
        );
    }

    #[test]
    fn print_classical_op() {
        let mut op_code = 0;
        while let Some(op) = ClassicalOp::from_i32(op_code) {
            println!("#define KET_{:#?} {}", op, op_code);
            op_code += 1;
        }
    }
}
