use std::{
    cell::{Ref, RefCell},
    rc::Rc,
};

use serde::{Deserialize, Serialize};

use crate::error::KetError;

pub trait Pid {
    fn pid(&self) -> usize;
}

#[derive(Debug, Clone)]
pub struct Qubit {
    index: usize,
    pid: usize,
    allocated: bool,
    measured: bool,
}

impl Qubit {
    pub fn new(index: usize, pid: usize) -> Qubit {
        Qubit {
            index,
            pid,
            allocated: true,
            measured: false,
        }
    }

    pub fn index(&self) -> usize {
        self.index
    }

    pub fn allocated(&self) -> bool {
        self.allocated
    }

    pub fn set_deallocated(&mut self) {
        self.allocated = false;
    }

    pub fn measured(&self) -> bool {
        self.measured
    }

    pub fn set_measured(&mut self) {
        self.measured = false;
    }

    pub fn assert_allocated(&self) -> Result<(), KetError> {
        if !self.allocated {
            Err(KetError::DeallocatedQubit)
        } else {
            Ok(())
        }
    }
}

impl Pid for Qubit {
    fn pid(&self) -> usize {
        self.pid
    }
}

#[derive(Debug)]
pub struct Future {
    index: usize,
    pid: usize,
    value: Rc<RefCell<Option<i64>>>,
}

impl Future {
    pub fn new(index: usize, pid: usize, value: Rc<RefCell<Option<i64>>>) -> Future {
        Future { index, pid, value }
    }

    pub fn value(&self) -> Ref<Option<i64>> {
        self.value.borrow()
    }

    pub fn index(&self) -> usize {
        self.index
    }
}

impl Pid for Future {
    fn pid(&self) -> usize {
        self.pid
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub enum DumpData {
    Vector {
        basis_states: Vec<Vec<u64>>,
        amplitudes_real: Vec<f64>,
        amplitudes_imag: Vec<f64>,
    },
    Probability {
        basis_states: Vec<Vec<u64>>,
        probabilities: Vec<f64>,
    },
    Shots {
        basis_states: Vec<Vec<u64>>,
        count: Vec<u32>,
        total: u64,
    },
}

impl DumpData {
    pub fn basis_states(&self) -> &[Vec<u64>] {
        match self {
            DumpData::Vector { basis_states, .. } => basis_states,
            DumpData::Shots { basis_states, .. } => basis_states,
            DumpData::Probability { basis_states, .. } => basis_states,
        }
    }

    pub fn amplitudes_real(&self) -> Option<&[f64]> {
        match self {
            DumpData::Vector {
                amplitudes_real, ..
            } => Some(amplitudes_real),
            DumpData::Shots { .. } => None,
            DumpData::Probability { .. } => None,
        }
    }

    pub fn amplitudes_imag(&self) -> Option<&[f64]> {
        match self {
            DumpData::Vector {
                amplitudes_imag, ..
            } => Some(amplitudes_imag),
            DumpData::Shots { .. } => None,
            DumpData::Probability { .. } => None,
        }
    }

    pub fn probabilities(&self) -> Option<&[f64]> {
        match self {
            DumpData::Vector { .. } => None,
            DumpData::Shots { .. } => None,
            DumpData::Probability { probabilities, .. } => Some(probabilities),
        }
    }

    pub fn count(&self) -> Option<&[u32]> {
        match self {
            DumpData::Vector { .. } => None,
            DumpData::Shots { count, .. } => Some(count),
            DumpData::Probability { .. } => None,
        }
    }

    pub fn total(&self) -> Option<u64> {
        match self {
            DumpData::Vector { .. } => None,
            DumpData::Shots { total, .. } => Some(*total),
            DumpData::Probability { .. } => None,
        }
    }
}

#[derive(Debug)]
pub struct Dump {
    value: Rc<RefCell<Option<DumpData>>>,
}

impl Dump {
    pub fn new(value: Rc<RefCell<Option<DumpData>>>) -> Dump {
        Dump { value }
    }

    pub fn value(&self) -> Ref<Option<DumpData>> {
        self.value.borrow()
    }
}

pub struct Label {
    index: usize,
    pid: usize,
}

impl Label {
    pub fn new(index: usize, pid: usize) -> Label {
        Label { index, pid }
    }

    pub fn index(&self) -> usize {
        self.index
    }
}

impl Pid for Label {
    fn pid(&self) -> usize {
        self.pid
    }
}
