//! # Quantum Process
//!
//! The `process` module provides the core functionality for representing and manipulating quantum codes.
//!
//! The `Process` struct serves as the main entry point for working with quantum codes.
//! It provides methods for constructing quantum programs, applying quantum gates and plugins,
//! performing measurements, controlling execution flow, managing serialized data, and retrieving metrics.
//!
//! Although accessing the `Process` directly can provide marginal performance improvements,
//! we recommend using the `gates` module for allocating, measuring, and applying gates to qubits.
//!
//! By using the `gates` module, you can leverage its higher-level abstractions and convenient methods
//! for working with gates. It encapsulates the necessary logic for qubit allocation, measurement, and gate application,
//!  making your code more readable and maintainable.
//!
//! # Examples
//! The following example demonstrates the implementation of
//! Grover's algorithm without the `gates` module:
//!  
//! ```rust
//! use ket::{Process, QuantumGate, Result};
//!
//! fn main() -> Result<()> {
//!     let n = 4;
//!
//!     let mut p = Process::new(1);
//!
//!     let mut qubits = (0..n)
//!         .map(|_| p.allocate_qubit(false))
//!         .collect::<Vec<_>>()
//!         .into_iter()
//!         .collect::<Result<Vec<_>>>()?;
//!
//!     let head = qubits.first().unwrap();
//!     let tail: Vec<_> = qubits.iter().skip(1).collect();
//!
//!     for qubit in &qubits {
//!         p.apply_gate(QuantumGate::Hadamard, qubit)?;
//!     }
//!
//!     let steps = (std::f64::consts::PI / 4.0 * f64::sqrt((1 << n) as f64)) as i32;
//!
//!     for _ in 0..steps {
//!         p.ctrl_push(&tail)?;
//!         p.apply_gate(QuantumGate::PauliZ, head)?;
//!         p.ctrl_pop()?;
//!
//!         for qubit in &qubits {
//!             p.apply_gate(QuantumGate::Hadamard, qubit)?;
//!             p.apply_gate(QuantumGate::PauliX, qubit)?;
//!         }
//!
//!         p.ctrl_push(&tail)?;
//!         p.apply_gate(QuantumGate::PauliZ, head)?;
//!         p.ctrl_pop()?;
//!
//!         for qubit in &qubits {
//!             p.apply_gate(QuantumGate::PauliX, qubit)?;
//!             p.apply_gate(QuantumGate::Hadamard, qubit)?;
//!         }
//!     }
//!
//!     let _ = p.measure(&mut qubits.iter_mut().collect::<Vec<_>>());
//!
//!     p.prepare_for_execution()?;
//!     println!("{:#?}", p.blocks());
//!
//!     Ok(())
//! }
//! ```

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

/// Set of features for a `Process` object.
#[derive(Clone, Debug)]
pub struct Features {
    /// Indicates whether using dirty qubits are allowed.
    pub allow_dirty_qubits: bool,
    /// Indicates whether the free qubit operation is allowed.
    pub allow_free_qubits: bool,
    /// Indicates whether the qubit remains valid after measurement.
    pub valid_after_measure: bool,
    /// Set of plugin names allowed with the features.
    pub plugins: BTreeSet<String>,
    /// Indicates whether classical control flow is allowed.
    pub classical_control_flow: bool,
    /// Indicates whether dump quantum state is allowed.
    pub allow_dump: bool,
    /// Indicates whether measurements are allowed.
    pub allow_measure: bool,
    /// Indicates whether execution continues after dump the quantum state.
    pub continue_after_dump: bool,
    /// Indicates whether decomposition is enabled.
    pub decompose: bool,
    /// Indicates whether RZ gates are used for phase rotations.
    pub use_rz_as_phase: bool,
}

impl Features {
    /// Creates a new instance of `Features` with the specified values for each field.
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

    /// Creates a new instance of `Features` with all fields set to `true`,
    /// except for `decompose` and `use_rz_as_phase`, which are set to `false`.
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

