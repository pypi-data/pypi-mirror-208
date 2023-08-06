use crate::convert;
use crate::error::Result;
use crate::{bitwise::*, error::KBWError};
use itertools::Itertools;
use ket::ir::Metrics;
use num::complex::Complex64;
use rand::distributions::WeightedIndex;
use rand::prelude::*;
use rayon::prelude::*;
use std::{collections::HashMap, f64::consts::FRAC_1_SQRT_2};
use twox_hash::RandomXxHashBuilder64;

type StateMap = HashMap<Vec<u64>, Complex64, RandomXxHashBuilder64>;

pub struct Sparse {
    state_0: StateMap,
    state_1: StateMap,
    state: bool,
    rng: StdRng,
}

impl Sparse {
    fn get_states(&mut self) -> (&mut StateMap, &mut StateMap) {
        self.state = !self.state;
        if self.state {
            (&mut self.state_1, &mut self.state_0)
        } else {
            (&mut self.state_0, &mut self.state_1)
        }
    }

    fn get_states_rng(&mut self) -> (&mut StateMap, &mut StateMap, &mut StdRng) {
        self.state = !self.state;
        if self.state {
            (&mut self.state_1, &mut self.state_0, &mut self.rng)
        } else {
            (&mut self.state_0, &mut self.state_1, &mut self.rng)
        }
    }

    fn get_current_state_mut(&mut self) -> &mut StateMap {
        if self.state {
            &mut self.state_0
        } else {
            &mut self.state_1
        }
    }

    fn get_current_state(&self) -> &StateMap {
        if self.state {
            &self.state_0
        } else {
            &self.state_1
        }
    }

    fn swap(&mut self, a: usize, b: usize) {
        let (current_state, next_state) = self.get_states();

        current_state.drain().for_each(|(mut state, amp)| {
            if is_one_at_vec(&state, a) != is_one_at_vec(&state, b) {
                state = bit_flip_vec(state, a);
                state = bit_flip_vec(state, b);
            }
            next_state.insert(state, amp);
        });
    }

    fn pown(&mut self, qubits_size: usize, args: &str) {
        let (current_state, next_state) = self.get_states();
        let args: Vec<&str> = args.split(' ').collect();
        let x: u64 = args[0].parse().unwrap();
        let n: u64 = args[1].parse().unwrap();
        let l = bit_len(n);

        current_state.drain().for_each(|(mut state, amp)| {
            let a_b = state[0] & ((1 << qubits_size) - 1);
            let a = a_b >> l;
            let mut b = a_b & ((1 << l) - 1);
            b *= crate::bitwise::pown(x, a, n);
            let a_b = (a << l) | b;
            state[0] = a_b;
            next_state.insert(state, amp);
        });
    }

    fn dump_vec(&self, qubits: &[usize]) -> ket::DumpData {
        let state = self.get_current_state();

        let (basis_states, amplitudes_real, amplitudes_imag): (Vec<_>, Vec<_>, Vec<_>) = state
            .iter()
            .sorted_by_key(|x| x.0)
            .map(|(state, amp)| {
                let mut state: Vec<u64> = qubits
                    .iter()
                    .rev()
                    .chunks(64)
                    .into_iter()
                    .map(|qubits| {
                        qubits
                            .into_iter()
                            .enumerate()
                            .map(|(index, qubit)| (is_one_at_vec(state, *qubit) as usize) << index)
                            .reduce(|a, b| a | b)
                            .unwrap_or(0) as u64
                    })
                    .collect();
                state.reverse();

                (state, amp.re, amp.im)
            })
            .multiunzip();

        ket::DumpData::Vector {
            basis_states,
            amplitudes_real,
            amplitudes_imag,
        }
    }
}

impl crate::QuantumExecution for Sparse {
    fn new(metrics: &Metrics) -> Result<Self> {
        for plugin in metrics.plugins.iter() {
            if plugin != "pown" {
                return Err(KBWError::UnsupportedPlugin);
            }
        }

        let num_states = (metrics.qubit_simultaneous + 64) / 64;

        let mut state_0 = StateMap::default();

        let mut zero = Vec::new();
        zero.resize(num_states, 0u64);

        state_0.insert(zero, Complex64::new(1.0, 0.0));

        let seed = std::env::var("KBW_SEED")
            .unwrap_or_default()
            .parse::<u64>()
            .unwrap_or_else(|_| rand::random());

        Ok(Sparse {
            state_0,
            state_1: StateMap::default(),
            state: true,
            rng: StdRng::seed_from_u64(seed),
        })
    }

    fn pauli_x(&mut self, target: usize, control: &[usize]) {
        let (current_state, next_state) = self.get_states();

        current_state.drain().for_each(|(state, amp)| {
            next_state.insert(
                if ctrl_check_vec(&state, control) {
                    bit_flip_vec(state, target)
                } else {
                    state
                },
                amp,
            );
        });
    }

