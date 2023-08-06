#pragma once
#include <libket.h>

#include <complex>
#include <memory>
#include <string>
#include <vector>

namespace ket {

class LibketException : public std::exception {
 public:
  LibketException(ket_error_code_t code) {
    _code = code;
    size_t size;
    const char* msg = (const char*)ket_error_message(code, &size);
    description.append(msg, size);
  }

  ~LibketException() noexcept {}

  int code() { return _code; }

  const char* what() const noexcept { return description.c_str(); }

 private:
  ket_error_code_t _code;
  std::string description;
};

#define ket_throw(code) \
  if (code != KET_SUCCESS) throw LibketException(code)

class Process;

class Features {
  friend class Process;

 public:
  Features(bool allow_dirty_qubits, bool allow_free_qubits,
           bool valid_after_measure, bool classical_control_flow,
           bool allow_dump, bool allow_measure, bool continue_after_dump,
           bool decompose, bool use_rz_as_phase) {
    ket_features_t features;
    ket_throw(ket_features_new(allow_dirty_qubits, allow_free_qubits,
                               valid_after_measure, classical_control_flow,
                               allow_dump, allow_measure, continue_after_dump,
                               decompose, use_rz_as_phase, &features));
    self = std::shared_ptr<void>(
        features, [](void* features) { ket_features_delete(features); });
  }

  static Features none() { return Features{ket_features_none}; };

  static Features all() { return Features{ket_features_all}; }

  void register_plugin(std::string name) {
    ket_throw(ket_features_register_plugin(self.get(), name.c_str()));
  }

 private:
  Features(ket_error_code_t (*init)(ket_features_t*)) {
    ket_features_t features;

    ket_throw(init(&features));

    self = std::shared_ptr<void>(
        features, [](void* features) { ket_features_delete(features); });
  }

  std::shared_ptr<void> self;
};

class Qubit {
  friend class Process;

 public:
  size_t pid() {
    size_t pid;
    ket_throw(ket_qubit_pid(self.get(), &pid));
    return pid;
  }

  bool allocated() {
    bool allocated;
    ket_throw(ket_qubit_allocated(self.get(), &allocated));
    return allocated;
  }

  bool measured() {
    bool measured;
    ket_throw(ket_qubit_measured(self.get(), &measured));
    return measured;
  }

 private:
  Qubit(ket_qubit_t qubit)
      : self{qubit, [](ket_qubit_t qubit) { ket_qubit_delete(qubit); }} {}

  std::shared_ptr<void> self;
};

class Future {
  friend class Process;

 public:
  int64_t value() {
    int64_t value;
    ket_future_value(self.get(), &value);
    return value;
  }

  size_t index() {
    size_t index;
    ket_future_index(self.get(), &index);
    return index;
  }

  size_t pid() {
    size_t pid;
    ket_future_pid(self.get(), &pid);
    return pid;
  }

  bool available() {
    bool available;
    ket_future_available(self.get(), &available);
    return available;
  }

 private:
  Future(ket_future_t future)
      : self{std::shared_ptr<void>{
            future, [](ket_future_t future) { ket_future_delete(future); }}} {}

  std::shared_ptr<void> self;
};

class Dump {
  friend class Process;

 public:
  std::vector<std::vector<uint64_t>> states() {
    size_t state_size;
    ket_throw(ket_dump_states_size(self.get(), &state_size));
    std::vector<std::vector<uint64_t>> states;
    for (size_t index = 0; index < state_size; index++) {
      size_t size;
      uint64_t* state;
      ket_throw(ket_dump_state(self.get(), index, &state, &size));
      states.push_back(std::vector<uint64_t>(state, state + size));
    }
    return states;
  }

  std::vector<std::complex<double>> amplitudes() {
    std::vector<std::complex<double>> result;
    double *real, *imag;
    size_t size;

    ket_throw(ket_dump_amplitudes_real(self.get(), &real, &size));
    ket_throw(ket_dump_amplitudes_imag(self.get(), &imag, &size));

    for (size_t i = 0; i < size; i++) {
      result.push_back(std::complex<double>(real[i], imag[i]));
    }

    return result;
  }

  std::vector<double> probabilities() {
    double* prob;
    size_t size;

    ket_throw(ket_dump_probabilities(self.get(), &prob, &size));

    return std::vector<double>(prob, prob + size);
  }

  std::vector<uint32_t> count() {
    uint32_t* cnt;
    size_t size;

    ket_throw(ket_dump_count(self.get(), &cnt, &size));

    return std::vector<uint32_t>(cnt, cnt + size);
  }

  uint64_t total() {
    uint64_t total;
    ket_throw(ket_dump_total(self.get(), &total));
    return total;
  }

  int32_t type() {
    int32_t dump_type;
    ket_throw(ket_dump_type(self.get(), &dump_type));
    return dump_type;
  }

  bool available() {
    bool available;
    ket_throw(ket_dump_available(self.get(), &available));
    return available;
  }

 private:
  Dump(ket_dump_t dump)
      : self{std::shared_ptr<void>{
            dump, [](ket_dump_t dump) { ket_dump_delete(dump); }}} {}

  std::shared_ptr<void> self;
};

class Label {
  friend class Process;

 public:
  size_t index() {
    size_t index;
    ket_label_index(self.get(), &index);
    return index;
  }

  size_t pid() {
    size_t pid;
    ket_label_pid(self.get(), &pid);
    return pid;
  }

