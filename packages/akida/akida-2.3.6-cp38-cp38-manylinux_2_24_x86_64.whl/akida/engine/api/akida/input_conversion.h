#pragma once

#include <cstdint>

#include "akida/dense.h"
#include "akida/sparse.h"

namespace akida {

namespace conversion {

const Sparse* as_sparse(const Tensor& input);

SparseUniquePtr to_sparse(const Dense& input, const uint8_t* program);

const Dense* as_dense(const Tensor& input);

DenseUniquePtr to_dense(const Sparse& input);

bool dense_input_expected(const uint8_t* program);

}  // namespace conversion
}  // namespace akida
