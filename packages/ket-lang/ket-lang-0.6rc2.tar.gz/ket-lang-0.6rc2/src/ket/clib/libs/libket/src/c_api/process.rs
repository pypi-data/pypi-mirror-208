use std::{ffi::CStr, os::raw::c_char};

use crate::{
    error::KetError,
    instruction::{ClassicalOp, QuantumGate},
    object::{Dump, Future, Label, Qubit},
    process::Process,
    serialize::{DataType, SerializedData},
    Features,
};

use num::{FromPrimitive, ToPrimitive};

use super::error::wrapper;

/// Creates a new `Process` instance with the given process ID.
///
/// # Arguments
///
/// * `pid` -  \[in\] The process ID.
/// * `process` -  \[out\] A mutable pointer to a `Process` pointer.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub extern "C" fn ket_process_new(pid: usize, process: &mut *mut Process) -> i32 {
    *process = Box::into_raw(Box::new(Process::new(pid)));
    KetError::Success.error_code()
}

/// Deletes the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A pointer to the `Process` instance to be deleted.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_process_delete(process: *mut Process) -> i32 {
    unsafe { Box::from_raw(process) };
    KetError::Success.error_code()
}

/// Sets the features for the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `features` -  \[in\] A reference to the `Features` instance to set.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_set_features(process: &mut Process, features: &Features) -> i32 {
    process.set_features(features.clone());
    KetError::Success.error_code()
}

/// Allocates a qubit for the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `dirty` -  \[in\] A boolean indicating whether the allocated qubit should be initialized as dirty.
/// * `qubit` -  \[out\] A mutable pointer to a `Qubit` pointer.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_allocate_qubit(
    process: &mut Process,
    dirty: bool,
    qubit: &mut *mut Qubit,
) -> i32 {
    match process.allocate_qubit(dirty) {
        Ok(result) => {
            *qubit = Box::into_raw(Box::new(result));
            KetError::Success.error_code()
        }
        Err(error) => error.error_code(),
    }
}

/// Frees the allocated qubit from the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `qubit` -  \[in\] A mutable reference to the `Qubit` instance to be freed.
/// * `dirty` -  \[in\] A boolean indicating whether the qubit should be marked as dirty before freeing.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_free_qubit(
    process: &mut Process,
    qubit: &mut Qubit,
    dirty: bool,
) -> i32 {
    wrapper(process.free_qubit(qubit, dirty))
}

/// Applies a quantum gate to the target `Qubit` in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `gate` -  \[in\] An integer representing the gate type. See the function body for the mapping of gate values to gate types.
/// * `param` -  \[in\] A floating-point parameter value used by certain gate types.
/// * `target` -  \[in\] A reference to the target `Qubit` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_apply_gate(
    process: &mut Process,
    gate: i32,
    param: f64,
    target: &Qubit,
) -> i32 {
    let gate = match gate {
        0 => QuantumGate::PauliX,
        1 => QuantumGate::PauliY,
        2 => QuantumGate::PauliZ,
        3 => QuantumGate::Hadamard,
        4 => QuantumGate::Phase(param),
        5 => QuantumGate::RX(param),
        6 => QuantumGate::RY(param),
        7 => QuantumGate::RZ(param),
        _ => {
            return KetError::UndefinedGate.error_code();
        }
    };

    wrapper(process.apply_gate(gate, target))
}

/// Applies a plugin to the target qubits in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `name` -  \[in\] A pointer to a null-terminated C string representing the name of the plugin.
/// * `args` -  \[in\] A pointer to a null-terminated C string representing the arguments for the plugin.
/// * `target` -  \[in\] A pointer to an array of references to `Qubit` instances.
/// * `target_size` -  \[in\] The size of the `target` array.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe due to the use of raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_process_apply_plugin(
    process: &mut Process,
    name: *const c_char,
    args: *const c_char,
    target: *const &Qubit,
    target_size: usize,
) -> i32 {
    let name = unsafe { CStr::from_ptr(name) }.to_str().unwrap();
    let args = unsafe { CStr::from_ptr(args) }.to_str().unwrap();
    let target = unsafe { std::slice::from_raw_parts(target, target_size) };

    wrapper(process.apply_plugin(name, target, args))
}

