use std::{cell::RefCell, collections::BTreeSet, ops::Deref, rc::Rc};

use rand::Rng;

use crate::{
    code_block::{CodeBlock, CodeBlockHandler},
    decompose::decompose,
    error::{KetError, Result},
    instruction::{ClassicalOp, EndInstruction, Instruction, QuantumGate},
    ir::{Metrics, ResultData},
    object::{Dump, DumpData, Future, Label, Pid, Qubit},
    serialize::{DataType, SerializedData},
};

#[derive(Clone, Debug)]
pub struct Features {
    allow_dirty_qubits: bool,
    allow_free_qubits: bool,
    valid_after_measure: bool,
    plugins: BTreeSet<String>,
    classical_control_flow: bool,
    allow_dump: bool,
    allow_measure: bool,
    continue_after_dump: bool,
    decompose: bool,
    use_rz_as_phase: bool,
}

impl Features {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        allow_dirty_qubits: bool,
        allow_free_qubits: bool,
        valid_after_measure: bool,
        classical_control_flow: bool,
        allow_dump: bool,
        allow_measure: bool,
        continue_after_dump: bool,
        decompose: bool,
        use_rz_as_phase: bool,
    ) -> Features {
        Features {
            allow_dirty_qubits,
            allow_free_qubits,
            valid_after_measure,
            plugins: BTreeSet::new(),
            classical_control_flow,
            allow_dump,
            allow_measure,
            continue_after_dump,
            decompose,
            use_rz_as_phase,
        }
    }

    pub fn all() -> Features {
        Features {
            allow_dirty_qubits: true,
            allow_free_qubits: true,
            valid_after_measure: true,
            plugins: BTreeSet::new(),
            classical_control_flow: true,
            allow_dump: true,
            allow_measure: true,
            continue_after_dump: true,
            decompose: false,
            use_rz_as_phase: false,
        }
    }

    pub fn none() -> Features {
        Features {
            allow_dirty_qubits: false,
            allow_free_qubits: false,
            valid_after_measure: false,
            plugins: BTreeSet::new(),
            classical_control_flow: false,
            allow_dump: false,
            allow_measure: true,
            continue_after_dump: false,
            decompose: false,
            use_rz_as_phase: false,
        }
    }

    pub fn register_plugin(&mut self, plugin: &str) {
        self.plugins.insert(plugin.to_string());
    }
}

#[derive(Debug)]

pub struct Process {
    pid: usize,

    metrics: Metrics,

    num_qubit: usize,
    blocks: Vec<CodeBlockHandler>,
    current_block: usize,

    ctrl_stack: Vec<Vec<usize>>,

    futures: Vec<Rc<RefCell<Option<i64>>>>,
    dumps: Vec<Rc<RefCell<Option<DumpData>>>>,

    quantum_code_serialized: Option<SerializedData>,
    metrics_serialized: Option<SerializedData>,

    exec_time: Option<f64>,

    features: Features,
}

impl Process {
    pub fn new(pid: usize) -> Self {
        Self {
            pid,
            metrics: Default::default(),
            num_qubit: Default::default(),
            blocks: vec![CodeBlockHandler::default()],
            current_block: Default::default(),
            ctrl_stack: Default::default(),
            futures: vec![Rc::new(RefCell::new(Some(0)))],
            dumps: Default::default(),
            quantum_code_serialized: Default::default(),
            metrics_serialized: Default::default(),
            exec_time: Default::default(),
            features: Features::all(),
        }
    }

    pub fn new_ptr() -> Rc<RefCell<Self>> {
        Rc::new(RefCell::new(Self::new(rand::thread_rng().gen())))
    }

    fn match_pid(&self, obj: &impl Pid) -> Result<()> {
        if obj.pid() != self.pid {
            Err(KetError::UnmatchedPid)
        } else {
            Ok(())
        }
    }

    fn get_control_qubits(&self) -> Vec<usize> {
        let mut tmp_vec = Vec::new();
        for inner_ctrl in self.ctrl_stack.iter() {
            tmp_vec.extend(inner_ctrl.iter());
        }
        tmp_vec
    }

    fn assert_target_not_in_control(&self, target: &Qubit) -> Result<()> {
        if self
            .ctrl_stack
            .iter()
            .any(|inner| inner.contains(&target.index()))
        {
            Err(KetError::TargetOnControl)
        } else {
            Ok(())
        }
    }

    pub fn set_features(&mut self, features: Features) {
        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .use_rz_as_phase = features.use_rz_as_phase;
        self.features = features;
    }

