//! # Quantum Types
//!
//! This module provides types quantum programming in Rust.
//!
//! See the `gates` module for the functions that can be used in quantum programs.

use std::{
    cell::{Ref, RefCell},
    rc::Rc,
};

use serde::{Deserialize, Serialize};

use crate::error::KetError;

/// A trait for objects that have a process ID associated with them.
pub(crate) trait Pid {
    /// Returns the process ID.
    fn pid(&self) -> usize;
}

/// Represents a quantum bit with properties such as index, process ID, allocation status, and measurement status.
#[derive(Debug, Clone)]
pub struct Qubit {
    index: usize,
    pid: usize,
    allocated: bool,
    measured: bool,
}

impl Qubit {
    /// Creates a new qubit with the specified index and process ID.
    ///
    /// # Arguments
    ///
    /// * `index` - The index of the qubit.
    /// * `pid` - The process ID associated with the qubit.
    ///
    /// # Returns
    ///
    /// A new `Qubit` instance.
    pub fn new(index: usize, pid: usize) -> Qubit {
        Qubit {
            index,
            pid,
            allocated: true,
            measured: false,
        }
    }

    /// Returns the index of the qubit.
    pub fn index(&self) -> usize {
        self.index
    }

    /// Returns the allocation status of the qubit.
    pub fn allocated(&self) -> bool {
        self.allocated
    }

    /// Sets the qubit as deallocated.
    pub fn set_deallocated(&mut self) {
        self.allocated = false;
    }

    /// Returns the measurement status of the qubit.
    pub fn measured(&self) -> bool {
        self.measured
    }

    /// Sets the qubit as measured.
    pub fn set_measured(&mut self) {
        self.measured = false;
    }

    /// Asserts that the qubit is allocated.
    ///
    /// # Returns
    ///
    /// An `Err` variant of `KetError::DeallocatedQubit` if the qubit is deallocated,
    /// otherwise returns `Ok`.
    pub fn assert_allocated(&self) -> Result<(), KetError> {
        if !self.allocated {
            Err(KetError::DeallocatedQubit)
        } else {
            Ok(())
        }
    }
}

impl Pid for Qubit {
    /// Returns the process ID associated with the qubit.
    fn pid(&self) -> usize {
        self.pid
    }
}

/// Represents a future value associated with the measurement of a qubit, with properties such as index, process ID, and shared value.
#[derive(Debug, Clone)]
pub struct Future {
    index: usize,
    pid: usize,
    value: Rc<RefCell<Option<i64>>>,
}

impl Future {
    /// Creates a new `Future` with the specified index, process ID, and value.
    ///
    /// # Arguments
    ///
    /// * `index` - The index of the future.
    /// * `pid` - The process ID associated with the future.
    /// * `value` - A shared reference to the future value.
    ///
    /// # Returns
    ///
    /// A new `Future` instance.
    pub fn new(index: usize, pid: usize, value: Rc<RefCell<Option<i64>>>) -> Future {
        Future { index, pid, value }
    }

    /// Returns a shared reference to the value contained in the future.
    pub fn value(&self) -> Ref<Option<i64>> {
        self.value.borrow()
    }

    /// Returns the index of the future.
    pub fn index(&self) -> usize {
        self.index
    }
}

impl Pid for Future {
    /// Returns the process ID associated with the future.
    fn pid(&self) -> usize {
        self.pid
    }
}

/// Enumerated type representing different types of quantum state dump data, such as vector, probability, or shots.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum DumpData {
    /// Vector data consisting of basis states, real amplitudes, and imaginary amplitudes.
    Vector {
        basis_states: Vec<Vec<u64>>,
        amplitudes_real: Vec<f64>,
        amplitudes_imag: Vec<f64>,
    },
    /// Probability data consisting of basis states and probabilities.
    Probability {
        basis_states: Vec<Vec<u64>>,
        probabilities: Vec<f64>,
    },
    /// Shots data consisting of basis states, shot counts, and a total count.
    Shots {
        basis_states: Vec<Vec<u64>>,
        count: Vec<u32>,
        total: u64,
    },
}

impl DumpData {
    /// Returns a reference to the basis states.
    pub fn basis_states(&self) -> &[Vec<u64>] {
        match self {
            DumpData::Vector { basis_states, .. } => basis_states,
            DumpData::Shots { basis_states, .. } => basis_states,
            DumpData::Probability { basis_states, .. } => basis_states,
        }
    }

    /// Returns an optional reference to the real amplitudes.
    pub fn amplitudes_real(&self) -> Option<&[f64]> {
        match self {
            DumpData::Vector {
                amplitudes_real, ..
            } => Some(amplitudes_real),
            DumpData::Shots { .. } => None,
            DumpData::Probability { .. } => None,
        }
    }

    /// Returns an optional reference to the imaginary amplitudes.
    pub fn amplitudes_imag(&self) -> Option<&[f64]> {
        match self {
            DumpData::Vector {
                amplitudes_imag, ..
            } => Some(amplitudes_imag),
            DumpData::Shots { .. } => None,
            DumpData::Probability { .. } => None,
        }
    }

    /// Returns an optional reference to the probabilities.
    pub fn probabilities(&self) -> Option<&[f64]> {
        match self {
            DumpData::Vector { .. } => None,
            DumpData::Shots { .. } => None,
            DumpData::Probability { probabilities, .. } => Some(probabilities),
        }
    }

    /// Returns an optional reference to the shots counts.
    pub fn count(&self) -> Option<&[u32]> {
        match self {
            DumpData::Vector { .. } => None,
            DumpData::Shots { count, .. } => Some(count),
            DumpData::Probability { .. } => None,
        }
    }

    /// Returns an optional total count.
    pub fn total(&self) -> Option<u64> {
        match self {
            DumpData::Vector { .. } => None,
            DumpData::Shots { total, .. } => Some(*total),
            DumpData::Probability { .. } => None,
        }
    }
}

/// Represents a dumped data object containing information about a quantum state, with a shared value.
#[derive(Debug, Clone)]
pub struct Dump {
    value: Rc<RefCell<Option<DumpData>>>,
}

impl Dump {
    /// Creates a new `Dump` instance with the given dump data.
    ///
    /// # Arguments
    ///
    /// * `value` - The optional dump data wrapped in a reference-counted mutable cell.
    ///
    /// # Returns
    ///
    /// A new `Dump` instance.
    pub fn new(value: Rc<RefCell<Option<DumpData>>>) -> Dump {
        Dump { value }
    }

    /// Returns a shared reference to the optional dump data.
    ///
    /// # Returns
    ///
    /// A shared reference to the optional dump data.
    pub fn value(&self) -> Ref<Option<DumpData>> {
        self.value.borrow()
    }
}

/// Represents a label associated with a code block, with properties such as index and process ID.
#[derive(Debug, Clone)]
pub struct Label {
    index: usize,
    pid: usize,
}

impl Label {
    /// Creates a new `Label` instance with the specified index and process ID.
    ///
    /// # Arguments
    ///
    /// * `index` - The index value of the label.
    /// * `pid` - The process ID associated with the label.
    ///
    /// # Returns
    ///
    /// A new `Label` instance.
    pub fn new(index: usize, pid: usize) -> Label {
        Label { index, pid }
    }

    /// Returns the index value of the label.
    ///
    /// # Returns
    ///
    /// The index value of the label.
    pub fn index(&self) -> usize {
        self.index
    }
}

impl Pid for Label {
    /// Returns the process ID associated with the label.
    ///
    /// # Returns
    ///
    /// The process ID associated with the label.
    fn pid(&self) -> usize {
        self.pid
    }
}