/// Measures the specified qubits in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `qubits` -  \[in\] A mutable pointer to an array of mutable references to `Qubit` instances.
/// * `qubits_size` -  \[in\] The size of the `qubits` array.
/// * `future` -  \[out\] A mutable pointer to a `Future` pointer.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe due to the use of raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_process_measure(
    process: &mut Process,
    qubits: *mut &mut Qubit,
    qubits_size: usize,
    future: &mut *mut Future,
) -> i32 {
    let qubits = unsafe { std::slice::from_raw_parts_mut(qubits, qubits_size) };

    match process.measure(qubits) {
        Ok(result) => {
            *future = Box::into_raw(Box::new(result));
            KetError::Success.error_code()
        }
        Err(error) => error.error_code(),
    }
}

/// Pushes control qubits onto the control stack in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `qubits` -  \[in\] A pointer to an array of references to `Qubit` instances.
/// * `qubits_size` -  \[in\] The size of the `qubits` array.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe due to the use of raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_process_ctrl_push(
    process: &mut Process,
    qubits: *const &Qubit,
    qubits_size: usize,
) -> i32 {
    let qubits = unsafe { std::slice::from_raw_parts(qubits, qubits_size) };

    wrapper(process.ctrl_push(qubits))
}

/// Pops control qubits from the control stack in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_ctrl_pop(process: &mut Process) -> i32 {
    wrapper(process.ctrl_pop())
}

/// Begins an adjoint operation in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_adj_begin(process: &mut Process) -> i32 {
    wrapper(process.adj_begin())
}

/// Ends an adjoint operation in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_adj_end(process: &mut Process) -> i32 {
    wrapper(process.adj_end())
}

/// Creates a new label in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `label` -  \[out\] A mutable pointer to a `Label` pointer.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_get_label(process: &mut Process, label: &mut *mut Label) -> i32 {
    *label = Box::into_raw(Box::new(match process.get_label() {
        Ok(label) => label,
        Err(err) => return err.error_code(),
    }));
    KetError::Success.error_code()
}

/// Opens a block in the `Process` instance using the specified label.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `label` -  \[in\] A reference to a `Label` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_open_block(process: &mut Process, label: &Label) -> i32 {
    wrapper(process.open_block(label))
}

/// Jumps to a specified label in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `label` -  \[in\] A reference to a `Label` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_jump(process: &mut Process, label: &Label) -> i32 {
    wrapper(process.jump(label))
}

/// Branches the `Process` instance based on the outcome of a future.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `test` -  \[in\] A reference to a `Future` instance.
/// * `then` -  \[in\] A reference to a `Label` instance representing the target label for the "then" branch.
/// * `otherwise` -  \[in\] A reference to a `Label` instance representing the target label for the "otherwise" branch.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_branch(
    process: &mut Process,
    test: &Future,
    then: &Label,
    otherwise: &Label,
) -> i32 {
    wrapper(process.branch(test, then, otherwise))
}

/// Dumps the quantum state of the specified qubits in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `qubits` -  \[in\] A pointer to an array of references to `Qubit` instances.
/// * `qubits_size` -  \[in\] The size of the `qubits` array.
/// * `dump` -  \[out\] A mutable pointer to a `Dump` pointer.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe due to the use of raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_process_dump(
    process: &mut Process,
    qubits: *const &Qubit,
    qubits_size: usize,
    dump: &mut *mut Dump,
) -> i32 {
    let qubits = unsafe { std::slice::from_raw_parts(qubits, qubits_size) };

    match process.dump(qubits) {
        Ok(result) => {
            *dump = Box::into_raw(Box::new(result));
            KetError::Success.error_code()
        }
        Err(error) => error.error_code(),
    }
}

