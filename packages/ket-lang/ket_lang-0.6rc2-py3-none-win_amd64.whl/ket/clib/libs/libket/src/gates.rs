use std::{cell::RefCell, ops::RangeBounds, rc::Rc, result};

use crate::{error::KetError, Dump, Future, Process, Qubit};

#[derive(Debug)]

pub struct Quant {
    pub(crate) qubits: Vec<Rc<RefCell<Qubit>>>,
    pub(crate) process: Rc<RefCell<Process>>,
}

pub type Result<T> = result::Result<T, KetError>;

impl Quant {
    pub fn new(process: &Rc<RefCell<Process>>, size: usize) -> Result<Quant> {
        let mut qubits = Vec::with_capacity(size);
        for _ in 0..size {
            qubits.push(Rc::new(RefCell::new(
                process.borrow_mut().allocate_qubit(false)?,
            )));
        }

        Ok(Quant {
            qubits,
            process: Rc::clone(process),
        })
    }

    pub fn slice<R: RangeBounds<usize>>(&self, range: R) -> Quant {
        let start = match range.start_bound() {
            std::ops::Bound::Included(start) => *start,
            std::ops::Bound::Excluded(_) => panic!(),
            std::ops::Bound::Unbounded => 0,
        };

        let end = match range.end_bound() {
            std::ops::Bound::Included(_) => panic!(),
            std::ops::Bound::Excluded(end) => *end,
            std::ops::Bound::Unbounded => self.qubits.len(),
        };

        Quant {
            process: Rc::clone(&self.process),
            qubits: Vec::from_iter(self.qubits[start..end].iter().map(Rc::clone)),
        }
    }

    pub fn cat(quants: &[&Quant]) -> Result<Quant> {
        let process = &quants
            .first()
            .expect("\"quants\" must have length >= 1")
            .process;

        let pid = process.borrow().pid();

        let mut qubits = Vec::new();
        for quant in quants {
            if quant.process.borrow().pid() != pid {
                return Err(KetError::UnmatchedPid);
            }
            qubits.extend(quant.qubits.iter().cloned());
        }

        Ok(Quant {
            qubits,
            process: Rc::clone(process),
        })
    }

    pub fn at(&self, index: usize) -> Quant {
        Quant {
            process: Rc::clone(&self.process),
            qubits: vec![self.qubits[index].clone()],
        }
    }
}

pub fn x(qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::PauliX, &target.borrow())?
    }

    Ok(())
}

pub fn y(qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::PauliY, &target.borrow())?
    }

    Ok(())
}

pub fn z(qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::PauliZ, &target.borrow())?
    }

    Ok(())
}

pub fn h(qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::Hadamard, &target.borrow())?
    }

    Ok(())
}

pub fn phase(lambda: f64, qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::Phase(lambda), &target.borrow())?
    }

    Ok(())
}

pub fn rx(theta: f64, qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::RX(theta), &target.borrow())?
    }

    Ok(())
}

pub fn ry(theta: f64, qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::RY(theta), &target.borrow())?
    }

    Ok(())
}

pub fn rz(theta: f64, qubits: &Quant) -> Result<()> {
    for target in &qubits.qubits {
        qubits
            .process
            .borrow_mut()
            .apply_gate(crate::QuantumGate::RZ(theta), &target.borrow())?
    }

    Ok(())
}

pub fn ctrl<F, T>(control: &Quant, gate: F) -> Result<T>
where
    F: FnOnce() -> T,
{
    control
        .process
        .borrow_mut()
        .ctrl_push_ref(&control.qubits)?;

    let result = gate();

    control.process.borrow_mut().ctrl_pop()?;

    Ok(result)
}

pub fn adj<F, T>(process: &Rc<RefCell<Process>>, gate: F) -> Result<T>
where
    F: FnOnce() -> T,
{
    process.borrow_mut().adj_begin()?;

    let result = gate();

    process.borrow_mut().adj_end()?;

    Ok(result)
}

pub fn around<Outer, Inner, T>(
    process: &Rc<RefCell<Process>>,
    outer: Outer,
    inner: Inner,
) -> Result<T>
where
    Outer: Fn(),
    Inner: FnOnce() -> T,
{
    outer();

    let result = inner();

    adj(process, outer)?;

    Ok(result)
}

pub fn measure(qubits: &mut Quant) -> Result<Future> {
    qubits.process.borrow_mut().measure_ref(&mut qubits.qubits)
}

pub fn plugin(name: &str, args: &str, qubits: &Quant) -> Result<()> {
    qubits
        .process
        .borrow_mut()
        .apply_plugin_ref(name, &qubits.qubits, args)
}

pub fn dump(qubits: &Quant) -> Result<Dump> {
    qubits.process.borrow_mut().dump_ref(&qubits.qubits)
}

#[cfg(test)]
mod tests {

    use crate::{dump, Process};

    use super::{ctrl, h, x, Quant};

    #[test]
    fn test_slice() {
        let p = Process::new_ptr();

        let q = Quant::new(&p, 10).unwrap();

        let tail = q.slice(1..);
        let head = q.at(0);
        print!("{:#?}", Quant::cat(&[&tail, &head]).unwrap().qubits)
    }

    #[test]
    fn test_bell() {
        let p = Process::new_ptr();

        let q = Quant::new(&p, 2).unwrap();
        h(&q.at(0)).unwrap();
        ctrl(&q.at(0), || x(&q.at(1)).unwrap()).unwrap();

        let d = dump(&q).unwrap();

        p.borrow_mut().prepare_for_execution().unwrap();

        let result = "{\n\"future\": [\n0\n],\n\"dump\": [\n{\n\"Vector\": {\n\"basis_states\": [\n[\n0\n],\n[\n3\n]\n],\n\"amplitudes_real\": [\n0.7071067811865476,\n0.7071067811865476\n],\n\"amplitudes_imag\": [\n0.0,\n0.0\n]\n}\n}\n],\n\"exec_time\": 0.00103683\n}";

        p.borrow_mut()
            .set_result(serde_json::from_str(result).unwrap())
            .unwrap();

        println!("{:#?}", d);
    }
}
