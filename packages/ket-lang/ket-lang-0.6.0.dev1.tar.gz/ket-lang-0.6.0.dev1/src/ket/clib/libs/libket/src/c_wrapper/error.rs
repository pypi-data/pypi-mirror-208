use crate::error::{KetError, Result};

#[no_mangle]
pub extern "C" fn ket_error_message(error_code: i32, size: &mut usize) -> *const u8 {
    let msg = KetError::from_error_code(error_code).to_str();
    *size = msg.len();
    msg.as_ptr()
}

pub fn wrapper(error: Result<()>) -> i32 {
    match error {
        Ok(_) => KetError::Success.error_code(),
        Err(error) => error.error_code(),
    }
}
