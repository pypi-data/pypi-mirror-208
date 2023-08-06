//! # Libket Quantum Programming Library
//!
//! The Libket library provides a set of tools for quantum programming in Rust.
//! It serves as the runtime library for the Python-embedded quantum programming language Ket.
//!
//! **Note:** For more information about the Ket programming language,
//! please visit <https://quantumket.org>.
//!
//! ## Usage
//!
//! To use this library, add the following line to your `Cargo.toml` file:
//!
//! ```text
//! [dependencies]
//! libket = "0.3.1"
//! ```
//!
//! Additionally, you may need to include the following dependencies for quantum code
//! serialization/deserialization and the KBW quantum computer simulator:
//!
//! ```text
//! serde = { version = "1.0", features = ["derive"] }
//! serde_json = "1.0"
//! kbw = "0.1.6"
//! ```
//!
//! ## Examples
//!
//! The following example demonstrates the implementation of
//! Grover's algorithm using Libket:
//!
//! ```rust
//! use ket::*;
//!
//! fn main() -> Result<()> {
//!     let n = 4;  // Number of qubits
//!
//!     let p = Process::new_ptr();  // Create a new quantum process
//!
//!     let mut qubits = Quant::new(&p, n)?;  // Create a quantum register with `n` qubits
//!
//!     h(&qubits)?;  // Apply Hadamard gate to all qubits
//!
//!     let steps = (std::f64::consts::PI / 4.0 * f64::sqrt((1 << n) as f64)) as i32;  // Calculate the number of steps for the Grover's algorithm
//!
//!     for _ in 0..steps {
//!         ctrl(&qubits.slice(1..), || z(&qubits.at(0)))??;  // Apply controlled-Z gate with the first qubit as the target and the rest as controls
//!
//!         around(
//!             &p,
//!             || {
//!                 h(&qubits).unwrap();  // Apply Hadamard gate to all qubits
//!                 x(&qubits).unwrap();  // Apply Pauli-X gate to all qubits
//!             },
//!             || ctrl(&qubits.slice(1..), || z(&qubits.at(0))),  // Apply controlled-Z gate with the first qubit as the target and the rest as controls
//!         )???;
//!     }
//!
//!     let _ = measure(&mut qubits)?;  // Perform measurement on the qubits
//!
//!     let mut p = p.borrow_mut();
//!     p.prepare_for_execution()?;  // Prepare the quantum program for execution
//!     println!("{:#?}", p.blocks());  // Print the blocks of the quantum program
//!
//!     Ok(())
//! }
//! ```
//!
//! The example demonstrates the usage of various Libket functions to implement Grover's algorithm,
//! including qubit initialization, gate operations, control structures, and measurement.
//!
//! For more examples, refer to the Libket Git repository <https://gitlab.com/quantum-ket/libket>.

pub mod c_api;
pub mod code_block;
pub mod decompose;
pub mod error;
pub mod gates;
pub mod instruction;
pub mod ir;
pub mod object;
pub mod process;
pub mod serialize;

pub use gates::*;
pub use instruction::*;
pub use object::*;
pub use process::*;
