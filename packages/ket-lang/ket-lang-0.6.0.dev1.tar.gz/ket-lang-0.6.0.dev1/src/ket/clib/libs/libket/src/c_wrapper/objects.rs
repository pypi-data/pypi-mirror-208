use crate::{
    error::KetError,
    object::{Dump, Future, Label, Pid, Qubit},
    DumpData,
};

#[no_mangle]
pub unsafe extern "C" fn ket_qubit_delete(qubit: *mut Qubit) -> i32 {
    unsafe { Box::from_raw(qubit) };
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_qubit_index(qubit: &Qubit, index: &mut usize) -> i32 {
    *index = qubit.index();
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_qubit_pid(qubit: &Qubit, pid: &mut usize) -> i32 {
    *pid = qubit.pid();
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_qubit_allocated(qubit: &Qubit, allocated: &mut bool) -> i32 {
    *allocated = qubit.allocated();
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_qubit_measured(qubit: &Qubit, measured: &mut bool) -> i32 {
    *measured = qubit.measured();
    KetError::Success.error_code()
}

#[no_mangle]
pub unsafe extern "C" fn ket_dump_delete(dump: *mut Dump) -> i32 {
    unsafe { Box::from_raw(dump) };
    KetError::Success.error_code()
}

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

#[no_mangle]
pub unsafe extern "C" fn ket_dump_probabilities(
    dump: &Dump,
    p: *mut *const f64,
    size: &mut usize,
) -> i32 {
    match dump.value().as_ref() {
        Some(value) => {
            let probabilities = match value.probabilities() {
                Some(count) => count,
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

#[no_mangle]
pub extern "C" fn ket_dump_available(dump: &Dump, available: &mut bool) -> i32 {
    *available = dump.value().is_some();
    KetError::Success.error_code()
}

#[no_mangle]
pub unsafe extern "C" fn ket_future_delete(future: *mut Future) -> i32 {
    unsafe { Box::from_raw(future) };
    KetError::Success.error_code()
}

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

#[no_mangle]
pub extern "C" fn ket_future_index(future: &Future, index: &mut usize) -> i32 {
    *index = future.index();
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_future_pid(future: &Future, pid: &mut usize) -> i32 {
    *pid = future.pid();
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_future_available(future: &Future, available: &mut bool) -> i32 {
    *available = future.value().is_some();
    KetError::Success.error_code()
}

#[no_mangle]
pub unsafe extern "C" fn ket_label_delete(label: *mut Label) -> i32 {
    unsafe { Box::from_raw(label) };
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_label_index(label: &Label, index: &mut usize) -> i32 {
    *index = label.index();
    KetError::Success.error_code()
}

#[no_mangle]
pub extern "C" fn ket_label_pid(label: &Label, pid: &mut usize) -> i32 {
    *pid = label.pid();
    KetError::Success.error_code()
}