/// Adds an integer operation to the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `op` -  \[in\] An integer representing the operation to perform.
/// * `lhs` -  \[in\] A reference to a `Future` instance representing the left-hand side of the operation.
/// * `rhs` -  \[in\] A reference to a `Future` instance representing the right-hand side of the operation.
/// * `result` -  \[out\] A mutable pointer to a `Future` pointer that will store the result of the operation.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_add_int_op(
    process: &mut Process,
    op: i32,
    lhs: &Future,
    rhs: &Future,
    result: &mut *mut Future,
) -> i32 {
    let op = match ClassicalOp::from_i32(op) {
        Some(op) => op,
        None => return KetError::UndefinedClassicalOp.error_code(),
    };

    match process.add_int_op(op, lhs, rhs) {
        Ok(future) => {
            *result = Box::into_raw(Box::new(future));
            KetError::Success.error_code()
        }
        Err(error) => error.error_code(),
    }
}

/// Creates a new `Future` instance representing an integer value in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `value` -  \[in\] The integer value.
/// * `future` -  \[out\] A mutable pointer to a `Future` pointer that will store the created future.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_int_new(
    process: &mut Process,
    value: i64,
    future: &mut *mut Future,
) -> i32 {
    match process.int_new(value) {
        Ok(result) => {
            *future = Box::into_raw(Box::new(result));
            KetError::Success.error_code()
        }
        Err(error) => error.error_code(),
    }
}

/// Sets the value of a destination `Future` to the value of a source `Future` in the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `dst` -  \[in\] A reference to the destination `Future`.
/// * `src` -  \[in\] A reference to the source `Future`.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_int_set(process: &mut Process, dst: &Future, src: &Future) -> i32 {
    wrapper(process.int_set(dst, src))
}

/// Prepares the `Process` instance for execution.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_prepare_for_execution(process: &mut Process) -> i32 {
    wrapper(process.prepare_for_execution())
}

