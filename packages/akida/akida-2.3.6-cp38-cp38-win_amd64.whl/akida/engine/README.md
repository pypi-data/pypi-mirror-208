# Akida Engine library

The **Akida Engine** library is a C++ library allowing to perform an inference
on an Akida model loaded into an Akida compatible device.

As a prerequisite, the Akida model program has to be generated on a host using
the [Akida python package](https://pypi.org/project/Akida/).

## Building the library

### Build system

The Akida Engine library does not have any specific build system requirements.

### Toolchain/Compiler

The Akida Engine library requires a 32 or 64 bit little endian toolchain with
support for floating point numbers.

The toolchain must include a C++ compiler supporting at least C++ 11.

The toolchain must provide a minimal implementation of the C standard library,
like for instance GCC newlib and the corresponding target-specific stubs.

The Akida Engine library does not use C++ exceptions, so exception support can
be disabled when generating binaries for embedded targets.

### Dependencies

The library relies on external symbols whose target-specific implementation must
be provided by the build system.

#### Google flatbuffers

The library has a dependency towards the Google flatbuffer header-only library:
   https://github.com/google/flatbuffers/releases/tag/v2.0.6

The sources must be downloaded from the link above and made available to the
library as an additional include path.

#### Standard Template Library (STL)

The Akida Engine library relies on a few C++ STL classes whose implementation
must be provided by the build system.

The following headers must be supported:

~~~~cpp
<algorithm>
<array>
<functional>
<memory>
<queue>
<set>
<tuple>
<typeindex>
<vector>
~~~~

#### System infra

The Akida Engine library requires a few system methods to be implemented.

Please refer to api/infra/system.h for a list and description of the methods to
implement.

### Building a static library

A basic cmake build file is provided for convenience:

~~~~
mkdir build
cmake . -B build
make -C build
~~~~

### Using the library

#### Hardware driver

The Akida Engine library primary entry point is the HardwareDevice class.

One can obtain an HardwareDevice instance by passing a target-specific
HardwareDriver instance to HardwareDevice::create().

~~~~cpp
#include "akida/hardware_device.h"
#include "infra/hardware_driver.h"

class MyDriver : public HardwareDriver {
...
}

...

auto driver = MyDriver();
auto device = HardwareDevice::create(driver);
~~~~

The HardwareDriver main purpose is to abstract the read and write operations
into the Akida DMA.
It also provides:
- the base address for Akida blocks registers
- the 'scratch' memory region where the library can allocate buffers to
communicate with the Akida DMA (runtime configuration, inputs/outputs).
- the 'visible from akida' memory region, defining the memory region directly
accessible by Akida DMAs.
Data put in this area will not be copied to scratch memory.

Please refer to api/infra/hardware_driver.h for a complete description of the
HardwareDriver API and how to implement your specific driver.

##### BareMetalDriver class

BareMetalDriver, a custom HardwareDriver implementation, is provided as an
example.
Its constructor takes 4 arguments that you can use to customize your
application:
- scratch_base_address: the base 'scratch' memory address.
- scratch_size: the size of 'scratch' memory that can be used. In case of
 overflow, application will panic at runtime.
- akida_visible_memory_base: the base address where Akida DMAs can directly
acccess data. This can be the location where program and inputs are put,
so they don't need to be copied to 'scratch' memory
- akida_visible_memory_size: the size of the 'visible' memory region.

#### Generate model programs

The akida engine library allows to program an akida device with machine
learning models previously trained and compiled.

The akida and cnn2snn python packages are required to generate model programs
from pre-trained keras models.

The akida_models python package contains helpers to fetch models from the akida
model zoo.

~~~~python
#!/usr/bin/env python
import os
from akida import AKD1000
from akida.generate array_to_cpp
from cnn2snn import convert
from akida_models import ds_cnn_kws_pretrained

# Load Keras pre-trained model from Akida model zoo
model_keras = ds_cnn_kws_pretrained()

# Convert Keras model to Akida
model_akida = convert(model_keras)

# Map/compile converted model for an AKD1000 device
model_akida.map(device=AKD1000(), hw_only=True)

# Check model mapping: NP allocation and binary size
model_akida.summary()

# Retrieve model program binary
program = model_akida.sequences[0].program

# Generate a binary that can be flashed
with open('kws_model.bin', 'wb') as file:
    file.write(program)
    file.close()

# Or generate source files to be included -> kws_model.{cpp,h}
    array_to_cpp('.’, program, 'kws_model')
~~~~

#### Load model programs

Once loaded in memory, the raw bytes buffer corresponding to a model program
can be passed to the HardwareDevice to program the model on the device.

~~~~cpp
#include "kws_model.h"

// Load program
device->program(kws_model, kws_model_size);
~~~~

#### Set batch size

After programming, one must configure the batch size to the number of inputs
that can be enqueued before fetching for outputs. A higher batch size has
higher memory requirements, but can allow for inputs pipelining. The batch size
must be set by calling `set_batch_size` function.
This function takes a `requested_batch_size` parameter, which is the batch size
one wants to set, and a boolean `allocate_inputs` to allocate space for inputs
in scratch memory.
`allocate_inputs` must be set to `true` if inputs are not in the range
specified by `akida_visible_memory_base` and `akida_visible_memory_size`.
Outputs are always allocated in scratch memory.

Note: the maximum effective batch size is 15 for a single pass program, or 1 if
the program is multi pass, or learning mode have been enabled. Passing a higher
value is allowed, but the effective batch size that has been set is returned by
`set_batch_size` method.

~~~~cpp
// Assume device has been programmed

// set a batch size of 2, and do not allocate space for inputs (they must be in
// the range specified by driver->akida_visible_memory_base(),
// driver->akida_visible_memory_size())
device->set_batch_size(2, false);
~~~~

#### Perform an inference

Once a model has been programmed and a batch size is set, inputs Tensor can be
enqueued into the device inference pipeline, by calling `enqueue` function. The
function immediately returns a boolean set to true if the tensor was
successfully enqueued, or false if the pipeline was full.
Depending on your program and device, you may have to convert your inputs to a
sparse format.

Two types of tensors can be passed as input and returned as outputs:
- Dense tensors are standard contiguous buffers whose items are ordered either
using the row-major or col-major convention,
- Sparse tensors are list of coordinates and values. These cannot be directly
constructed, they are output from Akida, or converted from a Dense.

Several static constructors are available to create tensors, depending on your
use case: pre-allocate, copy, etc.
Conversion functions also exist.

~~~~cpp
#include "akida/dense.h"

// Enqueue a single input from a raw input dense buffer
auto input = Dense::create_view(input_buf, TensorType::uint8, {49, 10, 1},
                                TensorLayout::RowMajor);
bool success = device->enqueue(*input);
~~~~

Then you can periodically check for outputs, by calling `fetch` function.
The function returns a pointer to an output Tensor, or nullptr if no output
was available.

~~~~cpp
auto output = device->fetch();
if (output != nullptr) {
    // do something with output
}
~~~~

If your program last layer ends with an activation, the outputs are normalized
n-bit values.
Otherwise, if your program does not end with an activation, you must dequantize
the output potentials to float values to project them in the same scale before
processing them. You can use the `dequantize` method to do so.

#### Perform edge learning

To perform edge learning, the generated model should have been compiled
beforehand.

Example:
~~~~python
model.compile(
    optimizer=akida.AkidaUnsupervised(
        num_weights=num_weights,
        num_classes=num_classes,
        learning_competition=learning_competition
        )
    )
~~~~

See https://doc.brainchipinc.com/examples/index.html#edge-examples
for more informations about learning and learning parameters.

Then, to activate edge learning in your application, you must call
`toggle_learn` method with the `learn_en` parameter set to `true`.
You can then pass a label corresponding to your input when calling `enqueue`.
Learning can be disabled by calling `toggle_learn` again with the `learn_en`
parameter set to `false`.
~~~~cpp
#include "akida/dense.h"

#include "kws_model.h"

// Program device (this is not required if you already did it previously)
device->program(kws_model, kws_model_size);

// Turn learning mode on because learning is disabled by default
device->toggle_learn(true);

// Set batch size to 1 because learning is on
device->set_batch_size(1, false);

// Enqueue a single input from a raw input dense buffer
auto input = Dense::create_view(input_buf, TensorType::uint8, {49, 10, 1},
                                TensorLayout::RowMajor);
// passing a single label
bool success = device->enqueue(input, 1);
~~~~

##### Updating weights

Weights used for learn are initially stored in the program buffer, then used to
program the FNP (FullyConnected Neural Processor) that will perform the learn.
In order to retrieve updated weights when learn is used, there are two possible
situations, depending on the FNP type used:

- FNP3 type: Akida has weights stored in its own SRAM, so a copy back from
internal SRAM to application memory must be done. To do that, a buffer must be
allocated with the correct size. `HardwareDevice::learn_mem_size()` method can
be called to know this size.
The output of this function is the number of 32 bits words required.
Then you can call `HardwareDevice::learn_mem(output_buffer)` that will copy
weights to the `output_buffer` parameter.

- FNP2 type: Akida reads directly weights from memory,
so that memory will be updated automatically after each fit call.
Note that if weights were not in 'akida visible memory', they have been copied
to 'scratch' memory, so only scratch memory have been updated. To update your
initial program, you will have to proceed the same way as FNP3.

~~~~cpp
std::vector<uint32_t> updated_weights(device->learn_mem_size());
device->learn_mem(updated_weights.data());
~~~~

The application can then store this buffer.
This can be reprogrammed by calling
`HardwareDevice::update_learn_mem(stored_weights)`, e.g. to restore learned
 weights after a power cycle.

~~~~cpp
// program Akida, e.g. after power cycle
device->program(model_buffer, model_size);

// toggle learning mode on
device->toggle_learn(true);

// set batch size to 1 because learning is on
device->set_batch_size(1, false);

std::vector<uint32_t> stored_weights = /* load weights from application */
// program previously saved weights to Akida
device->update_learn_mem(stored_weights.data());
~~~~

#### Higher level API

A higher level API is available as convenience:
- `forward` method that perform inference on vector of input Tensor, and
returns a vector of output Tensor.
- `predict` method, similar to forward but also performing the dequantize step.
- `fit` method that perform inference on vector of input Tensor, along with a
vector of labels, and returns a vector of output Tensor.

### Generating test applications

The test directory contains several 'fixtures' allowing to generate unit test
applications using the akida package.

~~~~
akida generate --fixture-files test/fixtures/*.py
               --dest-path <path>
~~~~

## Licensing

Copyright 2022 Brainchip, Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