 private:
  Label(ket_label_t label)
      : self{std::shared_ptr<void>{
            label, [](ket_label_t label) { ket_label_delete(label); }}} {}

  std::shared_ptr<void> self;
};

class Process {
 public:
  Process(size_t pid) {
    ket_process_t process;
    ket_throw(ket_process_new(pid, &process));
    self = std::shared_ptr<void>{
        process, [](ket_process_t process) { ket_process_delete(process); }};
  }

  void set_features(const Features& features) {
    ket_throw(ket_process_set_features(self.get(), features.self.get()));
  }

  Qubit allocate_qubit(bool dirty = false) {
    ket_qubit_t qubit;
    ket_throw(ket_process_allocate_qubit(self.get(), dirty, &qubit));
    return Qubit(qubit);
  }

  void free_qubit(Qubit& qubit, bool dirty = false) {
    ket_throw(ket_process_free_qubit(self.get(), qubit.self.get(), dirty));
  }

  void apply_gate(int32_t gate, double param, Qubit target) {
    ket_throw(
        ket_process_apply_gate(self.get(), gate, param, target.self.get()));
  }

  void apply_plugin(const std::string& name, const std::string args,
                    const std::vector<Qubit>& qubits) {
    ket_throw(ket_process_apply_plugin(self.get(), name.c_str(), args.c_str(),
                                       to_vec_ptr(qubits).data(),
                                       qubits.size()));
  }

  Future measure(const std::vector<Qubit>& qubits) {
    ket_future_t future;
    ket_throw(ket_process_measure(self.get(), to_vec_ptr(qubits).data(),
                                  qubits.size(), &future));
    return Future(future);
  }

  template <class F>
  void ctrl(const std::vector<Qubit>& qubits, F func) {
    ket_throw(ket_process_ctrl_push(self.get(), to_vec_ptr(qubits).data(),
                                    qubits.size()));
    func();
    ket_throw(ket_process_ctrl_pop(self.get()));
  }

  template <class F>
  void adj(F func) {
    ket_throw(ket_process_adj_begin(self.get()));
    func();
    ket_throw(ket_process_adj_end(self.get()));
  }

  Label get_label() {
    ket_label_t label;
    ket_throw(ket_process_get_label(self.get(), &label));
    return Label(label);
  }

  void open_block(const Label& label) {
    ket_throw(ket_process_open_block(self.get(), label.self.get()));
  }

  void jump(const Label& label) {
    ket_throw(ket_process_jump(self.get(), label.self.get()));
  }

  void branch(const Future& test, const Label& then, const Label& otherwise) {
    ket_throw(ket_process_branch(self.get(), test.self.get(), then.self.get(),
                                 otherwise.self.get()));
  }

  Dump dump(const std::vector<Qubit>& qubits) {
    ket_dump_t dump;
    ket_throw(ket_process_dump(self.get(), to_vec_ptr(qubits).data(),
                               qubits.size(), &dump));
    return Dump(dump);
  }

  Future add_int_op(int32_t op, const Future& lhs, const Future& rhs) {
    ket_future_t result;
    ket_throw(ket_process_add_int_op(self.get(), op, lhs.self.get(),
                                     rhs.self.get(), &result));
    return Future(result);
  }

  Future int_new(int64_t value) {
    ket_future_t result;
    ket_throw(ket_process_int_new(self.get(), value, &result));
    return Future(result);
  }

  void int_set(const Future& dst, const Future& src) {
    ket_throw(ket_process_int_set(self.get(), dst.self.get(), src.self.get()));
  }

  void prepare_for_execution() {
    ket_throw(ket_process_prepare_for_execution(self.get()));
  }

  double exec_time() {
    double time;
    ket_throw(ket_process_exec_time(self.get(), &time));
    return time;
  }

  void set_timeout(uint64_t timeout) {
    ket_throw(ket_process_set_timeout(self.get(), timeout));
  }

  void serialize_metrics(int32_t data_type) {
    ket_throw(ket_process_serialize_metrics(self.get(), data_type));
  }

  void serialize_quantum_code(int32_t data_type) {
    ket_throw(ket_process_serialize_quantum_code(self.get(), data_type));
  }

  std::pair<std::vector<uint8_t>, int32_t> get_serialized_metrics() {
    uint8_t* data;
    size_t size;
    int32_t data_type;
    ket_throw(ket_process_get_serialized_metrics(self.get(), &data, &size,
                                                 &data_type));

    return std::make_pair(std::vector<uint8_t>(data, data + size), data_type);
  }

  std::pair<std::vector<uint8_t>, int32_t> get_serialized_quantum_code() {
    uint8_t* data;
    size_t size;
    int32_t data_type;
    ket_throw(ket_process_get_serialized_quantum_code(self.get(), &data, &size,
                                                      &data_type));

    return std::make_pair(std::vector<uint8_t>(data, data + size), data_type);
  }

  void set_serialized_result(std::vector<uint8_t> result, int32_t data_type) {
    ket_throw(ket_process_set_serialized_result(self.get(), result.data(),
                                                result.size(), data_type));
  }

  ket_process_t c_process() { return self.get(); }

 private:
  static std::vector<ket_qubit_t> to_vec_ptr(const std::vector<Qubit>& qubits) {
    std::vector<ket_qubit_t> qubits_ptr;
    for (auto& qubit : qubits) {
      qubits_ptr.push_back(qubit.self.get());
    }
    return qubits_ptr;
  }

  std::shared_ptr<void> self;
};
};  // namespace ket