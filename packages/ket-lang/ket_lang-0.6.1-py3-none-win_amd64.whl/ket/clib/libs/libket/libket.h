#pragma once
#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef void *ket_process_t;
typedef void *ket_qubit_t;
typedef void *ket_future_t;
typedef void *ket_dump_t;
typedef void *ket_label_t;
typedef void *ket_features_t;
typedef void *ket_dump_states_t;
typedef int32_t ket_error_code_t;

#define KET_PAULI_X 0
#define KET_PAULI_Y 1
#define KET_PAULI_Z 2
#define KET_HADAMARD 3
#define KET_PHASE 4
#define KET_RX 5
#define KET_RY 6
#define KET_RZ 7

#define KET_EQ 0
#define KET_NEQ 1
#define KET_GT 2
#define KET_GEQ 3
#define KET_LT 4
#define KET_LEQ 5
#define KET_ADD 6
#define KET_SUB 7
#define KET_MUL 8
#define KET_MOD 9
#define KET_DIV 10
#define KET_SLL 11
#define KET_SRL 12
#define KET_AND 13
#define KET_OR 14
#define KET_XOR 15

#define KET_SUCCESS 0
#define KET_CONTROL_TWICE 1
#define KET_DATA_NOT_AVAILABLE 2
#define KET_DEALLOCATED_QUBIT 3
#define KET_FAIL_TO_PARSE_RESULT 4
#define KET_NO_ADJ 5
#define KET_NO_CTRL 6
#define KET_NON_GATE_INSTRUCTION 7
#define KET_NOT_BIN 8
#define KET_NOT_JSON 9
#define KET_NOT_UNITARY 10
#define KET_PLUGIN_ON_CTRL 11
#define KET_TARGET_ON_CONTROL 12
#define KET_TERMINATED_BLOCK 13
#define KET_UNDEFINED_CLASSICAL_OP 14
#define KET_UNDEFINED_DATA_TYPE 15
#define KET_UNDEFINED_GATE 16
#define KET_UNEXPECTED_RESULT_DATA 17
#define KET_UNMATCHED_PID 18
#define KET_DIRTY_NOT_ALLOWED 19
#define KET_DUMP_NOT_ALLOWED 20
#define KET_MEASURE_NOT_ALLOWED 21
#define KET_FREE_NOT_ALLOWED 22
#define KET_PLUGIN_NOT_REGISTERED 23
#define KET_CONTROL_FLOW_NOT_ALLOWED 24
#define KET_UNDEFINED_ERROR 25

#define KET_JSON 0
#define KET_BIN 1

#define KET_DUMP_VECTOR 0
#define KET_DUMP_PROBABILITY 1
#define KET_DUMP_SHOTS 2

const uint8_t *ket_error_message(ket_error_code_t error_code, size_t *size);

ket_error_code_t ket_process_new(size_t pid, ket_process_t *process);

ket_error_code_t ket_process_delete(ket_process_t process);

ket_error_code_t ket_process_set_features(ket_process_t process,
                                          ket_features_t features);

ket_error_code_t ket_process_allocate_qubit(ket_process_t process, bool dirty,
                                            ket_qubit_t *qubit);

ket_error_code_t ket_process_free_qubit(ket_process_t process,
                                        ket_qubit_t qubit, bool dirty);

ket_error_code_t ket_process_apply_gate(ket_process_t process, int32_t gate,
                                        double param, ket_qubit_t target);

ket_error_code_t ket_process_apply_plugin(ket_process_t process,
                                          const char *name, const char *args,
                                          ket_qubit_t *target,
                                          size_t target_size);

ket_error_code_t ket_process_measure(ket_process_t process, ket_qubit_t *qubits,
                                     size_t qubits_size, ket_future_t *future);

ket_error_code_t ket_process_ctrl_push(ket_process_t process,
                                       ket_qubit_t *qubits, size_t qubits_size);

ket_error_code_t ket_process_ctrl_pop(ket_process_t process);

ket_error_code_t ket_process_adj_begin(ket_process_t process);

ket_error_code_t ket_process_adj_end(ket_process_t process);

ket_error_code_t ket_process_get_label(ket_process_t process,
                                       ket_label_t *label);

ket_error_code_t ket_process_open_block(ket_process_t process,
                                        ket_label_t label);

ket_error_code_t ket_process_jump(ket_process_t process, ket_label_t label);

