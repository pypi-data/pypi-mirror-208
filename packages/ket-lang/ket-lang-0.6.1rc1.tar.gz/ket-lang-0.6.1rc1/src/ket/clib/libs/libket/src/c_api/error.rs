use crate::error::{KetError, Result};

/// Retrieves the error message associated with an error code.
///
/// This function takes an error code as input and returns a pointer to
/// the error message string. The `size` parameter is a mutable reference
/// that will be updated with the length of the error message string.
///
/// # Arguments
///
/// * `error_code` - \[in\] The error code for which to retrieve the error message.
/// * `size` - \[out\] A mutable reference to store the size of the error message.
///
/// # Returns
///
/// A pointer to the error message string.
#[no_mangle]
pub extern "C" fn ket_error_message(error_code: i32, size: &mut usize) -> *const u8 {
    let msg = KetError::from_error_code(error_code).to_str();
    *size = msg.len();
    msg.as_ptr()
}

/// Wraps the error handling logic for FFI functions.
///
/// This function is used to handle errors returned from FFI functions.
/// It takes a `Result` as input, where the `Ok` variant indicates success and
/// the `Err` variant represents an error. It returns the corresponding error
/// code based on the success or error case.
///
/// # Arguments
///
/// * `error` - The `Result` representing the success or failure of an operation.
///
/// # Returns
///
/// The error code. If the operation succeeded, it returns the error code for
/// success (`0`). If an error occurred, it returns the corresponding error code.
pub(super) fn wrapper(error: Result<()>) -> i32 {
    match error {
        Ok(_) => KetError::Success.error_code(),
        Err(error) => error.error_code(),
    }
}