    fn pauli_y(&mut self, target: usize, control: &[usize]) {
        let (current_state, next_state) = self.get_states();

        current_state.drain().for_each(|(state, mut amp)| {
            if ctrl_check_vec(&state, control) {
                amp *= if is_one_at_vec(&state, target) {
                    -Complex64::i()
                } else {
                    Complex64::i()
                };
                next_state.insert(bit_flip_vec(state, target), amp);
            } else {
                next_state.insert(state, amp);
            }
        });
    }

    fn pauli_z(&mut self, target: usize, control: &[usize]) {
        let current_state = self.get_current_state_mut();

        current_state.par_iter_mut().for_each(|(state, amp)| {
            if ctrl_check_vec(state, control) && is_one_at_vec(state, target) {
                *amp = -*amp;
            }
        });
    }

    fn hadamard(&mut self, target: usize, control: &[usize]) {
        let (current_state, next_state) = self.get_states();

        current_state.drain().for_each(|(state, mut amp)| {
            if ctrl_check_vec(&state, control) {
                amp *= FRAC_1_SQRT_2;
                let state_flipped = bit_flip_vec(Vec::clone(&state), target);

                match next_state.get_mut(&state_flipped) {
                    Some(c_amp) => {
                        *c_amp += amp;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state_flipped);
                        }
                    }
                    None => {
                        next_state.insert(state_flipped, amp);
                    }
                }

                amp = if is_one_at_vec(&state, target) {
                    -amp
                } else {
                    amp
                };

                match next_state.get_mut(&state) {
                    Some(c_amp) => {
                        *c_amp += amp;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state);
                        }
                    }
                    None => {
                        next_state.insert(state, amp);
                    }
                }
            } else {
                next_state.insert(state, amp);
            }
        });
    }

    fn phase(&mut self, lambda: f64, target: usize, control: &[usize]) {
        let current_state = self.get_current_state_mut();

        let phase = Complex64::exp(lambda * Complex64::i());

        current_state.par_iter_mut().for_each(|(state, amp)| {
            if ctrl_check_vec(state, control) && is_one_at_vec(state, target) {
                *amp *= phase;
            }
        });
    }

    fn rx(&mut self, theta: f64, target: usize, control: &[usize]) {
        let (current_state, next_state) = self.get_states();

        let cons_theta_2 = Complex64::from(f64::cos(theta / 2.0));
        let sin_theta_2 = -Complex64::i() * f64::sin(theta / 2.0);

        current_state.drain().for_each(|(state, amp)| {
            if ctrl_check_vec(&state, control) {
                let state_flipped = bit_flip_vec(Vec::clone(&state), target);

                match next_state.get_mut(&state_flipped) {
                    Some(c_amp) => {
                        *c_amp += amp * sin_theta_2;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state_flipped);
                        }
                    }
                    None => {
                        next_state.insert(state_flipped, amp * sin_theta_2);
                    }
                }

                match next_state.get_mut(&state) {
                    Some(c_amp) => {
                        *c_amp += amp * cons_theta_2;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state);
                        }
                    }
                    None => {
                        next_state.insert(state, amp * cons_theta_2);
                    }
                }
            } else {
                next_state.insert(state, amp);
            }
        });
    }

    fn ry(&mut self, theta: f64, target: usize, control: &[usize]) {
        let (current_state, next_state) = self.get_states();

        let cons_theta_2 = Complex64::from(f64::cos(theta / 2.0));
        let p_sin_theta_2 = Complex64::from(f64::sin(theta / 2.0));
        let m_sin_theta_2 = -p_sin_theta_2;

        current_state.drain().for_each(|(state, amp)| {
            if ctrl_check_vec(&state, control) {
                let state_flipped = bit_flip_vec(Vec::clone(&state), target);
                let flipped_amp = amp
                    * if is_one_at_vec(&state, target) {
                        m_sin_theta_2
                    } else {
                        p_sin_theta_2
                    };

                match next_state.get_mut(&state_flipped) {
                    Some(c_amp) => {
                        *c_amp += flipped_amp;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state_flipped);
                        }
                    }
                    None => {
                        next_state.insert(state_flipped, flipped_amp);
                    }
                }

                match next_state.get_mut(&state) {
                    Some(c_amp) => {
                        *c_amp += amp * cons_theta_2;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state);
                        }
                    }
                    None => {
                        next_state.insert(state, amp * cons_theta_2);
                    }
                }
            } else {
                next_state.insert(state, amp);
            }
        });
    }

    fn rz(&mut self, theta: f64, target: usize, control: &[usize]) {
        let current_state = self.get_current_state_mut();

        let phase_0 = Complex64::exp(-theta / 2.0 * Complex64::i());
        let phase_1 = Complex64::exp(theta / 2.0 * Complex64::i());

        current_state.par_iter_mut().for_each(|(state, amp)| {
            if ctrl_check_vec(state, control) {
                if is_one_at_vec(state, target) {
                    *amp *= phase_1;
                } else {
                    *amp *= phase_0;
                }
            }
        });
    }

    fn measure(&mut self, target: usize) -> bool {
        let (current_state, next_state, rng) = self.get_states_rng();

        let p1: f64 = current_state
            .iter()
            .map(|(state, amp)| {
                if is_one_at_vec(state, target) {
                    amp.norm().powi(2)
                } else {
                    0.0
                }
            })
            .sum();

        let p0 = match 1.0 - p1 {
            p0 if p0 >= 0.0 => p0,
            _ => 0.0,
        };

        let result = WeightedIndex::new([p0, p1]).unwrap().sample(rng) == 1;

        let p = 1.0 / f64::sqrt(if result { p1 } else { p0 });

        current_state.drain().for_each(|(state, amp)| {
            if is_one_at_vec(&state, target) == result {
                next_state.insert(state, amp * p);
            }
        });

        result
    }

    fn dump(&mut self, qubits: &[usize]) -> ket::DumpData {
        let dump_type = std::env::var("KBW_DUMP_TYPE")
            .unwrap_or("vector".to_string())
            .to_lowercase();

        let dump_type = if ["vector", "probability", "shots"].contains(&dump_type.as_str()) {
            dump_type
        } else {
            "vector".to_string()
        };

        if dump_type == "vector" {
            self.dump_vec(qubits)
        } else if dump_type == "probability" {
            convert::from_dump_vec_to_dump_prob(self.dump_vec(qubits))
        } else {
            let shots = std::env::var("KBW_SHOTS")
                .unwrap_or_default()
                .parse::<u64>()
                .unwrap_or(1024);

            convert::from_dump_prob_to_dump_shots(
                convert::from_dump_vec_to_dump_prob(self.dump_vec(qubits)),
                shots,
                &mut self.rng,
            )
        }
    }

    fn plugin(&mut self, _name: &str, args: &str, target: &[usize]) -> Result<()> {
        let mut pos: Vec<usize> = (0..target.len()).collect();
        let mut swap_list = Vec::new();

        for (index, qubit) in target.iter().enumerate() {
            if *qubit == pos[index] {
                continue;
            };
            swap_list.push((index, pos[index]));
            pos.swap(index, target[index]);
        }

        for (a, b) in swap_list.iter() {
            self.swap(*a, *b);
        }

        self.pown(target.len(), args);

        for (a, b) in swap_list {
            self.swap(a, b);
        }

        Ok(())
    }

    fn unitary(&mut self, gate: &[[(f64, f64); 2]; 2], target: usize, control: &[usize]) {
        let [[(ar, ai), (br, bi)], [(cr, ci), (dr, di)]] = gate;
        let [[a, b], [c, d]] = [
            [Complex64::new(*ar, *ai), Complex64::new(*br, *bi)],
            [Complex64::new(*cr, *ci), Complex64::new(*dr, *di)],
        ];

        let (current_state, next_state) = self.get_states();

        current_state.drain().for_each(|(state, mut amp)| {
            if ctrl_check_vec(&state, control) {
                let state_flipped = bit_flip_vec(Vec::clone(&state), target);
                let amp_flipped = amp * if is_one_at_vec(&state, target) { b } else { c };

                match next_state.get_mut(&state_flipped) {
                    Some(c_amp) => {
                        *c_amp += amp_flipped;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state_flipped);
                        }
                    }
                    None => {
                        next_state.insert(state_flipped, amp_flipped);
                    }
                }

                amp *= if is_one_at_vec(&state, target) { d } else { a };

                match next_state.get_mut(&state) {
                    Some(c_amp) => {
                        *c_amp += amp;
                        if c_amp.norm() < 1e-15 {
                            next_state.remove(&state);
                        }
                    }
                    None => {
                        next_state.insert(state, amp);
                    }
                }
            } else {
                next_state.insert(state, amp);
            }
        });
    }
}

