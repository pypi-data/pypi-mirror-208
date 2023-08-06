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

#[no_mangle]
pub extern "C" fn ket_process_new(pid: usize, process: &mut *mut Process) -> i32 {
    *process = Box::into_raw(Box::new(Process::new(pid)));
    KetError::Success.error_code()
}

#[no_mangle]
pub unsafe extern "C" fn ket_process_delete(process: *mut Process) -> i32 {
    unsafe { Box::from_raw(process) };
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_process_set_features(process: &mut Process, features: &Features) -> i32 {
    process.set_features(features.clone());
    KetError::Success.error_code()
}

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

#[no_mangle]
pub extern "C" fn ket_process_free_qubit(
    process: &mut Process,
    qubit: &mut Qubit,
    dirty: bool,
) -> i32 {
    wrapper(process.free_qubit(qubit, dirty))
}

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

#[no_mangle]
pub unsafe extern "C" fn ket_process_ctrl_push(
    process: &mut Process,
    qubits: *const &Qubit,
    qubits_size: usize,
) -> i32 {
    let qubits = unsafe { std::slice::from_raw_parts(qubits, qubits_size) };

    wrapper(process.ctrl_push(qubits))
}

#[no_mangle]
pub extern "C" fn ket_process_ctrl_pop(process: &mut Process) -> i32 {
    wrapper(process.ctrl_pop())
}

#[no_mangle]
pub extern "C" fn ket_process_adj_begin(process: &mut Process) -> i32 {
    wrapper(process.adj_begin())
}

#[no_mangle]
pub extern "C" fn ket_process_adj_end(process: &mut Process) -> i32 {
    wrapper(process.adj_end())
}

#[no_mangle]
pub extern "C" fn ket_process_get_label(process: &mut Process, label: &mut *mut Label) -> i32 {
    *label = Box::into_raw(Box::new(match process.get_label() {
        Ok(label) => label,
        Err(err) => return err.error_code(),
    }));
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_process_open_block(process: &mut Process, label: &Label) -> i32 {
    wrapper(process.open_block(label))
}

#[no_mangle]
pub extern "C" fn ket_process_jump(process: &mut Process, label: &Label) -> i32 {
    wrapper(process.jump(label))
}

#[no_mangle]
pub extern "C" fn ket_process_branch(
    process: &mut Process,
    test: &Future,
    then: &Label,
    otherwise: &Label,
) -> i32 {
    wrapper(process.branch(test, then, otherwise))
}

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

#[no_mangle]
pub extern "C" fn ket_process_int_set(process: &mut Process, dst: &Future, src: &Future) -> i32 {
    wrapper(process.int_set(dst, src))
}

#[no_mangle]
pub extern "C" fn ket_process_prepare_for_execution(process: &mut Process) -> i32 {
    wrapper(process.prepare_for_execution())
}

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

#[no_mangle]
pub extern "C" fn ket_process_set_timeout(process: &mut Process, timeout: u64) -> i32 {
    process.set_timeout(timeout);
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_process_serialize_metrics(process: &mut Process, data_type: i32) -> i32 {
    let data_type = match DataType::from_i32(data_type) {
        Some(data_type) => data_type,
        None => return KetError::UndefinedDataType.error_code(),
    };

    process.serialize_metrics(data_type);

    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_process_serialize_quantum_code(process: &mut Process, data_type: i32) -> i32 {
    let data_type = match DataType::from_i32(data_type) {
        Some(data_type) => data_type,
        None => return KetError::UndefinedDataType.error_code(),
    };

    process.serialize_quantum_code(data_type);

    KetError::Success.error_code()
}

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

#[no_mangle]
pub unsafe extern "C" fn ket_features_delete(features: *mut Features) -> i32 {
    unsafe { Box::from_raw(features) };
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_features_all(features: &mut *mut Features) -> i32 {
    *features = Box::into_raw(Box::new(Features::all()));
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_features_none(features: &mut *mut Features) -> i32 {
    *features = Box::into_raw(Box::new(Features::none()));
    KetError::Success.error_code()
}

#[no_mangle]
pub unsafe extern "C" fn ket_features_register_plugin(
    features: &mut Features,
    name: *const c_char,
) -> i32 {
    let name = unsafe { CStr::from_ptr(name) }.to_str().unwrap();
    features.register_plugin(name);
    KetError::Success.error_code()
}
