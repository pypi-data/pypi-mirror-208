use std::collections::HashMap;

use serde::{Deserialize, Serialize};

use crate::error::{KetError, Result};
use crate::instruction::Instruction;

#[derive(Default, Debug, Serialize, Deserialize)]
pub struct CodeBlock {
    pub instructions: Vec<Instruction>,
    pub gate_count: HashMap<usize, usize>,
    pub depth: usize,
}

#[derive(Default, Debug)]
pub struct CodeBlockHandler {
    block: CodeBlock,
    pub use_rz_as_phase: bool,
    adj_instructions: Vec<Vec<Instruction>>,
    gate_per_qubit: HashMap<usize, usize>,
    ended: bool,
}

impl CodeBlockHandler {
    pub fn add_instruction(&mut self, instruction: Instruction) -> Result<()> {
        if self.ended {
            return Err(KetError::TerminatedBlock);
        }

        if let Some(instruction) = match &instruction {
            Instruction::Gate {
                gate,
                target,
                control,
            } => {
                *self.block.gate_count.entry(control.len() + 1).or_default() += 1;
                *self.gate_per_qubit.entry(*target).or_default() += 1;

                control.iter().for_each(|control| {
                    *self.gate_per_qubit.entry(*control).or_default() += 1;
                });

                let instruction = if self.use_rz_as_phase && gate.is_phase() {
                    Instruction::Gate {
                        gate: gate.from_phase_to_rz()?,
                        target: *target,
                        control: control.to_vec(),
                    }
                } else {
                    instruction
                };

                if self.adj_instructions.is_empty() {
                    Some(instruction)
                } else {
                    self.adj_instructions.last_mut().unwrap().push(instruction);
                    None
                }
            }
            Instruction::End(_) => {
                if !self.adj_instructions.is_empty() {
                    return Err(KetError::NonGateInstruction);
                }
                self.ended = true;
                self.block.depth = self
                    .gate_per_qubit
                    .values()
                    .copied()
                    .max()
                    .unwrap_or_default();
                Some(instruction)
            }
            _ => {
                if !self.adj_instructions.is_empty() {
                    return Err(KetError::NonGateInstruction);
                }
                Some(instruction)
            }
        } {
            self.block.instructions.push(instruction);
        }

        Ok(())
    }

    pub fn in_adj(&self) -> bool {
        self.adj_instructions.len() % 2 == 1
    }

    pub fn adj_begin(&mut self) -> Result<()> {
        if self.ended {
            Err(KetError::TerminatedBlock)
        } else {
            self.adj_instructions.push(Vec::new());
            Ok(())
        }
    }

    pub fn adj_end(&mut self) -> Result<()> {
        if self.adj_instructions.is_empty() {
            return Err(KetError::NoAdj);
        }

        if self.adj_instructions.len() == 1 {
            while let Some(instruction) = self.adj_instructions.last_mut().unwrap().pop() {
                self.block.instructions.push(instruction);
            }
            self.adj_instructions.pop();
        } else {
            let mut to_pop = self.adj_instructions.pop().unwrap();
            while let Some(instruction) = to_pop.pop() {
                self.adj_instructions.last_mut().unwrap().push(instruction);
            }
        }

        Ok(())
    }

    pub fn block(&self) -> &CodeBlock {
        &self.block
    }
}

#[cfg(test)]
mod tests {

    use crate::code_block::*;
    use crate::instruction::*;

    fn bell(block: Option<CodeBlockHandler>, measure: bool, ended: bool) -> CodeBlockHandler {
        let mut block: CodeBlockHandler = match block {
            Some(block) => block,
            None => {
                let mut block: CodeBlockHandler = Default::default();
                for i in 0..2 {
                    block
                        .add_instruction(Instruction::Alloc {
                            dirty: false,
                            target: i,
                        })
                        .unwrap();
                }
                block
            }
        };

        block
            .add_instruction(Instruction::Gate {
                gate: QuantumGate::Hadamard,
                target: 0,
                control: Default::default(),
            })
            .unwrap();
        block
            .add_instruction(Instruction::Gate {
                gate: QuantumGate::PauliX,
                target: 1,
                control: vec![0],
            })
            .unwrap();

        if measure {
            block
                .add_instruction(Instruction::Measure {
                    qubits: vec![0, 1],
                    output: 1,
                })
                .unwrap();
        }
        if ended {
            block
                .add_instruction(Instruction::End(EndInstruction::Halt))
                .unwrap();
        }
        block
    }

    #[test]
    fn bell_code() {
        let block = bell(None, true, true);
        print!("{:#?}", block);
    }

    #[test]
    fn ended_block_error() {
        let mut block = bell(None, true, true);
        assert!(block
            .add_instruction(Instruction::Alloc {
                dirty: false,
                target: 2,
            })
            .is_err())
    }

    #[test]
    fn bell_adj() {
        let mut block = bell(None, false, false);
        block.adj_begin().unwrap();
        let mut block = bell(Some(block), false, false);
        block.adj_end().unwrap();
        block
            .add_instruction(Instruction::End(EndInstruction::Halt))
            .unwrap();
        print!("{:#?}", block);
    }

    #[test]
    fn adj_error() {
        let mut block = bell(None, false, false);
        block.adj_begin().unwrap();
        assert!(block
            .add_instruction(Instruction::End(EndInstruction::Halt))
            .is_err());
    }
}