#[cfg(test)]
mod tests {
    use std::f64::consts::FRAC_1_SQRT_2;

    use crate::*;
    use ket::*;

    fn bell() -> (Process, Qubit, Qubit) {
        let mut p = Process::new(0);
        let a = p.allocate_qubit(false).unwrap();
        let b = p.allocate_qubit(false).unwrap();

        p.apply_gate(QuantumGate::Hadamard, &a).unwrap();
        p.ctrl_push(&[&a]).unwrap();
        p.apply_gate(QuantumGate::PauliX, &b).unwrap();
        p.ctrl_pop().unwrap();

        (p, a, b)
    }

    #[test]
    fn dump_bell() {
        let (mut p, a, b) = bell();
        let d = p.dump(&[&a, &b]).unwrap();

        p.prepare_for_execution().unwrap();

        run_and_set_result::<Sparse>(&mut p).unwrap();

        println!("{:?}", d);
    }

    #[test]
    fn measure_bell() {
        for _ in 0..10 {
            let (mut p, mut a, mut b) = bell();

            let m = p.measure(&mut [&mut a, &mut b]).unwrap();

            p.prepare_for_execution().unwrap();

            run_and_set_result::<Sparse>(&mut p).unwrap();

            let m = m.value().unwrap();
            assert!(m == 0 || m == 3);
        }
    }

