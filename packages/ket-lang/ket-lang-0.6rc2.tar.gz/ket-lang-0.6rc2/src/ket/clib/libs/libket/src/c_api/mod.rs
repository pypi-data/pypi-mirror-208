//! # FFI Wrapper Module
//!
//! This module provides a wrapper for Foreign Function Interface (FFI) functions in Rust. 
//! It includes utility functions for error handling and retrieving error messages, 
//! as well as functions for interacting with FFI data structures.
//!
//! ## Error Handling
//!
//! The `ket_error_message` function allows retrieving error messages associated with error codes.
//! Given an error code, it returns a pointer to the corresponding error message string.
//!
//! ## FFI Data Structures
//!
//! This module also includes functions for interacting with FFI data structures such as `Features`, `Qubit`, `Dump`, `Future`, and `Label`. 
//! These functions provide operations for creating, deleting, and accessing properties of these data structures in the FFI context.
//!
//! # Safety
//!
//! Care should be taken when using FFI functions and data structures. 
//! Follow the provided documentation and ensure that proper memory management
//! and safety measures are followed.

pub mod error;
pub mod objects;
pub mod process;
