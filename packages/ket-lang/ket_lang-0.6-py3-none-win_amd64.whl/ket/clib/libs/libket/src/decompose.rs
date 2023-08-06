use crate::{Instruction, QuantumGate};

fn gray_list(size: usize) -> Vec<String> {
    (1..1 << size)
        .map(|i| format!("{:01$b}", i ^ (i >> 1), size))
        .collect()
}

fn gray_decompose(gate: &QuantumGate, control: &[usize], target: usize) -> Vec<Instruction> {
    let mut instructions = Vec::new();
    let ctrl_size = control.len();
    let mut last = format!("{:01$b}", 0, ctrl_size);

    for gray in gray_list(ctrl_size) {
        let lm_pos = gray.chars().position(|c| c == '1').unwrap();

        let pos = gray
            .chars()
            .zip(last.chars())
            .position(|(c1, c2)| c1 != c2)
            .unwrap();

        if pos != lm_pos {
            instructions.push(Instruction::Gate {
                gate: QuantumGate::PauliX,
                target: control[lm_pos],
                control: vec![control[pos]],
            });
        } else {
            let indices = gray
                .chars()
                .enumerate()
                .filter(|(_, x)| *x == '1')
                .map(|(i, _)| i)
                .skip(1);
            for idx in indices {
                instructions.push(Instruction::Gate {
                    gate: QuantumGate::PauliX,
                    target: control[lm_pos],
                    control: vec![control[idx]],
                });
            }
        }

        if gray.matches('1').count() % 2 == 0 {
            instructions.push(Instruction::Gate {
                gate: gate.inverse(),
                target,
                control: vec![control[lm_pos]],
            });
        } else {
            instructions.push(Instruction::Gate {
                gate: gate.clone(),
                target,
                control: vec![control[lm_pos]],
            })
        }

        last = gray;
    }

    instructions
}

pub fn decompose_multi_control(
    gate: &QuantumGate,
    control: &[usize],
    target: usize,
) -> Vec<Instruction> {
    let phase = |lambda: f64| {
        gray_decompose(
            &QuantumGate::Phase(lambda / (1 << (control.len() - 1)) as f64),
            control,
            target,
        )
    };

    let rx = |theta: f64| {
        gray_decompose(
            &QuantumGate::RX(theta / (1 << (control.len() - 1)) as f64),
            control,
            target,
        )
    };

    let ry = |theta: f64| {
        gray_decompose(
            &QuantumGate::RX(theta / (1 << (control.len() - 1)) as f64),
            control,
            target,
        )
    };

    let rz = |theta: f64| {
        gray_decompose(
            &QuantumGate::RX(theta / (1 << (control.len() - 1)) as f64),
            control,
            target,
        )
    };

    let mut result = Vec::new();
    match gate {
        QuantumGate::PauliX => {
            result.push(Instruction::Gate {
                gate: QuantumGate::Hadamard,
                target,
                control: vec![],
            });

            result.append(&mut phase(std::f64::consts::PI));

            result.push(Instruction::Gate {
                gate: QuantumGate::Hadamard,
                target,
                control: vec![],
            });
        }
        QuantumGate::PauliY => result = ry(std::f64::consts::PI),
        QuantumGate::PauliZ => result = phase(std::f64::consts::PI),
        QuantumGate::Hadamard => {
            result.push(Instruction::Gate {
                gate: QuantumGate::RY(std::f64::consts::FRAC_PI_4),
                target,
                control: vec![],
            });

            result.append(&mut decompose_multi_control(
                &QuantumGate::PauliX,
                control,
                target,
            ));

            result.push(Instruction::Gate {
                gate: QuantumGate::RY(-std::f64::consts::FRAC_PI_4),
                target,
                control: vec![],
            });
        }
        QuantumGate::Phase(lambda) => result = phase(*lambda),
        QuantumGate::RX(theta) => result = rx(*theta),
        QuantumGate::RY(theta) => result = ry(*theta),
        QuantumGate::RZ(theta) => result = rz(*theta),
        QuantumGate::Unitary(_) => todo!(),
    }

    result
}

