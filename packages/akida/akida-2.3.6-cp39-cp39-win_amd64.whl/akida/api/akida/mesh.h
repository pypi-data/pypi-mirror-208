#pragma once

#include <memory>
#include <vector>

#include "akida/hardware_device.h"
#include "akida/np.h"

namespace akida {

namespace mesh {

/**
 * Discover the topology of a Device Mesh
 */
AKIDASHAREDLIB_EXPORT std::unique_ptr<np::Mesh> discover(
    HardwareDevice* device);

}  // namespace mesh

}  // namespace akida
