use num_derive::{FromPrimitive, ToPrimitive};

#[derive(FromPrimitive, ToPrimitive, Debug)]
pub enum DataType {
    JSON,
    BIN,
}

#[derive(Debug)]
pub enum SerializedData {
    JSON(String),
    BIN(Vec<u8>),
}

#[cfg(test)]
mod tests {
    use super::DataType;
    use num::FromPrimitive;

    #[test]
    fn print_classical_op() {
        let mut data_type = 0;
        while let Some(data) = DataType::from_i32(data_type) {
            println!("#define KET_{:#?} {}", data, data_type);
            data_type += 1;
        }
    }
}
