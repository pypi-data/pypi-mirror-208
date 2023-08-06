use crate::{
    error::KetError,
    object::{Dump, Future, Label, Pid, Qubit},
    DumpData,
};

/// Deletes the `Qubit` instance.
///
/// # Arguments
///
/// * `qubit` - \[in\] A pointer to the `Qubit` instance to delete.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_qubit_delete(qubit: *mut Qubit) -> i32 {
    unsafe { Box::from_raw(qubit) };
    KetError::Success.error_code()
}

/// Retrieves the index of the qubit.
///
/// # Arguments
///
/// * `qubit` - \[in\] A reference to the `Qubit` instance.
/// * `index` - \[out\] A mutable reference to store the index of the qubit.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_qubit_index(qubit: &Qubit, index: &mut usize) -> i32 {
    *index = qubit.index();
    KetError::Success.error_code()
}

/// Retrieves the process ID associated with the qubit.
///
/// # Arguments
///
/// * `qubit` - \[in\] A reference to the `Qubit` instance.
/// * `pid` - \[out\] A mutable reference to store the process ID of the qubit.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_qubit_pid(qubit: &Qubit, pid: &mut usize) -> i32 {
    *pid = qubit.pid();
    KetError::Success.error_code()
}

/// Retrieves the allocation status of the qubit.
///
/// # Arguments
///
/// * `qubit` - \[in\] A reference to the `Qubit` instance.
/// * `allocated` - \[out\] A mutable reference to store the allocation status of the qubit.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_qubit_allocated(qubit: &Qubit, allocated: &mut bool) -> i32 {
    *allocated = qubit.allocated();
    KetError::Success.error_code()
}

/// Retrieves the measurement status of the qubit.
///
/// # Arguments
///
/// * `qubit` - \[in\] A reference to the `Qubit` instance.
/// * `measured` - \[out\] A mutable reference to store the measurement status of the qubit.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_qubit_measured(qubit: &Qubit, measured: &mut bool) -> i32 {
    *measured = qubit.measured();
    KetError::Success.error_code()
}

/// Deletes the `Dump` instance.
///
/// # Arguments
///
/// * `dump` -\[in\] A pointer to the `Dump` instance to delete.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_dump_delete(dump: *mut Dump) -> i32 {
    unsafe { Box::from_raw(dump) };
    KetError::Success.error_code()
}

/// Retrieves the size of the basis states in the dump.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `size` - \[out\] A mutable reference to store the size of the basis states.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_dump_states_size(dump: &Dump, size: &mut usize) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            *size = value.basis_states().len();
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves a specific basis state from the dump.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `index` - \[in\] The index of the basis state to retrieve.
/// * `state` - \[out\] A mutable pointer to store the basis state.
/// * `size` - \[out\] A mutable reference to store the size of the basis state.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_dump_state(
    dump: &Dump,
    index: usize,
    state: *mut *const u64,
    size: &mut usize,
) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            *state = value.basis_states()[index].as_ptr();
            *size = value.basis_states()[index].len();
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the real amplitudes from the dump.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `amp` - \[out\] A mutable pointer to store the real amplitudes.
/// * `size` - \[out\] A mutable reference to store the size of the amplitudes.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_dump_amplitudes_real(
    dump: &Dump,
    amp: *mut *const f64,
    size: &mut usize,
) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            let amplitudes_real = match value.amplitudes_real() {
                Some(amplitudes_real) => amplitudes_real,
                None => return KetError::DataNotAvailable.error_code(),
            };
            *size = amplitudes_real.len();
            unsafe {
                *amp = amplitudes_real.as_ptr();
            }
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the imaginary amplitudes from the dump.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `amp` - \[out\] A mutable pointer to store the imaginary amplitudes.
/// * `size` - \[out\] A mutable reference to store the size of the amplitudes.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_dump_amplitudes_imag(
    dump: &Dump,
    amp: *mut *const f64,
    size: &mut usize,
) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            let amplitudes_imag = match value.amplitudes_imag() {
                Some(amplitudes_imag) => amplitudes_imag,
                None => return KetError::DataNotAvailable.error_code(),
            };
            *size = amplitudes_imag.len();
            unsafe {
                *amp = amplitudes_imag.as_ptr();
            }
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the probabilities from the dump.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `p` - \[out\] A mutable pointer to store the probabilities.
/// * `size` - \[out\] A mutable reference to store the size of the probabilities.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_dump_probabilities(
    dump: &Dump,
    p: *mut *const f64,
    size: &mut usize,
) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            let probabilities = match value.probabilities() {
                Some(probabilities) => probabilities,
                None => return KetError::DataNotAvailable.error_code(),
            };
            *size = probabilities.len();
            unsafe {
                *p = probabilities.as_ptr();
            }
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the counts from the dump.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `cnt` - \[out\] A mutable pointer to store the counts.
/// * `size` - \[out\] A mutable reference to store the size of the counts.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_dump_count(
    dump: &Dump,
    cnt: *mut *const u32,
    size: &mut usize,
) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            let count = match value.count() {
                Some(count) => count,
                None => return KetError::DataNotAvailable.error_code(),
            };
            *size = count.len();
            unsafe {
                *cnt = count.as_ptr();
            }
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the total count from the dump.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `total` - \[out\] A mutable reference to store the total count.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_dump_total(dump: &Dump, total: &mut u64) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            *total = match value.total() {
                Some(total) => total,
                None => return KetError::DataNotAvailable.error_code(),
            };
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the type of the dump.
///
/// The `dump_type` parameter indicates the type of data stored in the `Dump`.
/// The mapping between the `dump_type` value and the actual data type is as follows:
///
/// - 0: "vector"
/// - 1: "probability"
/// - 2: "shots"
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `dump_type` - \[out\] A mutable reference to store the dump type.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_dump_type(dump: &Dump, dump_type: &mut i32) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            match value {
                DumpData::Vector { .. } => *dump_type = 0,
                DumpData::Probability { .. } => *dump_type = 1,
                DumpData::Shots { .. } => *dump_type = 2,
            }
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Checks if the dump is available.
///
/// # Arguments
///
/// * `dump` - \[in\] A reference to the `Dump` instance.
/// * `available` - \[out\] A mutable reference to store the availability of the dump.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_dump_available(dump: &Dump, available: &mut bool) -> i32 {
    *available = dump.value().is_some();
    KetError::Success.error_code()
}