    /// Creates a new instance of `Features` with all fields set to `false`,
    /// except for `allow_measure`, which is set to `true`.
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

    /// Registers a plugin by adding its name to the set of plugins.
    pub fn register_plugin(&mut self, plugin: &str) {
        self.plugins.insert(plugin.to_string());
    }
}

/// Represents a quantum process.
#[derive(Debug)]
pub struct Process {
    /// Process ID.
    pid: usize,

    /// Metrics associated with the process.
    metrics: Metrics,

    /// Number of qubits.
    num_qubit: usize,

    /// List of code block handlers.
    blocks: Vec<CodeBlockHandler>,

    /// Index of the current code block.
    current_block: usize,

    /// Control stack for managing nested control flow.
    ctrl_stack: Vec<Vec<usize>>,

    /// List of futures associated with the process.
    futures: Vec<Rc<RefCell<Option<i64>>>>,

    /// List of dump data associated with the process.
    dumps: Vec<Rc<RefCell<Option<DumpData>>>>,

    /// Serialized quantum code data.
    quantum_code_serialized: Option<SerializedData>,

    /// Serialized metrics data.
    metrics_serialized: Option<SerializedData>,

    /// Execution time of the process.
    exec_time: Option<f64>,

    /// Features associated with the process.
    features: Features,
}

impl Process {
    /// Creates a new `Process` with the specified process ID, using default values for other fields.
    ///
    /// # Arguments
    ///
    /// * `pid` - The process ID.
    ///
    /// # Returns
    ///
    /// A new `Process` instance.
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

    /// Creates a new shared pointer to a `Process` with a randomly generated process ID and default values for other fields.
    ///
    /// # Returns
    ///
    /// A shared pointer to a new `Process` instance.
    pub fn new_ptr() -> Rc<RefCell<Self>> {
        Rc::new(RefCell::new(Self::new(rand::thread_rng().gen())))
    }

    fn match_pid(&self, obj: &impl Pid) -> Result<()> {
        if obj.pid() != self.pid {
            Err(KetError::PidMismatch)
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
            Err(KetError::TargetInControl)
        } else {
            Ok(())
        }
    }

    /// Sets the features of the current process to the specified features.
    ///
    /// # Arguments
    ///
    /// * `features` - The features to be set.
    ///
    pub fn set_features(&mut self, features: Features) {
        self.blocks
            .get_mut(self.current_block)
            .unwrap()
            .use_rz_as_phase = features.use_rz_as_phase;
        self.features = features;
    }

    /// Allocates a qubit in the current process.
    ///
    /// # Arguments
    ///
    /// * `dirty` - A flag indicating whether the allocated qubit can be in a dirty state.
    ///
    /// # Returns
    ///
    /// A result containing the allocated `Qubit` if successful, or an error if allocation fails.
    /// Possible error variants include `KetError::DirtyNotAllowed` if dirty qubits are not allowed,
    /// and other errors related to instruction addition or qubit management.
    ///
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

    /// Frees a previously allocated qubit in the current process.
    ///
    /// # Arguments
    ///
    /// * `qubit` - A mutable reference to the qubit to be freed.
    /// * `dirty` - A flag indicating whether the qubit should be freed in a dirty state.
    ///
    /// # Returns
    ///
    /// A result indicating the success or failure of the operation.
    /// Possible error variants include `KetError::DirtyNotAllowed` if dirty qubits are not allowed,
    /// `KetError::FreeNotAllowed` if freeing qubits is not allowed,
    /// and other errors related to instruction addition or qubit management.
    ///
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

    /// Applies a quantum gate to a target qubit in the current process.
    ///
    /// # Arguments
    ///
    /// * `gate` - The quantum gate to be applied.
    /// * `target` - A reference to the target qubit.
    ///
    /// # Returns
    ///
    /// A result indicating the success or failure of the operation.
    /// Possible error variants include `KetError::QubitNotAllocated` if the target qubit is not allocated,
    /// `KetError::PidMismatch` if the target qubit belongs to a different process,
    /// `KetError::TargetInControl` if the target qubit is also a control qubit,
    /// and other errors related to instruction addition or gate decomposition.
    ///
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

