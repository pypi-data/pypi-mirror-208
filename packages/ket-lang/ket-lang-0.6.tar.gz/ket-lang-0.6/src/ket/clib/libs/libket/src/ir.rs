use std::collections::HashSet;

use crate::object::DumpData;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct ResultData {
    pub future: Vec<i64>,
    pub dump: Vec<DumpData>,
    pub exec_time: f64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Metrics {
    pub qubit_simultaneous: usize,
    pub qubit_count: usize,
    pub future_count: usize,
    pub dump_count: usize,
    pub block_count: usize,
    pub timeout: Option<u64>,
    pub plugins: HashSet<String>,
    pub ready: bool,
}

impl Default for Metrics {
    fn default() -> Self {
        Self {
            qubit_simultaneous: 0,
            qubit_count: 0,
            future_count: 1,
            dump_count: 0,
            block_count: 1,
            timeout: None,
            plugins: HashSet::new(),
            ready: false,
        }
    }
}