ket_error_code_t ket_process_branch(ket_process_t process, ket_future_t test,
                                    ket_label_t then, ket_label_t otherwise);

ket_error_code_t ket_process_dump(ket_process_t process, ket_qubit_t *qubits,
                                  size_t qubits_size, ket_dump_t *dump);

ket_error_code_t ket_process_add_int_op(ket_process_t process, int32_t op,
                                        ket_future_t lhs, ket_future_t rhs,
                                        ket_future_t *result);

ket_error_code_t ket_process_int_new(ket_process_t process, int64_t value,
                                     ket_future_t *future);

ket_error_code_t ket_process_int_set(ket_process_t process, ket_future_t dst,
                                     ket_future_t src);

ket_error_code_t ket_process_prepare_for_execution(ket_process_t process);

ket_error_code_t ket_process_exec_time(ket_process_t process, double *time);

ket_error_code_t ket_process_set_timeout(ket_process_t process,
                                         uint64_t timeout);

ket_error_code_t ket_process_serialize_metrics(ket_process_t process,
                                               int32_t data_type);

ket_error_code_t ket_process_serialize_quantum_code(ket_process_t process,
                                                    int32_t data_type);

ket_error_code_t ket_process_get_serialized_metrics(ket_process_t process,
                                                    uint8_t **data,
                                                    size_t *size,
                                                    int32_t *data_type);

ket_error_code_t ket_process_get_serialized_quantum_code(ket_process_t process,
                                                         uint8_t **data,
                                                         size_t *size,
                                                         int32_t *data_type);

ket_error_code_t ket_process_set_serialized_result(ket_process_t process,
                                                   uint8_t *result,
                                                   size_t result_size,
                                                   int32_t data_type);

ket_error_code_t ket_features_new(bool allow_dirty_qubits,
                                  bool allow_free_qubits,
                                  bool valid_after_measure,
                                  bool classical_control_flow, bool allow_dump,
                                  bool allow_measure, bool continue_after_dump,
                                  bool decompose, bool use_rz_as_phase,
                                  ket_features_t *features);

ket_error_code_t ket_features_delete(ket_features_t features);

ket_error_code_t ket_features_all(ket_features_t *features);

ket_error_code_t ket_features_none(ket_features_t *features);

ket_error_code_t ket_features_register_plugin(ket_features_t features,
                                              const char *name);

ket_error_code_t ket_qubit_delete(ket_qubit_t qubit);

ket_error_code_t ket_qubit_index(ket_qubit_t qubit, size_t *index);

ket_error_code_t ket_qubit_pid(ket_qubit_t qubit, size_t *pid);

ket_error_code_t ket_qubit_allocated(ket_qubit_t qubit, bool *allocated);

ket_error_code_t ket_qubit_measured(ket_qubit_t qubit, bool *measured);

ket_error_code_t ket_dump_delete(ket_dump_t dump);

ket_error_code_t ket_dump_states_size(ket_dump_t dump, size_t *size);

ket_error_code_t ket_dump_state(ket_dump_t dump, size_t index, uint64_t **state,
                                size_t *size);

ket_error_code_t ket_dump_amplitudes_real(ket_dump_t dump, double **amp,
                                          size_t *size);

ket_error_code_t ket_dump_amplitudes_imag(ket_dump_t dump, double **amp,
                                          size_t *size);

ket_error_code_t ket_dump_probabilities(ket_dump_t dump, double **prob,
                                        size_t *size);

ket_error_code_t ket_dump_count(ket_dump_t dump, uint32_t **amp, size_t *size);

ket_error_code_t ket_dump_total(ket_dump_t dump, uint64_t *total);

ket_error_code_t ket_dump_type(ket_dump_t dump, int32_t *dump_type);

ket_error_code_t ket_dump_available(ket_dump_t dump, bool *available);

ket_error_code_t ket_future_delete(ket_future_t future);

ket_error_code_t ket_future_value(ket_future_t future, int64_t *value);

ket_error_code_t ket_future_index(ket_future_t future, size_t *index);

ket_error_code_t ket_future_pid(ket_future_t future, size_t *pid);

ket_error_code_t ket_future_available(ket_dump_t dump, bool *available);

ket_error_code_t ket_label_delete(ket_label_t label);

ket_error_code_t ket_label_index(ket_label_t label, size_t *index);

ket_error_code_t ket_label_pid(ket_label_t label, size_t *pid);

#ifdef __cplusplus
}
#endif