/// Deletes a `Future` instance.
///
/// # Arguments
///
/// * `future` - \[in\] A raw pointer to the `Future` instance to delete.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_future_delete(future: *mut Future) -> i32 {
    unsafe { Box::from_raw(future) };
    KetError::Success.error_code()
}

/// Retrieves the value of a `Future`.
///
/// # Arguments
///
/// * `future` - \[in\] A reference to the `Future` instance.
/// * `value` - \[out\] A mutable reference to store the future value.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_future_value(future: &Future, value: &mut i64) -> i32 {
    match future.value().as_ref() {
        Some(data) => {
            *value = *data;
            KetError::Success.error_code()
        }
        None => KetError::DataNotAvailable.error_code(),
    }
}

/// Retrieves the index of a `Future`.
///
/// # Arguments
///
/// * `future` - \[in\] A reference to the `Future` instance.
/// * `index` - \[out\] A mutable reference to store the future index.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_future_index(future: &Future, index: &mut usize) -> i32 {
    *index = future.index();
    KetError::Success.error_code()
}

/// Retrieves the process ID (PID) of a `Future`.
///
/// # Arguments
///
/// * `future` - \[in\] A reference to the `Future` instance.
/// * `pid` - \[out\] A mutable reference to store the PID of the future.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_future_pid(future: &Future, pid: &mut usize) -> i32 {
    *pid = future.pid();
    KetError::Success.error_code()
}

/// Checks if the value of a `Future` is available.
///
/// # Arguments
///
/// * `future` - \[in\] A reference to the `Future` instance.
/// * `available` - \[out\] A mutable reference to store the availability of the future value.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_future_available(future: &Future, available: &mut bool) -> i32 {
    *available = future.value().is_some();
    KetError::Success.error_code()
}

/// Deletes a `Label` instance.
///
/// # Arguments
///
/// * `label` - \[in\] A raw pointer to the `Label` instance to delete.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
///
/// # Safety
///
/// This function is marked as unsafe because it deals with raw pointers.
#[no_mangle]
pub unsafe extern "C" fn ket_label_delete(label: *mut Label) -> i32 {
    unsafe { Box::from_raw(label) };
    KetError::Success.error_code()
}

/// Retrieves the index of a `Label`.
///
/// # Arguments
///
/// * `label` - \[in\] A reference to the `Label` instance.
/// * `index` - \[out\] A mutable reference to store the label index.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_label_index(label: &Label, index: &mut usize) -> i32 {
    *index = label.index();
    KetError::Success.error_code()
}

/// Retrieves the process ID (PID) of a `Label`.
///
/// # Arguments
///
/// * `label` - \[in\] A reference to the `Label` instance.
/// * `pid` - \[out\] A mutable reference to store the PID of the label.
///
/// # Returns
///
/// An integer representing the error code. `0` indicates success.
#[no_mangle]
pub extern "C" fn ket_label_pid(label: &Label, pid: &mut usize) -> i32 {
    *pid = label.pid();
    KetError::Success.error_code()
}