    pub fn allocate_qubit(&mut self, dirty: bool) -> Result<Qubit> {
        if !self.features.allow_dirty_qubits && dirty {
            return Err(KetError::DirtyNotAllowed);
        }

        let index = self.metrics.qubit_count;
        self.metrics.qubit_count += 1;
        self.num_qubit += 1;
        self.metrics.qubit_simultaneous = if self.num_qubit > self.metrics.qubit_simultaneous {
            self.num_qubit
        } else {
            self.metrics.qubit_simultaneous
        };

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Alloc {
                dirty,
                target: index,
            })?;

        Ok(Qubit::new(index, self.pid))
    }

    pub fn free_qubit(&mut self, qubit: &mut Qubit, dirty: bool) -> Result<()> {
        if !self.features.allow_dirty_qubits && dirty {
            return Err(KetError::DirtyNotAllowed);
        }

        if !self.features.allow_free_qubits {
            return Err(KetError::FreeNotAllowed);
        }

        self.match_pid(qubit)?;
        qubit.assert_allocated()?;

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Free {
                dirty,
                target: qubit.index(),
            })?;

        qubit.set_deallocated();

        Ok(())
    }

    pub fn apply_gate(&mut self, gate: QuantumGate, target: &Qubit) -> Result<()> {
        target.assert_allocated()?;
        self.match_pid(target)?;
        let control = self.get_control_qubits();
        self.assert_target_not_in_control(target)?;

        let block = self.blocks.get_mut(self.current_block).unwrap();

        let gate = if block.in_adj() { gate.inverse() } else { gate };

        if self.features.decompose {
            let mut decomposed_gate = decompose(gate, control, target.index());
            if block.in_adj() {
                decomposed_gate.reverse();
            }
            for instruction in decomposed_gate {
                block.add_instruction(instruction)?;
            }
        } else {
            block.add_instruction(Instruction::Gate {
                gate,
                target: target.index(),
                control,
            })?;
        }
        Ok(())
    }

    pub fn apply_plugin(&mut self, name: &str, target: &[&Qubit], args: &str) -> Result<()> {
        if !self.features.plugins.contains(name) {
            return Err(KetError::PluginNotRegistered);
        }

        if !self.ctrl_stack.is_empty() {
            return Err(KetError::PluginOnCtrl);
        }

        for target in target {
            self.match_pid(*target)?;
        }

        self.metrics.plugins.insert(String::from(name));

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Plugin {
                name: String::from(name),
                target: target.iter().map(|q| q.index()).collect(),
                args: String::from(args),
            })?;

        Ok(())
    }

    pub fn apply_plugin_ref(
        &mut self,
        name: &str,
        target: &[Rc<RefCell<Qubit>>],
        args: &str,
    ) -> Result<()> {
        if !self.features.plugins.contains(name) {
            return Err(KetError::PluginNotRegistered);
        }

        if !self.ctrl_stack.is_empty() {
            return Err(KetError::PluginOnCtrl);
        }

        for target in target {
            self.match_pid(target.as_ref().borrow().deref())?;
        }

        self.metrics.plugins.insert(String::from(name));

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Plugin {
                name: String::from(name),
                target: target.iter().map(|q| q.as_ref().borrow().index()).collect(),
                args: String::from(args),
            })?;

        Ok(())
    }

    pub fn measure(&mut self, qubits: &mut [&mut Qubit]) -> Result<Future> {
        if !self.features.allow_measure {
            return Err(KetError::MeasureNotAllowed);
        }

        for qubit in qubits.iter_mut() {
            self.match_pid(*qubit)?;
            qubit.assert_allocated()?;
            qubit.set_measured();
        }

        if !self.features.valid_after_measure {
            for qubit in qubits.iter_mut() {
                qubit.set_deallocated();
            }
        }

        let future_index = self.metrics.future_count;
        self.metrics.future_count += 1;

        let future_value = Rc::new(RefCell::new(None));

        self.futures.push(Rc::clone(&future_value));

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Measure {
                qubits: qubits.iter().map(|qubit| qubit.index()).collect(),
                output: future_index,
            })?;

        Ok(Future::new(future_index, self.pid, future_value))
    }

    pub fn measure_ref(&mut self, qubits: &mut [Rc<RefCell<Qubit>>]) -> Result<Future> {
        if !self.features.allow_measure {
            return Err(KetError::MeasureNotAllowed);
        }

        for qubit in qubits.iter() {
            self.match_pid(qubit.as_ref().borrow().deref())?;
            qubit.as_ref().borrow().assert_allocated()?;
            qubit.borrow_mut().set_measured();
        }

        if !self.features.valid_after_measure {
            for qubit in qubits.iter() {
                qubit.borrow_mut().set_deallocated();
            }
        }

        let future_index = self.metrics.future_count;
        self.metrics.future_count += 1;

        let future_value = Rc::new(RefCell::new(None));

        self.futures.push(Rc::clone(&future_value));

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Measure {
                qubits: qubits
                    .iter()
                    .map(|qubit| qubit.as_ref().borrow().index())
                    .collect(),
                output: future_index,
            })?;

        Ok(Future::new(future_index, self.pid, future_value))
    }

    pub fn ctrl_push(&mut self, qubits: &[&Qubit]) -> Result<()> {
        for ctrl_list in self.ctrl_stack.iter() {
            for qubit in qubits.iter() {
                qubit.assert_allocated()?;
                self.match_pid(*qubit)?;
                if ctrl_list.contains(&qubit.index()) {
                    return Err(KetError::ControlTwice);
                }
            }
        }

        self.ctrl_stack
            .push(qubits.iter().map(|qubit| qubit.index()).collect());

        Ok(())
    }

    pub fn ctrl_push_ref(&mut self, qubits: &[Rc<RefCell<Qubit>>]) -> Result<()> {
        for ctrl_list in self.ctrl_stack.iter() {
            for qubit in qubits {
                let qubit = qubit.as_ref().borrow();
                qubit.assert_allocated()?;
                self.match_pid(qubit.deref())?;
                if ctrl_list.contains(&qubit.index()) {
                    return Err(KetError::ControlTwice);
                }
            }
        }

        self.ctrl_stack.push(
            qubits
                .iter()
                .map(|qubit| qubit.deref().borrow().index())
                .collect(),
        );

        Ok(())
    }

    pub fn ctrl_pop(&mut self) -> Result<()> {
        match self.ctrl_stack.pop() {
            Some(_) => Ok(()),
            None => Err(KetError::NoCtrl),
        }
    }

    pub fn adj_begin(&mut self) -> Result<()> {
        self.blocks.get_mut(self.current_block).unwrap().adj_begin()
    }

    pub fn adj_end(&mut self) -> Result<()> {
        self.blocks.get_mut(self.current_block).unwrap().adj_end()
    }

    pub fn get_label(&mut self) -> Result<Label> {
        if !self.features.classical_control_flow {
            return Err(KetError::ControlFlowNotAllowed);
        }

        let index = self.metrics.block_count;
        self.metrics.block_count += 1;
        let mut new_block = CodeBlockHandler::default();
        new_block.use_rz_as_phase = self.features.use_rz_as_phase;
        self.blocks.push(new_block);
        Ok(Label::new(index, self.pid))
    }

    pub fn open_block(&mut self, label: &Label) -> Result<()> {
        self.match_pid(label)?;
        self.current_block = label.index();
        Ok(())
    }

    pub fn jump(&mut self, label: &Label) -> Result<()> {
        self.match_pid(label)?;
        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::End(EndInstruction::Jump {
                addr: label.index(),
            }))?;
        Ok(())
    }

    pub fn branch(&mut self, test: &Future, then: &Label, otherwise: &Label) -> Result<()> {
        self.match_pid(test)?;
        self.match_pid(then)?;
        self.match_pid(otherwise)?;

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::End(EndInstruction::Branch {
                test: test.index(),
                then: then.index(),
                otherwise: otherwise.index(),
            }))?;

        Ok(())
    }

    pub fn dump(&mut self, qubits: &[&Qubit]) -> Result<Dump> {
        if !self.features.allow_dump {
            return Err(KetError::DumpNotAllowed);
        }

        for qubit in qubits.iter() {
            self.match_pid(*qubit)?;
            qubit.assert_allocated()?;
        }

        let dump_index = self.metrics.dump_count;
        self.metrics.dump_count += 1;

        let dump_value = Rc::new(RefCell::new(None));
        self.dumps.push(Rc::clone(&dump_value));

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Dump {
                qubits: qubits.iter().map(|qubit| qubit.index()).collect(),
                output: dump_index,
            })?;

        if !self.features.continue_after_dump {
            self.prepare_for_execution()?
        }

        Ok(Dump::new(dump_value))
    }

    pub fn dump_ref(&mut self, qubits: &[Rc<RefCell<Qubit>>]) -> Result<Dump> {
        if !self.features.allow_dump {
            return Err(KetError::DumpNotAllowed);
        }

        for qubit in qubits {
            self.match_pid(qubit.as_ref().borrow().deref())?;
            qubit.deref().borrow().assert_allocated()?;
        }

        let dump_index = self.metrics.dump_count;
        self.metrics.dump_count += 1;

        let dump_value = Rc::new(RefCell::new(None));
        self.dumps.push(Rc::clone(&dump_value));

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::Dump {
                qubits: qubits
                    .iter()
                    .map(|qubit| qubit.deref().borrow().index())
                    .collect(),
                output: dump_index,
            })?;

        if !self.features.continue_after_dump {
            self.prepare_for_execution()?
        }

        Ok(Dump::new(dump_value))
    }

    pub fn add_int_op(&mut self, op: ClassicalOp, lhs: &Future, rhs: &Future) -> Result<Future> {
        if !self.features.classical_control_flow {
            return Err(KetError::ControlFlowNotAllowed);
        }

        self.match_pid(lhs)?;
        self.match_pid(rhs)?;

        let result_index = self.metrics.future_count;
        self.metrics.future_count += 1;

        let result_value = Rc::new(RefCell::new(None));

        self.futures.push(Rc::clone(&result_value));

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::IntOp {
                op,
                result: result_index,
                lhs: lhs.index(),
                rhs: rhs.index(),
            })?;

        Ok(Future::new(result_index, self.pid, result_value))
    }

    pub fn int_set(&mut self, dst: &Future, src: &Future) -> Result<()> {
        if !self.features.classical_control_flow {
            return Err(KetError::ControlFlowNotAllowed);
        }

        self.match_pid(dst)?;
        self.match_pid(src)?;

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::IntOp {
                op: ClassicalOp::Add,
                result: dst.index(),
                lhs: 0,
                rhs: src.index(),
            })?;

        Ok(())
    }

    pub fn int_new(&mut self, value: i64) -> Result<Future> {
        if !self.features.classical_control_flow {
            return Err(KetError::ControlFlowNotAllowed);
        }

        let index = self.metrics.future_count;
        self.metrics.future_count += 1;

        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .add_instruction(Instruction::IntSet {
                result: index,
                value,
            })?;

        let value = Rc::new(RefCell::new(None));
        self.futures.push(Rc::clone(&value));

        Ok(Future::new(index, self.pid, value))
    }

    pub fn prepare_for_execution(&mut self) -> Result<()> {
        if !self.metrics.ready {
            self.metrics.ready = true;

            self.blocks
                .get_mut(self.current_block)
                .unwrap()
                .add_instruction(Instruction::End(EndInstruction::Halt))?;
        }
        Ok(())
    }

    pub fn exec_time(&self) -> Option<f64> {
        self.exec_time
    }

    pub fn set_timeout(&mut self, timeout: u64) {
        self.metrics.timeout = Some(timeout);
    }

    pub fn metrics(&self) -> &Metrics {
        &self.metrics
    }

    pub fn blocks(&self) -> Vec<&CodeBlock> {
        self.blocks.iter().map(|handler| handler.block()).collect()
    }

    pub fn serialize_metrics(&mut self, data_type: DataType) -> &SerializedData {
        match data_type {
            DataType::JSON => {
                self.metrics_serialized = Some(SerializedData::JSON(
                    serde_json::to_string(&self.metrics).unwrap(),
                ))
            }
            DataType::BIN => {
                self.metrics_serialized = Some(SerializedData::BIN(
                    bincode::serialize(&self.metrics).unwrap(),
                ))
            }
        }

        self.metrics_serialized.as_ref().unwrap()
    }

    pub fn serialize_quantum_code(&mut self, data_type: DataType) -> &SerializedData {
        match data_type {
            DataType::JSON => {
                self.quantum_code_serialized = Some(SerializedData::JSON(
                    serde_json::to_string(&self.blocks()).unwrap(),
                ));
            }
            DataType::BIN => {
                self.quantum_code_serialized = Some(SerializedData::BIN(
                    bincode::serialize(&self.blocks()).unwrap(),
                ));
            }
        }
        self.quantum_code_serialized.as_ref().unwrap()
    }

    pub fn get_serialized_metrics(&self) -> Option<&SerializedData> {
        self.metrics_serialized.as_ref()
    }

    pub fn get_serialized_quantum_code(&self) -> Option<&SerializedData> {
        self.quantum_code_serialized.as_ref()
    }

    pub fn set_result(&mut self, mut result: ResultData) -> Result<()> {
        if (self.futures.len() != result.future.len()) | (self.dumps.len() != result.dump.len()) {
            Err(KetError::UnexpectedResultData)
        } else {
            for (index, value) in result.future.iter().enumerate() {
                *(self.futures.get(index).unwrap().borrow_mut()) = Some(*value);
            }

            for dump in self.dumps.iter_mut().rev() {
                *dump.borrow_mut() = result.dump.pop();
            }

            self.exec_time = Some(result.exec_time);

            Ok(())
        }
    }

    pub fn set_serialized_result(&mut self, result: &SerializedData) -> Result<()> {
        match result {
            SerializedData::JSON(result) => self.set_result(match serde_json::from_str(result) {
                Ok(result) => result,
                Err(_) => return Err(KetError::FailToParseResult),
            }),
            SerializedData::BIN(result) => self.set_result(match bincode::deserialize(result) {
                Ok(result) => result,
                Err(_) => return Err(KetError::FailToParseResult),
            }),
        }
    }

    pub fn pid(&self) -> usize {
        self.pid
    }
}
