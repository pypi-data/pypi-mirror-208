#include "akida/hardware_device.h"

/**
 * @brief Akida model unit test based on TESTNAME configuration
 *
 * The implementation of the method relies on three serialized arrays:
 * - the model,
 * - the predefined test inputs,
 * - the expected test outputs.
 *
 * This method loads the model, the inputs and the outputs from the serialized
 * arrays.
 *
 * It then performs an inference on the predefined inputs and compares the
 * result with the expected outputs.
 *
 * @return true if the model outputs match the expected outputs.
 */
bool TEST_NAME();
