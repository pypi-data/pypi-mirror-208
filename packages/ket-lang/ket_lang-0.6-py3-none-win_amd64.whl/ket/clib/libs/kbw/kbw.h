#pragma once
#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>

typedef void* kbw_ket_process_t;
typedef int32_t kbw_error_code_t;

#define KBW_DENSE 0
#define KBW_SPARSE 1

#define KBW_JSON 0
#define KBW_BIN 1

const uint8_t* kbw_error_message(int32_t error_code, size_t* size);

kbw_error_code_t kbw_run_and_set_result(kbw_ket_process_t process,
                                        int32_t sim_mode);

kbw_error_code_t kbw_run_serialized(const uint8_t* quantum_code,
                                    size_t quantum_code_size,
                                    const uint8_t* metrics, size_t metrics_size,
                                    int32_t data_type, int32_t sim_mode,
                                    void** result);

kbw_error_code_t kbw_result_get(void* result, uint8_t** data, size_t* size);

kbw_error_code_t kbw_result_delete(void* result);

#ifdef __cplusplus
}
#endif
