#include <iostream>
#include <memory>

#include "akida/dense.h"
#include "akida/model.h"

#include "TEST_NAME/inputs.h"
#include "TEST_NAME/model.h"
#include "TEST_NAME/outputs.h"

#define SUCCESS true
#define FAILURE false

akida::DensePtr to_dense_ptr(const unsigned char* array, size_t lenght,
                             akida::TensorType type, akida::Shape shape) {
  auto signed_array = reinterpret_cast<const char*>(array);
  return akida::Dense::copy(signed_array, lenght, type, shape,
                            akida::Dense::Layout::RowMajor);
}

bool TEST_NAME() {
  // Arrange
  auto model_buffer = reinterpret_cast<const char*>(model);
  auto ak_model = akida::Model::from_buffer(model_buffer, model_len);
  auto dense_input =
      to_dense_ptr(inputs, inputs_len, inputs_type, inputs_shape);
  auto dense_output =
      to_dense_ptr(outputs, outputs_len, outputs_type, outputs_shape);

  // Act
  auto ak_outputs = ak_model->forward(dense_input);

  // Assert
  if (!(*ak_outputs == *dense_output)) {
    return FAILURE;
  }

  return SUCCESS;
}
