#pragma once

#include <cstddef>
#include <cstdint>

#include "infra/exports.h"

namespace akida {

/**
 * @brief Return the number of bytes required to store 1 input for the given
 * program
 * @param program: the program whose input size will be requested
 */
AKIDASHAREDLIB_EXPORT
size_t input_memory_required(const uint8_t* program);

/**
 * @brief Return the number of bytes required to store 1 output for the given
 * program
 * @param program: the program whose output size will be requested
 */
AKIDASHAREDLIB_EXPORT
size_t output_memory_required(const uint8_t* program);

/**
 * @brief Return the number of bytes required for 1 input descriptor for the
 * given program
 * @param program: the program whose required input dma size will be requested
 */
AKIDASHAREDLIB_EXPORT
size_t input_descriptor_memory_required(const uint8_t* program);

/**
 * @brief Return the number of bytes required for program descriptors
 * @param program: the program whose descriptors required size will be requested
 */
AKIDASHAREDLIB_EXPORT
size_t program_descriptors_memory_required(const uint8_t* program);

/**
 * @brief Return the number of bytes required for program
 * @param program: the program whose size will be requested
 */
AKIDASHAREDLIB_EXPORT
size_t program_data_memory_required(const uint8_t* program);

/**
 * @brief Return the number of bytes required for extra program data
 * @param program: the program whose extra data size will be requested
 */
AKIDASHAREDLIB_EXPORT
size_t extra_program_memory_required(const uint8_t* program);

}  // namespace akida
