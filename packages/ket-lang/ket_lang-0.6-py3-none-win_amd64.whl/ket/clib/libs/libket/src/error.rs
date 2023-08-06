use std::{error::Error, fmt::Display, result};

use num::{FromPrimitive, ToPrimitive};
use num_derive::{FromPrimitive, ToPrimitive};

#[derive(Debug, FromPrimitive, ToPrimitive)]
pub enum KetError {
    Success,
    ControlTwice,
    DataNotAvailable,
    DeallocatedQubit,
    FailToParseResult,
    NoAdj,
    NoCtrl,
    NonGateInstruction,
    NotBIN,
    NotJSON,
    NotUnitary,
    PluginOnCtrl,
    TargetOnControl,
    TerminatedBlock,
    UndefinedClassicalOp,
    UndefinedDataType,
    UndefinedGate,
    UnexpectedResultData,
    UnmatchedPid,
    DirtyNotAllowed,
    DumpNotAllowed,
    MeasureNotAllowed,
    FreeNotAllowed,
    PluginNotRegistered,
    ControlFlowNotAllowed,
    NotPhaseGate,
    UndefinedError,
}

pub type Result<T> = result::Result<T, KetError>;

impl KetError {
    pub fn to_str(&self) -> &'static str {
        match self {
            KetError::Success => "the call returned successfully",
            KetError::ControlTwice => "cannot set a qubit as a control twice",
            KetError::DeallocatedQubit => "cannot operate with a deallocated or invalid qubit",
            KetError::FailToParseResult => "fail to parse serialized result data",
            KetError::NoAdj => "no inverse scope to end",
            KetError::NoCtrl => "no control scope to end",
            KetError::NonGateInstruction => {
                "cannot apply a non-gate instruction within a controlled or inverse scope"
            }
            KetError::NotBIN => "data is not BIN",
            KetError::NotJSON => "data is not JSON",
            KetError::NotUnitary => "the given matrix is not unitary",
            KetError::PluginOnCtrl => "cannot apply plugin within a controlled scope",
            KetError::TargetOnControl => {
                "a qubit cannot be targeted and controlled at the same time"
            }
            KetError::TerminatedBlock => "cannot append statements to a terminated block",
            KetError::UndefinedClassicalOp => "undefined classical operation",
            KetError::UndefinedDataType => "undefined data type",
            KetError::UndefinedGate => "undefined quantum gate",
            KetError::UnexpectedResultData => "result do not have the expected number of values",
            KetError::UnmatchedPid => "unmatched pid",
            KetError::UndefinedError => "undefined error",
            KetError::DataNotAvailable => "data not available",
            KetError::DirtyNotAllowed => "cannot allocate or free dirty qubits (feature disabled)",
            KetError::FreeNotAllowed => "cannot free qubit (feature disabled)",
            KetError::PluginNotRegistered => "plugin not registered",
            KetError::ControlFlowNotAllowed => {
                "classical control flow not allowed (feature disabled)"
            }
            KetError::DumpNotAllowed => "cannot dump qubits (feature disabled)",
            KetError::MeasureNotAllowed => "cannot measure qubit (feature disabled)",
            KetError::NotPhaseGate => "expecting a phase gate",
        }
    }

    pub fn error_code(&self) -> i32 {
        self.to_i32().unwrap()
    }

    pub fn from_error_code(error_code: i32) -> KetError {
        Self::from_i32(error_code).unwrap_or(KetError::UndefinedError)
    }
}

impl Display for KetError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.to_str())
    }
}

impl Error for KetError {}

#[cfg(test)]
mod tests {
    use super::KetError;

    #[test]
    fn success_is_zero() {
        assert!(KetError::Success.error_code() == 0)
    }

    #[test]
    fn print_error_code() {
        let mut error_code = 0;
        loop {
            let error = KetError::from_error_code(error_code);
            let error_str = format!("{:#?}", error);
            let error_str = error_str
                .split_inclusive(char::is_uppercase)
                .map(|part| {
                    let size = part.len();
                    let lest = part.chars().last().unwrap();
                    if size > 1 && char::is_uppercase(lest) {
                        format!("{}_{}", &part[..size - 1], lest)
                    } else {
                        String::from(part)
                    }
                })
                .collect::<Vec<String>>()
                .concat()
                .to_uppercase();
            println!("#define KET_{} {}", error_str, error_code);

            if let KetError::UndefinedError = error {
                break;
            } else {
                error_code += 1;
            }
        }
    }
}
