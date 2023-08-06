#pragma once

#include <cstddef>
#include <cstdint>

#include "akida/shape.h"
#include "dma_events_ops.h"

#include "hardware_device_impl.h"
#include "multipass_memory.h"

namespace akida {
namespace program {

void rewind(HardwareDeviceImpl* device, const uint8_t* program_data);

void play_single_pass(HardwareDeviceImpl* device, const uint8_t* program_data);
void play_multi_pass(HardwareDeviceImpl* device, const uint8_t* program_data,
                     MultiPassMemory* multipass_memory);

void configure_learning_mode_single_pass(HardwareDeviceImpl* device,
                                         const uint8_t* program_data,
                                         bool learn_en);
void configure_learning_mode_multi_pass(HardwareDeviceImpl* device,
                                        const uint8_t* program_data,
                                        const MultiPassMemory& multipass_memory,
                                        bool learn_en);

void verify(const HardwareDeviceImpl& device, const uint8_t* data, size_t size);

// Utility functions to get informations from program
const Index* input_dims(const uint8_t* program_data);
Shape output_dims(const uint8_t* program_data);
bool input_is_dense(const uint8_t* program_data);
bool input_is_fnp(const uint8_t* program_data);
bool output_is_dense(const uint8_t* program_data);
dma::OutputFormat output_format(const uint8_t* program_data);
bool activation(const uint8_t* program_data);
uint32_t dense_window_w(const uint8_t* program_data);
uint32_t dense_window_h(const uint8_t* program_data);
bool can_learn(const uint8_t* program_data);
uint32_t learn_mem_size(const uint8_t* program_data);
void learn_mem(HardwareDeviceImpl* device, const uint8_t* program_data,
               uint32_t* ram_dump);
void update_learn_mem(HardwareDeviceImpl* device, const uint8_t* program_data,
                      const uint32_t* ram_dump);
uint8_t max_num_desc(const uint8_t* program_data);
bool is_multi_pass(const uint8_t* program_data);
uint32_t num_passes(const uint8_t* program_data);
// returns the number of program descriptors required for a given program (it
// does not include extra descriptor for learning if any)
uint32_t number_of_program_descriptors_required(const uint8_t* program_data);
// returns number of extra descriptors for a multipass program
uint32_t number_of_extra_program_descriptors_required(
    const uint8_t* program_data);
size_t program_data_required_memory(const uint8_t* program_data);
size_t fnp2_tracks_byte_size(const uint8_t* program_data);

template<typename Type>
using Buffer = std::pair<const Type*, size_t>;
Buffer<int32_t> shifts(const uint8_t* program_data);
Buffer<float> scales(const uint8_t* program_data);

}  // namespace program
}  // namespace akida
