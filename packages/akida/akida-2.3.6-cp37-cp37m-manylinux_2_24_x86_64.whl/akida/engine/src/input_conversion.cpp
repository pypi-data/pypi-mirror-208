#include "akida/input_conversion.h"

#include "akida/dense.h"
#include "akida/sparse.h"

#include "dma_events.h"
#include "program_play.h"

namespace akida {

namespace conversion {
const Sparse* as_sparse(const Tensor& input) {
  return dynamic_cast<const DmaEvents*>(&input);
}

SparseUniquePtr to_sparse(const Dense& input, const uint8_t* program) {
  const auto nb_dims = input.dimensions().size();
  if (nb_dims != 3 && nb_dims != 1) {
    panic("Sparse can only be 1D or 3D");
  }
  return to_dma_events(input, program::input_is_fnp(program));
}

const Dense* as_dense(const Tensor& input) {
  return dynamic_cast<const Dense*>(&input);
}

DenseUniquePtr to_dense(const Sparse& input) {
  return Dense::from_sparse(input, Dense::Layout::RowMajor);
}

bool dense_input_expected(const uint8_t* program) {
  return program::input_is_dense(program);
}

}  // namespace conversion
}  // namespace akida
