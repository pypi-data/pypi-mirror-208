#pragma once
#include <cstdint>

#include "akida/shape.h"
#include "akida/tensor.h"
#include "engine/dma.h"
#include "infra/hardware_driver.h"

#include "dma_desc_ops.h"
#include "dma_events.h"

namespace akida {

namespace dma {

enum class OutputFormat {
  ConvActivations /**<Convolution Sparse 4-bit Activations*/,
  HrcActivations /**<Convolution Sparse 4-bit Activations in HRC*/,
  ConvPotentials /**<Convolution Sparse 20-bit Potentials*/,
  ConvHighPotentials /**<Convolution Sparse 24-bit Potentials*/,
  FullyActivations /**<FullyConnected Sparse 4-bit Activations*/,
  FullyPotentials /**<FullyConnected Sparse 20-bit Potentials*/,
  DenseActivations /**<Dense 4-bit Activations*/,
  DensePotentials /**<Dense 32-bit Potentials*/
};

}  // namespace dma

// convert tensor to dma events
DmaEventsPtr to_dma_events(const Tensor& inputs, bool input_is_fnp);

// Read events at the given memory address and reformat them to spikes
TensorUniquePtr dma_events_read_outputs(HardwareDriver* driver,
                                        const uint32_t addr_output_events,
                                        const Shape output_dimensions,
                                        dma::OutputFormat output_format);

}  // namespace akida
