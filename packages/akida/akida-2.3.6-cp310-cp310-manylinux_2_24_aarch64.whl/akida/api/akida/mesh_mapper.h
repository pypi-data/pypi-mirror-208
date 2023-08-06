#pragma once

#include <memory>
#include <tuple>
#include <vector>

#include "akida/device.h"
#include "akida/layer.h"
#include "infra/exports.h"
#include "np_mapping.h"

namespace akida {

class MeshMapper;

using MeshMapperPtr = std::shared_ptr<MeshMapper>;

class AKIDASHAREDLIB_EXPORT MeshMapper {
 public:
  virtual ~MeshMapper() {}
  /**
   * @brief Select a set of Neural Processors (NP)
   *
   * This allows to select from a predefined list a specified number of NPs.
   */
  virtual np::IdentVector select_nps(const np::IdentVector& source_nps,
                                     size_t num_nps, np::Type type) = 0;

  /**
   * @brief Get the maximum width allowed for a CNP
   */
  virtual uint32_t cnp_max_width() = 0;

  /**
   * @brief Get the maximum height allowed for a CNP
   */
  virtual uint32_t cnp_max_height() = 0;

  /**
   * @brief Get the maximum number of filters allowed for a CNP
   */
  virtual uint32_t cnp_max_filters() = 0;

  /**
   * @brief Override the default MeshMapper
   *
   * Passing nullptr to this method restores the default MeshMapper.
   *
   * @param : a pointer to a MeshMapper instance, or nullptr
   */
  static void replace(MeshMapperPtr mapper);
};

}  // namespace akida