pub fn decompose_single_control(
    gate: &QuantumGate,
    control: usize,
    target: usize,
) -> Vec<Instruction> {
    let around = |outer: QuantumGate, target: usize, mut inner: Vec<Instruction>| {
        let mut result = vec![Instruction::Gate {
            gate: outer.inverse().inverse(),
            target,
            control: Vec::new(),
        }];

        result.append(&mut inner);

        result.push(Instruction::Gate {
            gate: outer.inverse(),
            target,
            control: Vec::new(),
        });

        result
    };

    let mut result = Vec::new();

    match gate {
        QuantumGate::PauliX => {
            result.push(Instruction::Gate {
                gate: QuantumGate::PauliX,
                target,
                control: vec![control],
            });
        }
        QuantumGate::PauliY => {
            result.append(&mut around(
                QuantumGate::Phase(-std::f64::consts::FRAC_PI_2),
                target,
                vec![Instruction::Gate {
                    gate: QuantumGate::PauliX,
                    target,
                    control: vec![control],
                }],
            ));
        }
        QuantumGate::PauliZ => {
            result.append(&mut around(
                QuantumGate::Hadamard,
                target,
                vec![Instruction::Gate {
                    gate: QuantumGate::PauliX,
                    target,
                    control: vec![control],
                }],
            ));
        }
        QuantumGate::Hadamard => {
            result.append(&mut around(
                QuantumGate::RY(-std::f64::consts::FRAC_PI_4),
                target,
                decompose_single_control(&QuantumGate::PauliZ, control, target),
            ));
        }
        QuantumGate::Phase(lambda) => {
            result.push(Instruction::Gate {
                gate: QuantumGate::Phase(lambda / 2.0),
                target: control,
                control: Vec::new(),
            });

            result.push(Instruction::Gate {
                gate: QuantumGate::PauliX,
                target,
                control: vec![control],
            });

            result.append(&mut around(
                QuantumGate::Phase(-lambda / 2.0),
                target,
                vec![Instruction::Gate {
                    gate: QuantumGate::PauliX,
                    target,
                    control: vec![control],
                }],
            ));
        }
        QuantumGate::RX(theta) => {
            let mut inner = around(
                QuantumGate::RY(theta / 2.0),
                target,
                vec![Instruction::Gate {
                    gate: QuantumGate::PauliX,
                    target,
                    control: vec![control],
                }],
            );

            inner.push(Instruction::Gate {
                gate: QuantumGate::PauliX,
                target,
                control: vec![control],
            });

            result.append(&mut around(
                QuantumGate::RZ(std::f64::consts::FRAC_PI_2),
                target,
                inner,
            ));
        }
        QuantumGate::RY(theta) => {
            result.append(&mut around(
                QuantumGate::RY(theta / 2.0),
                target,
                vec![Instruction::Gate {
                    gate: QuantumGate::PauliX,
                    target,
                    control: vec![control],
                }],
            ));

            result.push(Instruction::Gate {
                gate: QuantumGate::PauliX,
                target,
                control: vec![control],
            });
        }
        QuantumGate::RZ(theta) => {
            result.append(&mut around(
                QuantumGate::Phase(theta / 2.0),
                target,
                vec![Instruction::Gate {
                    gate: QuantumGate::PauliX,
                    target,
                    control: vec![control],
                }],
            ));

            result.push(Instruction::Gate {
                gate: QuantumGate::PauliX,
                target,
                control: vec![control],
            });
        }
        QuantumGate::Unitary(_) => todo!(),
    };

    result
}

pub fn decompose(gate: QuantumGate, control: Vec<usize>, target: usize) -> Vec<Instruction> {
    match control.len() {
        0 => vec![Instruction::Gate {
            gate,
            target,
            control,
        }],
        1 => decompose_single_control(&gate, control[0], target),
        _ => decompose_multi_control(&gate, &control, target),
    }
}