    /// Applies a plugin operation to the specified target qubits in the current process.
    ///
    /// # Arguments
    ///
    /// * `name` - The name of the plugin to be applied.
    /// * `target` - An array of references to the target qubits.
    /// * `args` - The arguments for the plugin operation.
    ///
    /// # Returns
    ///
    /// A result indicating the success or failure of the operation.
    /// Possible error variants include `KetError::PluginNotRegistered` if the plugin is not registered,
    /// `KetError::PluginOnCtrl` if a plugin operation is attempted while control qubits are active,
    /// `KetError::PidMismatch` if any of the target qubits belong to a different process,
    /// and other errors related to instruction addition or plugin execution.
    ///
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

    pub(crate) fn apply_plugin_ref(
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

    /// Measures the specified qubits in the current process.
    ///
    /// # Arguments
    ///
    /// * `qubits` - An array of mutable references to the qubits to be measured.
    ///
    /// # Returns
    ///
    /// A result containing a `Future` representing the measurement result if successful, or an error if measurement fails.
    /// Possible error variants include `KetError::MeasureNotAllowed` if measuring qubits is not allowed,
    /// `KetError::PidMismatch` if any of the qubits belong to a different process,
    /// `KetError::DeallocatedQubit` if a qubit is not allocated,
    /// and other errors related to instruction addition or future creation.
    ///
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

    pub(crate) fn measure_ref(&mut self, qubits: &mut [Rc<RefCell<Qubit>>]) -> Result<Future> {
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

    /// Pushes control qubits onto the control stack.
    ///
    /// # Arguments
    ///
    /// * `qubits` - An array of references to the control qubits.
    ///
    /// # Returns
    ///
    /// A result indicating success or an error if the control configuration is invalid.
    /// Possible error variants include `KetError::DeallocatedQubit` if any of the control qubits are not allocated,
    /// `KetError::PidMismatch` if any of the control qubits belong to a different process,
    /// and `KetError::ControlTwice` if a control qubit is included in multiple control configurations.
    ///
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

    pub(crate) fn ctrl_push_ref(&mut self, qubits: &[Rc<RefCell<Qubit>>]) -> Result<()> {
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

    /// Pops the top control qubit configuration from the control stack.
    ///
    /// # Returns
    ///
    /// A result indicating success or an error if the control stack is empty (`KetError::NoCtrl`).
    ///
    pub fn ctrl_pop(&mut self) -> Result<()> {
        match self.ctrl_stack.pop() {
            Some(_) => Ok(()),
            None => Err(KetError::NoCtrl),
        }
    }

    /// Begins an adjoint block, where gates are inverted upon insertion.
    ///
    /// # Returns
    ///
    /// A result indicating success or an error if there are issues with the current block.
    /// Possible error variants include `KetError::TerminatedBlock` if the current block ended.
    ///
    pub fn adj_begin(&mut self) -> Result<()> {
        self.blocks.get_mut(self.current_block).unwrap().adj_begin()
    }

    /// Ends the adjoint block, reverting to normal gate insertion.
    ///
    /// # Returns
    ///
    /// A result indicating success or an error if there are issues with the current block.
    /// Possible error variants include `KetError::TerminatedBlock` if the current block ended.
    ///
    pub fn adj_end(&mut self) -> Result<()> {
        self.blocks.get_mut(self.current_block).unwrap().adj_end()
    }

    /// Generates a new unique label for branching and control flow operations.
    ///
    /// # Returns
    ///
    /// A result containing a new label if classical control flow is enabled by the features,
    /// or an error (`KetError::ControlFlowNotAllowed`) if control flow is not allowed.
    ///
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

    /// Opens a block specified by the given label for control flow operations.
    ///
    /// # Arguments
    ///
    /// * `label` - The label representing the block to be opened.
    ///
    /// # Returns
    ///
    /// A result indicating success or an error if there are issues with the label.
    /// Possible error variants include `KetError::PidMismatch` if the label belongs to a different process.
    ///
    pub fn open_block(&mut self, label: &Label) -> Result<()> {
        self.match_pid(label)?;
        self.current_block = label.index();
        Ok(())
    }

    /// Adds a jump instruction to the specified label in the current block.
    ///
    /// # Arguments
    ///
    /// * `label` - The label representing the target block to jump to.
    ///
    /// # Returns
    ///
    /// A result indicating success or an error if there are issues with the label or the current block.
    /// Possible error variants include `KetError::PidMismatch` if the label belongs to a different process.
    ///
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

    /// Adds a branch instruction to the current block, branching based on the given future's value.
    ///
    /// # Arguments
    ///
    /// * `test` - The future representing the condition to test for branching.
    /// * `then` - The label representing the target block to jump to if the condition is true.
    /// * `otherwise` - The label representing the target block to jump to if the condition is false.
    ///
    /// # Returns
    ///
    /// A result indicating success or an error if there are issues with the futures or the labels.
    /// Possible error variants include `KetError::PidMismatch` if any of the labels or the future belongs to a different process.
    ///
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

    /// Dumps the state of the specified qubits.
    ///
    /// # Arguments
    ///
    /// * `qubits` - The mutable references to the qubits to be dumped.
    ///
    /// # Returns
    ///
    /// A result containing a new dump object if dumping is allowed by the features,
    /// or an error (`KetError::DumpNotAllowed`) if dumping is not allowed.
    ///
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

    pub(crate) fn dump_ref(&mut self, qubits: &[Rc<RefCell<Qubit>>]) -> Result<Dump> {
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

    /// Adds an integer operation to the current block.
    ///
    /// # Arguments
    ///
    /// * `op` - The type of integer operation to perform.
    /// * `lhs` - The reference to the left-hand side future.
    /// * `rhs` - The reference to the right-hand side future.
    ///
    /// # Returns
    ///
    /// A result containing a new future if the classical control flow feature is enabled,
    /// or an error (`KetError::ControlFlowNotAllowed`) if the feature is not enabled.
    ///
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

    /// Sets the value of a future using another future as the source.
    ///
    /// # Arguments
    ///
    /// * `dst` - The reference to the destination future.
    /// * `src` - The reference to the source future.
    ///
    /// # Returns
    ///
    /// A result indicating success if the classical control flow feature is enabled,
    /// or an error (`KetError::ControlFlowNotAllowed`) if the feature is not enabled.
    ///
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

    /// Creates a new future with the specified integer value.
    ///
    /// # Arguments
    ///
    /// * `value` - The integer value for the future.
    ///
    /// # Returns
    ///
    /// A result containing a new future if the classical control flow feature is enabled,
    /// or an error (`KetError::ControlFlowNotAllowed`) if the feature is not enabled.
    ///
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

    /// Returns the execution time of the quantum code if it has been executed.
    ///
    /// # Returns
    ///
    /// An optional `f64` value representing the execution time in seconds,
    /// or `None` if the code has not been executed.
    ///
    pub fn exec_time(&self) -> Option<f64> {
        self.exec_time
    }

    /// Sets the timeout value for the quantum code execution.
    ///
    /// # Arguments
    ///
    /// * `timeout` - The timeout value in milliseconds.
    ///
    pub fn set_timeout(&mut self, timeout: u64) {
        self.metrics.timeout = Some(timeout);
    }

    /// Returns a reference to the metrics of the quantum code.
    ///
    /// # Returns
    ///
    /// A reference to the `Metrics` struct containing various metrics of the quantum code.
    ///
    pub fn metrics(&self) -> &Metrics {
        &self.metrics
    }

    /// Returns a vector of references to the code blocks in the quantum code.
    ///
    /// # Returns
    ///
    /// A vector containing references to the `CodeBlock` instances in the quantum code.
    ///
    pub fn blocks(&self) -> Vec<&CodeBlock> {
        self.blocks.iter().map(|handler| handler.block()).collect()
    }

    /// Serializes the metrics of the quantum code into the specified data type.
    ///
    /// # Arguments
    ///
    /// * `data_type` - The data type to serialize into (`DataType::Json` or `DataType::Bin`).
    ///
    /// # Returns
    ///
    /// A reference to the serialized metrics data.
    ///
    pub fn serialize_metrics(&mut self, data_type: DataType) -> &SerializedData {
        match data_type {
            DataType::Json => {
                self.metrics_serialized = Some(SerializedData::Json(
                    serde_json::to_string(&self.metrics).unwrap(),
                ));
            }
            DataType::Bin => {
                self.metrics_serialized = Some(SerializedData::Bin(
                    bincode::serialize(&self.metrics).unwrap(),
                ));
            }
        }

        self.metrics_serialized.as_ref().unwrap()
    }

    /// Serializes the quantum code into the specified data type.
    ///
    /// # Arguments
    ///
    /// * `data_type` - The data type to serialize into (`DataType::Json` or `DataType::Bin`).
    ///
    /// # Returns
    ///
    /// A reference to the serialized quantum code data.
    ///
    pub fn serialize_quantum_code(&mut self, data_type: DataType) -> &SerializedData {
        match data_type {
            DataType::Json => {
                self.quantum_code_serialized = Some(SerializedData::Json(
                    serde_json::to_string(&self.blocks()).unwrap(),
                ));
            }
            DataType::Bin => {
                self.quantum_code_serialized = Some(SerializedData::Bin(
                    bincode::serialize(&self.blocks()).unwrap(),
                ));
            }
        }

        self.quantum_code_serialized.as_ref().unwrap()
    }

    /// Returns a reference to the serialized metrics data of the quantum code.
    ///
    /// # Returns
    ///
    /// An optional reference to the serialized metrics data (`SerializedData`), or `None` if it is not available.
    ///
    pub fn get_serialized_metrics(&self) -> Option<&SerializedData> {
        self.metrics_serialized.as_ref()
    }

    /// Returns a reference to the serialized quantum code data.
    ///
    /// # Returns
    ///
    /// An optional reference to the serialized quantum code data (`SerializedData`), or `None` if it is not available.
    ///
    pub fn get_serialized_quantum_code(&self) -> Option<&SerializedData> {
        self.quantum_code_serialized.as_ref()
    }

    /// Sets the result of the quantum code execution.
    ///
    /// # Arguments
    ///
    /// * `result` - The result data containing the future values, dump values, and execution time.
    ///
    /// # Returns
    ///
    /// A `Result` indicating success (`Ok`) or an error (`Err`) if the result data is unexpected.
    ///
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

    /// Sets the result of the quantum code execution from a serialized result data.
    ///
    /// # Arguments
    ///
    /// * `result` - The serialized result data (`SerializedData`) to set as the result.
    ///
    /// # Returns
    ///
    /// A `Result` indicating success (`Ok`) or an error (`Err`) if the result data fails to parse.
    ///
    pub fn set_serialized_result(&mut self, result: &SerializedData) -> Result<()> {
        match result {
            SerializedData::Json(result) => self.set_result(match serde_json::from_str(result) {
                Ok(result) => result,
                Err(_) => return Err(KetError::FailToParseResult),
            }),
            SerializedData::Bin(result) => self.set_result(match bincode::deserialize(result) {
                Ok(result) => result,
                Err(_) => return Err(KetError::FailToParseResult),
            }),
        }
    }

    /// Returns the process ID (PID) associated with the quantum code.
    ///
    /// # Returns
    ///
    /// The process ID (PID) as a `usize` value.
    ///
    pub fn pid(&self) -> usize {
        self.pid
    }
}