    #[test]
    fn dump_h_3() {
        std::env::set_var("KBW_DUMP_TYPE", "shoTs");
        std::env::set_var("KBW_SHOTS", "1");
        //std::env::set_var("KBW_SEED", "112");

        let mut p = Process::new(0);
        let q: Vec<Qubit> = (0..3)
            .into_iter()
            .map(|_| p.allocate_qubit(false).unwrap())
            .collect();

        q.iter()
            .for_each(|q| p.apply_gate(QuantumGate::Hadamard, q).unwrap());

        let q: Vec<&Qubit> = q.iter().collect();
        let d = p.dump(&q).unwrap();

        p.prepare_for_execution().unwrap();

        run_and_set_result::<Sparse>(&mut p).unwrap();

        println!("{:?}", d);
    }

    #[test]
    fn measure_hzh_10() {
        let mut p = Process::new(0);
        let mut q: Vec<Qubit> = (0..10)
            .into_iter()
            .map(|_| p.allocate_qubit(false).unwrap())
            .collect();

        q.iter()
            .for_each(|q| p.apply_gate(QuantumGate::Hadamard, q).unwrap());

        q.iter()
            .for_each(|q| p.apply_gate(QuantumGate::PauliZ, q).unwrap());

        q.iter()
            .for_each(|q| p.apply_gate(QuantumGate::Hadamard, q).unwrap());

        let mut q: Vec<&mut Qubit> = q.iter_mut().collect();
        let m = p.measure(&mut q).unwrap();

        p.prepare_for_execution().unwrap();

        run_and_set_result::<Sparse>(&mut p).unwrap();

        assert!(m.value().unwrap() == ((1 << 10) - 1));
        println!("Execution Time = {}", p.exec_time().unwrap());
    }

    #[test]
    fn measure_h_10() {
        let mut p = Process::new(0);
        let mut q: Vec<Qubit> = (0..10)
            .into_iter()
            .map(|_| p.allocate_qubit(false).unwrap())
            .collect();

        q.iter()
            .for_each(|q| p.apply_gate(QuantumGate::Hadamard, q).unwrap());

        let mut q: Vec<&mut Qubit> = q.iter_mut().collect();
        let m = p.measure(&mut q).unwrap();

        p.prepare_for_execution().unwrap();

        run_and_set_result::<Sparse>(&mut p).unwrap();

        println!("{:?}; Execution Time = {}", m, p.exec_time().unwrap());
    }

    #[test]
    fn unitary_hadamard() {
        let mut p = Process::new(0);

        let q = p.allocate_qubit(false).unwrap();

        p.apply_gate(QuantumGate::PauliX, &q).unwrap();
        p.apply_gate(
            QuantumGate::unitary([
                [(FRAC_1_SQRT_2, 0.0), (FRAC_1_SQRT_2, 0.0)],
                [(FRAC_1_SQRT_2, 0.0), (-FRAC_1_SQRT_2, 0.0)],
            ])
            .unwrap(),
            &q,
        )
        .unwrap();

        p.apply_gate(QuantumGate::Hadamard, &q).unwrap();

        let d = p.dump(&[&q]).unwrap();

        p.prepare_for_execution().unwrap();

        run_and_set_result::<Sparse>(&mut p).unwrap();

        assert!(d.value().as_ref().unwrap().basis_states()[0][0] == 1);
        println!("{:?}", d);
    }

    #[test]
    fn dump_ghz_100() {
        let mut p = Process::new(0);
        let q: Vec<Qubit> = (0..100)
            .into_iter()
            .map(|_| p.allocate_qubit(false).unwrap())
            .collect();

        p.apply_gate(QuantumGate::Hadamard, &q[0]).unwrap();

        p.ctrl_push(&[&q[0]]).unwrap();

        q.iter()
            .skip(1)
            .for_each(|q| p.apply_gate(QuantumGate::PauliX, q).unwrap());

        p.ctrl_pop().unwrap();

        let q: Vec<&Qubit> = q.iter().collect();
        let d = p.dump(&q).unwrap();

        p.prepare_for_execution().unwrap();

        run_and_set_result::<Sparse>(&mut p).unwrap();

        println!("{:?}; Execution Time = {}", d, p.exec_time().unwrap());
    }
}