/// Retrieves the execution time of the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A reference to the `Process` instance.
/// * `time` -  \[out\] A mutable reference to a `f64` value that will store the execution time.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_exec_time(process: &Process, time: &mut f64) -> i32 {
    match process.exec_time() {
        Some(t) => {
            *time = t;
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Sets the timeout value for the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `timeout` -  \[in\] The timeout value in milliseconds.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_process_set_timeout(process: &mut Process, timeout: u64) -> i32 {
    process.set_timeout(timeout);
    KetError::Success.error_code()
}

/// Serializes the metrics data of the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `data_type` -  \[in\] An integer representing the data type for serialization.
///   Use `0` for JSON serialization, and `1` for binary serialization.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Compatibility
///
/// Binary serialization compatibility depends on various factors, including
/// the Rust version and any external dependencies used for binary serialization.
/// Ensure that the necessary requirements are met for binary serialization to
/// work correctly in your specific environment.
#[no_mangle]
pub extern "C" fn ket_process_serialize_metrics(process: &mut Process, data_type: i32) -> i32 {
    let data_type = match DataType::from_i32(data_type) {
        Some(data_type) => data_type,
        None => return KetError::UndefinedDataType.error_code(),
    };

    process.serialize_metrics(data_type);

    KetError::Success.error_code()
}

/// Serializes the quantum code of the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `data_type` -  \[in\] An integer representing the data type for serialization.
///   Use `0` for JSON serialization, and `1` for binary serialization.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Compatibility
///
/// Binary serialization compatibility depends on various factors, including
/// the Rust version and any external dependencies used for binary serialization.
/// Ensure that the necessary requirements are met for binary serialization to
/// work correctly in your specific environment.
#[no_mangle]
pub extern "C" fn ket_process_serialize_quantum_code(process: &mut Process, data_type: i32) -> i32 {
    let data_type = match DataType::from_i32(data_type) {
        Some(data_type) => data_type,
        None => return KetError::UndefinedDataType.error_code(),
    };

    process.serialize_quantum_code(data_type);

    KetError::Success.error_code()
}

/// Retrieves the serialized metrics data from the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A reference to the `Process` instance.
/// * `data` -  \[out\] A mutable pointer to the serialized data buffer.
/// * `size` -  \[out\] A mutable reference to the size of the serialized data.
/// * `data_type` -  \[out\] A mutable reference to the data type indicator.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Remarks
///
/// This function retrieves the serialized metrics data from the `Process` instance.
/// The data buffer pointer, size, and data type are updated accordingly.
///
/// # Compatibility
///
/// Binary serialization compatibility depends on various factors, including
/// the Rust version and any external dependencies used for binary serialization.
/// Ensure that the necessary requirements are met for binary serialization to
/// work correctly in your specific environment.
#[no_mangle]
pub extern "C" fn ket_process_get_serialized_metrics(
    process: &Process,
    data: &mut *const u8,
    size: &mut usize,
    data_type: &mut i32,
) -> i32 {
    match process.get_serialized_metrics() {
        Some(metrics) => {
            match metrics {
                SerializedData::JSON(json) => {
                    *data = json.as_ptr();
                    *size = json.len();
                    *data_type = DataType::JSON.to_i32().unwrap();
                }
                SerializedData::BIN(bin) => {
                    *data = bin.as_ptr();
                    *size = bin.len();
                    *data_type = DataType::BIN.to_i32().unwrap();
                }
            }
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the serialized quantum code from the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A reference to the `Process` instance.
/// * `data` -  \[out\] A mutable pointer to the serialized data buffer.
/// * `size` -  \[out\] A mutable reference to the size of the serialized data.
/// * `data_type` -  \[out\] A mutable reference to the data type indicator.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Remarks
///
/// This function retrieves the serialized quantum code from the `Process` instance.
/// The data buffer pointer, size, and data type are updated accordingly.
///
/// # Compatibility
///
/// Binary serialization compatibility depends on various factors, including
/// the Rust version and any external dependencies used for binary serialization.
/// Ensure that the necessary requirements are met for binary serialization to
/// work correctly in your specific environment.
#[no_mangle]
pub extern "C" fn ket_process_get_serialized_quantum_code(
    process: &Process,
    data: &mut *const u8,
    size: &mut usize,
    data_type: &mut i32,
) -> i32 {
    match process.get_serialized_quantum_code() {
        Some(code) => {
            match code {
                SerializedData::JSON(json) => {
                    *data = json.as_ptr();
                    *size = json.len();
                    *data_type = DataType::JSON.to_i32().unwrap();
                }
                SerializedData::BIN(bin) => {
                    *data = bin.as_ptr();
                    *size = bin.len();
                    *data_type = DataType::BIN.to_i32().unwrap();
                }
            }
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Sets the serialized result data for the `Process` instance.
///
/// # Arguments
///
/// * `process` -  \[in\] A mutable reference to the `Process` instance.
/// * `result` -  \[in\] A pointer to the serialized result data.
/// * `result_size` -  \[in\] The size of the serialized result data.
/// * `data_type` -  \[in\] The data type indicator.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Remarks
///
/// This function sets the serialized result data for the `Process` instance.
/// The `result` pointer should point to the serialized data buffer, and `result_size`
/// should specify the size of the buffer. The `data_type` indicates
/// the format of the serialized data.
///
/// The `data_type` can be `0` for JSON serialization or `1` for binary serialization.
/// If `data_type` is `0`, the serialized data is expected to be a valid UTF-8 encoded JSON string.
/// If `data_type` is `1`, the serialized data is treated as a binary blob.
///
/// # Safety
///
/// This function is marked as `unsafe` because it accepts a raw pointer as input.
/// It is the caller's responsibility to ensure that the pointer is valid and properly aligned.
/// The caller must also guarantee that the serialized data is valid and correctly matches the
/// specified data type.
#[no_mangle]
pub unsafe extern "C" fn ket_process_set_serialized_result(
    process: &mut Process,
    result: *const u8,
    result_size: usize,
    data_type: i32,
) -> i32 {
    let data_type = match DataType::from_i32(data_type) {
        Some(data_type) => data_type,
        None => return KetError::UndefinedDataType.error_code(),
    };

    let result = unsafe { std::slice::from_raw_parts(result, result_size) };

    let result = match data_type {
        DataType::JSON => SerializedData::JSON(String::from(std::str::from_utf8(result).unwrap())),
        DataType::BIN => SerializedData::BIN(result.to_vec()),
    };

    wrapper(process.set_serialized_result(&result))
}

/// Creates a new `Features` instance with the specified feature flags.
///
/// # Arguments
///
/// * `allow_dirty_qubits` -  \[in\] Indicates whether dirty qubits are allowed.
/// * `allow_free_qubits` -  \[in\] Indicates whether free qubits are allowed.
/// * `valid_after_measure` -  \[in\] Indicates whether the state remains valid after measurement.
/// * `classical_control_flow` -  \[in\] Indicates whether classical control flow is enabled.
/// * `allow_dump` -  \[in\] Indicates whether dumping is allowed.
/// * `allow_measure` -  \[in\] Indicates whether measurements are allowed.
/// * `continue_after_dump` -  \[in\] Indicates whether execution continues after dumping.
/// * `decompose` -  \[in\] Indicates whether decomposition is enabled.
/// * `use_rz_as_phase` -  \[in\] Indicates whether RZ gates are used for phase operations.
/// * `features` -  \[out\] A mutable pointer to store the created `Features` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_features_new(
    allow_dirty_qubits: bool,
    allow_free_qubits: bool,
    valid_after_measure: bool,
    classical_control_flow: bool,
    allow_dump: bool,
    allow_measure: bool,
    continue_after_dump: bool,
    decompose: bool,
    use_rz_as_phase: bool,
    features: &mut *mut Features,
) -> i32 {
    *features = Box::into_raw(Box::new(Features::new(
        allow_dirty_qubits,
        allow_free_qubits,
        valid_after_measure,
        classical_control_flow,
        allow_dump,
        allow_measure,
        continue_after_dump,
        decompose,
        use_rz_as_phase,
    )));
    KetError::Success.error_code()
}

/// Deletes the `Features` instance.
///
/// # Arguments
///
/// * `features` -  \[in\] A pointer to the `Features` instance to delete.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
/// 
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_features_delete(features: *mut Features) -> i32 {
    unsafe { Box::from_raw(features) };
    KetError::Success.error_code()
}

/// Creates a new `Features` instance with all features enabled.
///
/// # Arguments
///
/// * `features` -  \[out\] A mutable pointer to store the created `Features` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_features_all(features: &mut *mut Features) -> i32 {
    *features = Box::into_raw(Box::new(Features::all()));
    KetError::Success.error_code()
}

/// Creates a new `Features` instance with no features enabled.
///
/// # Arguments
///
/// * `features` -  \[out\] A mutable pointer to store the created `Features` instance.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_features_none(features: &mut *mut Features) -> i32 {
    *features = Box::into_raw(Box::new(Features::none()));
    KetError::Success.error_code()
}

/// Registers a plugin with the `Features` instance.
///
/// # Arguments
///
/// * `features` -  \[in\] A mutable reference to the `Features` instance.
/// * `name` -  \[in\] The name of the plugin to register.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
/// 
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_features_register_plugin(
    features: &mut Features,
    name: *const c_char,
) -> i32 {
    let name = unsafe { CStr::from_ptr(name) }.to_str().unwrap();
    features.register_plugin(name);
    KetError::Success.error_code()
}
